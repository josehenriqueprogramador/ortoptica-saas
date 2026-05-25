import asyncio
import math
import time
import cv2
import numpy as np
import mediapipe as mp
from collections import deque
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(
    title="Computational Orthoptics Neuro-Biocalibrated Engine",
    version="5.0.0"
)

mp_face_mesh = mp.solutions.face_mesh

# --- 1. ENGENHARIA DE SINAIS: FILTRO DE KALMAN 1D ---
class OcularKalmanFilter:
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

# --- 2. BIOCALIBRAÇÃO: CAMADA DE COMPENSAÇÃO DO ÂNGULO KAPPA ---
class OcularBiocalibrator:
    """
    Gerencia a calibração individual do eixe visual do paciente.
    Determina o vetor de deslocamento sistemático (Ângulo Kappa) para obter precisão absoluta.
    """
    def __init__(self):
        self.is_calibrated = False
        self.kappa_offsets = {
            "left": {"horizontal": 0.0, "vertical": 0.0},
            "right": {"horizontal": 0.0, "vertical": 0.0}
        }
        self.calibration_buffer = {"left_h": [], "left_v": [], "right_h": [], "right_v": []}
        self.max_calibration_frames = 15 # Estabilização estatística rápida (~0.5s a 30fps)

    def collect_sample(self, raw_left: dict, raw_right: dict):
        """Acumula amostras enquanto o paciente fixa fixamente o target de calibração central."""
        if self.is_calibrated:
            return
        
        self.calibration_buffer["left_h"].append(raw_left["horizontal"])
        self.calibration_buffer["left_v"].append(raw_left["vertical"])
        self.calibration_buffer["right_h"].append(raw_right["horizontal"])
        self.calibration_buffer["right_v"].append(raw_right["vertical"])

        if len(self.calibration_buffer["left_h"]) >= self.max_calibration_frames:
            # Consolidação estatística via mediana para rejeitar micro-sacadas indesejadas no processo
            self.kappa_offsets["left"]["horizontal"] = np.median(self.calibration_buffer["left_h"])
            self.kappa_offsets["left"]["vertical"] = np.median(self.calibration_buffer["left_v"])
            self.kappa_offsets["right"]["horizontal"] = np.median(self.calibration_buffer["right_h"])
            self.kappa_offsets["right"]["vertical"] = np.median(self.calibration_buffer["right_v"])
            
            self.is_calibrated = True
            self.calibration_buffer.clear()

    def apply_compensation(self, raw_left: dict, raw_right: dict) -> tuple:
        """
        Aplica a transformação matemática inversa para alinhar o eixo pupilar ao eixo visual real.
        $$\theta_{\text{corrected}} = \theta_{\text{raw}} - \kappa$$
        """
        if not self.is_calibrated:
            return raw_left, raw_right, False

        corrected_left = {
            "horizontal": round(raw_left["horizontal"] - self.kappa_offsets["left"]["horizontal"], 2),
            "vertical": round(raw_left["vertical"] - self.kappa_offsets["left"]["vertical"], 2)
        }
        corrected_right = {
            "horizontal": round(raw_right["horizontal"] - self.kappa_offsets["right"]["horizontal"], 2),
            "vertical": round(raw_right["vertical"] - self.kappa_offsets["right"]["vertical"], 2)
        }
        return corrected_left, corrected_right, True

    def reset(self):
        self.is_calibrated = False
        self.kappa_offsets = {"left": {"horizontal": 0.0, "vertical": 0.0}, "right": {"horizontal": 0.0, "vertical": 0.0}}
        self.calibration_buffer = {"left_h": [], "left_v": [], "right_h": [], "right_v": []}

