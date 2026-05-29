import 'package:flutter/material.dart';
import '../../../core/models/telemetry_response.dart';

class TelemetryPanel extends StatelessWidget {
  final TelemetryResponse telemetry;

  const TelemetryPanel({Key? key, required this.telemetry}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final bool isPostureValid = !telemetry.status.contains('INVALID');
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.85),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isPostureValid ? Colors.greenAccent : Colors.redAccent,
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'TELEMETRIA SaMD',
                style: TextStyle(color: Colors.white70, fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 1.2),
              ),
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: isPostureValid ? Colors.green : Colors.red,
                  shape: BoxShape.circle,
                ),
              )
            ],
          ),
          const Divider(color: Colors.white24, height: 16),
          _buildMetricRow('Gaze X / Y:', '[${telemetry.gazeX.toStringAsFixed(3)}, ${telemetry.gazeY.toStringAsFixed(3)}]'),
          _buildMetricRow('Confiança:', '${(telemetry.confidenceScore * 100).toStringAsFixed(0)}%'),
          _buildMetricRow('Latência:', '${(telemetry.latencySec * 1000).toStringAsFixed(1)} ms'),
          const SizedBox(height: 8),
          const Text(
            'POSTURA DO CRÂNIO (6 DoF)',
            style: TextStyle(color: Colors.white38, fontSize: 9, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildAngleBadge('PITCH', telemetry.headAngles['pitch'] ?? 0.0),
              _buildAngleBadge('YAW', telemetry.headAngles['yaw'] ?? 0.0),
              _buildAngleBadge('ROLL', telemetry.headAngles['roll'] ?? 0.0),
            ],
          )
        ],
      ),
    );
  }

  Widget _buildMetricRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.white94, fontSize: 13)),
          Text(value, style: const TextStyle(color: Colors.cyanAccent, fontSize: 13, fontFamily: 'Courier')),
        ],
      ),
    );
  }

  Widget _buildAngleBadge(String label, double value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white10,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        '$label: ${value > 0 ? "+" : ""}${value.toStringAsFixed(1)}°',
        style: const TextStyle(color: Colors.white, fontSize: 10, fontFamily: 'Courier'),
      ),
    );
  }
}
