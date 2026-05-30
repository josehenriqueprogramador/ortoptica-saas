import 'dart:convert';
import 'dart:async';
import '../models/clinical_packet.dart';

class ClinicalStreamingService {
  final StreamController<ClinicalPacket> _controller = StreamController<ClinicalPacket>.broadcast();
  
  Stream<ClinicalPacket> get packetStream => _controller.stream;

  void handleIncomingMessage(String message) {
    try {
      final Map<String, dynamic> json = jsonDecode(message);
      final packet = ClinicalPacket.fromJson(json);
      
      // O controller expõe apenas o envelope consolidado
      _controller.sink.add(packet);
    } catch (e) {
      print("Erro de parsing no ClinicalPacket: $e");
    }
  }

  void dispose() {
    _controller.close();
  }
}
