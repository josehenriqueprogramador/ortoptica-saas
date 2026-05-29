import 'package:flutter/material.dart';
import '../controllers/examination_controller.dart';
import '../widgets/telemetry_panel.dart';
import '../widgets/calibration_target.dart';

class ExaminationPage extends StatefulWidget {
  final String sessionId;
  
  const ExaminationPage({Key? key, required this.sessionId}) : super(key: key);

  @override
  State<ExaminationPage> createState() => _ExaminationPageState();
}

class _ExaminationPageState extends State<ExaminationPage> {
  late final ExaminationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = ExaminationController();
    _controller.initializeSession(widget.sessionId);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF121214),
      body: AnimatedBuilder(
        animation: _controller,
        builder: (context, _) {
          // Fallback visual de carregamento ou erro crítico de rede
          if (_controller.state == ExamState.connecting) {
            return const Center(
              child: CircularProgressIndicator(color: Colors.cyanAccent),
            );
          }

          final telemetry = _controller.currentTelemetry;
          final double patientX = telemetry?.gazeX ?? 0.0;
          final double patientY = telemetry?.gazeY ?? 0.0;
          final double confidence = telemetry?.confidenceScore ?? 0.0;

          return Stack(
            children: [
              // 🎯 Renderização Cartesiana dos Vetores e Alvo Ortóptico
              Positioned.fill(
                child: CalibrationTarget(
                  targetX: _controller.targetX,
                  targetY: _controller.targetY,
                  patientX: patientX,
                  patientY: patientY,
                  confidence: confidence,
                ),
              ),

              // 📊 Painel de Controle de Telemetria Flutuante
              if (telemetry != null)
                Positioned(
                  top: 40,
                  right: 20,
                  width: 240,
                  child: TelemetryPanel(telemetry: telemetry),
                ),

              // 📢 Banner Dinâmico de Status Clínico (Rodapé Superior)
              Positioned(
                top: 40,
                left: 20,
                right: 260,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.black54,
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Text(
                    _controller.statusMessage,
                    style: const TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                ),
              ),

              // 🕹️ Painel de Orquestração do Médico (Barra Inferior)
              Positioned(
                bottom: 30,
                left: 20,
                right: 20,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    ElevatedButton.icon(
                      onPressed: () {
                        _controller.abortSession();
                        Navigator.pop(context);
                      },
                      icon: const Icon(Icons.close),
                      label: const Text('Abortar'),
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
                    ),
                    ElevatedButton.icon(
                      onPressed: () {
                        // Varre os eixos diagnósticos mudando a posição do estímulo
                        if (_controller.targetX == 0.0) {
                          _controller.transitionTarget(0.6, 0.6, 'UP_RIGHT_STRABISMUS_CHECK');
                        } else {
                          _controller.transitionTarget(0.0, 0.0, 'CENTER_FIXATION');
                        }
                      },
                      icon: const Icon(Icons.track_changes),
                      label: Text(_controller.targetX == 0.0 ? 'Avançar Posição' : 'Resetar Centro'),
                    ),
                    ElevatedButton.icon(
                      onPressed: () async {
                        await _controller.consolidateSession();
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Sessão selada no banco de dados!')),
                        );
                        Navigator.pop(context);
                      },
                      icon: const Icon(Icons.check_circle),
                      label: const Text('Finalizar e Salvar'),
                      style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                    ),
                  ],
                ),
              )
            ],
          );
        },
      ),
    );
  }
}
