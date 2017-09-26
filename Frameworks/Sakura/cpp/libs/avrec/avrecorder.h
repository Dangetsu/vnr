#ifndef AVRECORDER_H
#define AVRECORDER_H

// avrecorder.h
// 10/28/2014 jichi
// All string must be in UTF-8 encoding.

#include "sakurakit/skglobal.h"
#include <libavutil/pixfmt.h>
#include <stdint.h>

class AVRecorderSettings;
class AVRecorderPrivate;
class AVRecorder
{
  SK_CLASS(AVRecorder)
  SK_DISABLE_COPY(AVRecorder)
  SK_DECLARE_PRIVATE(AVRecorderPrivate)

  // - Construction -
public:
  static bool init();

  AVRecorder();
  ~AVRecorder();
  AVRecorderSettings *settings() const;

  const char *path() const; // path in UTF-8 encoding
  void setPath(const char *path);

  bool start();
  bool stop();

  bool addImageData(const uint8_t *data, int64_t size,
                    int bytesPerLine, int width, int height, AVPixelFormat fmt);
  bool addAudioData(const uint8_t *data, int64_t size);
};

#endif // AVRECORDER_H
