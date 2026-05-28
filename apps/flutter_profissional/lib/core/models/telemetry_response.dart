class TelemetryResponse {
  final bool faceDetected;
  final double trackingConfidence;
  final double latencyInternalMs;
  final String engineVersion;
  final String mathModel;

  TelemetryResponse({
    required this.faceDetected,
    required this.trackingConfidence,
    required this.latencyInternalMs,
    required this.engineVersion,
    required this.mathModel,
  });

  factory TelemetryResponse.fromJson(Map<String, dynamic> json) {
    final auditing = json['engine_auditing'] as Map<String, dynamic>? ?? {};
    return TelemetryResponse(
      faceDetected: json['face_detected'] ?? false,
      trackingConfidence: (json['tracking_confidence'] as num?)?.toDouble() ?? 0.0,
      latencyInternalMs: (json['latency_internal_ms'] as num?)?.toDouble() ?? 0.0,
      engineVersion: auditing['version'] ?? 'unknown',
      mathModel: auditing['math_model'] ?? 'unknown',
    );
  }
}