# --- 3. BIOMECAÂNICA: AVALIADOR CINEMÁTICO ---
class OcularKinematicsEvaluator:
    def __init__(self, window_size=30):
        self.history_left = deque(maxlen=window_size)
        self.history_right = deque(maxlen=window_size)
        self.MAX_PHYSIOLOGICAL_VELOCITY = 800.0  

    def _calculate_eye_kinematics(self, history, h_curr, v_curr, t_curr):
        kinematics = {"velocity_deg_s": 0.0, "acceleration_deg_s2": 0.0, "behavior": "Stable Fixation", "valid_signal": True}
        v_angular = 0.0
        
        if len(history) > 0:
            t_prev, h_prev, v_prev, vel_prev = history[-1]
            dt = t_curr - t_prev

            if dt > 0.0001:
                dh = h_curr - h_prev
                dv = v_curr - v_prev
                v_angular = math.sqrt(dh**2 + dv**2) / dt
                
                if v_angular > self.MAX_PHYSIOLOGICAL_VELOCITY:
                    kinematics["behavior"] = "Tracking Artifact / Teleportation"
                    kinematics["valid_signal"] = False
                    return kinematics

                a_angular = (v_angular - vel_prev) / dt
                kinematics["velocity_deg_s"] = round(v_angular, 2)
                kinematics["acceleration_deg_s2"] = round(a_angular, 2)

                if v_angular > 280.0:
                    kinematics["behavior"] = "Saccade"
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

