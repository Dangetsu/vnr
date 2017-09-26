# coding: utf8
# comets.py
# 8/31/2014 jichi

import qmldialog

# Global static comet

def globalComet(): # -> QObject
  inst = qmldialog.Kagami.instance
  if inst:
    return inst.globalComet

def gameComet(): # -> QObject
  inst = qmldialog.Kagami.instance
  if inst:
    return inst.gameComet

def termComet(): # -> QObject or None  not available before termview is created
  inst = qmldialog.TermView.instance
  if inst:
    return inst.termComet

# Dynamic comets

def _createQmlPostComet(): return qmldialog.Kagami.instance.createPostComet()

def createPostComet(*args, **kwargs):
  q = _createQmlPostComet()
  return Comet(q, *args, **kwargs)

class Comet(object):
  __slots__ = 'q',
  def __init__(self, q, path='', active=False):
    self.q = q # PostDataComet
    if path:
      self.setPath(path)
    if active:
      self.setActive(active)

  def path(self): return self.q.property('path') # -> str
  def setPath(self, v): self.q.setProperty('path', v)

  def isActive(self): return self.q.property('active') # -> bool
  def setActive(self, t): self.q.setProperty('active', t)

# EOF
