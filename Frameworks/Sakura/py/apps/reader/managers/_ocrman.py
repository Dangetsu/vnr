# coding: utf8
# _ocrman.py
# 9/7/2014 jichi

__all__ = 'OcrImageObject', 'OcrSettings'

import math, os
from PySide.QtCore import Qt, QObject, Property, Signal, Slot, QUrl
from PySide.QtGui import QPixmap
from sakurakit import skfileio
from sakurakit.skclass import Q_Q
from sakurakit.skdebug import dprint, dwarn
from colorconv import colorconv
from modi import modi
import ocrutil, termman

# TODO: Move to colorutil
# http://www.had2know.com/technology/hsi-rgb-color-converter-equations.html

#from sakurakit.skprof import SkProfiler

OCR_MIN_WIDTH = 3
OCR_MIN_HEIGHT = 3

OCR_IMAGE_FORMAT = 'png'
OCR_IMAGE_QUALITY = 100 # -1 or [0, 100], 100 is lossless quality

FG_PIXEL = 0xff000000 # black text
BG_PIXEL = 0xffffffff # white background

def capture_pixmap(x, y, width, height, hwnd=None):
  """
  @param  x  int
  @param  y  int
  @param  width  int
  @param  height  int
  @param  hwnd  int
  @return  QPixmap
  """
  if width < OCR_MIN_WIDTH or height < OCR_MIN_HEIGHT:
    dwarn("skip image that is too small: %sx%s" %(width, height))
    return
  if hwnd:
    from sakurakit import skwidgets
    return QPixmap.grabWindow(skwidgets.to_wid(hwnd), x, y, width, height)
  else:
    from PySide.QtCore import QCoreApplication
    qApp = QCoreApplication.instance()
    wid = qApp.desktop().winId()
    return QPixmap.grabWindow(wid, x, y, width, height)

def save_pixmap(pm, path): # QPixmap or QImage, unicode -> bool
  return bool(pm) and not pm.isNull() and pm.save(path, OCR_IMAGE_FORMAT, OCR_IMAGE_QUALITY) and os.path.exists(path)

class OcrSettings(object):
  def __init__(self):
    self.deliminator = '' # str
    self.languages = [] # [str lang]
    self.languageFlags = modi.LANG_JA # int

  def isSpaceEnabled(self): return bool(self.deliminator)
  def setSpaceEnabled(self, t): self.deliminator = ' ' if t else ''

  def language(self): return self.languages[0] if self.languages else 'ja' # -> str

  def setLanguages(self, v): # [str]
    self.languageFlags = modi.locales2lang(v) or modi.LANG_JA # Japanese by default

