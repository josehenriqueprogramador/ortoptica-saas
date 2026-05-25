import asyncio
import math
import time
import cv2
import numpy as np
import mediapipe as mp
from collections import deque
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(
    title="Computational Orthoptics Spatial Ray-Casting Engine",
    version="4.0.0"
)

mp_face_mesh = mp.solutions.face_mesh

# --- 1. ENGENHARIA DE SINAIS: FILTRO DE KALMAN 1D ---
class OcularKalmanFilter:
    """Filtro de Kalman Monodimensional para suavização de jitter estocástico."""
    def __init__(self, q_process_noise=1e-4, r_measure_noise=1e-2):
        self.q = q_process_noise  
        self.r = r_measure_noise  
        self.x_estimated = None   
        self.p_covariance = 1.0   

    def filter(self, measurement: float) -> float:
        if self.x_estimated is None:
            self.x_estimated = measurement
            return self.x_estimated
        self.p_covariance = self.p_covariance + self.q
        kalman_gain = self.p_covariance / (self.p_covariance + self.r)
        self.x_estimated = self.x_estimated + kalman_gain * (measurement - self.x_estimated)
        self.p_covariance = (1 - kalman_gain) * self.p_covariance
        return self.x_estimated

# --- 2. BIOMECÂNICA: AVALIADOR CINEMÁTICO BASEADO EM VETOR DE OLHAR REAL ---
class OcularKinematicsEvaluator:
    """Analisa velocidade e aceleração angular a partir do vetor de olhar real suavizado."""
    def __init__(self, window_size=30):
        self.history_left = deque(maxlen=window_size)
        self.history_right = deque(maxlen=window_size)
        self.MAX_PHYSIOLOGICAL_VELOCITY = 800.0  # Graus/segundo

    def _calculate_eye_kinematics(self, history, h_curr, v_curr, t_curr):
        kinematics = {"velocity_deg_s": 0.0, "acceleration_deg_s2": 0.0, "behavior": "Stable Fixation", "valid_signal": True}
        v_angular = 0.0
        
        if len(history) > 0:
            t_prev, h_prev, v_prev, vel_prev = history[-1]
            dt = t_curr - t_prev

            if dt > 0.0001:
                dh = h_curr - h_prev
                dv = v_curr - v_prev
                angular_displacement = math.sqrt(dh**2 + dv**2)
                v_angular = angular_displacement / dt
                
                if v_angular > self.MAX_PHYSIOLOGICAL_VELOCITY:
                    kinematics["behavior"] = "Tracking Artifact / Teleportation"
                    kinematics["valid_signal"] = False
                    return kinematics

                a_angular = (v_angular - vel_prev) / dt
                kinematics["velocity_deg_s"] = round(v_angular, 2)
                kinematics["acceleration_deg_s2"] = round(a_angular, 2)

                if v_angular > 280.0:
                    kinematics["behavior"] = "Saccade (Movimento Rápido)"
                elif v_angular > 40.0 and abs(a_angular) > 500.0:
                    kinematics["behavior"] = "Nystagmus Phase / Micro-correction"
                elif v_angular < 8.0:
                    kinematics["behavior"] = "Stable Fixation"
                else:
                    kinematics["behavior"] = "Smooth Pursuit / Drift"
                    
        history.append((t_curr, h_curr, v_curr, v_angular))
        return kinematics

    def analyze(self, left_angles: dict, right_angles: dict) -> dict:
        t_current = time.perf_counter()
        return {
            "left_eye": self._calculate_eye_kinematics(self.history_left, left_angles["horizontal"], left_angles["vertical"], t_current),
            "right_eye": self._calculate_eye_kinematics(self.history_right, right_angles["horizontal"], right_angles["vertical"], t_current)
        }

