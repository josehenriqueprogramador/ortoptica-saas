import asyncio
import math
import time
import struct
import cv2
import numpy as np
import mediapipe as mp
from collections import deque
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(
    title="Multithreaded Kinematic & Regularized Estimation Engine",
    version="10.0.0"
)

mp_face_mesh = mp.solutions.face_mesh

# --- 1. FILTRO DE KALMAN 1D ---
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

# --- 2. REGRESSÃO RIDGE (TIKHONOV) PARA EVITAR OVERFITTING ---
class RegularizedSurfaceCalibrator:
    def __init__(self):
        self.is_surface_fitted = False
        self.coeff_left_h = None
        self.coeff_left_v = None
        self.coeff_right_h = None
        self.coeff_right_v = None
        self.calibration_dataset = deque(maxlen=250)

    def accumulate_target_samples(self, target_h: float, target_v: float, raw_left: dict, raw_right: dict):
        self.calibration_dataset.append({
            "true_h": target_h, "true_v": target_v,
            "raw_l_h": raw_left["horizontal"], "raw_l_v": raw_left["vertical"],
            "raw_r_h": raw_right["horizontal"], "raw_r_v": raw_right["vertical"]
        })

    def _build_polynomial_features(self, h: float, v: float) -> list:
        return [1.0, h, v, h**2, h*v, v**2]

    def fit_surface_ridge_sync(self, alpha: float = 1e-2) -> bool:
        """
        Aplica a Regularização Ridge para impedir oscilações selvagens na periferia da tela.
        Matematicamente: W = (A^T * A + alpha * I)^(-1) * A^T * B
        """
        if len(self.calibration_dataset) < 6: # Grau de liberdade mínimo para polinômio quadrático estável
            return False
        try:
            A_l, A_r = [], []
            B_lh, B_lv, B_rh, B_rv = [], [], [], []

            for data in self.calibration_dataset:
                A_l.append(self._build_polynomial_features(data["raw_l_h"], data["raw_l_v"]))
                A_r.append(self._build_polynomial_features(data["raw_r_h"], data["raw_r_v"]))
                B_lh.append(data["true_h"] - data["raw_l_h"])
                B_lv.append(data["true_v"] - data["raw_l_v"])
                B_rh.append(data["true_h"] - data["raw_r_h"])
                B_rv.append(data["true_v"] - data["raw_r_v"])

            A_l, A_r = np.array(A_l), np.array(A_r)
            
            # Construção da penalidade Ridge (Identidade modificada)
            I_matrix = np.eye(6)
            I_matrix[0, 0] = 0.0 # Não penaliza o termo de intercepto (offset estático)

            # Resolução analítica regularizada estável
            self.coeff_left_h = np.linalg.solve(A_l.T @ A_l + alpha * I_matrix, A_l.T @ B_lh)
            self.coeff_left_v = np.linalg.solve(A_l.T @ A_l + alpha * I_matrix, A_l.T @ B_lv)
            self.coeff_right_h = np.linalg.solve(A_r.T @ A_r + alpha * I_matrix, A_r.T @ B_r)
            self.coeff_right_v = np.linalg.solve(A_r.T @ A_r + alpha * I_matrix, A_r.T @ B_rv)

            self.is_surface_fitted = True
            return True
        except Exception:
            return False

    def evaluate_compensated_axis(self, raw_left: dict, raw_right: dict) -> tuple:
        if not self.is_surface_fitted:
            return raw_left, raw_right, False

        feat_l = self._build_polynomial_features(raw_left["horizontal"], raw_left["vertical"])
        feat_r = self._build_polynomial_features(raw_right["horizontal"], raw_right["vertical"])

        corrected_left = {
            "horizontal": raw_left["horizontal"] + float(np.dot(feat_l, self.coeff_left_h)),
            "vertical": raw_left["vertical"] + float(np.dot(feat_l, self.coeff_left_v))
        }
        corrected_right = {
            "horizontal": raw_right["horizontal"] + float(np.dot(feat_r, self.coeff_right_h)),
            "vertical": raw_right["vertical"] + float(np.dot(feat_r, self.coeff_right_v))
        }
        return corrected_left, corrected_right, True

    def reset(self):
        self.is_surface_fitted = False
        self.calibration_dataset.clear()

