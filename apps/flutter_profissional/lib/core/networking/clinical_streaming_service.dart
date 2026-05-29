import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../models/telemetry_response.dart';

class ClinicalStreamingService {
  WebSocketChannel? _channel;
  final StreamController<TelemetryResponse> _telemetryController = StreamController<TelemetryResponse>.broadcast();

  Stream<TelemetryResponse> get telemetryStream => _telemetryController.stream;
  bool _isConnected = false;

  bool get isConnected => _isConnected;

  /// Inicializa a conexão persistente com o cluster de inferência geométrica
  Future<void> connect(String wsUrl, String sessionId) async {
    if (_isConnected) return;

    final uri = Uri.parse('$wsUrl/tracking/stream/$sessionId');
    try {
      _channel = WebSocketChannel.connect(uri);
      _isConnected = true;

      _channel!.stream.listen(
        (message) {
          try {
            if (message is String) {
              final Map<String, dynamic> jsonMap = jsonDecode(message);
              final telemetry = TelemetryResponse.fromJson(jsonMap);
              _telemetryController.add(telemetry);
            }
          } catch (e) {
            // Silencia ou loga falhas pontuais de parse sem derrubar a stream principal
            print('🚨 Erro de parse na telemetria reversa: $e');
          }
        },
        onError: (error) => _handleDisconnect(),
        onDone: () => _handleDisconnect(),
      );
    } catch (e) {
      _handleDisconnect();
      rethrow;
    }
  }

  /// Injeta frames na esteira de ML respeitando o protocolo binário proprietário:
  /// [8 Bytes: Little-Endian Float64 (Timestamp)] + [Restante: Imagem JPEG]
  void sendFrame(Uint8List jpegBytes) {
    if (!_isConnected || _channel == null) return;

    final double timestamp = DateTime.now().millisecondsSinceEpoch / 1000.0;
    
    // Aloca buffer exatamente com o tamanho do payload + 8 bytes de header
    final totalLength = 8 + jpegBytes.length;
    final Uint8List packet = Uint8List(totalLength);
    final ByteData byteData = ByteData.sublistView(packet);

    // Grava o timestamp no formato little-endian (coincidindo com o "<d" do Python struct)
    byteData.setFloat64(0, timestamp, Endian.little);

    // Copia o corpo da imagem JPEG logo após o cabeçalho de 8 bytes
    packet.setRange(8, totalLength, jpegBytes);

    // Dispara via canal binário puro do WebSocket
    _channel!.sink.add(packet);
  }

  void _handleDisconnect() {
    _isConnected = false;
    _channel = null;
  }

  Future<void> disconnect() async {
    await _channel?.sink.close();
    _handleDisconnect();
  }
}
