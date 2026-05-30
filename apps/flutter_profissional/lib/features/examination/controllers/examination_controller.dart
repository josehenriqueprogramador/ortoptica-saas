import 'dart:async';
import 'package:flutter/foundation.dart';
import '../../../core/models/clinical_packet.dart';
import '../../../core/models/pre_exam_status.dart';
import '../../../core/models/telemetry_response.dart';
import '../../../core/models/examination_state.dart';
import '../../../core/networking/clinical_streaming_service.dart';

class ExaminationController extends ChangeNotifier {
  final ClinicalStreamingService _service;
  late final StreamSubscription<ClinicalPacket> _subscription;

  ClinicalPacket? _lastPacket;
  ExaminationState _state = ExaminationState.idle;

  ExaminationController(this._service) {
    _subscription = _service.packetStream.listen((packet) {
      _lastPacket = packet;
      notifyListeners();
    });
  }

  ClinicalPacket? get packet => _lastPacket;
  ExaminationState get state => _state;
  bool get isReady => _lastPacket?.preExam?.isReady ?? false;
  PreExamStatus? get preExam => _lastPacket?.preExam;
  TelemetryResponse? get telemetry => _lastPacket?.telemetry;

  void updateState(ExaminationState newState) {
    _state = newState;
    notifyListeners();
  }

  @override
  void dispose() {
    _subscription.cancel();
    super.dispose();
  }
}