# --- 3. ADAPTAÇÃO ANTROPOMÉTRICA DA MORFOLOGIA CRANIANA ---
class CranialMorphologyAdapter:
    def __init__(self):
        self.BASE_FACE_MODEL_3D = np.array([
            [0.0, 0.0, 0.0], [0.0, -63.6, -12.5], [-43.3, 32.7, -26.0],
            [43.3, 32.7, -26.0], [-28.9, -28.9, -24.1], [28.9, -28.9, -24.1]
        ], dtype=np.float64)

    def generate_personalized_mesh(self, landmarks, width: int, height: int) -> tuple:
        p_left_eye = np.array([landmarks[33].x * width, landmarks[33].y * height])
        p_right_eye = np.array([landmarks[263].x * width, landmarks[263].y * height])
        
        observed_2d_distance = np.linalg.norm(p_left_eye - p_right_eye)
        scale_factor = np.clip(observed_2d_distance / 110.0, 0.65, 1.3) if observed_2d_distance > 0 else 1.0

        scaled_model = self.BASE_FACE_MODEL_3D * scale_factor
        center_left_3d = np.array([-32.0, 32.7, -28.0], dtype=np.float64) * scale_factor
        center_right_3d = np.array([32.0, 32.7, -28.0], dtype=np.float64) * scale_factor
        return scaled_model, center_left_3d, center_right_3d, 12.0 * scale_factor, round(scale_factor, 2)

