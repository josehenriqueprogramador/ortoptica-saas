import 'package:flutter/material.dart';
import '../../../core/models/telemetry_response.dart';

class TelemetryPanel extends StatelessWidget {
  final TelemetryResponse telemetry;

  const TelemetryPanel({
    Key? key,
    required this.telemetry,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Telemetria Clínica',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const Divider(),
            _metric('Gaze X', telemetry.gazeX.toStringAsFixed(3)),
            _metric('Gaze Y', telemetry.gazeY.toStringAsFixed(3)),
            _metric(
              'Confiança',
              '${(telemetry.confidenceScore * 100).toStringAsFixed(1)}%',
            ),
            _metric(
              'Latência',
              '${(telemetry.latencySec * 1000).toStringAsFixed(0)} ms',
            ),
          ],
        ),
      ),
    );
  }

  Widget _metric(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
