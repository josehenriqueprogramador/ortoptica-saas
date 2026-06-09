class TelemetryResponse {
  final String sessionId;
  final bool trackingActive;
  final double gazeX;
  final double gazeY;
  final double confidence;
  final double pitch;
  final double yaw;
  final double roll;
  final double timestamp;

  TelemetryResponse({
    required this.sessionId,
    required this.trackingActive,
    required this.gazeX,
    required this.gazeY,
    required this.confidence,
    required this.pitch,
    required this.yaw,
    required this.roll,
    required this.timestamp,
  });

  factory TelemetryResponse.fromJson(Map<String, dynamic> json) {
    return TelemetryResponse(
      sessionId: json['session_id'],
      trackingActive: json['tracking_active'],
      gazeX: (json['gaze_x'] as num).toDouble(),
      gazeY: (json['gaze_y'] as num).toDouble(),
      confidence: (json['confidence'] as num).toDouble(),
      pitch: (json['pitch'] as num).toDouble(),
      yaw: (json['yaw'] as num).toDouble(),
      roll: (json['roll'] as num).toDouble(),
      timestamp: (json['timestamp'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'session_id': sessionId,
        'tracking_active': trackingActive,
        'gaze_x': gazeX,
        'gaze_y': gazeY,
        'confidence': confidence,
        'pitch': pitch,
        'yaw': yaw,
        'roll': roll,
        'timestamp': timestamp,
      };
}
