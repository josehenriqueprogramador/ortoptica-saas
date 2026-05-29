import math
from typing import Dict, List, Any
import numpy as np

class GazeVectorCalculator:
    """
    Motor geométrico dedicado ao cálculo do vetor de foveação binocular.
    Mapeia a excentricidade da pupila em relação à fenda palpebral e projeta o olhar.
    """

    def __init__(self):
        # Escala ortóptica padrão para mapear deslocamento de pupila em vetor cartesiano normalizado
        self.GAZE_SCALE_FACTOR_X = 5.0
        self.GAZE_SCALE_FACTOR_Y = 6.0
        print("🎯 GazeVectorCalculator inicializado com calibração geométrica padrão.")

    def calculate_gaze_coordinate(
        self, 
        landmarks: Dict[str, List[float]], 
        head_angles: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Determina o vetor de olhar cartesiano (X, Y) com base na excentricidade binocular,
        compensando matematicamente os ângulos de rotação do crânio (Yaw e Pitch).
        """
        if not landmarks or "left_pupil" not in landmarks:
            return {
                "gaze_valid": False,
                "gaze_x": 0.0,
                "gaze_y": 0.0,
                "confidence": 0.0,
                "status": "INSUFFICIENT_LANDMARKS"
            }

        try:
            # 1. Extração Vetorial do Olho Esquerdo (Perspectiva do observador)
            le_pupil = np.array(landmarks["left_pupil"])
            le_in = np.array(landmarks["left_inner_corner"])
            le_out = np.array(landmarks["left_outer_corner"])

            # 2. Extração Vetorial do Olho Direito (Perspectiva do observador)
            re_pupil = np.array(landmarks["right_pupil"])
            re_in = np.array(landmarks["right_inner_corner"])
            re_out = np.array(landmarks["right_outer_corner"])

            # --- Cálculo de Excentricidade Horizontal (Eixo X) ---
            # Determina a posição relativa da pupila entre o canto interno e externo
            le_center_x = (le_in[0] + le_out[0]) / 2.0
            re_center_x = (re_in[0] + re_out[0]) / 2.0
            
            le_width_x = abs(le_in[0] - le_out[0])
            re_width_x = abs(re_in[0] - re_out[0])

            # Deslocamento normalizado (-0.5 a 0.5) em relação ao centro orbital
            le_offset_x = (le_pupil[0] - le_center_x) / (le_width_x if le_width_x > 0 else 1.0)
            re_offset_x = (re_pupil[0] - re_center_x) / (re_width_x if re_width_x > 0 else 1.0)

            # Média binocular horizontal
            raw_gaze_x = float((le_offset_x + re_offset_x) / 2.0)

            # --- Cálculo de Excentricidade Vertical (Eixo Y) ---
            # O MediaPipe FaceMesh fornece maior precisão vertical cruzando dados de pálpebra superior/inferior.
            # Aqui calculamos de forma simplificada em relação à linha média dos cantos
            le_center_y = (le_in[1] + le_out[1]) / 2.0
            re_center_y = (re_in[1] + re_out[1]) / 2.0

            le_offset_y = (le_pupil[1] - le_center_y) / (le_width_x if le_width_x > 0 else 1.0)
            re_offset_y = (re_pupil[1] - re_center_y) / (re_width_x if re_width_x > 0 else 1.0)

            # Média binocular vertical (Invertendo sinal para adequar ao plano cartesiano onde para cima é positivo)
            raw_gaze_y = float(-((le_offset_y + re_offset_y) / 2.0))

            # --- Compensação Craniométrica (Remoção da rotação da cabeça) ---
            # Se o paciente vira a cabeça para a direita (Yaw positivo), o olho tende a ir
            # para a esquerda na órbita de forma compensatória (reflexo vestíbulo-ocular).
            # Precisamos adicionar o ângulo da cabeça para anular esse efeito.
            yaw_compensation = head_angles.get("yaw", 0.0) * 0.015
            pitch_compensation = head_angles.get("pitch", 0.0) * 0.015

            compensated_x = (raw_gaze_x * self.GAZE_SCALE_FACTOR_X) + yaw_compensation
            compensated_y = (raw_gaze_y * self.GAZE_SCALE_FACTOR_Y) + pitch_compensation

            # --- Cálculo do Score de Confiança Anatômica ---
            # Estima a viabilidade geométrica baseado na profundidade Z e simetria das pupilas
            asymmetry = abs(le_offset_x - re_offset_x)
            # Uma assimetria extrema indica falha de tracking (oclusão, piscada ou reflexo de luz na córnea)
            confidence = max(0.0, 1.0 - (asymmetry * 2.0))

            return {
                "gaze_valid": True,
                "gaze_x": round(compensated_x, 6),
                "gaze_y": round(compensated_y, 6),
                "confidence": round(confidence, 4),
                "status": "COMPUTATION_SUCCESS"
            }

        except Exception as e:
            return {
                "gaze_valid": False,
                "gaze_x": 0.0,
                "gaze_y": 0.0,
                "confidence": 0.0,
                "status": f"GAZE_ERROR: {str(e)}"
            }
