class TelemetryResponse {
  final double gazeX;
  final double gazeY;
  final double confidenceScore;
  final double latencySec;

  const TelemetryResponse({
    required this.gazeX,
    required this.gazeY,
    required this.confidenceScore,
    required this.latencySec,
  });

  factory TelemetryResponse.fromJson(Map<String, dynamic> json) {
    return TelemetryResponse(
      gazeX: (json['gaze_x'] as num?)?.toDouble() ?? 0.0,
      gazeY: (json['gaze_y'] as num?)?.toDouble() ?? 0.0,
      confidenceScore: (json['confidence_score'] as num?)?.toDouble() ?? 0.0,
      latencySec: (json['latency_sec'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
