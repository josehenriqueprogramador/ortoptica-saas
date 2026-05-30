import 'package:flutter/material.dart';
import '../controllers/examination_controller.dart';

class CalibrationTarget extends StatelessWidget {
  final UIClinicalState state;

  const CalibrationTarget({Key? key, required this.state}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    Color targetColor = Colors.red;
    bool shouldPulse = false;

    switch (state) {
      case UIClinicalState.calibrating:
        targetColor = Colors.orange;
        shouldPulse = true;
        break;
      case UIClinicalState.tracking:
        targetColor = Colors.green;
        break;
      case UIClinicalState.consolidating:
        targetColor = Colors.purple;
        break;
      default:
        targetColor = Colors.red;
    }

    return Center(
      child: _PulseAnimation(
        enabled: shouldPulse,
        child: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(color: targetColor, width: 4),
          ),
          child: Center(
            child: Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: targetColor,
                shape: BoxShape.circle,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _PulseAnimation extends StatefulWidget {
  final Widget child;
  final bool enabled;

  const _PulseAnimation({required this.child, required this.enabled});

  @override
  __PulseAnimationState createState() => __PulseAnimationState();
}

class __PulseAnimationState extends State<_PulseAnimation> with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);
    _scaleAnimation = Tween<double>(begin: 0.8, end: 1.2).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.enabled) return widget.child;
    return ScaleTransition(scale: _scaleAnimation, child: widget.child);
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }
}