# --- 3. MOTOR ESPACIAL DE RECONSTRUÇÃO 3D (RAY-SPHERE INTERSECTION) ---
class OcularTrackingSession:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # PRIORIDADE 1: Filtros de Kalman dedicados para estabilização de Pose Craniana (6 eixos)
        self.pose_filters = {
            "rvec_0": OcularKalmanFilter(q_process_noise=1e-5, r_measure_noise=1e-2),
            "rvec_1": OcularKalmanFilter(q_process_noise=1e-5, r_measure_noise=1e-2),
            "rvec_2": OcularKalmanFilter(q_process_noise=1e-5, r_measure_noise=1e-2),
            "tvec_0": OcularKalmanFilter(q_process_noise=1e-4, r_measure_noise=1e-1),
            "tvec_1": OcularKalmanFilter(q_process_noise=1e-4, r_measure_noise=1e-1),
            "tvec_2": OcularKalmanFilter(q_process_noise=1e-4, r_measure_noise=1e-1)
        }

        # Filtros para os landmarks 2D das íris antes do Ray-Casting
        self.iris_filters = {
            "lx": OcularKalmanFilter(), "ly": OcularKalmanFilter(),
            "rx": OcularKalmanFilter(), "ry": OcularKalmanFilter()
        }
        
        self.kinematics_engine = OcularKinematicsEvaluator(window_size=30)
        
        # Constantes Biométricas e Anatômicas do Olho Humano Padrão
        self.EYEBALL_RADIUS_MM = 12.0  # Raio médio esférico escleral

        # MODELO FACIAL 3D CANÔNICO RÍGIDO (Referencial do Crânio com Origem na Ponta do Nariz)
        self.FACE_MODEL_3D = np.array([
            [0.0, 0.0, 0.0],          # Nose tip (Landmark 1)
            [0.0, -63.6, -12.5],      # Chin (Landmark 152)
            [-43.3, 32.7, -26.0],     # Left Eye Outer Corner (Landmark 33)
            [43.3, 32.7, -26.0],      # Right Eye Outer Corner (Landmark 263)
            [-28.9, -28.9, -24.1],    # Left Mouth Corner (Landmark 61)
            [28.9, -28.9, -24.1]      # Right Mouth Corner (Landmark 291)
        ], dtype=np.float64)

        # ETAPA A: Centros anatômicos dos globos oculares fixados rigidamente no espaço craniano
        self.LEFT_EYEBALL_CENTER_3D = np.array([-32.0, 32.7, -28.0], dtype=np.float64)
        self.RIGHT_EYEBALL_CENTER_3D = np.array([32.0, 32.7, -28.0], dtype=np.float64)

    def _intersect_ray_sphere(self, ray_direction, sphere_center_camera):
        """
        Calcula matematicamente a interseção exata entre o raio óptico e a esfera ocular.
        Equação quadrática: t^2 - 2(d.c)t + (||c||^2 - R^2) = 0
        """
        # Origem do raio da câmera é intrinsicamente (0,0,0)
        dot_dc = np.dot(ray_direction, sphere_center_camera)
        mag_c2 = np.dot(sphere_center_camera, sphere_center_camera)
        
        discriminant = (dot_dc ** 2) - mag_c2 + (self.EYEBALL_RADIUS_MM ** 2)
        
        if discriminant < 0:
            # Fallback geométrico de contingência caso o raio passe raspando tangencialmente
            return sphere_center_camera + (ray_direction * self.EYEBALL_RADIUS_MM)
            
        # Retorna o ponto mais próximo da lente da câmera (superfície anterior/córnea)
        t = dot_dc - math.sqrt(discriminant)
        return ray_direction * t

    def process_frame(self, frame_bytes: bytes) -> dict:
        np_array = np.frombuffer(frame_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        if image is None:
            return {"face_detected": False, "status": "corrupted_frame"}

        height, width, _ = image.shape
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)

        if not results.multi_face_landmarks:
            return {"face_detected": False, "status": "no_face_tracked"}

        landmarks = results.multi_face_landmarks[0].landmark

        # Gating Fisiológico Inicial: Detecção de Piscada (EAR)
        p_le_top, p_le_bottom = landmarks[159], landmarks[145]
        le_opening = math.sqrt((p_le_top.x - p_le_bottom.x)**2 + (p_le_top.y - p_le_bottom.y)**2)
        if le_opening < 0.015:
            return {"face_detected": True, "status": "blink_detected"}

        # Extração de pontos rígidos 2D para o PnP
        image_points = np.array([
            [landmarks[1].x * width, landmarks[1].y * height],
            [landmarks[152].x * width, landmarks[152].y * height],
            [landmarks[33].x * width, landmarks[33].y * height],
            [landmarks[263].x * width, landmarks[263].y * height],
            [landmarks[61].x * width, landmarks[61].y * height],
            [landmarks[291].x * width, landmarks[291].y * height]
        ], dtype=np.float64)

        # Matriz Intrínseca Inicial K
        focal_length = width
        center_x, center_y = width / 2.0, height / 2.0
        camera_matrix = np.array([
            [focal_length, 0, center_x],
            [0, focal_length, center_y],
            [0, 0, 1]
        ], dtype=np.float64)
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        # Resolução robusta da Pose da cabeça via PnP
        success, rvec_raw, tvec_raw = cv2.solvePnP(
            self.FACE_MODEL_3D, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return {"face_detected": True, "status": "pnp_geometry_failed"}

        # PRIORIDADE 1: Suavização temporal fina dos vetores de Pose (Remoção do tremor espacial)
        rvec = np.array([
            self.pose_filters["rvec_0"].filter(rvec_raw[0][0]),
            self.pose_filters["rvec_1"].filter(rvec_raw[1][0]),
            self.pose_filters["rvec_2"].filter(rvec_raw[2][0])
        ]).reshape((3, 1))

        tvec = np.array([
            self.pose_filters["tvec_0"].filter(tvec_raw[0][0]),
            self.pose_filters["tvec_1"].filter(tvec_raw[1][0]),
            self.pose_filters["tvec_2"].filter(tvec_raw[2][0])
        ]).reshape((3, 1))

        # Matriz de Rotação Homogênea R
        R, _ = cv2.Rodrigues(rvec)

        # Telemetria angular da cabeça (Ângulos de Euler) para descarte de posturas espúrias
        pitch = math.degrees(math.atan2(-R[1, 2], R[2, 2]))
        yaw = math.degrees(math.atan2(R[0, 2], math.sqrt(R[1, 2]**2 + R[2, 2]**2)))
        roll = math.degrees(math.atan2(-R[0, 1], R[0, 0]))
        z_depth_cm = float(tvec[2]) / 10.0

        # Transformação dos Centros Anatômicos Oculares do Crânio para o Espaço da Câmera
        center_left_cam = R @ self.LEFT_EYEBALL_CENTER_3D + tvec.flatten()
        center_right_cam = R @ self.RIGHT_EYEBALL_CENTER_3D + tvec.flatten()

        # Captura filtrada das coordenadas de pixel 2D das Íris
        l_iris_x = self.iris_filters["lx"].filter(landmarks[468].x * width)
        l_iris_y = self.iris_filters["ly"].filter(landmarks[468].y * height)
        r_iris_x = self.iris_filters["rx"].filter(landmarks[473].x * width)
        r_iris_y = self.iris_filters["ry"].filter(landmarks[473].y * height)

        # ETAPA B: Construção do Raio Óptico Unitário da Câmera ($ r = K^{-1} \cdot p $)
        K_inv = np.linalg.inv(camera_matrix)
        
        ray_left_dir = K_inv @ np.array([l_iris_x, l_iris_y, 1.0])
        ray_left_dir /= np.linalg.norm(ray_left_dir) # Normalização do vetor unitário de direção

        ray_right_dir = K_inv @ np.array([r_iris_x, r_iris_y, 1.0])
        ray_right_dir /= np.linalg.norm(ray_right_dir)

        # ETAPA C: Interseção Geométrica Real entre Raio e as Esferas Oculares 3D (Espaço da Câmera)
        p_iris_left_cam = self._intersect_ray_sphere(ray_left_dir, center_left_cam)
        p_iris_right_cam = self._intersect_ray_sphere(ray_right_dir, center_right_cam)

        # Inversão de Espaço: Mapeando os pontos tridimensionais de volta para o ambiente craniano isolado
        p_iris_left_cranial = R.T @ (p_iris_left_cam - tvec.flatten())
        p_iris_right_cranial = R.T @ (p_iris_right_cam - tvec.flatten())

        # PRIORIDADE 3: Gaze Vector Unitário Real do Olhar no espaço tridimensional estável ($ \vec{gaze} $)
        v_gaze_left = p_iris_left_cranial - self.LEFT_EYEBALL_CENTER_3D
        v_gaze_left /= np.linalg.norm(v_gaze_left)

        v_gaze_right = p_iris_right_cranial - self.RIGHT_EYEBALL_CENTER_3D
        v_gaze_right /= np.linalg.norm(v_gaze_right)

        # Extração Trigonométrica Esférica Estável dos Ângulos Médicos (Invariância Absoluta)
        left_angles = {
            "horizontal": math.degrees(math.atan2(v_gaze_left[0], v_gaze_left[2])),
            "vertical": math.degrees(math.atan2(v_gaze_left[1], v_gaze_left[2]))
        }
        right_angles = {
            "horizontal": math.degrees(math.atan2(v_gaze_right[0], v_gaze_right[2])),
            "vertical": math.degrees(math.atan2(v_gaze_right[1], v_gaze_right[2]))
        }

        # Pipelines Cinemáticos alimentados puramente por dados esféricos puros
        kinematics_report = self.kinematics_engine.analyze(left_angles, right_angles)

        # Avaliação de Assimetria de Alinhamento Binocular (Triagem Estrábica)
        alignment_str = "Ortoforia (Alinhamento Normal)"
        desvio_limiar = 4.5  
        diff_horizontal = left_angles["horizontal"] - right_angles["horizontal"]
        
        if diff_horizontal > desvio_limiar:
            alignment_str = "Assimetria Binocular (Suspeita de Exotropia)"
        elif diff_horizontal < -desvio_limiar:
            alignment_str = "Assimetria Binocular (Suspeita de Esotropia)"

        return {
            "face_detected": true,
            "status": "tracking_active",
            "head_telemetry": {
                "distance_cm": round(z_depth_cm, 1),
                "pitch_deg": round(pitch, 1),
                "yaw_deg": round(yaw, 1),
                "roll_deg": round(roll, 1)
            },
            "gaze_vectors_3d": {
                "left_eye_vector": {"x": round(v_gaze_left[0], 4), "y": round(v_gaze_left[1], 4), "z": round(v_gaze_left[2], 4)},
                "right_eye_vector": {"x": round(v_gaze_right[0], 4), "y": round(v_gaze_right[1], 4), "z": round(v_gaze_right[2], 4)},
                "left_eye_angles_deg": left_angles,
                "right_eye_angles_deg": right_angles
            },
            "kinematics_analysis": kinematics_report,
            "clinical_evaluation": {
                "status": alignment_str,
                "inter_ocular_diff_deg": round(abs(diff_horizontal), 2)
            }
        }

    def close(self):
        self.face_mesh.close()

# --- 4. ENDPOINT WEBSOCKET MULTI-SESSION SECURE ---
@app.websocket("/tracking/stream")
async def websocket_tracking_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = OcularTrackingSession()
    print("🚀 Engine v4.0.0 Online. Ray-Casting Tridimensional Ativo e Estabilizado.")

    try:
        while True:
            data = await websocket.receive_bytes()
            analysis_result = session.process_frame(data)
            await websocket.send_json(analysis_result)
            
    except WebSocketDisconnect:
        print("🛑 Conexão interrompida de forma controlada.")
    except Exception as e:
        print(f"⚠️ Falha operacional no loop Ray-Casting: {str(e)}")
    finally:
        session.close()
        print("🧹 Memória desalocada. Estruturas geométricas limpas.")
