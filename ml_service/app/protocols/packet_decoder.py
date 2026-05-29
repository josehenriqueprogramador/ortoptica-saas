import struct
from typing import Tuple

class PacketDecoder:
    """
    Decodificador de alta performance para o protocolo binário proprietário da Ortóptica.
    Layout do pacote: [8 bytes: Double (Timestamp)] + [Restante: Bytes do JPEG Bruto]
    """
    
    @staticmethod
    def unpack_frame(binary_packet: bytes) -> Tuple[float, bytes]:
        """
        Extrai o timestamp de aquisição e o buffer de imagem sem gerar cópias duplicadas na memória.
        """
        if len(binary_packet) < 8:
            raise ValueError("Pacote binário corrompido ou incompleto (tamanho menor que 8 bytes).")
            
        # Extrai o double (64-bit float) no formato Little-Endian
        acquisition_timestamp = struct.unpack_from("<d", binary_packet, 0)[0]
        
        # Fatia os bytes restantes que correspondem ao payload do JPEG
        jpeg_buffer = binary_packet[8:]
        
        return acquisition_timestamp, jpeg_buffer
