import 'dart:async';
import 'dart:isolate';
import 'dart:typed_data';

/// Mensagem de controle enviada para o Isolate de processamento
class CameraTaskPacket {
  final SendPort replyPort;
  final dynamic rawCameraImage; // Representa o CameraImage ou buffer planar do Flutter
  final double timestamp;

  CameraTaskPacket({
    required this.replyPort,
    required this.rawCameraImage,
    required this.timestamp,
  });
}

/// Resposta emitida pelo Isolate contendo o JPEG compactado e pronto para a rede
class CameraOutputPacket {
  final Uint8List jpegBytes;
  final double timestamp;

  CameraOutputPacket({
    required this.jpegBytes,
    required this.timestamp,
  });
}

class CameraProcessor {
  Isolate? _isolate;
  ReceivePort? _receivePort;
  SendPort? _isolateSendPort;
  
  StreamController<CameraOutputPacket>? _outputController;
  Stream<CameraOutputPacket> get processedFramesStream => _outputController?.stream ?? const Stream.empty();

  /// Inicializa a infraestrutura de concorrência e o Isolate em background
  Future<void> initialize() async {
    _outputController = StreamController<CameraOutputPacket>.broadcast();
    _receivePort = ReceivePort();

    // Dispara a Thread separada de processamento
    _isolate = await Isolate.spawn(_imageProcessingWorker, _receivePort!.sendPort);

    // Aguarda o Handshake inicial para obter a porta de escuta do Isolate
    _receivePort!.listen((message) {
      if (message is SendPort) {
        _isolateSendPort = message;
      } else if (message is CameraOutputPacket) {
        // Redireciona o pacote pronto para quem está consumindo o pipeline
        _outputController?.add(message);
      }
    });
  }

  /// Despacha um frame bruto para compressão assíncrona
  void processFrameAsync(dynamic cameraImage) {
    if (_isolateSendPort == null) return;

    final timestamp = DateTime.now().millisecondsSinceEpoch / 1000.0;
    
    _isolateSendPort!.send(CameraTaskPacket(
      replyPort: _receivePort!.sendPort,
      rawCameraImage: cameraImage,
      timestamp: timestamp,
    ));
  }

  /// O WORKER ISOLADO (Executado fora da UI Thread principal)
  static void _imageProcessingWorker(SendPort initialReplyPort) {
    final workerReceivePort = ReceivePort();
    
    // Devolve para a Main Isolate a porta onde este worker escuta comandos
    initialReplyPort.send(workerReceivePort.sendPort);

    workerReceivePort.listen((message) {
      if (message is CameraTaskPacket) {
        try {
          // -----------------------------------------------------------------
          // PIPELINE OPTIMIZADO PARA HARDWARE ARM (Compressão & Conversão)
          // -----------------------------------------------------------------
          // Em produção, aqui você utiliza pacotes nativos (como image ou os
          // ponteiros de memória do camera_android) para extrair os planos YUV420
          // e encodá-los rapidamente para JPEG.
          
          // MOCK DE CONVERSÃO TÉRMICA:
          // Simula um buffer JPEG de 40KB gerado instantaneamente
          final compressedBytes = Uint8List(40000); 

          // Devolve o pacote empacotado para a Thread principal despachar
          message.replyPort.send(CameraOutputPacket(
            jpegBytes: compressedBytes,
            timestamp: message.timestamp,
          ));
        } catch (e) {
          // Mecanismo silencioso contra quebras de frame
          print('🚨 Erro de compressão de imagem no worker Isolate: $e');
        }
      }
    });
  }

  /// Encerra as threads abertas para liberar recursos do sistema operacional
  void dispose() {
    _isolate?.kill(priority: Isolate.immediate);
    _receivePort?.close();
    _outputController?.close();
  }
}
