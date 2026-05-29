from typing import Tuple, Dict, Any

class TemporalFilter:
    """
    Filtro de suavização temporal adaptativo baseado em Média Móvel Exponencial (EMA).
    Reduz o ruído de alta frequência (jitter) preservando a latência de sacadas reais.
    """

    def __init__(self, alpha_base: float = 0.25, jitter_threshold: float = 0.015):
        # Fator de suavização padrão (valores menores suavizam mais, porém adicionam latência)
        self.alpha_base = alpha_base
        # Limiar de corte matemático para diferenciar micro-ruídos de movimentos voluntários do olhar
        self.jitter_threshold = jitter_threshold
        
        # Estados internos persistentes por olho/instância
        self.prev_x: float | None = None
        self.prev_y: float | None = None

    def filter(self, raw_x: float, raw_y: float) -> Tuple[float, float]:
        """
        Aplica a suavização exponencial adaptativa nas coordenadas cartesianas do olhar.
        Responsabilidade Única: Atenuação de ruído matemático temporal.
        """
        # Bootstrap inicial do filtro no primeiro frame do exame
        if self.prev_x == None or self.prev_y == None:
            self.prev_x = raw_x
            self.prev_y = raw_y
            return raw_x, raw_y

        # 1. Calcula a magnitude euclidiana do deslocamento instantâneo
        delta_x = raw_x - self.prev_x
        delta_y = raw_y - self.prev_y
        distance = (delta_x**2 + delta_y**2) ** 0.5

        # 2. Adaptação dinâmica do Alpha (Fator de corte)
        # Se o deslocamento for menor que o limiar (jitter de pixel), diminui o alpha para filtrar pesado.
        # Se for um movimento sacádico (distância alta), aumenta o alpha para evitar atraso visual na tela.
        if distance > self.jitter_threshold:
            # Movimento ocular real detectado: abre o filtro (resposta rápida)
            alpha = min(1.0, self.alpha_base * (1.0 + (distance * 10.0)))
        else:
            # Olho em ponto de foveação fixa: fecha o filtro para estabilizar o cálculo
            alpha = self.alpha_base

        # 3. Aplicação da Equação Core da Média Móvel Exponencial
        filtered_x = (alpha * raw_x) + ((1.0 - alpha) * self.prev_x)
        filtered_y = (alpha * raw_y) + ((1.0 - alpha) * self.prev_y)

        # Atualiza os registros de estado para o próximo frame
        self.prev_x = filtered_x
        self.prev_y = filtered_y

        return round(filtered_x, 6), round(filtered_y, 6)

    def reset(self) -> None:
        """Limpa o histórico do filtro para evitar contaminação entre exames ou trocas de pacientes."""
        self.prev_x = None
        self.prev_y = None
