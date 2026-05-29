import math
from typing import Dict, Any, List
import numpy as np

class PoseEstimator:
    """
    Nó matemático especializado no cálculo da pose craniométrica (6 DoF).
    Isola os desvios de rotação da cabeça (Pitch, Yaw, Roll) usando vetores espaciais.
    """

    def __init__(self):
        # Limiares de estabilidade clínica para alertar a postura do paciente
        self.PITCH_THRESHOLD_DEG = 12.0
        self.YAW_THRESHOLD_DEG = 12.0
        self.ROLL_THRESHOLD_DEG = 10.0
        print("📐 PoseEstimator configurado com limites de estabilidade postural.")

    def estimate_head_pose(self, landmarks: Dict[str, List[float]], width: int, height: int) -> Dict[str, Any]:
        """
        Calcula os ângulos espaciais da cabeça baseando-se nos marcos oculares 3D.
        Responsabilidade Única: Landmarks Faciais -> Ângulos de Pose Craniométrica.
        """
        # Se os landmarks estiverem vazios ou incompletos, invalida a postura
        if not landmarks or "left_inner_corner" not in landmarks:
            return {
                "head_pose_valid": False,
                "angles": {"pitch": 0.0, "yaw": 0.0, "roll": 0.0},
                "status": "MISSING_LANDMARKS"
            }

        try:
            # Reconstrói os vetores espaciais a partir do mapeamento do tracker
            p_left_out = np.array(landmarks["left_outer_corner"])
            p_left_in = np.array(landmarks["left_inner_corner"])
            p_right_in = np.array(landmarks["right_inner_corner"])
            p_right_out = np.array(landmarks["right_outer_corner"])

            # 1. Ângulo de Roll (Inclinação lateral nos eixos X e Y)
            # Medido pela linha inter-pupilar ou inter-comissural dos cantos oculares
            eye_vector = p_right_in - p_left_in
            roll_rad = math.atan2(eye_vector[1], eye_vector[0])
            roll_deg = math.degrees(roll_rad)

            # 2. Ângulo de Yaw (Rotação para os lados)
            # Medido pela assimetria de distância projetada entre o centro da face e as bordas
            left_width = np.linalg.norm(p_left_in - p_left_out)
            right_width = np.linalg.norm(p_right_out - p_right_in)
            
            # Evita divisões por zero em frames degenerados
            if (left_width + right_width) > 0:
                yaw_ratio = (left_width - right_width) / (left_width + right_width)
                yaw_deg = yaw_ratio * 45.0  # Fator de escala empírico aproximado para pequenos ângulos
            else:
                yaw_deg = 0.0

            # 3. Ângulo de Pitch (Inclinação para cima ou para baixo)
            # Medido pela profundidade Z relativa dos cantos internos comparados ao plano dos cantos externos
            center_in = (p_left_in + p_right_in) / 2.0
            center_out = (p_left_out + p_right_out) / 2.0
            pitch_depth = center_in[2] - center_out[2]
            pitch_deg = pitch_depth * 90.0  # Projeção aproximada do arco cordal da face

            # Valida se os ângulos violam as restrições do protocolo clínico (PVC detectada)
            is_valid = (
                abs(pitch_deg) <= self.PITCH_THRESHOLD_DEG and
                abs(yaw_deg) <= self.YAW_THRESHOLD_DEG and
                abs(roll_deg) <= self.ROLL_THRESHOLD_DEG
            )

            status = "POSTURE_OK" if is_valid else "PATIENT_MOVING_HEAD_PVC"

            # Formata vetores de rotação estrutural para compatibilidade com a GazeEngine
            # rvec e tvec emulados com precisão escalar para alimentar equações subsequentes
            return {
                "head_pose_valid": is_valid,
                "angles": {
                    "pitch": round(float(pitch_deg), 2),
                    "yaw": round(float(yaw_deg), 2),
                    "roll": round(float(roll_deg), 2)
                },
                "rvec": [pitch_rad_approx := math.radians(pitch_deg), math.radians(yaw_deg), roll_rad],
                "tvec": [0.0, 0.0, 1.0],  # Profundidade de plano de referência estática
                "status": status
            }

        except Exception as e:
            return {
                "head_pose_valid": False,
                "angles": {"pitch": 0.0, "yaw": 0.0, "roll": 0.0},
                "status": f"POSE_CALCULATION_ERROR: {str(e)}"
            }
