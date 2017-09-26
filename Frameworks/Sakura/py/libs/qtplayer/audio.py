# coding: utf8
# 10/27/2014

from PySide.phonon import Phonon
from PySide.QtCore import QObject

class AudioPlayer(QObject):

  def __init__(self, parent=None):
    super(AudioPlayer, self).__init__(parent)

    self.mediaObject = Phonon.MediaObject(self)
    self.audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
    self.path = Phonon.createPath(self.mediaObject, self.audioOutput)

  def volume(self, v):
    """
    @return  float
    """
    return  self.audioOutput.volume()

  def setVolume(self, v):
    """
    @param  v  float
    """
    self.audioOutput.setVolume(v)

  def setCurrentSource(self, path):
    """
    @param  path  unicode
    """
    self.mediaObject.setCurrentSource(path)

  def play(self): self.mediaObject.play()
  def stop(self): self.mediaObject.stop()

if __name__ == '__main__':
  import os, sys
  from PySide.QtCore import *
  a = QCoreApplication(sys.argv)

  # http://qt-project.org/doc/qt-4.8/phonon-overview.html#audio
  url = "z:/Users/jichi/tmp/test.mp3"
  print os.path.exists(url)
  mo = Phonon.MediaObject()
  audioOutput = Phonon.AudioOutput(Phonon.MusicCategory)
  path = Phonon.createPath(mo, audioOutput)


  #mo.setCurrentSource(Phonon.MediaSource(url))
  mo.setCurrentSource(url)
  print mo.play()

  a.exec_()

# EOF