# --- 4. ENGINE DE EXTRAÇÃO E KINEMATICS AVANÇADA ---
class OcularTrackingSession:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False, max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.7, min_tracking_confidence=0.7
        )
        self.pose_filters = {
            f"{var}_{i}": OcularKalmanFilter(q_process_noise=1e-5 if var=="rvec" else 1e-4, r_measure_noise=1e-2 if var=="rvec" else 1e-1)
            for var in ["rvec", "tvec"] for i in range(3)
        }
        self.iris_filters = {f"{eye}_{ax}": OcularKalmanFilter() for eye in ["l", "r"] for ax in ["x", "y"]}
        self.smooth_filters = {f"{eye}_{ax}": OcularKalmanFilter(q_process_noise=1e-3, r_measure_noise=5e-2) for eye in ["l", "r"] for ax in ["h", "v"]}
        
        self.morphology_adapter = CranialMorphologyAdapter()
        self.surface_calibrator = RegularizedSurfaceCalibrator()
        
        # Estado Histórico para Derivação Cinemática de Alta Precisão
        self.last_timestamp = None
        self.last_head_pose = {"pitch": 0.0, "yaw": 0.0}
        self.last_blink_metric = 0.030
        
        self.cached_width, self.cached_height = 0, 0
        self.camera_matrix, self.K_inv = None, None

    def _update_camera_cache(self, width: int, height: int):
        if width == self.cached_width and height == self.cached_height:
            return
        self.cached_width, self.cached_height = width, height
        focal_length = (width / 2.0) / math.tan(math.radians(60.0) / 2.0)
        self.camera_matrix = np.array([[focal_length, 0, width / 2.0], [0, focal_length, height / 2.0], [0, 0, 1]], dtype=np.float64)
        self.K_inv = np.linalg.inv(self.camera_matrix)

    def _intersect_ray_sphere(self, ray_direction, sphere_center_camera, radius):
        dot_dc = np.dot(ray_direction, sphere_center_camera)
        mag_c2 = np.dot(sphere_center_camera, sphere_center_camera)
        discriminant = (dot_dc ** 2) - mag_c2 + (radius ** 2)
        if discriminant < 0:
            return sphere_center_camera + (ray_direction * radius)
        return ray_direction * (dot_dc - math.sqrt(discriminant))

    def process_frame(self, frame_bytes: bytes, client_timestamp: float, current_target: dict = None) -> dict:
        t_start = time.perf_counter()
        
        np_array = np.frombuffer(frame_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        if image is None:
            return {"face_detected": False, "status": "corrupted_frame"}

        height, width, _ = image.shape
        processing_width = 640
        processing_height = int(height * (processing_width / width))
        resized_image = cv2.resize(image, (processing_width, processing_height), interpolation=cv2.INTER_LINEAR)
        self._update_camera_cache(processing_width, processing_height)

        results = self.face_mesh.process(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return {"face_detected": False, "status": "no_face_tracked", "confidence": 0.0}

        landmarks = results.multi_face_landmarks[0].landmark

        # CINEMÁTICA PALPEBRAL (Blink Velocity Estimation)
        blink_metric = math.sqrt((landmarks[159].x - landmarks[145].x)**2 + (landmarks[159].y - landmarks[145].y)**2)
        
        dt = (client_timestamp - self.last_timestamp) if self.last_timestamp else 0.033
        if dt <= 0: dt = 0.001 # Proteção contra estouro de divisão por zero
        
        blink_velocity = (blink_metric - self.last_blink_metric) / dt
        self.last_blink_metric = blink_metric

        if blink_metric < 0.015 or abs(blink_velocity) > 1.5: # Ejeção por dinâmica de fechamento rápido
            self.last_timestamp = client_timestamp
            return {"face_detected": True, "status": "blink_or_saccade_rejection", "confidence": 0.0}

        face_model_3d, left_eye_center_3d, right_eye_center_3d, current_radius, morph_scale = self.morphology_adapter.generate_personalized_mesh(landmarks, processing_width, processing_height)
        image_points = np.array([[landmarks[idx].x * processing_width, landmarks[idx].y * processing_height] for idx in [1, 152, 33, 263, 61, 291]], dtype=np.float64)

        success, rvec_raw, tvec_raw = cv2.solvePnP(face_model_3d, image_points, self.camera_matrix, np.zeros((4, 1)), flags=cv2.SOLVEPNP_EPNP)
        if not success:
            return {"face_detected": True, "status": "pnp_failed", "confidence": 0.0}

        rvec = np.array([self.pose_filters[f"rvec_{i}"].filter(rvec_raw[i][0]) for i in range(3)]).reshape((3, 1))
        tvec = np.array([self.pose_filters[f"tvec_{i}"].filter(tvec_raw[i][0]) for i in range(3)]).reshape((3, 1))
        R, _ = cv2.Rodrigues(rvec)

        pitch = math.degrees(math.atan2(-R[1, 2], R[2, 2]))
        yaw = math.degrees(math.atan2(R[0, 2], math.sqrt(R[1, 2]**2 + R[2, 2]**2)))

        # CINEMÁTICA CEFÁLICA (Head Angular Velocity Tracking)
        yaw_velocity = (yaw - self.last_head_pose["yaw"]) / dt
        pitch_velocity = (pitch - self.last_head_pose["pitch"]) / dt
        
        self.last_head_pose = {"pitch": pitch, "yaw": yaw}
        self.last_timestamp = client_timestamp

        # REAQUISIÇÃO GEOMÉTRICA DO VETOR UNITÁRIO
        center_left_cam = R @ left_eye_center_3d + tvec.flatten()
        center_right_cam = R @ right_eye_center_3d + tvec.flatten()

        l_ray = self.K_inv @ np.array([self.iris_filters["l_x"].filter(landmarks[468].x * processing_width), self.iris_filters["l_y"].filter(landmarks[468].y * processing_height), 1.0])
        r_ray = self.K_inv @ np.array([self.iris_filters["r_x"].filter(landmarks[473].x * processing_width), self.iris_filters["r_y"].filter(landmarks[473].y * processing_height), 1.0])
        l_ray /= np.linalg.norm(l_ray)
        r_ray /= np.linalg.norm(r_ray)

        v_gaze_left = (R.T @ (self._intersect_ray_sphere(l_ray, center_left_cam, current_radius) - tvec.flatten())) - left_eye_center_3d
        v_gaze_right = (R.T @ (self._intersect_ray_sphere(r_ray, center_right_cam, current_radius) - tvec.flatten())) - right_eye_center_3d
        v_gaze_left /= np.linalg.norm(v_gaze_left)
        v_gaze_right /= np.linalg.norm(v_gaze_right)

        raw_l = {"horizontal": math.degrees(math.atan2(v_gaze_left[0], v_gaze_left[2])), "vertical": math.degrees(math.atan2(v_gaze_left[1], v_gaze_left[2]))}
        raw_r = {"horizontal": math.degrees(math.atan2(v_gaze_right[0], v_gaze_right[2])), "vertical": math.degrees(math.atan2(v_gaze_right[1], v_gaze_right[2]))}

        if current_target is not None:
            self.surface_calibrator.accumulate_target_samples(current_target["h"], current_target["v"], raw_l, raw_r)

        left_angles, right_angles, surface_active = self.surface_calibrator.evaluate_compensated_axis(raw_l, raw_r)

        # SUAVIZAÇÃO ALÉM DO RIDGE REGRESSION
        left_angles["horizontal"] = round(self.smooth_filters["l_h"].filter(left_angles["horizontal"]), 2)
        left_angles["vertical"] = round(self.smooth_filters["l_v"].filter(left_angles["vertical"]), 2)
        right_angles["horizontal"] = round(self.smooth_filters["r_h"].filter(right_angles["horizontal"]), 2)
        right_angles["vertical"] = round(self.smooth_filters["r_v"].filter(right_angles["vertical"]), 2)

        # CÁLCULO DA CONFIANÇA MATEMÁTICA MULTI-VARIÁVEL DA v10.0.0
        head_penalty = max(0.0, (abs(yaw) - 20.0) / 20.0) + max(0.0, (abs(pitch) - 15.0) / 15.0)
        # Nova penalização por velocidade cinética (movimentos rápidos destroem a acurácia do tracking)
        velocity_penalty = max(0.0, (abs(yaw_velocity) - 40.0) / 40.0) + max(0.0, (abs(pitch_velocity) - 40.0) / 40.0)
        
        tracking_confidence = np.clip(1.0 - (head_penalty + velocity_penalty), 0.0, 1.0)
        diff_horizontal = left_angles["horizontal"] - right_angles["horizontal"]

        return {
            "face_detected": True,
            "tracking_confidence": round(float(tracking_confidence), 2),
            "latency_internal_ms": round((time.perf_counter() - t_start) * 1000.0, 2),
            "kinematics": {
                "head_yaw_velocity_deg_s": round(yaw_velocity, 1),
                "eyelid_velocity_px_s": round(blink_velocity, 2)
            },
            "cranial_morphology_scale": morph_scale,
            "surface_calibration_fitted": surface_active,
            "visual_axis_surface_deg": {"left_eye": left_angles, "right_eye": right_angles},
            "clinical_evaluation": {
                "status": "Ortoforia" if abs(diff_horizontal) <= 4.5 else ("Suspeita de Exotropia" if diff_horizontal > 4.5 else "Suspeita de Esotropia"),
                "inter_ocular_diff_deg": round(abs(diff_horizontal), 2)
            }
        }

    def close(self):
        self.face_mesh.close()

# --- 5. ENDPOINT WEBSOCKET BIFÁSICO ---
@app.websocket("/tracking/stream")
async def websocket_tracking_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = OcularTrackingSession()
    current_target = None
    print("🚀 Engine v10.0.0 Online. Regularização Ridge e Filtro de Cinemática Ativos.")

    try:
        while True:
            message = await websocket.receive()
            if "text" in message:
                import json
                command_data = json.loads(message["text"])
                command = command_data.get("command")
                if command == "SET_TARGET":
                    current_target = command_data.get("target")
                elif command == "CLEAR_TARGET":
                    current_target = None
                elif command == "FIT_SURFACE":
                    # Despacha o cálculo regularizado Ridge para worker thread dedicada
                    success = await asyncio.to_thread(session.surface_calibrator.fit_surface_ridge_sync, 1e-2)
                    await websocket.send_json({"status": "surface_fitting_completed", "success": success})
                elif command == "RESET_CALIBRATION":
                    session.surface_calibrator.reset()
                    await websocket.send_json({"status": "calibration_wiped"})
            
            elif "bytes" in message:
                payload = message["bytes"]
                if len(payload) < 8: continue
                client_timestamp = struct.unpack("d", payload[:8])[0]
                analysis_result = session.process_frame(payload[8:], client_timestamp, current_target=current_target)
                await websocket.send_json(analysis_result)
                
    except WebSocketDisconnect:
        print("🛑 Sessão clínica encerrada.")
    finally:
        session.close()
