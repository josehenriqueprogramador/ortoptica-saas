import 'dart:async';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import '../../../core/models/telemetry_response.dart';
import '../../../core/networking/clinical_streaming_service.dart';

enum ExamState { idle, connecting, calibrating, active, consolidated, error }

class ExaminationController extends ChangeNotifier {
  final ClinicalStreamingService _streamingService = ClinicalStreamingService();
  Timer? _frameSimulationTimer;
  StreamSubscription<TelemetryResponse>? _telemetrySubscription;

  // Estados operacionais
  ExamState _state = ExamState.idle;
  String _statusMessage = 'Aguardando inicialização médica.';
  TelemetryResponse? _currentTelemetry;

  // Coordenadas cartesianas do Alvo Ortóptico [-1.0 a 1.0]
  double _targetX = 0.0;
  double _targetY = 0.0;
  String _currentTargetLabel = 'CENTER_FIXATION';

  // Getters públicos para consumo seguro na UI
  ExamState get state => _state;
  String get statusMessage => _statusMessage;
  TelemetryResponse? get currentTelemetry => _currentTelemetry;
  double get targetX => _targetX;
  double get targetY => _targetY;
  String get currentTargetLabel => _currentTargetLabel;
  bool get isConnected => _streamingService.isConnected;

  /// Resolve dinamicamente o endereço do cluster de ML baseando-se no ambiente de execução
  String get _backendWsUrl {
    if (kIsWeb) return 'ws://127.0.0.1:8000';
    // Mapeamento nativo para o host da máquina servidora dependendo do SO do emulador
    final String host = (defaultTargetPlatform == TargetPlatform.android) ? '10.0.2.2' : '127.0.0.1';
    return 'ws://$host:8000';
  }

  /// Inicializa e amarra os barramentos de rede e escuta assíncrona de telemetria
  Future<void> initializeSession(String sessionId) async {
    _state = ExamState.connecting;
    _statusMessage = 'Estabelecendo canal binário com motor de ML...';
    notifyListeners();

    try {
      await _streamingService.connect(_backendWsUrl, sessionId);
      
      // Assina a Stream de telemetria distribuída da engine
      _telemetrySubscription = _streamingService.telemetryStream.listen(
        _onTelemetryReceived,
        onError: (err) => _handleFailure('Falha na stream de dados: $err'),
      );

      _state = ExamState.active;
      _statusMessage = 'Sessão ativa. Capturando foveação do paciente.';
      _startFramePipeline();
    } catch (e) {
      _handleFailure('Erro ao conectar ao cluster de inferência: $e');
    }
    notifyListeners();
  }

  void _onTelemetryReceived(TelemetryResponse data) {
    _currentTelemetry = data;
    notifyListeners();
  }

  /// Dispara a esteira síncrona de captura e injeção de pacotes (30 FPS)
  void _startFramePipeline() {
    _frameSimulationTimer?.cancel();
    _frameSimulationTimer = Timer.periodic(const Duration(milliseconds: 33), (timer) {
      if (_streamingService.isConnected) {
        // Buffer JPEG mínimo transacionado para batimento de coração/keep-alive do pipeline
        final Uint8List transparentFrame = Uint8List.fromList([
          0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
          0x01, 0x01, 0x00, 0x60, 0x00, 0x60, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
          0x00, 0xFF, 0xFF, 0xD9
        ]);
        _streamingService.sendFrame(transparentFrame);
      }
    });
  }

  /// Transiciona o estímulo visual ortóptico entre os 9 pontos diagnósticos
  void transitionTarget(double x, double y, String label) {
    _targetX = x;
    _targetY = y;
    _currentTargetLabel = label;
    _statusMessage = 'Alvo ortóptico deslocado para: $label';
    notifyListeners();
    // NOTA: Aqui será acoplado o disparo do endpoint HTTP /transition para sincronia com o backend
  }

  /// Executa o congelamento clínico e consolidação dos dados diagnósticos
  Future<void> consolidateSession() async {
    _state = ExamState.consolidated;
    _statusMessage = 'Exame concluído com sucesso. Gerando laudo BCEA...';
    _cleanupPipeline();
    notifyListeners();
  }

  /// Aborta o exame imediatamente limpando buffers em memória por segurança do paciente
  void abortSession() {
    _state = ExamState.idle;
    _statusMessage = 'Sessão abortada pelo profissional de saúde.';
    _cleanupPipeline();
    notifyListeners();
  }

  void _handleFailure(String message) {
    _state = ExamState.error;
    _statusMessage = message;
    _cleanupPipeline();
  }

  void _cleanupPipeline() {
    _frameSimulationTimer?.cancel();
    _telemetrySubscription?.cancel();
    _streamingService.disconnect();
    _currentTelemetry = null;
  }

  @override
  void dispose() {
    _cleanupPipeline();
    super.dispose();
  }
}
