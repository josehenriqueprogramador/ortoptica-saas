import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import '../controllers/examination_controller.dart';
import '../widgets/calibration_target.dart';
import '../widgets/telemetry_panel.dart';

class ExaminationPage extends StatefulWidget {
  final int sessionId;
  final String backendUrl;

  const ExaminationPage({
    Key? key,
    required this.sessionId,
    required this.backendUrl,
  }) : super(key: key);

  @override
  State<ExaminationPage> createState() => _ExaminationPageState();
}

class _ExaminationPageState extends State<ExaminationPage> {
  final ExaminationController _controller = ExaminationController();
  CameraController? _cameraController;
  bool _isCameraInitialized = false;
  
  final List<Alignment> _ninePositions = [
    Alignment.center,       // Posição Primária do Olhar (PPO)
    Alignment.topCenter,    // Supraversão
    Alignment.bottomCenter, // Infraversão
    Alignment.centerLeft,   // Levoversão
    Alignment.centerRight,  // Dextroversão
    Alignment.topLeft,      // Supralevoversão
    Alignment.topRight,     // Supradextroversão
    Alignment.bottomLeft,   // Infralevoversão
    Alignment.bottomRight,  // Infradextroversão
  ];
  
  int _currentPositionIndex = 0;

  @override
  void initState() {
    super.initState();
    _initializeClinicalPipeline();
  }

  /// Inicializa de forma síncrona a conexão de rede e o hardware da câmera
  Future<void> _initializeClinicalPipeline() async {
    // 1. Conecta o WebSocket com a Engine Python v11.1.0
    await _controller.startExamination(widget.backendUrl, widget.sessionId);
    _controller.addListener(_onControllerUpdated);

    try {
      // 2. Busca as câmeras disponíveis no dispositivo (Prefere a frontal para rastreamento)
      final cameras = await availableCameras();
      final frontCamera = cameras.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.front,
        orElse: () => cameras.first,
      );

      // 3. Configura o controller com resolução ideal (VGA ou 720p é o teto para sub-80KB/frame)
      _cameraController = CameraController(
        frontCamera,
        ResolutionPreset.medium,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.yuv420, // Formato bruto de alta frequência
      );

      await _cameraController!.initialize();
      
      if (!mounted) return;
      setState(() {
        _isCameraInitialized = true;
      });

      // 4. Dispara o Stream nativo de hardware acoplado diretamente ao nosso driver de Isolate
      await _cameraController!.startImageStream((CameraImage availableImage) {
        _controller.handleCameraStreamFrame(availableImage);
      });

    } catch (e) {
      debugPrint("⚠️ Falha crítica ao inicializar hardware de captura: $e");
    }
  }

  void _onControllerUpdated() {
    if (mounted) setState(() {});
  }

  void _nextPosition() {
    if (_currentPositionIndex < _ninePositions.length - 1) {
      setState(() {
        _currentPositionIndex++;
      });
    } else {
      _finishExam();
    }
  }

  void _finishExam() async {
    // Interrompe o fluxo de frames e fecha o canal WebSocket
    if (_cameraController != null && _cameraController!.value.isStreamingImages) {
      await _cameraController!.stopImageStream();
    }
    await _controller.stopExamination();
    
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: Color(0xFF00F2FE),
          content: Text(
            'Mapeamento concluído! Sessão consolidada na Engine.',
            style: TextStyle(color: Color(0xFF0B132B), fontWeight: FontWeight.bold),
          ),
        ),
      );
      Navigator.pop(context);
    }
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    _controller.removeListener(_onControllerUpdated);
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final bool isStreamingActive = _isCameraInitialized && _controller.state == ExaminationState.streaming;

    return Scaffold(
      backgroundColor: const Color(0xFF0B132B), // Azul Titânio
      body: Row(
        children: [
          // Área Clínica Principal (Onde o paciente foca o olhar)
          Expanded(
            child: Stack(
              children: [
                // Renderização sutil do Preview da Câmera no fundo (para o técnico verificar o enquadramento)
                if (_isCameraInitialized)
                  Opacity(
                    opacity: 0.15, // Opacidade baixa para não distrair o paciente do alvo visual
                    child: Center(child: CameraPreview(_cameraController!)),
                  ),

                // Alvo dinâmico pulsante nas 9 posições da marca PRECISION VISION
                CalibrationTarget(
                  alignment: _ninePositions[_currentPositionIndex],
                  isActive: isStreamingActive,
                ),
                
                // Botão de controle de avanço do Ortoptista
                Positioned(
                  bottom: 24,
                  right: 24,
                  child: FloatingActionButton.extended(
                    backgroundColor: const Color(0xFF00F2FE),
                    foregroundColor: const Color(0xFF0B132B),
                    icon: const Icon(Icons.arrow_forward),
                    label: Text(_currentPositionIndex == _ninePositions.length - 1 ? 'Finalizar Exame' : 'Próxima Posição'),
                    onPressed: isStreamingActive ? _nextPosition : null,
                  ),
                ),
                
                if (!isStreamingActive)
                  const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        CircularProgressIndicator(color: Color(0xFF00F2FE)),
                        SizedBox(height: 16),
                        Text(
                          'Sincronizando Hardware e Engine Biomédica...',
                          style: TextStyle(color: Color(0xFF94A3B8), fontSize: 14),
                        )
                      ],
                    ),
                  ),
              ],
            ),
          ),
          
          // Painel Lateral Direto de Telemetria Biomédica
          TelemetryPanel(telemetry: _controller.latestTelemetry),
        ],
      ),
    );
  }
}
