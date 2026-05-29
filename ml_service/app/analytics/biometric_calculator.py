import math
from typing import Dict, List
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class BiometricCalculator:
    """
    Motor estatístico biomédico da plataforma Ortóptica.
    
    Responsável pelo cálculo de:
    - BCEA (Bivariate Contour Ellipse Area)
    - Desvio prismático horizontal/vertical
    - Métricas de estabilidade ocular
    """

    @staticmethod
    async def compute_session_bcea(session_id: str, db: AsyncSession) -> float:
        """
        Orquestrador clínico. Busca a série temporal do banco de dados,
        extrai as coordenadas do olhar e invoca o cálculo do BCEA.
        """
        # Evita a importação circular importando o modelo localmente dentro do método
        from app.session.session_models import GazeTelemetryPoint

        query = select(GazeTelemetryPoint).where(GazeTelemetryPoint.session_id == session_id)
        result = await db.execute(query)
        points = result.scalars().all()

        if not points:
            print(f"⚠️ Nenhum ponto de telemetria encontrado para a sessão {session_id}. Retornando BCEA zerado.")
            return 0.0

        x_points = [p.gaze_x for p in points]
        y_points = [p.gaze_y for p in points]

        bcea_results = BiometricCalculator.calculate_bcea(x_points, y_points)
        return bcea_results.get("bcea", 0.0)

    @staticmethod
    def calculate_bcea(
        x_points: List[float],
        y_points: List[float],
        probability: float = 0.682,
    ) -> Dict:
        """
        Calcula a BCEA (Bivariate Contour Ellipse Area).

        Fórmula:
        BCEA = 2 * π * k * σx * σy * sqrt(1 - ρ²)
        """
        if len(x_points) < 2 or len(y_points) < 2:
            return {
                "status": "INSUFFICIENT_DATA",
                "bcea": 0.0,
                "sigma_x": 0.0,
                "sigma_y": 0.0,
                "correlation": 0.0,
                "points_count": 0,
            }

        x = np.array(x_points, dtype=np.float64)
        y = np.array(y_points, dtype=np.float64)

        # Remove valores inválidos
        valid_mask = np.isfinite(x) & np.isfinite(y)
        x = x[valid_mask]
        y = y[valid_mask]

        if len(x) < 2:
            return {
                "status": "INVALID_NUMERICAL_DATA",
                "bcea": 0.0,
                "sigma_x": 0.0,
                "sigma_y": 0.0,
                "correlation": 0.0,
                "points_count": 0,
            }

        # Desvios padrão
        sigma_x = float(np.std(x))
        sigma_y = float(np.std(y))

        # Correlação de Pearson
        correlation_matrix = np.corrcoef(x, y)
        rho = float(correlation_matrix[0, 1])

        # Proteção numérica contra overflow geométrico
        rho = max(min(rho, 0.999999), -0.999999)

        # Constante estatística k baseada na distribuição desejada
        # Fórmula: k = -2 * ln(1 - probability)
        k = float(-2.0 * math.log(1.0 - probability))

        # BCEA geométrica
        bcea = (
            2.0
            * math.pi
            * k
            * sigma_x
            * sigma_y
            * math.sqrt(1.0 - (rho ** 2))
        )

        # Classificação clínica simplificada
        if bcea < 0.5:
            fixation_stability = "EXCELLENT"
        elif bcea < 1.5:
            fixation_stability = "GOOD"
        elif bcea < 3.0:
            fixation_stability = "MODERATE"
        else:
            fixation_stability = "UNSTABLE"

        return {
            "status": "SUCCESS",
            "bcea": round(float(bcea), 6),
            "sigma_x": round(sigma_x, 6),
            "sigma_y": round(sigma_y, 6),
            "correlation": round(rho, 6),
            "probability": probability,
            "k_value": round(k, 6),
            "points_count": int(len(x)),
            "mean_x": round(float(np.mean(x)), 6),
            "mean_y": round(float(np.mean(y)), 6),
            "fixation_stability": fixation_stability,
        }

    @staticmethod
    def calculate_prism_deviation(
        gaze_x: float,
        gaze_y: float,
        target_x: float = 0.0,
        target_y: float = 0.0,
    ) -> Dict:
        """
        Calcula o desvio prismático aproximado baseado
        na distância angular entre o alvo e a fixação.
        """
        horizontal_offset = gaze_x - target_x
        vertical_offset = gaze_y - target_y

        prism_horizontal = horizontal_offset * 15.0
        prism_vertical = vertical_offset * 15.0

        if prism_horizontal > 1:
            horizontal_label = "EXOTROPIA"
        elif prism_horizontal < -1:
            horizontal_label = "ESOTROPIA"
        else:
            horizontal_label = "ORTHO"

        if prism_vertical > 1:
            vertical_label = "HYPERTROPIA"
        elif prism_vertical < -1:
            vertical_label = "HYPOTROPIA"
        else:
            vertical_label = "ORTHO"

        magnitude = math.sqrt(prism_horizontal ** 2 + prism_vertical ** 2)

        return {
            "horizontal_prism_diopters": round(prism_horizontal, 3),
            "vertical_prism_diopters": round(prism_vertical, 3),
            "horizontal_classification": horizontal_label,
            "vertical_classification": vertical_label,
            "total_deviation_magnitude": round(magnitude, 3),
        }

    @staticmethod
    def compute_fixation_instability_index(
        x_points: List[float],
        y_points: List[float],
    ) -> Dict:
        """
        Índice simplificado de micro-instabilidade ocular.
        Mede a distância média entre amostras consecutivas.
        """
        if len(x_points) < 2 or len(y_points) < 2:
            return {
                "status": "INSUFFICIENT_DATA",
                "instability_index": 0.0,
            }

        x = np.array(x_points, dtype=np.float64)
        y = np.array(y_points, dtype=np.float64)

        dx = np.diff(x)
        dy = np.diff(y)

        distances = np.sqrt((dx ** 2) + (dy ** 2))
        instability_index = float(np.mean(distances))

        return {
            "status": "SUCCESS",
            "instability_index": round(instability_index, 6),
            "samples": int(len(distances)),
        }
