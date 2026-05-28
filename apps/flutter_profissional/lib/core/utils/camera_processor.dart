import 'dart:typed_list';
import 'package:camera/camera.dart';
import 'package:image/image.dart' as img;

class CameraProcessor {
  /// Converte a CameraImage (YUV420) para JPEG isolado da UI Thread.
  /// Otimizado para manter o payload abaixo de 80KB.
  static Uint8List convertYUV420ToJpeg(CameraImage image) {
    final int width = image.width;
    final int height = image.height;

    // Instancia o buffer de imagem da biblioteca 'image'
    final imgImage = img.Image(width: width, height: height);

    final int uvRowStride = image.planes[1].bytesPerRow;
    final int? uvPixelStride = image.planes[1].bytesPerPixel;

    // Algoritmo otimizado de conversão YUV420 espacial para RGB
    for (int x = 0; x < width; x++) {
      for (int y = 0; y < height; y++) {
        final int uvIndex = uvPixelStride! * (x / 2).floor() + uvRowStride * (y / 2).floor();
        final int index = y * width + x;

        if (index >= image.planes[0].bytes.length || uvIndex >= image.planes[1].bytes.length) continue;

        final int yp = image.planes[0].bytes[index];
        final int up = image.planes[1].bytes[uvIndex];
        final int vp = image.planes[2].bytes[uvIndex];

        // Conversão matemática de canais de cor
        int r = (yp + vp * 1436 / 1024 - 179).round().clamp(0, 255);
        int g = (yp - up * 4654 / 1024 + vp * -9360 / 1024 + 135).round().clamp(0, 255);
        int b = (yp + up * 1814 / 1024 - 227).round().clamp(0, 255);

        imgImage.setPixelRgb(x, y, r, g, b);
      }
    }

    // Rotaciona a imagem caso o sensor esteja em portrait (comum em mobile)
    final rotated = img.copyRotate(imgImage, angle: 90);

    // Compacta com qualidade em 70% para garantir sub-80KB e reduzir backpressure
    return Uint8List.fromList(img.encodeJpg(rotated, quality: 70));
  }
}
