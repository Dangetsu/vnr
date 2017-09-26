# coding: utf8
# libman.py
# 12/8/2012 jichi

import os
from sakurakit import skos, skpaths
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint
import settings

#class Library(object):
#  def __init__(self): pass
#  def isAvailable(self): return False
#  def refresh(self): pass
#  def location(self): return ""
#  #def url(self): return ""

# Cached abstract class
class Library(object):

  def __init__(self):
    self.__exists = None

  def location(self):
    """
    @return  str not None
    """
    return ""

  def refresh(self):
    self.__exists = None

  def exists(self):
    """Cached"""
    if self.__exists is None:
      self.__exists = self.verifyLocation(self.location())
    return self.__exists

  def verifyLocation(self, path):
    return bool(path) and os.path.exists(path)

class AppLocale(Library):
  URL = "http://www.microsoft.com/en-us/download/details.aspx?id=13209"

  def location(self):
    """@reimp"""
    return os.path.join(skpaths.WINDIR, "AppPatch")

  def verifyLocation(self, path):
    """@reimp"""
    return bool(path) and os.path.exists(os.path.join(path, "AlLayer.dll"))

class Atlas(Library):
  URL = "http://www.fujitsu.com/global/services/software/translation/atlas/downloads/trial.html"

  def location(self):
    """@reimp"""
    ret = settings.global_().atlasLocation()
    if self.verifyLocation(ret):
      return ret

    from atlas import atlas
    ret = atlas.location()
    if self.verifyLocation(ret):
      return ret

    return settings.global_().atlasLocation()

  def verifyLocation(self, path):
    """@reimp"""
    return bool(path) and os.path.exists(os.path.join(path, "AtleCont.dll"))

  def setLocation(self, path):
    if path != self.location():
      settings.global_().setAtlasLocation(path)
      if path:
        skpaths.append_path(path)

class Lec(Library):
  URL = "http://www.lec.com/listProduct.asp?product=Premium&family=Power-Translator"

  def location(self):
    """@reimp"""
    ret = settings.global_().lecLocation()
    if self.verifyLocation(ret):
      return ret

    from lec import powertrans
    ret = powertrans.location()
    if self.verifyLocation(ret):
      return ret

    return settings.global_().lecLocation()

  def verifyLocation(self, path):
    """@reimp"""
    return bool(path) and os.path.exists(os.path.join(path, "Nova/JaEn/EngineDll_je.dll"))

  def setLocation(self, path):
    if path != self.location():
      settings.global_().setLecLocation(path)
      if path:
        skpaths.append_path(os.path.join(path, r"Nova\JaEn"))

class JBeijing(Library):
  URL = "http://www.kodensha.jp/soft/jb/"

  def location(self):
    """@reimp"""
    ret = settings.global_().jbeijingLocation()
    if self.verifyLocation(ret):
      return ret

    from jbeijing import jbeijing
    ret = jbeijing.location()
    if self.verifyLocation(ret):
      return ret
    return settings.global_().jbeijingLocation()

  def verifyLocation(self, path):
    """@reimp"""
    return bool(path) and os.path.exists(os.path.join(path, "JBJCT.dll"))

  def setLocation(self, path):
    if path != self.location():
      settings.global_().setJBeijingLocation(path)
      if path:
        skpaths.append_path(path)

class FastAIT(Library):
  URL = "http://ky.iciba.com"

  def location(self):
    """@reimp"""
    return settings.global_().fastaitLocation()

  def verifyLocation(self, path):
    """@reimp"""
    return bool(path) and os.path.exists(os.path.join(path, "GTS"))

  def setLocation(self, path):
    if path != self.location():
      settings.global_().setFastaitLocation(path)
      if path:
        from sakurakit import skfileio
        dllpaths = skfileio.listdirs(os.path.join(path, "GTS"))
        if dllpaths:
          skpaths.append_paths(dllpaths)

class Dreye(Library):
  URL = "http://www.dreye.com"

  def location(self):
    """@reimp"""
    ret = settings.global_().dreyeLocation()
    if self.verifyLocation(ret):
      return ret
    from dreye import dreyemt
    ret = dreyemt.location()
    if self.verifyLocation(ret):
      return ret
    return settings.global_().dreyeLocation()

  def verifyLocation(self, path):
    """@reimp"""
    return bool(path) and os.path.exists(os.path.join(path, r"DreyeMT\SDK\bin"))

  def setLocation(self, path):
    if path != self.location():
      settings.global_().setDreyeLocation(path)
      if path:
        skpaths.append_path(os.path.join(path, r"DreyeMT\SDK\bin"))

