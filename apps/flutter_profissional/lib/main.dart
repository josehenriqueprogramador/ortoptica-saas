import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'core/networking/clinical_streaming_service.dart';
import 'features/examination/controllers/examination_controller.dart';
import 'features/examination/pages/examination_page.dart';

// Variável global para armazenar as câmeras disponíveis do dispositivo
List<CameraDescription> availableSystemCameras = [];

Future<void> main() async {
  // Garante que o motor do Flutter esteja inicializado antes de chamar APIs nativas
  WidgetsFlutterBinding.ensureInitialized();
  
  try {
    // Busca as câmeras de hardware do dispositivo
    availableSystemCameras = await availableCameras();
  } catch (e) {
    debugPrint('🚨 Erro ao carregar o hardware de câmera: $e');
  }

  runApp(const OrtopticaProfissionalApp());
}

class OrtopticaProfissionalApp extends StatelessWidget {
  const OrtopticaProfissionalApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Injeção de dependência básica
    final streamingService = ClinicalStreamingService();
    final examinationController = ExaminationController(streamingService);

    return MaterialApp(
      title: 'Ortóptica SaaS - Médico',
      theme: ThemeData.dark().copyWith(
        primaryColor: Colors.emerald,
        scaffoldBackgroundColor: const Color(0xFF0F172A), // slate-900
      ),
      home: ExaminationPage(controller: examinationController),
    );
  }
}
