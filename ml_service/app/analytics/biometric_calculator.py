import numpy as np
import math
from typing import Dict, Any, List

class BiometricAnalytics:
    @staticmethod
    def calculate_bcea(x_coords: List[float], y_coords: List[float], confidence_level: float = 0.6827) -> Dict[str, Any]:
        if len(x_coords) < 10:
            return {"bcea_area": 0.0, "eccentricity": 0.0, "status": "insufficient_data"}
        x = np.array(x_coords)
        y = np.array(y_coords)
        std_x = np.std(x)
        std_y = np.std(y)
        if std_x == 0 or std_y == 0:
            return {"bcea_area": 0.0, "eccentricity": 0.0, "status": "no_variance"}
        correlation = np.corrcoef(x, y)[0, 1]
        if np.isnan(correlation):
            correlation = 0.0
        k = -math.log(1.0 - confidence_level)
        bcea_area = 2 * k * math.pi * std_x * std_y * math.sqrt(1.0 - correlation**2)
        a = max(std_x, std_y)
        b = min(std_x, std_y)
        eccentricity = math.sqrt(1.0 - (b**2 / a**2)) if a > 0 else 0.0
        status = "normal"
        if bcea_area > 50.0:
            status = "severe_instability"
        elif bcea_area > 15.0:
            status = "mild_instability"
        return {
            "bcea_area_mm2": round(bcea_area, 4),
            "eccentricity": round(eccentricity, 4),
            "pearson_correlation": round(correlation, 4),
            "clinical_status": status
        }

    @staticmethod
    def convert_angle_to_prism_diopters(deviation_degrees: float) -> float:
        radians = math.radians(deviation_degrees)
        prism_diopters = 100 * math.tan(radians)
        return round(prism_diopters, 2)
