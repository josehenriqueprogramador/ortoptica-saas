class TelemetryResponse {
  final double gazeX;
  final double gazeY;
  final double confidenceScore;
  final String currentTarget;
  final double latencySec;
  final Map<String, double> headAngles;
  final String status;

  TelemetryResponse({
    required this.gazeX,
    required this.gazeY,
    required this.confidenceScore,
    required this.currentTarget,
    required this.latencySec,
    required this.headAngles,
    required this.status,
  });

  factory TelemetryResponse.fromJson(Map<String, dynamic> json) {
    final anglesRaw = json['head_angles'] as Map<String, dynamic>? ?? {};
    final Map<String, double> convertedAngles = {
      'pitch': (anglesRaw['pitch'] ?? 0.0).toDouble(),
      'yaw': (anglesRaw['yaw'] ?? 0.0).toDouble(),
      'roll': (anglesRaw['roll'] ?? 0.0).toDouble(),
    };

    return TelemetryResponse(
      gazeX: (json['gaze_x'] ?? 0.0).toDouble(),
      gazeY: (json['gaze_y'] ?? 0.0).toDouble(),
      confidenceScore: (json['confidence_score'] ?? 0.0).toDouble(),
      currentTarget: json['current_target'] ?? 'UNKNOWN',
      latencySec: (json['latency_sec'] ?? 0.0).toDouble(),
      status: json['status'] ?? 'ERROR',
      headAngles: convertedAngles,
    );
  }
}
