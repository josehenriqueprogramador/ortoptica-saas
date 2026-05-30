import 'pre_exam_status.dart';

class TelemetryResponse {
  final double gazeX;
  final double gazeY;
  final double confidenceScore;
  final double latencySec;
  final PreExamStatus? preExam;

  TelemetryResponse({
    required this.gazeX,
    required this.gazeY,
    required this.confidenceScore,
    required this.latencySec,
    this.preExam,
  });

  factory TelemetryResponse.fromJson(Map<String, dynamic> json) {
    return TelemetryResponse(
      gazeX: (json['telemetry']['gaze_x'] as num).toDouble(),
      gazeY: (json['telemetry']['gaze_y'] as num).toDouble(),
      confidenceScore: (json['telemetry']['confidence_score'] as num).toDouble(),
      latencySec: (json['telemetry']['latency_sec'] as num).toDouble(),
      preExam: json.containsKey('pre_exam') 
          ? PreExamStatus.fromJson(json['pre_exam']) 
          : null,
    );
  }
}
