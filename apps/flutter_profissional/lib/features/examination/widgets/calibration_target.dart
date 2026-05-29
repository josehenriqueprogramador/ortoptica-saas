import 'package:flutter/material.dart';

class CalibrationTarget extends StatelessWidget {
  final double targetX;
  final double targetY;
  final double patientX;
  final double patientY;
  final double confidence;

  const CalibrationTarget({
    Key? key,
    required this.targetX,
    required this.targetY,
    required this.patientX,
    required this.patientY,
    required this.confidence,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final double width = constraints.maxWidth;
        final double height = constraints.maxHeight;

        final double targetPixelX = ((targetX + 1.0) / 2.0) * width;
        final double targetPixelY = ((targetY + 1.0) / 2.0) * height;

        final double patientPixelX = ((patientX + 1.0) / 2.0) * width;
        final double patientPixelY = ((patientY + 1.0) / 2.0) * height;

        return Stack(
          children: [
            // 🎯 1. ALVO ORTÓPTICO DE FIXAÇÃO
            Positioned(
              left: targetPixelX - 20,
              top: targetPixelY - 20,
              child: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.3),
                  shape: BoxShape.circle,
                ),
                child: Center(
                  child: Container(
                    width: 12,
                    height: 12,
                    decoration: const BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                    ),
                  ),
                ),
              ),
            ),

            // 👁️ 2. ESTRELA RETICULAR DO OLHAR
            Positioned(
              left: patientPixelX - 12,
              top: patientPixelY - 12,
              child: AnimatedOpacity(
                duration: const Duration(milliseconds: 50),
                opacity: confidence > 0.2 ? 1.0 : 0.2,
                child: Container(
                  width: 24,
                  height: 24,
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.cyanAccent, width: 2),
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Container(
                      width: 6,
                      height: 6,
                      decoration: const BoxDecoration(
                        color: Colors.cyanAccent,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}
