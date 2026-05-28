import 'dart:async';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import '../../../core/models/telemetry_response.dart';
import '../../../core/networking/clinical_streaming_service.dart';

enum ExaminationState { idle, connecting, streaming, completed, error }

class ExaminationController extends ChangeNotifier {
  final ClinicalStreamingService _streamingService = ClinicalStreamingService();
  
  ExaminationState _state = ExaminationState.idle;
  TelemetryResponse? _latestTelemetry;
  String _errorMessage = '';
  StreamSubscription<TelemetryResponse>? _telemetrySubscription;

  ExaminationState get state => _state;
  TelemetryResponse? get latestTelemetry => _latestTelemetry;
  String get errorMessage => _errorMessage;

  Future<void> startExamination(String baseUrl, int sessionId) async {
    _state = ExaminationState.connecting;
    _errorMessage = '';
    notifyListeners();

    try {
      await _streamingService.connect(baseUrl, sessionId);
      _state = ExaminationState.streaming;
      
      _telemetrySubscription = _streamingService.telemetryStream.listen(
        (telemetry) {
          _latestTelemetry = telemetry;
          notifyListeners();
        },
        onError: (error) {
          _state = ExaminationState.error;
          _errorMessage = error.toString();
          notifyListeners();
        },
      );
    } catch (e) {
      _state = ExaminationState.error;
      _errorMessage = 'Falha na conexão biomédica: $e';
      notifyListeners();
    }
  }

  /// Alimenta o fluxo em tempo real com a imagem vinda diretamente do hardware do dispositivo
  void handleCameraStreamFrame(CameraImage image) {
    if (_state == ExaminationState.streaming) {
      _streamingService.processAndSendCameraImage(image);
    }
  }

  Future<void> stopExamination() async {
    if (_state != ExaminationState.streaming) return;
    
    _state = ExaminationState.completed;
    await _telemetrySubscription?.cancel();
    await _streamingService.disconnect();
    _latestTelemetry = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _telemetrySubscription?.cancel();
    _streamingService.disconnect();
    super.dispose();
  }
}
