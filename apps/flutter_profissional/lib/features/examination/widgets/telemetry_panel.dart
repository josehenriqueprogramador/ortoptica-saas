import 'package:flutter/material.dart';
import '../../../core/models/telemetry_response.dart';

class TelemetryPanel extends StatelessWidget {
  final TelemetryResponse? telemetry;

  const TelemetryPanel({Key? key, this.telemetry}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final hasData = telemetry != null;
    final faceDetected = telemetry?.faceDetected ?? false;
    final confidence = (telemetry?.trackingConfidence ?? 0.0) * 100;

    return Container(
      width: 280,
      color: const Color(0xFF0F172A).withOpacity(0.9), // Fundo Navy escuro da logo
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'TELEMETRIA BIOMÉDICA',
            style: TextStyle(
              color: Colors.white, 
              fontWeight: FontWeight.bold, 
              fontSize: 14,
              letterSpacing: 1.2
            ),
          ),
          const Divider(color: Color(0xFF94A3B8), height: 24),
          
          // Indicador de Detecção Facial
          _buildStatusRow(
            'Rastreamento Facial:',
            faceDetected ? 'ATIVO' : 'PROCURANDO...',
            faceDetected ? const Color(0xFF00F2FE) : Colors.redAccent,
          ),
          const SizedBox(height: 16),

          // Barra de Confiança do Olhar
          const Text('Confiabilidade do Gaze:', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
          const SizedBox(height: 6),
          LinearProgressIndicator(
            value: (telemetry?.trackingConfidence ?? 0.0),
            backgroundColor: Colors.white10,
            color: confidence > 75 ? const Color(0xFF00F2FE) : Colors.amber,
            minHeight: 6,
          ),
          const SizedBox(height: 4),
          Text(
            '${confidence.toStringAsFixed(1)}%',
            style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),

          // Latência Interna da Pipeline
          _buildStatusRow(
            'Latência do Motor:',
            hasData ? '${telemetry!.latencyInternalMs.toStringAsFixed(1)} ms' : '--',
            const Color(0xFF00F2FE),
          ),
          
          const Spacer(),
          const Divider(color: Color(0xFF94A3B8)),
          Text(
            'Engine: ${telemetry?.engineVersion ?? "11.1.0"}',
            style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 10),
          ),
          Text(
            'Model: ${telemetry?.mathModel ?? "ridge_v2_spatial"}',
            style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 10),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusRow(String label, String value, Color valueColor) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
        Text(value, style: TextStyle(color: valueColor, fontSize: 12, fontWeight: FontWeight.bold)),
      ],
    );
  }
}
