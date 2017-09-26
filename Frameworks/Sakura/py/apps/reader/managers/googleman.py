# coding: utf8
# googleman.py
# 1/22/2015 jichi

from sakurakit.skclass import memoized
from google import googletrans

@memoized
def manager(): return GoogleManager()

def setsession(s): # requests.Session ->
  manager().gt.session = s

def setapi(url): # string ->
  manager().gt.api = url
  #manager().gt.api_translate = url + '/t'
  #manager().gt.api_analyze = url + '/single'
def resetapi():
  gt = manager().gt
  gt.api = gt.API

# This class is reserved to parse complicated google translation analysis
class GoogleManager:

  def __init__(self):
    self.gt = googletrans.GoogleJsonTranslator()

  def translate(self, *args, **kwargs): # -> unicode  text
    return self.gt.translate(*args, **kwargs)

# EOF
