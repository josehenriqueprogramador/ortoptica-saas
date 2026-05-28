import struct
from typing import Tuple, Optional

class MedicalPacketDecoder:
    """
    Decodificador especializado em extrair metadados e streams binários de alta frequência.
    Garante o desempacotamento do Header temporal sem overhead de decodificação de string.
    """
    HEADER_SIZE = 8  # 8 bytes para o Double (acquisition_timestamp)

    @classmethod
    def decode_frame_packet(cls, payload: bytes) -> Tuple[Optional[float], Optional[bytes]]:
        if len(payload) < cls.HEADER_SIZE:
            return None, None
            
        # Extrai o timestamp de aquisição de hardware (double - 8 bytes nativos)
        acq_timestamp = struct.unpack("d", payload[:cls.HEADER_SIZE])[0]
        
        # O restante dos bytes é o payload puro da imagem (JPEG/PNG comprimido na RAM do cliente)
        frame_bytes = payload[cls.HEADER_SIZE:]
        
        return acq_timestamp, frame_bytes