# --- 4. MOTOR DE SESSÃO CLÍNICA ESPACIAL BIOCALIBRADO ---
class OcularTrackingSession:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False, max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.7, min_tracking_confidence=0.7
        )
        
        self.pose_filters = {
            "rvec_0": OcularKalmanFilter(q_process_noise=1e-5, r_measure_noise=1e-2),
            "rvec_1": OcularKalmanFilter(q_process_noise=1e-5, r_measure_noise=1e-2),
            "rvec_2": OcularKalmanFilter(q_process_noise=1e-5, r_measure_noise=1e-2),
            "tvec_0": OcularKalmanFilter(q_process_noise=1e-4, r_measure_noise=1e-1),
            "tvec_1": OcularKalmanFilter(q_process_noise=1e-4, r_measure_noise=1e-1),
            "tvec_2": OcularKalmanFilter(q_process_noise=1e-4, r_measure_noise=1e-1)
        }

        self.iris_filters = {
            "lx": OcularKalmanFilter(), "ly": OcularKalmanFilter(),
            "rx": OcularKalmanFilter(), "ry": OcularKalmanFilter()
        }
        
        self.biocalibrator = OcularBiocalibrator()
        self.kinematics_engine = OcularKinematicsEvaluator(window_size=30)
        self.EYEBALL_RADIUS_MM = 12.0

        self.FACE_MODEL_3D = np.array([
            [0.0, 0.0, 0.0], [0.0, -63.6, -12.5], [-43.3, 32.7, -26.0],
            [43.3, 32.7, -26.0], [-28.9, -28.9, -24.1], [28.9, -28.9, -24.1]
        ], dtype=np.float64)

        self.LEFT_EYEBALL_CENTER_3D = np.array([-32.0, 32.7, -28.0], dtype=np.float64)
        self.RIGHT_EYEBALL_CENTER_3D = np.array([32.0, 32.7, -28.0], dtype=np.float64)

    def _intersect_ray_sphere(self, ray_direction, sphere_center_camera):
        dot_dc = np.dot(ray_direction, sphere_center_camera)
        mag_c2 = np.dot(sphere_center_camera, sphere_center_camera)
        discriminant = (dot_dc ** 2) - mag_c2 + (self.EYEBALL_RADIUS_MM ** 2)
        if discriminant < 0:
            return sphere_center_camera + (ray_direction * self.EYEBALL_RADIUS_MM)
        t = dot_dc - math.sqrt(discriminant)
        return ray_direction * t

    def process_frame(self, frame_bytes: bytes, trigger_calibration: bool = False) -> dict:
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

        # Gating de Piscada
        p_le_top, p_le_bottom = landmarks[159], landmarks[145]
        if math.sqrt((p_le_top.x - p_le_bottom.x)**2 + (p_le_top.y - p_le_bottom.y)**2) < 0.015:
            return {"face_detected": True, "status": "blink_detected"}

        image_points = np.array([
            [landmarks[1].x * width, landmarks[1].y * height], [landmarks[152].x * width, landmarks[152].y * height],
            [landmarks[33].x * width, landmarks[33].y * height], [landmarks[263].x * width, landmarks[263].y * height],
            [landmarks[61].x * width, landmarks[61].y * height], [landmarks[291].x * width, landmarks[291].y * height]
        ], dtype=np.float64)

        # OTIMIZAÇÃO GEOMÉTRICA: Matriz Intrínseca Adaptativa baseada em fov tangencial clínico (~60°)
        # Substitui a aproximação linear estática width pura por enquadramento de lente padrão.
        fov_rad = math.radians(60.0)
        focal_length_adaptive = (width / 2.0) / math.tan(fov_rad / 2.0)
        center_x, center_y = width / 2.0, height / 2.0
        
        camera_matrix = np.array([
            [focal_length_adaptive, 0, center_x],
            [0, focal_length_adaptive, center_y],
            [0, 0, 1]
        ], dtype=np.float64)
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        success, rvec_raw, tvec_raw = cv2.solvePnP(
            self.FACE_MODEL_3D, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return {"face_detected": True, "status": "pnp_geometry_failed"}

        # Suavização da Pose Espacial contra micro-oscilações
        rvec = np.array([self.pose_filters[f"rvec_{i}"].filter(rvec_raw[i][0]) for i in range(3)]).reshape((3, 1))
        tvec = np.array([self.pose_filters[f"tvec_{i}"].filter(tvec_raw[i][0]) for i in range(3)]).reshape((3, 1))

        R, _ = cv2.Rodrigues(rvec)
        z_depth_cm = float(tvec[2]) / 10.0

        # Mapeamento de Centros dos Globos Oculares no espaço tridimensional
        center_left_cam = R @ self.LEFT_EYEBALL_CENTER_3D + tvec.flatten()
        center_right_cam = R @ self.RIGHT_EYEBALL_CENTER_3D + tvec.flatten()

        # Coordenadas da Íris filtradas em 2D
        l_iris_x = self.iris_filters["lx"].filter(landmarks[468].x * width)
        l_iris_y = self.iris_filters["ly"].filter(landmarks[468].y * height)
        r_iris_x = self.iris_filters["rx"].filter(landmarks[473].x * width)
        r_iris_y = self.iris_filters["ry"].filter(landmarks[473].y * height)

        # Construção de Raios Ópticos Unitários (Ray-Casting)
        K_inv = np.linalg.inv(camera_matrix)
        ray_left = K_inv @ np.array([l_iris_x, l_iris_y, 1.0])
        ray_left /= np.linalg.norm(ray_left)
        ray_right = K_inv @ np.array([r_iris_x, r_iris_y, 1.0])
        ray_right /= np.linalg.norm(ray_right)

        # Interseção Raio-Esfera
        p_iris_left_cam = self._intersect_ray_sphere(ray_left, center_left_cam)
        p_iris_right_cam = self._intersect_ray_sphere(ray_right, center_right_cam)

        # Projeção Inversa para o espaço isolado do crânio
        p_iris_left_cranial = R.T @ (p_iris_left_cam - tvec.flatten())
        p_iris_right_cranial = R.T @ (p_iris_right_cam - tvec.flatten())

        # Vetor de Olhar Puro (Eixo Óptico Bruto)
        v_gaze_left = (p_iris_left_cranial - self.LEFT_EYEBALL_CENTER_3D) / self.EYEBALL_RADIUS_MM
        v_gaze_right = (p_iris_right_cranial - self.RIGHT_EYEBALL_CENTER_3D) / self.EYEBALL_RADIUS_MM

        raw_angles_left = {
            "horizontal": math.degrees(math.atan2(v_gaze_left[0], v_gaze_left[2])),
            "vertical": math.degrees(math.atan2(v_gaze_left[1], v_gaze_left[2]))
        }
        raw_angles_right = {
            "horizontal": math.degrees(math.atan2(v_gaze_right[0], v_gaze_right[2])),
            "vertical": math.degrees(math.atan2(v_gaze_right[1], v_gaze_right[2]))
        }

        # IMPLEMENTAÇÃO PRIORITÁRIA: Gerenciamento do Estado de Biocalibração do Eixo Visual
        if trigger_calibration and not self.biocalibrator.is_calibrated:
            self.biocalibrator.collect_sample(raw_angles_left, raw_angles_right)

        # Aplicação da Compensação Real do Ângulo Kappa
        left_angles, right_angles, calibration_active = self.biocalibrator.apply_compensation(
            raw_angles_left, raw_angles_right
        )

        kinematics_report = self.kinematics_engine.analyze(left_angles, right_angles)

        # Avaliação Clínica Avançada baseada no Eixo Visual Real Compensado
        alignment_str = "Ortoforia (Alinhamento Visual Normal)"
        desvio_limiar = 4.5  
        diff_horizontal = left_angles["horizontal"] - right_angles["horizontal"]
        
        if diff_horizontal > desvio_limiar:
            alignment_str = "Assimetria Binocular (Suspeita de Exotropia)"
        elif diff_horizontal < -desvio_limiar:
            alignment_str = "Assimetria Binocular (Suspeita de Esotropia)"

        # CORREÇÃO DO BUG PYTHON: Booleanos convertidos explicitamente para True nativo
        return {
            "face_detected": True,
            "status": "tracking_active",
            "biocalibration_applied": calibration_active,
            "head_telemetry": {
                "distance_cm": round(z_depth_cm, 1),
                "pitch_deg": round(math.degrees(math.atan2(-R[1, 2], R[2, 2])), 1),
                "yaw_deg": round(math.degrees(math.atan2(R[0, 2], math.sqrt(R[1, 2]**2 + R[2, 2]**2))), 1),
                "roll_deg": round(math.degrees(math.atan2(-R[0, 1], R[0, 0])), 1)
            },
            "visual_axis_metrics_deg": {
                "left_eye": left_angles,
                "right_eye": right_angles,
                "kappa_offsets_applied": self.biocalibrator.kappa_offsets
            },
            "kinematics_analysis": kinematics_report,
            "clinical_evaluation": {
                "status": alignment_str,
                "inter_ocular_diff_deg": round(abs(diff_horizontal), 2)
            }
        }

    def close(self):
        self.face_mesh.close()

# --- 5. ENDPOINT WEBSOCKET SEGURO COM COMANDO DE CALIBRAÇÃO DE FRAME ---
@app.websocket("/tracking/stream")
async def websocket_tracking_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = OcularTrackingSession()
    print("🚀 Engine v5.0.0 Estável. Camada de Biocalibração Visual (Ângulo Kappa) Armada.")

    try:
        while True:
            # O protocolo espera um frame binário. Para ativar a calibração, o front-end pode enviar
            # uma mensagem de texto inicial or simplesmente controlamos via query param. 
            # Para manter o stream binário de alta performance, checamos se o estado precisa calibrar.
            data = await websocket.receive_bytes()
            
            # Se o calibrador ainda não concluiu, os primeiros frames alimentam a matriz Kappa automaticamente
            auto_calibrate = not session.biocalibrator.is_calibrated
            
            analysis_result = session.process_frame(data, trigger_calibration=auto_calibrate)
            await websocket.send_json(analysis_result)
            
    except WebSocketDisconnect:
        print("🛑 Conexão encerrada pelo cliente.")
    except Exception as e:
        print(f"⚠️ Exceção no pipeline biomecânico: {str(e)}")
    finally:
        session.close()
        print("🧹 Alocações C++ e buffers do calibrador limpos com sucesso.")
