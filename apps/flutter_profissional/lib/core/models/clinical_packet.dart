import 'telemetry_response.dart';
import 'pre_exam_status.dart';

class ClinicalPacket {
  final TelemetryResponse telemetry;
  final PreExamStatus? preExam;

  const ClinicalPacket({
    required this.telemetry,
    this.preExam,
  });

  factory ClinicalPacket.fromJson(Map<String, dynamic> json) {
    return ClinicalPacket(
      telemetry: TelemetryResponse.fromJson(json),
      preExam: json.containsKey('pre_exam') 
          ? PreExamStatus.fromJson(json['pre_exam']) 
          : null,
    );
  }
}
