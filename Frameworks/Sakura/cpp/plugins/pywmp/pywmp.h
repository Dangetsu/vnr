#ifndef PYWMP_H
#define PYWMP_H

// pywmp.h
// 10/5/2014 jichi

#include "sakurakit/skglobal.h"
#include <string>

class WindowsMediaPlayer_p;
class WindowsMediaPlayer
{
  SK_CLASS(WindowsMediaPlayer)
  SK_DISABLE_COPY(WindowsMediaPlayer)
  SK_DECLARE_PRIVATE(WindowsMediaPlayer_p)

public:
  // Construction
  //
  WindowsMediaPlayer();
  ~WindowsMediaPlayer();

  bool isValid() const;

  std::wstring version() const;

  // Controls

  bool play(const std::wstring &url);
  bool stop();

  // Settings

  int volume() const; // [0, 100] or 0 if failed
  void setVolume(int v);

  double speed() const; // 1.0 by default
  void setSpeed(double v);
};

#endif // PYWMP_H
