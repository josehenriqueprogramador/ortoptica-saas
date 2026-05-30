import 'package:flutter/material.dart';
import '../controllers/examination_controller.dart';
import '../../../../core/models/examination_state.dart';

class ExaminationPage extends StatefulWidget {
  final ExaminationController controller;

  const ExaminationPage({Key? key, required this.controller}) : super(key: key);

  @override
  State<ExaminationPage> createState() => _ExaminationPageState();
}

class _ExaminationPageState extends State<ExaminationPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Exame Precision Vision")),
      body: Center(
        child: ListenableBuilder(
          listenable: widget.controller,
          builder: (context, _) {
            final packet = widget.controller.packet;
            final isReady = widget.controller.isReady;

            return Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  "Status: ${packet?.preExam?.status ?? 'CONECTANDO...'}",
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: isReady
                      ? () => _iniciarExame(context)
                      : null,
                  child: const Text("Iniciar Exame"),
                ),
                const SizedBox(height: 20),
                if (packet?.preExam != null)
                  Text("Qualidade: ${packet!.preExam!.qualityScore}%"),
              ],
            );
          },
        ),
      ),
    );
  }

  void _iniciarExame(BuildContext context) {
    widget.controller.updateState(ExaminationState.running);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Exame iniciado com sucesso!")),
    );
  }
}
