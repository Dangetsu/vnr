# coding: utf8
# debug.py
# 11/16/2012 jichi

import sys, os
def initenv():

  # Add current and parent folder to module path
  mainfile = os.path.abspath(__file__)
  maindir = os.path.dirname(mainfile)

  sys.path.append(maindir)
  os.chdir(maindir)

  import config
  map(sys.path.append, config.ENV_PYTHONPATH)
  map(sys.path.append, config.APP_PYTHONPATH)

  for it in 'PATH', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH':
    try: os.environ[it] += os.pathsep + os.pathsep.join(config.ENV_PATH)
    except: pass

def debugon():
  from sakurakit import skdebug
  skdebug.DEBUG = True
  import config
  config.APP_DEBUG = True

def app():
  debugon()

  import app
  a = app.Application(sys.argv)
  a.loadTranslations()
  return a

def app_exec(timeout=1000):
  debugon()

  from PySide.QtCore import QTimer
  from Qt5.QtWidgets import QApplication
  app = QApplication(sys.argv)
  QTimer.singleShot(timeout, app.quit)
  return app.exec_()

SHOW_WIDGETS = {}
def show(text, key=None):
  w = SHOW_WIDGETS.get(key)
  if not w:
    from Qt5 import QtWidgets
    SHOW_WIDGETS[key] = w = QtWidgets.QTextEdit()
    w.setAcceptRichText(False)
  if not isinstance(text, basestring):
    import json
    text = json.dumps(text, indent=2, ensure_ascii=False)
  w.setWindowTitle("key: %s" % key)
  w.setPlainText(text)
  w.show()

def dumpzhongri():
  from scripts import eb2db

  import rc
  gaiji = rc.gaiji_dict('ZHONG_RI')
  path = 'Z:/Local/Windows/Applications/EB/ZHONG_RI'

  eb2db.dump(path, gaiji)

if __name__ == '__main__':
  print "debug: enter"

  #import settings
  #ss = settings.global_()
  #ss.setBlockedLanguages({'en','de'})
  #print ss.blockedLanguages()

  def test_vnragent():
    import rpcman, config

    if False:
      import app
      a = QApplication(sys.argv)

      d = rpcman._RpcServer()
      d.startClient('127.0.0.1', config.QT_METACALL_PORT)
      d.waitForReady()
      #d.q_activated.emit()
      #d.q_pingServer.emit(123)
      d.q_updateServerJson.emit("123456")
      #d.q_push.emit(123)
      a.processEvents()
      sys.exit(0)

    import procutil
    path = ur'S:\Games\カミカゼ☆エクスプローラー！\cs2.exe'
    pid = procutil.get_process_by_path(path).pid

    from sakurakit import skwinsec
    # It is better to use injectfunc1(AddDllDirectory), which is only supported by win8
    dlls = [
      r'S:\Stream\Library\Frameworks\Qt\PySide\QtCore4.dll',
      r'S:\Stream\Library\Frameworks\Qt\PySide\QtNetwork4.dll',
      r'S:\Stream\Library\Frameworks\Sakura\build\vnragent.dll',
    ]
    for dll in dlls:
      import os
      print os.path.exists(dll)
      skwinsec.injectdll(dll, pid=pid)
    print "debug: leave"

  def test_wmp():
    import os
    from sakurakit import skthreads
    from sakurakit.skwincom import SkCoInitializer
    from wmp.wmp import WindowsMediaPlayer

    #url = "http://translate.google.com/translate_tts?tl=ja&q=hello"
    url = "http://tts.baidu.com/text2audio?lan=jp&ie=UTF-8&text=hello"
    #url = "Z:/Users/jichi/tmp/test.mp3"
    #url = r"Z:\Users\jichi\tmp\test.mp3"
    #url = "Z:\Users\jichi\tmp\test.mp3"
    #url = "Z:\\Users\\jichi\\tmp\\test.mp3"
    print os.path.exists(url)
    p = WindowsMediaPlayer()
    def run():
      with SkCoInitializer(threading=True):
        print p.isValid()
        print p.play(url)
        os.system("pause")

    a = app()
    skthreads.runasync(run)
    a.exec_()

  def test_ocr():
    from modi import modi
    path = "wiki.tiff"
    #path = r"Z:\Users\jichi\opt\stream\Library\Frameworks\Sakura\py\apps\reader\wiki.tiff"
    lang = modi.LANG_JA
    ok = modi.readfile(path, lang)

  def test_chat():
    a = app()
    import chatview
    chatview.manager().showTopic('global')
    a.exec_()

  def test_zunko():
    from sakurakit import skpaths
    path = r'Z:\Local\Windows\Applications\AHS\VOICEROID+\zunko'
    #skpaths.append_path(path) # crash
    skpaths.prepend_path(path)

    from voiceroid.zunko import ZunkoTalk
    ai = ZunkoTalk()
    print ai.load()
    #ai.setVolume(1)
    t = "hello world"
    print ai.speak(t)

    #from PySide.QtCore import QCoreApplication
    #a = QCoreApplication(sys.argv)
    a = app()
    a.exec_()

  def test_cc():
    from opencc import opencc
    import config
    opencc.setdicdir(config.OPENCC_DIC_LOCATION)

    #t = u"里面"
    t = u"我方"
    t = u"轻轻地"
    #t = opencc.zhs2zht(t)
    t = opencc.containszhs(t)
    #t = opencc.zht2tw(t)
    print t
    return

    a = app()
    from Qt5.QtWidgets import QLabel
    w = QLabel("%s" % t)
    w.show()
    a.exec_()

  def test_phonon():
    from PySide.phonon import Phonon
    a = app()

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

  #test_phonon()

  def test_dll():
    from pytrscript import TranslationScriptPerformer
    from pytrcodec import TranslationCoder

  def test_dpwing():
    dumpzhongri()

  def test_wadoku():
    import ebdict
    d = ebdict.wadoku()
    t = u'可愛い'
    #t = u'風'
    #t = u'です'
    #t = u'薫'
    #t = u'わたし'
    #t = u'友達'
    q = d.lookup(t)
    if q:
      result = None
      for it in q:
        print "heading:", it.heading().decode('utf8')
        result = it.text().decode('utf8')
        break
      if result:
        from dictp import wadokudictp
        t = wadokudictp.parsedef(result)
        print result
        print t
        #result += "\n\n" + t
        #a = app()
        #show(result)
        #a.exec_()

  def test_jmdict():
    import ebdict
    #lang = 'nl'
    #lang = 'ru'
    lang = 'fr'
    d = ebdict.jmdict(lang)
    #t = u'可愛い'
    #t = u'親父'
    #t = u'想像'
    t = u'貰う'
    #t = u'殺す'
    #t = u'風'
    #t = u'です'
    #t = u'薫'
    #t = u'わたし'
    #t = u'友達'
    q = d.lookup(t)
    if q:
      result = None
      for it in q:
        print "heading:", it.heading().decode('utf8')
        result = it.text().decode('utf8')
        break
      if result:
        from dictp import jmdictp
        t = jmdictp.parsedef(result, lang)
        print result
        print t
        #result += "\n\n" + t
        #a = app()
        #show(result)
        #a.exec_()

  def test_lib():
    from transliterate import translit
    lang = "ru"
    #lang = "uk"
    #lang = "el"
    print translit("helloi", lang)

  initenv()
  #test_jmdict()
  test_lib()

# EOF
