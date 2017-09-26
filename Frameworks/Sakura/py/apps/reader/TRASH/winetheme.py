# coding: utf8
# winetheme.py
# 9/29/2013 jichi

if __name__ == '__main__':
  import debug
  debug.initenv()

import features
if features.WINE:
  from sakurakit.skdebug import dwarn

  MAC_THEME = {
    'ActiveBorder' : "240 240 240",
    'ActiveTitle' : "240 240 240",
    'AppWorkSpace' : "198 198 191",
    'Background' : "0 0 0",
    'ButtonAlternativeFace' : "216 216 216",
    'ButtonDkShadow' : "85 85 82",
    'ButtonFace' : "240 240 240",
    'ButtonHilight' : "255 255 255",
    'ButtonLight' : "255 255 255",
    'ButtonShadow' : "198 198 191",
    'ButtonText' : "0 0 0",
    'GradientActiveTitle' : "240 240 240",
    'GradientInactiveTitle' : "240 240 240",
    'GrayText' : "198 198 191",
    'Hilight' : "119 153 221",
    'HilightText' : "0 0 0",
    'InactiveBorder' : "240 240 240",
    'InactiveTitle' : "240 240 240",
    'InactiveTitleText' : "255 255 255",
    'InfoText' : "0 0 0",
    'InfoWindow' : "216 216 216",
    'Menu' : "240 240 240",
    'MenuBar' : "0 0 0",
    'MenuHilight' : "179 145 105",
    'MenuText' : "0 0 0",
    'Scrollbar' : "240 240 240",
    'TitleText' : "255 255 255",
    'Window' : "255 255 255",
    'WindowFrame' : "0 0 0",
    'WindowText' : "0 0 0",
  }

  def dump():
    theme = MAC_THEME
    USERDIC_REG_PATH   = r"Control Panel\Colors"
    import _winreg
    hk = _winreg.HKEY_CURRENT_USER
    try:
      with _winreg.ConnectRegistry(None, hk) as reg: # computer_name = None
        with _winreg.OpenKey(reg, USERDIC_REG_PATH) as path:
          for k in theme.iterkeys():
            try:
              v = _winreg.QueryValueEx(path, k)[0]
              print k, "=", v
            except WindowsError:
              print k, "=", None
    except (WindowsError, TypeError, AttributeError), e: dwarn(e)

  # FIXME 9/29/2013: WindowsError 5: permission denied on Wine!
  def install():
    theme = MAC_THEME
    USERDIC_REG_PATH   = r"Control Panel\Colors"
    import _winreg
    hk = _winreg.HKEY_CURRENT_USER
    try:
      with _winreg.ConnectRegistry(None, hk) as reg: # computer_name = None
        with _winreg.OpenKey(reg, USERDIC_REG_PATH, _winreg.KEY_SET_VALUE) as path:
          for k,v in theme.iteritems():
            _winreg.SetValueEx(path, k, 0, _winreg.REG_SZ, v)
    except (WindowsError, TypeError, AttributeError), e: dwarn(e)

  # FIXME 9/29/2013: WindowsError 5: permission denied on Wine!
  def uninstall():
    theme = MAC_THEME
    USERDIC_REG_PATH   = r"Control Panel\Colors"
    import _winreg
    hk = _winreg.HKEY_CURRENT_USER
    try:
      with _winreg.ConnectRegistry(None, hk) as reg: # computer_name = None
        with _winreg.OpenKey(reg, USERDIC_REG_PATH, _winreg.KEY_SET_VALUE) as path:
          for k in theme.iterkeys():
            try: _winreg.DeleteKeyEx(path, k) # in case the path does not exist
            except WindowsError: pass
    except (WindowsError, TypeError, AttributeError), e: dwarn(e)

else:
  def dump(): pass
  def install(): pass
  def uninstall(): pass

if __name__ == '__main__':
  dump()
  install()
  #uninstall()

# EOF
