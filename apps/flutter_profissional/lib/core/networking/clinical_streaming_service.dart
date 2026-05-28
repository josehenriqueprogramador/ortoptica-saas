import 'dart:async';
import 'dart:convert';
import 'dart:typed_list';
import 'package:web_socket_channel/web_socket_channel.dart';

class ClinicalStreamingService {
  WebSocketChannel? _channel;
  StreamController<TelemetryResponse>? _telemetryController;
  bool _isStreaming = false;

  Stream<TelemetryResponse> get telemetryStream => 
      _telemetryController?.stream ?? const Stream.empty();

  bool get isStreaming => _isStreaming;

  /// Inicializa o canal de comunicação biomédica com a engine v11.1.0
  Future<void> connect(String baseUrl, int sessionId) async {
    final wsUrl = Uri.parse('$baseUrl/tracking/stream/$sessionId');
    
    _telemetryController = StreamController<TelemetryResponse>.broadcast();
    _channel = WebSocketChannel.connect(wsUrl);

    // Escuta o loop de feedback de baixa latência vindo da IA
    _channel!.stream.listen(
      (message) {
        try {
          if (message is String) {
            final Map<String, dynamic> jsonMap = jsonDecode(message);
            final telemetry = TelemetryResponse.fromJson(jsonMap);
            _telemetryController?.add(telemetry);
          }
        } catch (e) {
          _telemetryController?.addError('Erro ao decodificar telemetria: $e');
        }
      },
      onError: (error) {
        _telemetryController?.addError('Falha na conexão do stream: $error');
        _isStreaming = false;
      },
      onDone: () {
        _telemetryController?.close();
        _isStreaming = false;
      },
    );

    _isStreaming = true;
  }

  /// Empacota e despacha o frame de imagem injetando o Hardware Timestamp nativo
  void sendBiometricFrame(Uint8List jpegBytes) {
    if (_channel == null || !_isStreaming) return;

    // 1. Geração do timestamp de aquisição em segundos fracionados (precisão double)
    final double timestamp = DateTime.now().microsecondsSinceEpoch / 1000000.0;

    // 2. Alocação do Header de 8 bytes e escrita em Little Endian
    final ByteData header = ByteData(8);
    header.setFloat64(0, timestamp, Endian.little);

    // 3. Alocação do buffer unificado para evitar múltiplas cópias na RAM
    final Uint8List payload = Uint8List(header.lengthInBytes + jpegBytes.length);

    // Copia o cabeçalho temporal para o início do payload
    payload.setRange(0, header.lengthInBytes, header.buffer.asUint8List());
    
    // Copia os bytes puros do frame comprimido logo em seguida
    payload.setRange(header.lengthInBytes, payload.length, jpegBytes);

    // 4. Despacha o pacote binário via transporte de rede de alta frequência
    _channel!.sink.add(payload);
  }

  /// Encerra a sessão garantindo a execução do Flush preventivo no backend
  Future<void> disconnect() async {
    _isStreaming = false;
    await _channel?.sink.close();
    await _telemetryController?.close();
    _channel = null;
    _telemetryController = null;
  }
}