class EzTrans(Library):
  URL = "http://www.cssoft.co.kr"

  def location(self):
    """@reimp"""
    ret = settings.global_().ezTransLocation()
    if self.verifyLocation(ret):
      return ret

    from eztrans import eztrans
    ret = eztrans.location()
    if self.verifyLocation(ret):
      return ret
    return settings.global_().ezTransLocation()

  def verifyLocation(self, path):
    """@reimp"""
    return bool(path) and os.path.exists(os.path.join(path, "J2KEngine.dll"))

  def setLocation(self, path):
    if path != self.location():
      settings.global_().setEzTransLocation(path)
      if path:
        skpaths.append_path(path)

class TransCAT(Library):
  URL = "http://www.clickq.com"

  def location(self):
    """@reimp"""
    ret = settings.global_().transcatLocation()
    if self.verifyLocation(ret):
      return ret

    from transcat import transcat
    ret = transcat.location()
    if self.verifyLocation(ret):
      return ret
    return settings.global_().transcatLocation()

  def verifyLocation(self, path):
    """@reimp"""
    return bool(path) and os.path.exists(os.path.join(path, "D_JK.dll"))

  def setLocation(self, path):
    if path != self.location():
      settings.global_().setTranscatLocation(path)
      if path:
        skpaths.append_path(path)

class LocaleEmulator(Library):
  #URL = "http://www.hongfire.com/forum/showthread.php/418962-Locale-Emulator-another-tool-for-japanese-locale-emulation"
  #URL = "https://github.com/xupefei/Locale-Emulator"
  #URL = "http://bbs.sumisora.org/read.php?tid=11045407"
  #URL = "https://app.box.com/LocaleEmulator"
  URL = "https://github.com/xupefei/Locale-Emulator/releases"

  def location(self):
    """@reimp"""
    return settings.global_().localeEmulatorLocation()

  def verifyLocation(self, path):
    """@reimp"""
    return bool(path) and os.path.exists(os.path.join(path, "LEProc.exe"))

  def setLocation(self, path):
    if path != self.location():
      settings.global_().setLocaleEmulatorLocation(path)
      if path:
        skpaths.append_path(path)

class Ntleas(Library):
  URL = "http://ntlea.codeplex.com"

  def location(self):
    """@reimp"""
    return settings.global_().ntleasLocation()

  def verifyLocation(self, path):
    """@reimp"""
    return bool(path) and os.path.exists(os.path.join(path, "ntleas.exe"))

  def setLocation(self, path):
    if path != self.location():
      settings.global_().setNtleasLocation(path)
      if path:
        skpaths.append_path(path)

class ModiOcr(Library):
  URL = "http://www.microsoft.com/office/downloads/"
  DOWNLOAD_URL = "https://mega.co.nz/#F!g00SQJZS!pm3bAcS6qHotPzJQUT596Q"

  def location(self):
    from modi import modi
    return modi.MODI_PATH

class WindowsMediaPlayer(Library):
  URL = "http://windows.microsoft.com/en-us/windows/download-windows-media-player"

  def location(self):
    from wmp import wmp
    return wmp.WMP_DLL_PATH

class QuickTime(Library):
  URL = "http://www.apple.com/quicktime/download/"

  def location(self):
    """@reimp"""
    if not skos.WIN:
      return ""

    QT_REG_PATH   = r"SOFTWARE\Apple Computer, Inc.\QuickTime"
    QT_REG_KEY    = r"InstallDir"
    try:
      import _winreg
      with _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE) as reg:
        with _winreg.OpenKey(reg, QT_REG_PATH) as key:
          return _winreg.QueryValueEx(key, QT_REG_KEY)[0]
    except WindowsError, e:
      dprint(e)
      #dwarn(e) # this is always error if QuickTime is not installed, no need to warn
    return ""

@memoized
def localeEmulator(): return LocaleEmulator()
@memoized
def ntleas(): return Ntleas()
@memoized
def apploc(): return AppLocale()
@memoized
def atlas(): return Atlas()
@memoized
def lec(): return Lec()
@memoized
def jbeijing(): return JBeijing()
@memoized
def fastait(): return FastAIT()
@memoized
def dreye(): return Dreye()
@memoized
def eztrans(): return EzTrans()
@memoized
def transcat(): return TransCAT()
@memoized
def quicktime(): return QuickTime()
@memoized
def modiocr(): return ModiOcr()
@memoized
def wmp(): return WindowsMediaPlayer()

# EOF

#class Ntlea(Library):
#  URL = "" # TODO
#
#  def location(self):
#    """@reimp"""
#    return settings.global_().ntleaLocation()
#
#  def verifyLocation(self, path):
#    """@reimp"""
#    return bool(path) and os.path.exists(os.path.join(path, "ntleac.exe"))
#
#  def setLocation(self, path):
#    if path != self.location():
#      settings.global_().setNtleaLocation(path)
#      if path:
#        skpaths.append_path(path)
