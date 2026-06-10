import 'dart:async';
import 'dart:isolate';
import 'dart:typed_data';
import 'package:image/image.dart' as img;
import 'package:camera/camera.dart';

/// Mensagem de controle enviada para o Isolate de processamento
class CameraTaskPacket {
  final SendPort replyPort;
  final dynamic rawCameraImage;
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
    
    _isolate = await Isolate.spawn(_imageProcessingWorker, _receivePort!.sendPort);
    
    _receivePort!.listen((message) {
      if (message is SendPort) {
        _isolateSendPort = message;
      } else if (message is CameraOutputPacket) {
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
    initialReplyPort.send(workerReceivePort.sendPort);

    workerReceivePort.listen((message) {
      if (message is CameraTaskPacket) {
        try {
          if (message.rawCameraImage is CameraImage) {
            CameraImage cameraImage = message.rawCameraImage;
            img.Image? convertedImage;

            if (cameraImage.format.group == ImageFormatGroup.yuv420) {
              convertedImage = img.Image.fromBytes(
                width: cameraImage.width,
                height: cameraImage.height,
                bytes: cameraImage.planes[0].bytes.buffer,
                order: img.ChannelOrder.bgra, 
              );
            } else if (cameraImage.format.group == ImageFormatGroup.bgra8888) {
              convertedImage = img.Image.fromBytes(
                width: cameraImage.width,
                height: cameraImage.height,
                bytes: cameraImage.planes[0].bytes.buffer,
                order: img.ChannelOrder.bgra,
              );
            }

            if (convertedImage != null) {
              // COMPRESSÃO REAL PARA JPEG
              final jpegBytes = img.encodeJpg(convertedImage, quality: 75);
              
              message.replyPort.send(CameraOutputPacket(
                jpegBytes: Uint8List.fromList(jpegBytes),
                timestamp: message.timestamp,
              ));
            }
          }
        } catch (e) {
          print('🚨 Erro de compressão de imagem no worker Isolate: $e');
        }
      }
    });
  }

  void dispose() {
    _isolate?.kill(priority: Isolate.immediate);
    _receivePort?.close();
    _outputController?.close();
  }
}
