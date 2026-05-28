import 'dart:math' as math;
import 'package:flutter/material.dart';

class CalibrationTarget extends StatefulWidget {
  final Alignment alignment;
  final bool isActive;

  const CalibrationTarget({
    Key? key,
    required this.alignment,
    required this.isActive,
  }) : super(key: key);

  @override
  State<CalibrationTarget> createState() => _CalibrationTargetState();
}

class _CalibrationTargetState extends State<CalibrationTarget> with SingleTickerProviderStateMixin {
  late AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.isActive) return const SizedBox.shrink();

    return Align(
      alignment: widget.alignment,
      child: AnimatedBuilder(
        animation: _animationController,
        builder: (context, child) {
          final scale = 1.0 + (_animationController.value * 0.25);
          return Transform.scale(
            scale: scale,
            child: Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: const Color(00000000), // Fundo transparente para o anel laser
                border: Border.all(color: const Color(0xFF00F2FE), width: 3),
                boxShadow: [
                  BoxShadow(
                    color: const Color(0xFF00F2FE).withOpacity(0.5),
                    blurRadius: 10 * _animationController.value,
                    spreadRadius: 2,
                  )
                ],
              ),
              child: Center(
                child: Container(
                  width: 10,
                  height: 10,
                  decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
