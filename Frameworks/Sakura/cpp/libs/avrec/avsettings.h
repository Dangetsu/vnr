#ifndef AVSETTINGS_H
#define AVSETTINGS_H

// avsettings.h
// 10/29/2014 jichi

#include <stdint.h>

class AVRecorderSettings
{
public:
  int fps; // frame per second
  int gop; // group of pictures
  int width,
      height;

  AVRecorderSettings()
  : fps(25), gop(15) // the same as PAL, 25fps, gop = 0.6 second = 1/25*15
    , width(1280), height(720) // 720P
  {}
};

#endif // AVSETTINGS_H
