class PreExamStatus {
  final String status;
  final int qualityScore;
  final bool faceDetected;
  final bool lightingOk;
  final bool poseOk;
  final bool confidenceOk;

  PreExamStatus({
    required this.status,
    required this.qualityScore,
    required this.faceDetected,
    required this.lightingOk,
    required this.poseOk,
    required this.confidenceOk,
  });

  factory PreExamStatus.fromJson(Map<String, dynamic> json) {
    final checks = json['checks'] ?? {};
    return PreExamStatus(
      status: json['status'] ?? "WAITING",
      qualityScore: (json['quality_score'] as num?)?.toInt() ?? 0,
      faceDetected: checks['face_detected'] ?? false,
      lightingOk: checks['lighting_ok'] ?? false,
      poseOk: checks['pose_ok'] ?? false,
      confidenceOk: checks['confidence_ok'] ?? false,
    );
  }

  bool get isReady => status == "READY_TO_START";
}
