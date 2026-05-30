import 'package:flutter/material.dart';
import '../../../core/models/pre_exam_status.dart';

class PreExamChecklist extends StatelessWidget {
  final PreExamStatus status;

  const PreExamChecklist({Key? key, required this.status}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _buildCheckItem("Face Detectada", status.faceDetected),
        _buildCheckItem("Postura Adequada", status.poseOk),
        _buildCheckItem("Iluminação OK", status.lightingOk),
        _buildCheckItem("Confiança da IA", status.confidenceOk),
        const SizedBox(height: 15),
        Text(
          "Qualidade Geral: ${status.qualityScore.toStringAsFixed(1)}%",
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  Widget _buildCheckItem(String label, bool isOk) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(isOk ? Icons.check_circle : Icons.error, 
               color: isOk ? Colors.green : Colors.red),
          const SizedBox(width: 8),
          Text(label),
        ],
      ),
    );
  }
}