@Q_Q
class _OcrImageObject(object):

  def __init__(self, q, pixmap, settings,
      x, y, width, height, hwnd):
    self.settings = settings # OcrSettings
    self.pixmap = pixmap # QPixmap
    self.path = '' # str
    self.editable = False # image transformation enabled

    self.x = x # int
    self.y = y # int
    self.width = width # int
    self.height = height # int
    self.hwnd = hwnd # long

    self.colorIntensityEnabled = True
    self.minimumColorIntensity = 0.7
    self.maximumColorIntensity = 1.0

    self.hueEnabled = False
    self.minimumHue = 1/3.
    self.maximumHue = 2/3.

    self.saturationEnabled = False
    self.minimumSaturation = 0.0
    self.maximumSaturation = 0.3

    self.scaleEnabled = False
    self.scaleFactor = 1.0

  @staticmethod
  def _randomPath():
    """
    @return  unicode
    """
    import rc
    from time import time
    return "%s/%f.%s" % (rc.DIR_TMP_OCR, time(), OCR_IMAGE_FORMAT)

  # OCR

  def ocr(self):
    """
    @return  unicode
    """
    img = self.transformPixmap(self.pixmap)
    if not self._savePixmap(img):
      return ''
    # FIXME: Async would crash
    #ret = skthreads.runsync(partial(self._readImageFile, path))
    #with SkProfiler(): # take around 0.5 seconds
    text = self._readImage()
    if text:
      lang = self.settings.language()
      text = termman.manager().applyOcrTerms(text, lang)
    return text

  def captureWindow(self):
    self.pixmap = capture_pixmap(self.x, self.y, self.width, self.height, self.hwnd)

  def captureDesktop(self):
    self.pixmap = capture_pixmap(self.x, self.y, self.width, self.height)

  def _readImage(self, async=True):
    """
    @return  unicode  text
    """
    delim = self.settings.deliminator
    if delim:
      return delim.join(ocrutil.readtexts(self.path, self.settings.languageFlags, async=async))
    else:
      return ocrutil.readtext(self.path, self.settings.languageFlags, async=async)

  # Pixmap

  def _savePixmap(self, pm):
    """
    @param  pm  QPixmap or QImage
    @param  path  unicode
    @return  bool
    """
    path = self._randomPath()
    ret = save_pixmap(pm, path)
    if ret:
      skfileio.removefile(self.path)
      self.setPath(path)
    return ret

  def setPath(self, v):
    self.path = v
    self.q.imageUrlChanged.emit(QUrl.fromLocalFile(v))

  def transformPixmap(self, pm):
    """
    @param  pm  QPixmap
    @return  QPixmap or QImage
    """
    if not pm or pm.isNull() or not self.editable:
      return pm
    img = pm.toImage()
    width = pm.width()
    height = pm.height()

    intensityEnabled = self.colorIntensityEnabled
    hueEnabled = self.hueEnabled
    saturationEnabled = self.saturationEnabled

    # HSI model
    # http://www.had2know.com/technology/hsi-rgb-color-converter-equations.html
    # https://en.wikipedia.org/wiki/HSL_and_HSV#Lightness

    if intensityEnabled and not (hueEnabled or saturationEnabled):
      imin3 = 255 * 3 * self.minimumColorIntensity
      imax3 = 255 * 3 * self.maximumColorIntensity
      for x in xrange(width):
        for y in xrange(height):
          px = img.pixel(x, y) # int
          #a = px >> 24 & 0xff # alpha
          r = px >> 16 & 0xff
          g = px >> 8 & 0xff
          b = px & 0xff
          i3 = r + g +b # I in HSI model * 3
          px = FG_PIXEL if imin3 <= i3 and i3 <=  imax3 else BG_PIXEL
          img.setPixel(x, y, px)

    elif hueEnabled or saturationEnabled or intensityEnabled:

      if hueEnabled:
        hmin = self.minimumHue * math.pi * 2
        hmax = self.maximumHue * math.pi * 2

      if saturationEnabled:
        smin = self.minimumSaturation
        smax = self.maximumSaturation

      if intensityEnabled:
        imin = self.minimumColorIntensity * 255
        imax = self.maximumColorIntensity * 255

      for x in xrange(width):
        for y in xrange(height):
          px = img.pixel(x, y) # int
          rgb = colorconv.pix2rgb(px)

          s,i = colorconv.rgb2hsi_si(*rgb)

          fg = True

          if intensityEnabled and not (imin <= i and i <= imax):
            fg = False

          if fg and saturationEnabled and not (smin <= s and s <= smax):
            fg = False

          if fg and hueEnabled:
            h = colorconv.rgb2hsi_h(*rgb)
            if h is None: # black or white
              fg = False
            elif hmin <= hmax:
              if h < hmin or h > hmax:
                fg = False
            elif hmax < h and h < hmin: # hmax < hmin
              fg = False

          img.setPixel(x, y, FG_PIXEL if fg else BG_PIXEL)

    if self.scaleEnabled and self.scaleFactor != 1.0:
      width *= self.scaleFactor
      height *= self.scaleFactor
      #img = img.scaled(width, height)
      img = img.scaled(width, height, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    return img

# Passed to QML
class OcrImageObject(QObject):
  def __init__(self, parent=None, **kwargs):
    """
    @param  parent  QObject
    @param  pixmap  QPixmap
    @param  settings  OcrSettings
    """
    super(OcrImageObject, self).__init__(parent)
    self.__d = _OcrImageObject(self, **kwargs)

  imageUrlChanged = Signal(QUrl)
  imageUrl = Property(QUrl,
      lambda self: QUrl.fromLocalFile(self.__d.path),
      notify=imageUrlChanged)

  def language(self):
    """
    @return  str
    """
    return self.__d.settings.language()

  def setEditable(self, t): self.__d.editable = t
  def isEditable(self): return self.__d.editable
  editableChanged = Signal(bool)
  editable = Property(bool,
      lambda self: self.__d.editable,
      setEditable,
      notify=editableChanged)

  #winIdChanged = Signal(long)
  #winId = Property(long,
  #    lambda self: self.__d.hwnd,
  #    notify=winIdChanged)

  #@Slot(result=bool)
  #def hasWindow(self): return bool(self.__d.hwnd)

  def setX(self, v): self.__d.x = v
  xChanged = Signal(int)
  x = Property(int,
      lambda self: self.__d.x,
      setX,
      notify=xChanged)

  def setY(self, v): self.__d.y = v
  yChanged = Signal(int)
  y = Property(int,
      lambda self: self.__d.y,
      setY,
      notify=yChanged)

  def setWidth(self, v): self.__d.width = v
  widthChanged = Signal(int)
  width = Property(int,
      lambda self: self.__d.width,
      setWidth,
      notify=widthChanged)

  def setHeight(self, v): self.__d.height = v
  heightChanged = Signal(int)
  height = Property(int,
      lambda self: self.__d.height,
      setHeight,
      notify=heightChanged)

  # Zoom image

  def setScaleEnabled(self, t): self.__d.scaleEnabled = t
  scaleEnabledChanged = Signal(bool)
  scaleEnabled = Property(bool,
      lambda self: self.__d.scaleEnabled,
      setScaleEnabled,
      notify=scaleEnabledChanged)

  def setScaleFactor(self, v): self.__d.scaleFactor = v
  scaleFactorChanged = Signal(float)
  scaleFactor = Property(float,
      lambda self: self.__d.scaleFactor,
      setScaleFactor,
      notify=scaleFactorChanged)

  # Color intensity

  def setColorIntensityEnabled(self, t): self.__d.colorIntensityEnabled = t
  colorIntensityEnabledChanged = Signal(bool)
  colorIntensityEnabled = Property(bool,
      lambda self: self.__d.colorIntensityEnabled,
      setColorIntensityEnabled,
      notify=colorIntensityEnabledChanged)

  def setMinimumColorIntensity(self, v): self.__d.minimumColorIntensity = v
  minimumColorIntensityChanged = Signal(float)
  minimumColorIntensity = Property(float,
      lambda self: self.__d.minimumColorIntensity,
      setMinimumColorIntensity,
      notify=minimumColorIntensityChanged)

  def setMaximumColorIntensity(self, v): self.__d.maximumColorIntensity = v
  maximumColorIntensityChanged = Signal(float)
  maximumColorIntensity = Property(float,
      lambda self: self.__d.maximumColorIntensity,
      setMaximumColorIntensity,
      notify=maximumColorIntensityChanged)

  # Color saturation

  def setSaturationEnabled(self, t): self.__d.saturationEnabled = t
  saturationEnabledChanged = Signal(bool)
  saturationEnabled = Property(bool,
      lambda self: self.__d.saturationEnabled,
      setSaturationEnabled,
      notify=saturationEnabledChanged)

  def setMinimumSaturation(self, v): self.__d.minimumSaturation = v
  minimumSaturationChanged = Signal(float)
  minimumSaturation = Property(float,
      lambda self: self.__d.minimumSaturation,
      setMinimumSaturation,
      notify=minimumSaturationChanged)

  def setMaximumSaturation(self, v): self.__d.maximumSaturation = v
  maximumSaturationChanged = Signal(float)
  maximumSaturation = Property(float,
      lambda self: self.__d.maximumSaturation,
      setMaximumSaturation,
      notify=maximumSaturationChanged)

  # Color hue

  def setHueEnabled(self, t): self.__d.hueEnabled = t
  hueEnabledChanged = Signal(bool)
  hueEnabled = Property(bool,
      lambda self: self.__d.hueEnabled,
      setHueEnabled,
      notify=hueEnabledChanged)

  def setMinimumHue(self, v): self.__d.minimumHue = v
  minimumHueChanged = Signal(float)
  minimumHue = Property(float,
      lambda self: self.__d.minimumHue,
      setMinimumHue,
      notify=minimumHueChanged)

  def setMaximumHue(self, v): self.__d.maximumHue = v
  maximumHueChanged = Signal(float)
  maximumHue = Property(float,
      lambda self: self.__d.maximumHue,
      setMaximumHue,
      notify=maximumHueChanged)

  @Slot(result=unicode)
  def ocr(self):
    """
    @return  unicode
    """
    return self.__d.ocr()

  @Slot()
  def captureWindow(self):
    self.__d.captureWindow()

  @Slot()
  def captureDesktop(self):
    self.__d.captureDesktop()

  @Slot()
  def release(self):
    skfileio.removefile(self.__d.path)
    self.setParent(None)
    dprint("pass")

  #@classmethod
  #def create(cls, x, y, width, height, hwnd=0, **kwargs): # -> cls or None
  #  """
  #  @param  x  int
  #  @param  y  int
  #  @param  width  int
  #  @param  height  int
  #  @param* hwnd  int
  #  @param* kwargs  parameters to create OcrImageObject
  #  """
  #  pm = capture_pixmap(x, y, width, height, hwnd)
  #  if not pm or pm.isNull():
  #    dwarn("failed to capture image")
  #    return
  #  return cls(pixmap=pm, x=x, y=y, width=width, height=height, hwnd=hwnd, **kwargs)


  def transformPixmap(self, pm):
    """
    @param  pm  QPixmap
    @return  QPixmap or QImage or None
    """
    #with SkProfiler(): # 9/12/2014: time = 1.3e-05
    return self.__d.transformPixmap(pm)

# EOF
