# coding: utf8
# dataman.py
# 10/8/2012 jichi
#
# Always use long for unixtimestamp, as after year 2038 int32 will overflow.

from sakurakit.skprof import SkProfiler

import itertools, operator, os, re #, weakref #, shutil
#from collections import OrderedDict
from ctypes import c_longlong
from datetime import datetime
from functools import partial
#import xml.etree.cElementTree as etree
import yaml
from lxml import etree
from PySide.QtCore import Signal, Slot, Property, Qt, QObject, QDir, QTimer, QCoreApplication, \
                          QAbstractListModel, QModelIndex
from sakurakit import skcursor, skdatetime, skevents, skfileio, sknetio, skpaths, skstr, skthreads, skyaml
from sakurakit.skclass import Q_Q, staticproperty, memoized, memoizedproperty
from sakurakit.skcontainer import uniquelist
from sakurakit.skdebug import dprint, dwarn, derror
#from sakurakit.skqml import QmlObject
from sakurakit.sktr import tr_, notr_
from sakurakit.skunicode import sjis_encodable
from convutil import wide2thin, zhs2zht, ja2zh_name_test
from unitraits import jpchars, unichars
from opencc import opencc
from mytr import my, mytr_
import cacheman, config, defs, features, gameman, growl, hashutil, i18n, main, mecabman, netman, osutil, prompt, proxy, refman, rc, settings, termman, textutil

SUBMIT_INTERVAL = 5000 # 5 seconds
REF_SUBMIT_INTERVAL = 1000 # 1 second

def _get_user_name(userId):
  """
  @param  userId  int
  @return  unicode
  """
  if not userId:
    return ''
  u = manager().queryUser(userId)
  return u.name if u else str(userId)

def _is_protected_data(d):
  """
  @param  d  _Comment or _Term or _Reference
  @return  bool
  """
  return d.userId == GUEST_USER_ID and d.timestamp < skdatetime.CURRENT_UNIXTIME - defs.PROTECTED_INTERVAL

def create_game_link(path, launchPath=''): # unicode, unicode -> unicode
  if not path:
    return ''
  return 'javascript://main.launchGameWithLaunchPath("%s", "%s")' % (
      QDir.fromNativeSeparators(path) if path else '',
      QDir.fromNativeSeparators(launchPath) if launchPath else '')

## Data types ##

class UserDigest(object):
  __slots__ = (
    'id',
    'name',
    'language',
    'gender',
    'homepage',
    'avatar',
    'color',
    'termLevel',
    'commentLevel',
    'access',
  )
  def __init__(self, id=0, name='', language='', avatar='', gender='', color='', homepage='',
      termLevel=0, commentLevel=0, access=''):
    self.id = id            # long
    self.name = name        # str
    self.language = language  # str
    self.gender = gender    # 'f' or 'm' or ''
    self.homepage = homepage # unicode
    self.avatar = avatar    # unicode
    self.color = color      # unicode
    self.termLevel = termLevel # int
    self.commentLevel = commentLevel # int
    self.access = access # str

class User(object):
  __slots__ = (
    'id',
    'name',
    'password',
    'language',
    'gender',
    'homepage',
    'avatar',
    'color',
    'termLevel',
    'commentLevel',
    'access',
  )
  def __init__(self, id=0, name='', password='', language='', gender='', color='', avatar='', homepage='',
      termLevel=0, commentLevel=0, access=''):
    self.id = id
    self.name = name         # unicode
    self.password = password # str
    self.language = language # str
    self.gender = gender    # 'f' or 'm' or ''
    self.homepage = homepage # unicode
    self.avatar = avatar    # unicode
    self.color = color      # unicode
    self.termLevel = termLevel # int
    self.commentLevel = commentLevel # int
    self.access = access # str

  def clone(self, language=None, gender=None, homepage=None, color=None, avatar=None):
    return User(
      id=self.id, name=self.name, password=self.password,
      language=language or self.language,
      gender=gender if gender is not None else self.gender,
      homepage=homepage if homepage is not None else self.homepage,
      color=color if color is not None else self.color,
      avatar=avatar if avatar is not None else self.avatar,
      commentLevel=self.commentLevel,
      termLevel=self.termLevel,
      access=self.access,
    )

  #def isGuest(self): return self.id == GUEST_USER_ID and self.name == GUEST.name
  def isGuest(self): return self.name == GUEST.name

  def isLoginable(self):
    return all((self.name, self.password))

  def isMale(self): return self.gender == 'm'
  def isFemale(self): return self.gender == 'f'

  @property
  def avatarUrl(self): # -> string
    return manager().queryUserAvatarUrl(self.userId, cache=True)

ADMIN_USER_ID = 2
GUEST_USER_ID = 4
GUEST = User(id=GUEST_USER_ID, name='guest', password='guest', language='en')

## Game ##

class GameInfo(object):
  __slots__ = (
    '_memoized', # @memoized

    'gameId',
    'itemId',
    'async',
  )

  def __init__(self, gameId=0, itemId=0, async=True):
    self.gameId = gameId # long
    self.itemId = itemId # long
    self.async = async   # bool
    self._refresh()

  def _refresh(self):
    if self.gameId and not self.itemId:
      g = self.game
      if g:
        self.itemId = g.itemId
      if not self.itemId:
        self.itemId = manager().queryGameItemId(id=self.gameId)
    if self.itemId and not self.gameId:
      g = self.game
      if g:
        self.gameId = g.id
      if not self.gameId:
        digs = self.gameFiles
        if digs:
          self.gameId = max(digs, key=lambda it:it.visitCount).id

  @memoizedproperty
  def game(self):
    """Offline
    @return  Game or None
    """
    ret = None
    if self.gameId:
      ret = manager().queryGame(id=self.gameId)
    if not ret and self.itemId:
      ret = manager().queryGame(itemId=self.itemId)
    return ret

  @memoizedproperty
  def gameItem(self):
    """Offline
    @return  GameItem or None
    """
    return manager().queryGameItem(id=self.itemId) if self.itemId else None

  @property
  def local(self): return bool(self.game)

  @memoizedproperty
  def gameFiles(self):
    """Offline
    @return  [GameFile] not None
    """
    ret = None
    if self.itemId:
      ret = manager().queryGameFiles(self.itemId)
    if not ret and self.gameId:
      dig = manager().queryGameFiles(id=self.gameId)
      if dig:
        ret = [dig]
    return ret

  @memoizedproperty
  def upcoming0(self):
    """
    @return  bool
    """
    return bool(self.date0) and self.date0 > skdatetime.CURRENT_UNIXTIME

  @memoizedproperty
  def upcoming(self):
    """
    @return  bool
    """
    return bool(self.date) and self.date > skdatetime.CURRENT_UNIXTIME

  @memoizedproperty
  def recent0(self):
    """
    @return  bool
    """
    return bool(self.date0) and not self.upcoming0 and self.date0 > skdatetime.CURRENT_UNIXTIME - 86400*30 # a month

  @memoizedproperty
  def recent(self):
    """
    @return  bool
    """
    return bool(self.date) and not self.upcoming and self.date > skdatetime.CURRENT_UNIXTIME - 86400*30 # a month

  #@memoizedproperty
  #def type(self): # -> str
  #  return 'otome' if self.otome else 'nuki' if self.okazu else 'junai'

  #@memoizedproperty
  #def typeName(self): # -> unicode
  #  return u'乙女' if self.otome else u'抜き' if self.okazu else u'純愛'

  #@memoizedproperty
  #def referenceDigests(self):
  #  """Offline
  #  @return  [ReferenceDigest] not None
  #  """
  #  return manager().queryReferenceDigests(itemId=self.itemId) if self.itemId else []

  def hasOfflineReferences(self):
    return bool (self.gameId) and manager().containsReferences(gameId=self.gameId)

  @memoizedproperty
  def referenceData(self):
    """Offline
    @return  [Reference] not None
    """
    #if self.gameId: #and manager().containsReferences(gameId=self.gameId):
    return list(manager().queryReferenceData(gameId=self.gameId, onlineLater=True)) if self.gameId else []

  @memoizedproperty
  def amazon(self):
    """Online
    @return  AmazonReference or None
    """
    for it in self.referenceData:
      if it.type == 'amazon':
        kw = refman.manager().queryOne(key=it.key, type=it.type, async=self.async)
        if kw:
          return AmazonReference(**kw)

  @memoizedproperty
  def dmm(self):
    """Online
    @return  DmmReference or None
    """
    for it in self.referenceData:
      if it.type == 'dmm':
        kw = refman.manager().queryOne(key=it.key, type=it.type, async=self.async)
        if kw:
          return DmmReference(**kw)

  @memoizedproperty
  def freem(self):
    """Online
    @return  FreemReference or None
    """
    for it in self.referenceData:
      if it.type == 'freem':
        kw = refman.manager().queryOne(key=it.key, type=it.type, async=self.async)
        if kw:
          return FreemReference(**kw)

  @memoizedproperty
  def steam(self):
    """Online
    @return  SteamReference or None
    """
    for it in self.referenceData:
      if it.type == 'steam':
        kw = refman.manager().queryOne(key=it.key, type=it.type, async=self.async)
        if kw:
          return SteamReference(**kw)

  @memoizedproperty
  def trailers(self):
    """Online
    @return  TrailersReference or None
    """
    for it in self.referenceData:
      if it.type == 'trailers':
        kw = refman.manager().queryOne(key=it.key, type=it.type, async=self.async)
        if kw:
          return TrailersReference(**kw)

  @memoizedproperty
  def trailersItem(self):
    """Online
    @return  {kw} or None
    """
    for it in self.referenceData:
      if it.type == 'trailers':
        kw = refman.trailers().query(it.key, async=self.async)
        if kw:
          return TrailersItem(**kw)

  @memoizedproperty
  def tokuten(self):
    """Online
    @return  TokutenItem
    """
    r = self.scape
    if r:
      key = r.tokuten
      if key:
        kw = refman.tokuten().query(key, async=self.async)
        if kw:
          return TokutenItem(**kw)

  @memoizedproperty
  def scape(self):
    """Online
    @return  ScapeReference
    """
    key = None
    type = 'scape'
    for it in self.referenceData:
      if it.type == type:
        key = it.key
        break
    if not key:
      r = self.trailers
      if r:
        key = r.erogamescape
    if key:
      kw = refman.manager().queryOne(key=key, type=type, async=self.async)
      if kw:
        return ScapeReference(**kw)

  @memoizedproperty
  def getchu(self):
    """Online
    @return  GetchuReference
    """
    key = None
    type = 'getchu'
    for it in self.referenceData:
      if it.type == type:
        key = it.key
        break
    if not key:
      r = self.trailers
      if r:
        key = r.getchu
    if key:
      kw = refman.manager().queryOne(key=key, type=type, async=self.async)
      if kw:
        return GetchuReference(**kw)

  @memoizedproperty
  def gyutto(self):
    """Online
    @return  kw or None
    """
    key = None
    type = 'gyutto'
    for it in self.referenceData:
      if it.type == type:
        key = it.key
        break
    if not key:
      for r in self.trailers, self.scape:
        if r and r.gyutto:
          key = r.gyutto
          break
    if key:
      if self.otome0:
        key = 'http://gyutto.me/i/item%s' % key
      kw = refman.manager().queryOne(key=key, type=type, async=self.async)
      if kw:
        return GyuttoReference(**kw)

  #@memoizedproperty
  #def gyutto(self):
  #  """Online
  #  @return  kw or None
  #  """
  #  for r in self.trailers, self.scape:
  #    if r and r.gyutto:
  #      kw = refman.gyutto().query(r.gyutto)
  #      if kw:
  #        return GyuttoItem(**kw)

  @memoizedproperty
  def melon(self):
    """Online
    @return  kw or None
    """
    key = None
    type = 'melon'
    for it in self.referenceData:
      if it.type == type:
        key = it.key
        break
    if key:
      kw = refman.manager().queryOne(key=key, type=type, async=self.async)
      if kw:
        return MelonReference(**kw)

  @memoizedproperty
  def digiket(self):
    """Online
    @return  kw or None
    """
    key = None
    type = 'digiket'
    for it in self.referenceData:
      if it.type == type:
        key = it.key
        break
    if not key:
      r = self.scape
      if r:
        key = r.digiket
    if key:
      kw = refman.manager().queryOne(key=key, type=type, async=self.async)
      if kw:
        return DiGiketReference(**kw)

  @memoizedproperty
  def dlsite(self):
    """Online
    @return  kw or None
    """
    key = None
    type = 'dlsite'
    for it in self.referenceData:
      if it.type == type:
        key = it.url
        break
    if not key:
      r = self.scape
      if r:
        key = r.dlsiteUrl
    if key:
      kw = refman.manager().queryOne(key=key, type=type, async=self.async)
      if kw:
        return DLsiteReference(**kw)

  @memoizedproperty
  def holyseal(self):
    """Online
    @return  kw or None
    """
    key = None
    type = 'holyseal'
    for it in self.referenceData:
      if it.type == type:
        key = it.key
        break
    if not key:
      r = self.trailers
      if r:
        key = r.holyseal
    if key:
      kw = refman.manager().queryOne(key=key, type=type, async=self.async)
      if kw:
        return HolysealReference(**kw)

  def iterCharacterReferences(self):
    """Online
    @yield  Reference
    """
    for r in self.getchu, self.digiket:
      if r and r.characters:
        yield r

  def hasNames(self):
    """Online
    @return  bool
    """
    return bool(self.getchu and self.getchu.characters)

  def iterNameYomi(self):
    """Online
    yield (unicode name, unicode yomi)
    """
    if self.getchu:
      for name,yomi in self.getchu.iterNameYomi():
        yield name, yomi

  def hasCharacters(self):
    """Online
    @return  bool
    """
    for r in self.iterCharacterReferences():
      return True
    return False

  #@memoizedproperty
  @property
  def scapeCount0(self):
    """
    @return  int not None
    """
    g = self.gameItem
    return g.scapeCount if g else 0

  #@memoizedproperty
  @property
  def scapeMedian0(self):
    """
    @return  int not None
    """
    g = self.gameItem
    return g.scapeMedian if g else 0

  @memoizedproperty
  def overallScore0(self):
    """
    @return  int not None
    """
    g = self.gameItem
    return g.overallScoreSum / g.overallScoreCount if g and g.overallScoreCount else 0

  @memoizedproperty
  def ecchiScore0(self):
    """
    @return  int not None
    """
    g = self.gameItem
    return g.ecchiScoreSum / g.ecchiScoreCount if g and g.ecchiScoreCount else 0

  @property
  def overallScoreCount0(self):
    """
    @return  int not None
    """
    g = self.gameItem
    return g.overallScoreCount if g else 0

  @property
  def ecchiScoreCount0(self):
    """
    @return  int not None
    """
    g = self.gameItem
    return g.ecchiScoreCount if g else 0

  @property
  def overallScoreSum0(self):
    """
    @return  int not None
    """
    g = self.gameItem
    return g.overallScoreSum if g else 0

  @property
  def ecchiScoreSum0(self):
    """
    @return  int not None
    """
    g = self.gameItem
    return g.ecchiScoreSum if g else 0

  def _iterReferences(self):
    for it in self.trailers, self.freem, self.scape, self.holyseal, self.melon, self.digiket, self.getchu, self.gyutto, self.dlsite, self.dmm, self.amazon, self.steam:
      if it:
        yield it

  @property
  def icon(self):
    """
    @return  QtGui.QIcon or None
    """
    g = self.game
    return g.icon() if g else None

  @memoizedproperty
  def title0(self): # str not None
    g = self.gameItem
    return g.title if g else ""

  @memoizedproperty
  def romajiTitle0(self): # str not None
    g = self.gameItem
    return g.romajiTitle if g else ""

  #@memoizedproperty
  @property
  def title(self): # str not None
    ret = self.title0
    if ret:
      return ret
    for r in self._iterReferences():
      return r.title
    return ''

  @property
  def englishTitle(self): # str not None
    r = self.steam
    return r.title if r else ''

  @memoizedproperty
  def romajiTitle(self): # str not None
    r = self.trailers
    if r and r.romanTitle:
      return r.romanTitle
    m = mecabman.manager()
    if m.isLoaded():
      return m.toRomaji(self.title, capital=True)
    return ''

  @property
  def empty(self):
    # Using title is online
    #return not self.title0 and not self.title
    return not self.title0 and not self.itemId and not self.hasOfflineReferences()

  @property
  def homepage(self): # str or None
    for r in self.trailers, self.scape, self.dlsite, self.steam:
      if r and r.homepage:
        return r.homepage

  @property
  def event(self):
    for r in self.melon, self.digiket:
      if r and r.event:
        return r.event

  def hasTwitterWidgets(self):
    r = self.scape
    return bool(r and r.twitterWidgets)

  def iterTwitterWidgets(self):
    """
    @yield  long
    """
    r = self.scape
    if r:
      for it in r.twitterWidgets:
        yield it

    #kw = self.scape
    #if kw:
    #  for k in 'twitter_data_widget_id_official', 'twitter_data_widget_id':
    #    v = kw[k]
    #    if v:
    #      yield v

  @property
  def tokutenUrl(self): # str or None
    r = self.scape
    if r:
      return r.tokutenUrl

  #@property
  #def digiketUrl(self): # str or None
  #  r = self.scape
  #  if r:
  #    return r.digiketUrl

  #@property
  #def holysealUrl(self): # str or None
  #  r = self.trailers
  #  if r:
  #    return r.holysealUrl

  #@property
  #def gyuttoUrl(self): # str or None
  #  for r in self.trailers, self.scape:
  #    if r and r.gyutto:
  #      return r.gyuttoUrl

  @property
  def trailersUrl(self): # str or None
    r = self.trailers
    if r:
      return r.url
    r = self.scape
    if r:
      return r.erogetrailersUrl

  #def iterUrlsWithType(self):
  #  """
  #  @yield  (str url, str type)
  #  """
  #  v = self.homepage
  #  if v:
  #    yield v, 'homepage'
  #  for r in self.scape, self.holyseal:
  #    if r:
  #      yield r.url, r.type
  #  v = self.tokutenUrl
  #  if v:
  #    yield v, 'tokuten'
  #  for r in self.getchu, self.gyutto, self.amazon, self.dmm, self.digiket, self.dlsite:
  #    if r:
  #      yield r.url, r.type
  #  v = self.trailersUrl
  #  if v:
  #    yield v, 'trailers'
  #  v = self.wiki
  #  if v:
  #    yield v, 'wiki'

  #def iterUrlsWithName(self):
  #  """
  #  @yield  (str url, str name)
  #  """
  #  for url, type in self.iterUrlsWithType():
  #    yield url, i18n.site_name(type) or type

  def hasLinks(self):
    """
    @return  bool
    """
    return bool(self.getchu or self.gyutto or self.digiket or self.melon or self.dlsite or self.dmm or self.amazon or self.trailers or self.holyseal or self.scape or self.freem or self.steam) #or self.tokutenUrl

  def iterLinks(self):
    """
    @yield  {str url, str type}
    """
    for r in self.getchu,:
      if r:
        yield r.url, r.type

    if self.gyutto:
       url = ('http://gyutto.me/i/item%s' if self.otome else 'http://gyutto.com/i/item%s') % self.gyutto.key
       yield url, 'gyutto'

    for r in self.amazon, self.melon, self.digiket, self.dlsite, self.dmm, self.steam, self.freem, self.trailers:
      if r:
        yield r.url, r.type

    if self.tokutenUrl:
      yield self.tokutenUrl, 'tokuten'

    for r in self.holyseal, self.scape:
      if r:
        yield r.url, r.type

  @property
  def fileSize0(self): # int
    g = self.gameItem
    return g.fileSize if g else 0

  @memoizedproperty
  def fileSize(self): # long not None
    try: return max(it.fileSize for it in (self.digiket, self.gyutto, self.dlsite, self.freem) if it)
    except ValueError: return 0

  @staticmethod
  def _unparseFileSize(size): # int -> str
    if not size:
      return '0 B'
    elif size < 1024:
      return "%s B" % size
    elif size < 1024 * 1024:
      return "%s KB" % (size / 1024)
    elif size < 1024 * 1024 * 1024:
      return "%s MB" % (size / (1024 * 1024))
    else: # size >= 1024 * 1024 * 1024:
      return "%.2f GB" % (float(size) / (1024 * 1024 * 1024))

  @memoizedproperty
  def fileSizeString(self): return self._unparseFileSize(self.fileSize)
  @memoizedproperty
  def fileSizeString0(self): return self._unparseFileSize(self.fileSize0)

  @memoizedproperty
  def date0(self): # long not None
    date = self.dateObject0
    return skdatetime.date2timestamp(date) if date else 0
    #try: return min(it.date for it in self._iterTrailersAmazonDmmDigests() if it.date)
    #except ValueError: return 0

  @memoizedproperty
  def date(self): # long not None
    if self.date0:
      return self.date0
    try: return min(it.date for it in self._iterReferences() if it.date)
    except ValueError: return 0

  @property
  def dateObject0(self): # datetime or None
    g = self.gameItem
    if g:
      return g.date

  @memoizedproperty
  def dateObject(self):
    return datetime.fromtimestamp(self.date)

  @memoizedproperty
  def brand0(self): # str not None
    g = self.gameItem
    return g.brand if g else ""

  @memoizedproperty
  def brand(self): # str or None
    ret = self.brand0
    if ret:
      return ret
    for r in self.trailers, self.freem, self.melon, self.digiket, self.dmm, self.amazon, self.getchu, self.gyutto, self.dlsite, self.steam:
      if r:
        ret = r.brand
        if ret:
          return ret.replace(u"、", ',').replace(" / ", ',').replace("/", ',').replace(u"／", ',')

  @property
  def brands(self): # [kw] or None
    r = self.trailersItem
    if r:
      return r.brands

  @memoizedproperty
  def price(self): # long or None
    try: return max(it.price
        for it in (self.getchu, self.dlsite, self.amazon, self.dmm, self.digiket, self.melon) if it)
    except ValueError: return 0

  @memoizedproperty
  def series0(self): # unicode
    g = self.gameItem
    if g:
      return g.series

  @memoizedproperty
  def series(self): # unicode or None
    g = self.gameItem
    if g:
      return g.series
    for r in self.trailersItem, self.gyutto, self.dlsite, self.dmm:
      if r and r.series:
        return r.series

  @property
  def wiki(self): # str not None
    g = self.gameItem
    return g.wiki if g else ''

  @memoizedproperty
  def otome0(self): # bool not None
    brand = self.brand0
    if brand and brand in config.OTOME_BRANDS:
      return True
    g = self.gameItem
    return bool(g) and g.otome

  @memoizedproperty
  def ecchi0(self): # bool not None
    g = self.gameItem
    return bool(g) and g.ecchi

  @property
  def otome(self): # bool not None
    if self.otome0:
      return True
    for r in self.trailersItem, self.freem, self.getchu, self.gyutto, self.digiket, self.dlsite, self.dmm, self.steam:
      if r and r.otome:
        return True
    return False

  @property
  def ecchi(self): # bool not None
    if self.ecchi0:
      return True
    for r in self.trailers, self.freem, self.holyseal, self.dmm, self.amazon, self.dlsite, self.melon:
      if r:
        return r.ecchi
    if self.steam:
      return False
    return True

  @memoizedproperty
  def okazu0(self): # bool not None
    brand = self.brand0
    if brand:
      if brand in config.NUKI_BRANDS:
        return True
      if brand in config.JUNAI_BRANDS:
        return False
    g = self.gameItem
    if g and g.okazu:
      return True
    title = self.title0
    for it in defs.OKAZU_TAGS:
      if it in title:
        return True
    #digs = self.referenceDigests
    #if digs:
    #  for it in digs:
    #    if it.type == 'amazon':
    #      return False
    #  for it in digs:
    #    if it.type == 'dmm':
    #      return True
    return False

  @property
  def okazu(self): # bool not None
    if not self.ecchi:
      return False
    if self.doujin:
      return True
    brand = self.brand
    if brand:
      if brand in config.NUKI_BRANDS:
        return True
      if brand in config.JUNAI_BRANDS:
        return False
    r = self.scape
    if r and r.okazu == True:
      return True
    if (self.dmm or self.dlsite) and not self.amazon:
      return True
    title = self.title
    for it in defs.OKAZU_TAGS:
      if it in title:
        return True
    return False

  @memoizedproperty
  def doujin(self): # bool not None
    if self.dlsite and not self.amazon and self.price < 3000:
      return True
    for r in self.dmm, self.trailers, self.gyutto: #, self.melon
      if r and r.doujin:
        return True
    return False

  @memoizedproperty
  def genres(self): # [str] or None
    tags = self.tags
    rpg = self.dlsite and self.dlsite.rpg
    if tags:
      ret = [v for k,v in (
        ('RPG', 'RPG'),
        ('SLG', 'SLG'),
        (u'シミュレーション', 'SLG'),
        ('ACT', 'ACT'),
        (u'アクション', 'ACT'),
        ('3D', '3D'),
        #('3DCG', '3D'),
        (u'アニメ', 'Anime'),
        (u'動画', 'Anime'),
        #(u'アニメーション', 'Anime'),
        #(u'動画・アニメーション', 'Anime'),
        #(u'アドベンチャー', 'AVG'),
      ) if k in tags]
      if rpg and 'RPG' not in ret:
        ret.insert(0, 'RPG')
      slogan = self.slogan
      if slogan:
        if slogan.endswith('SLG'):
          ret.insert(0, 'SLG')
        if slogan.endswith('RPG'):
          ret.insert(0, 'RPG')
        if slogan.endswith('SRPG'):
          ret.insert(0, 'SLG')
          ret.insert(0, 'RPG')
      return uniquelist(ret)
    elif rpg:
      return ['RPG']

  #@memoizedproperty
  #def hasDescriptions(self):
  #  """
  #  @return  bool
  #  """
  #  r = self.getchu
  #  if r and r.story:
  #    return True
  #  r = self.amazon
  #  if r and r.descriptions:
  #    return True
  #  return False

  #@property
  #def descriptions(self): # [unicode] or None
  #  r = self.getchu
  #  if r and r.story:
  #    return r.iterDescriptions()
  #  r = self.amazon
  #  if r and r.descriptions:
  #    return r.iterDescriptions()

  #def hasReview(self): # bool
  #  r = self.amazon
  #  return bool(r and r.review)

  #@property
  #def reviewUrl(self): # str or None
  #  r = self.amazon
  #  if r:
  #    return r.review

  @property
  def comics(self): # [str] or None
    r = self.getchu
    if r:
      return r.comics

  def iterDescriptionReferences(self):
    """
    @yield  Reference
    """
    for r in self.getchu, self.amazon, self.digiket, self.melon, self.dlsite, self.dmm, self.freem, self.steam:
      if r and r.hasDescriptions():
        yield r

  def hasDescriptions(self):
    """
    @return  bool
    """
    for r in self.iterDescriptionReferences():
      return True
    return False

  def iterReviewReferences(self):
    """
    @yield  Reference
    """
    for r in self.scape, self.getchu, self.amazon, self.gyutto, self.digiket, self.dlsite, self.dmm, self.steam: #, self.amazon, self.scape
      if r and r.hasReview():
        yield r

  def hasReviews(self):
    """
    @return  bool
    """
    for r in self.iterReviewReferences():
      return True
    return False

  def iterCharacterDescriptionReferences(self):
    """
    @yield  Reference
    """
    for r in self.getchu, self.digiket, self.dlsite:
      if r and r.characterDescription:
        yield r

  def hasCharacterDescriptions(self):
    """
    @return  bool
    """
    for r in self.iterCharacterDescriptionReferences():
      return True
    return False

  def hasBannerImages(self):
    """
    @return  bool
    """
    g = self.gameItem
    if g and g.banner:
      return True
    r = self.scape
    if r and r.bannerUrl:
      return True
    r = self.trailersItem
    if r and r.banner:
      return True
    r = self.holyseal
    if r and r.banner:
      return True
    # Disabled
    #r = self.getchu
    #if r and r.hasBannerImages():
    #  return True
    return False

  def iterBannerImageUrls(self): # str or None
    g = self.gameItem
    if g and g.banner:
      yield cacheman.cache_image_url(proxy.get_image_url(g.banner))
    # Trailers banner is usually larger
    trailersBanner = scapeBanner = None
    r = self.trailersItem
    if r and r.banner:
      yield cacheman.cache_image_url(proxy.get_image_url(r.banner))
      trailersBanner = r.banner
    r = self.scape
    if r and r.bannerUrl and not sknetio.urleq(r.bannerUrl, trailersBanner):
      yield cacheman.cache_image_url(proxy.get_image_url(r.bannerUrl))
      scapeBanner = r.bannerUrl
    r = self.holyseal
    if r and r.banner and not sknetio.urleq(r.banner, trailersBanner) and not sknetio.urleq(r.banner, scapeBanner):
      yield cacheman.cache_image_url(proxy.get_image_url(r.banner))
    # Disabled
    #r = self.getchu
    #if r and r.hasBannerImages():
    #  for it in r.iterBannerImageUrls():
    #    yield it

  #@memoizedproperty
  #def banner(self): # str or None
  #  for kw in self.scape, self.trailersDetails:
  #    if kw:
  #      ret = kw.get('banner_url') or kw.get('banner') # scape or trailers
  #      if ret:
  #        return ret

  #@property
  #def bannerUrl(self): # str or None
  #  ret = self.banner
  #  if ret:
  #    ret = cacheman.cache_image_url(ret)
  #  return ret

  def iterImageUrlsWithName(self, cache=True):
    """
    @param  yield  (str url, unicode name):
    """
    fn = cacheman.cache_image_url if cache else lambda x: x
    for r,rname in (
        (self.amazon, 'amazon'),
        (self.dmm, 'dmm'),
        (self.getchu, 'getchu'),
        (self.melon, 'melon'),
        (self.dlsite, 'dlsite'),
        (self.digiket, 'digiket'),
        (self.freem, 'freem'),
        (self.steam, 'steam'),

        #(self.gyutto, 'gyutto'),   # crash Qt!
        #(self.tokuten, 'tokuten'),   # crash Qt!
      ):
      if r:
        if r.image:
          yield fn(r.image), 'cover_' + rname
        if r.hasSampleImages():
          for index,url in enumerate(r.iterSampleImageUrls(cache=cache)):
            yield url, 'sample_%s_%i' % (rname, index+1)

    r = self.scape
    if r and r.bannerUrl:
      yield fn(r.bannerUrl), 'banner_scape'

    r = self.holyseal
    if r and r.banner:
      yield fn(r.banner), 'banner_holyseal'

    r = self.trailersItem
    if r:
      if r.banner:
        yield fn(r.banner), 'banner_trailers'
      if r.videos:
        for vid,img in r.iterVideoIdsWithImage(cache=cache):
          yield img, 'youtube_%s' % vid

    r = self.getchu
    if r:
      if r.bannerImages:
        for index,url in enumerate(r.bannerImages):
          url = proxy.get_image_url(url)
          yield fn(url), 'banner_getchu_%i' % (index+1)
      #if r.comics:
      #  for index,url in enumerate(r.comics):
      #    yield fn(url), 'comics_getchu_%i' % (index+1)
      if r.characters:
        for it in r.characters:
          url = it['img']
          if url:
            url = proxy.get_getchu_url(url)
            yield fn(url), 'chara_getchu_%s' % it['id']
      if r.videos:
        for vid,img in r.iterVideoIdsWithImage(cache=cache):
          yield img, 'youtube_%s' % vid
    r = self.freem
    if r and r.videos:
      for vid,img in r.iterVideoIdsWithImage(cache=cache):
        yield img, 'youtube_%s' % vid

    r = self.digiket
    if r:
      if r.characters:
        for it in r.characters:
          url = it['img']
          if url:
            yield fn(url), 'chara_digiket_%s' % it['id']

  @property
  def image0(self): # str or None
    g = self.gameItem
    if g:
      ret = g.image
      if ret and not (features.MAINLAND_CHINA and 'dlsite' in ret):
        return ret
    # amazon first as dmm has NOW PRINTING
    #for r in itertools.chain(
    #    self._iterAmazonDmmDigests(), self._iterAmazonDmmReferences()):
    #for r in self._iterAmazonDmmDigests():
    #  if r.image:
    #    return r.image

  @memoizedproperty
  def image(self): # str or None, amazon first as dmm has NOW PRINTING
    l = [self.getchu, self.freem, self.melon, self.dlsite, self.amazon, self.dmm, self.digiket, self.steam]
    if features.MAINLAND_CHINA and self.dlsite: # disable dlsite in MAINLAND_CHINA
      l.remove(self.dlsite)
    for r in l:
      if r and r.image:
        return r.image
    return self.image0
    #r = self.trailers
    #if r and r.getchu:
    #  gid = r.getchu
    #  return "http://www.getchu.com/brandnew/%s/c%spackage.jpg" % (gid, gid) # example: www.getchu.com/brandnew/756396/c756396package.jpg
    #r = self.getchu
    #if r and r.image:
    #  return r.image
    #for r in itertools.chain(
    #    self._iterAmazonDmmDigests(), self._iterAmazonDmmReferences()):
    #for r in self._iterAmazonDmm():
    #  if r.image:
    #    return r.image

  @property
  def imageUrl0(self): # str or None
    ret = self.image0
    if ret:
      if proxy.enabled():
        ret = proxy.get_getchu_url(ret)
        ret = proxy.get_dlsite_url(ret)
      ret = cacheman.cache_image_url(ret)
    else:
      ret = rc.image_url('game-cover').toString()
    return ret

  def imageFitsBackground0(self):
    img = self.image0
    return bool(img) and (
        'getchu.com' in img or
        'melonbooks.co.jp' in img or
        'gyutto.com' in img or
        'dlsite.jp' in img or
        'digiket.net' in img or
        'freem.ne.jp' in img or
        'steamstatic.com' in img or
        'images-amazon.com' in img and (self.otome0 or not self.ecchi0))

  @property
  def imageUrl(self): # str or None
    ret = self.image
    if ret:
      if proxy.enabled():
        ret = proxy.get_getchu_url(ret)
        ret = proxy.get_dlsite_url(ret)
      ret = cacheman.cache_image_url(ret)
    return ret

  @property
  def artists0(self): # unicode
    r = self.gameItem
    return r.artists if r else ''
  @property
  def sdartists0(self): # unicode
    r = self.gameItem
    return r.sdartists if r else ''
  @property
  def writers0(self): # unicode
    r = self.gameItem
    return r.writers if r else ''
  @property
  def musicians0(self): # unicode
    r = self.gameItem
    return r.musicians if r else ''

  @memoizedproperty
  def artists(self): # [kw] or None
    for r in self.trailersItem, self.melon, self.digiket, self.getchu, self.gyutto, self.holyseal, self.dmm:
      if r and r.artists:
        return r.artists

  @memoizedproperty
  def sdartists(self): # [kw] or None
    for r in self.trailersItem, self.digiket, self.getchu, self.gyutto, self.holyseal: #, self.dmm:
      if r and r.sdartists:
        return r.sdartists

  @memoizedproperty
  def writers(self): # [kw] or None
    for r in self.trailersItem, self.melon, self.digiket, self.getchu, self.gyutto, self.holyseal: #, self.dmm:
      if r and r.writers:
        return r.writers

  @memoizedproperty
  def musicians(self): # [kw] or None
    for r in self.trailersItem, self.digiket, self.getchu, self.gyutto, self.holyseal: #, self.dmm:
      if r and r.musicians:
        return r.musicians

  @memoizedproperty
  def slogan(self): # str or None
    for r in self.scape, self.freem, self.holyseal, self.getchu, self.digiket, self.gyutto:
      if r and r.slogan:
        return wide2thin(r.slogan)

  @property
  def tags0(self): # unicode not None
    g = self.gameItem
    return g.tags if g else ''

  @memoizedproperty
  def tags(self): # unicode not None
    dmm = self.dmm
    ret = ','.join(dmm.tags) if dmm else '' # unicode
    for r in self.getchu, self.gyutto, self.digiket, self.dlsite:
      if r and r.tags: # [unicode]
        if not ret:
          ret = ','.join(r.tags) # unicode
        else:
          for it in r.tags: # [unicode]
            if it not in ret:
              ret = ','.join((it, ret))
    g = self.gameItem
    if g and g.tags: # unicode
      if not ret:
        ret = g.tags # unicode
      else:
        #ret = ret.split(',')
        for it in g.tags.split(','):
          if it not in ret:
            ret = ','.join((it, ret))
    t = u"イチオシ作品," # move it to the beginning
    if t in ret:
      ret = t + ret.replace(t, '')
    ret = ret.replace(u',アドベンチャー', '')
    return ret

  def iterSampleImageReferences(self):
    """
    @yield  Reference
    """
    for r in self.getchu, self.melon, self.dlsite, self.amazon, self.dmm, self.digiket, self.freem, self.steam: #, self.tokuten:
      if r and r.hasSampleImages():
        yield r

  def hasSampleImages(self): # bool
    for r in self.iterSampleImageReferences():
      return True
    return False
    #r = self.getchu
    #if r and r.hasBannerImages():
    #  return True
    #return False

  #def iterSampleImageUrls(self): # yield str
  #  r = self.digiket # show digiket first as it has summary
  #  if r and r.hasSampleImages():
  #    for it in r.iterSampleImageUrls():
  #      yield it

  #  showdmm = True
  #  showgyutto = True
  #  for r in self.getchu, : #self.gyutto: FIXME: gyutto image would crash webkit
  #    if r and r.hasSampleImages():
  #      showgyutto = showdmm = False
  #      for it in r.iterSampleImageUrls():
  #        yield it
  #  if showgyutto:
  #    for r in self.gyutto, : #self.gyutto: FIXME: gyutto image would crash webkit
  #      if r and r.hasSampleImages():
  #        showdmm = False
  #        for it in r.iterSampleImageUrls():
  #          yield it
  #  if showdmm: # do not display DMM CG if getchu exists
  #    r = self.dmm
  #    if r and r.hasSampleImages():
  #      for it in r.iterSampleImageUrls():
  #        yield it
  #  r = self.dlsite
  #  if r and r.hasSampleImages():
  #    for it in r.iterSampleImageUrls():
  #      yield it
  #  r = self.amazon # always display amazon CG if exists
  #  if r and r.hasSampleImages():
  #    for it in r.iterSampleImageUrls():
  #      yield it
  #  r = self.getchu # show getchu banner as sample images
  #  if r and r.hasBannerImages():
  #    for it in r.iterBannerImageUrls():
  #      yield it

  @memoizedproperty
  def visitCount(self):
    try: return sum(it.visitCount for it in self.gameFiles) or 1
    except TypeError: return 1

  @memoizedproperty
  def commentCount(self):
    try: return sum(it.commentCount for it in self.gameFiles)
    except TypeError: return 0

  #@memoizedproperty
  @property
  def topicCount(self):
    try: return self.gameItem.topicCount
    except AttributeError: return 0

  @memoizedproperty
  def subtitleCount(self):
    try: return self.gameItem.subtitleCount
    except AttributeError: return 0

  @memoizedproperty
  def playUserCount(self):
    try: return self.gameItem.playUserCount
    except AttributeError: return 0

  @memoizedproperty
  def timestamp(self):
    try: return self.gameItem.timestamp
    except AttributeError: return 0
    #try: return max(it.timestamp for it in self.referenceDigests)
    #except TypeError: return 0

  #@memoizedproperty
  #def videoCount(self):
  #  """
  #  @return  int
  #  """
  #  r = self.trailers
  #  return r.videoCount if r else 0

  def hasVideos(self):
    """
    @return  bool
    """
    for r in self.getchu, self.freem:
      if r and r.videos:
        return True
    r = self.trailers
    if r and r.videoCount:
      return True
    return False

  def iterVideos(self):
    """
    @yield  {kw}
    """
    vids = set()
    r = self.trailers
    if r and r.videoCount:
      item = self.trailersItem
      if item:
        for it in item.videos:
          vid = it['vid']
          vids.add(vid)
          #it['img'] = proxy.make_ytimg_url(vid)
          yield it
    for r in self.getchu, self.freem:
      if r and r.videos:
        for index,vid in enumerate(it for it in r.videos if it not in vids):
          yield {
            'vid': vid,
            'title': u"動画 #%s" % (index+1) if index else u"動画",
            #'img': proxy.make_ytimg_url(vid),
            #'date': '', # unknown
          }

  def iterVideoIds(self):
    """
    @yield  {kw}
    """
    vids = set()
    r = self.trailers
    if r and r.videoCount:
      item = self.trailersItem
      if item:
        for it in item.videos:
          vid = it['vid']
          vids.add(vid)
          yield vid
    for r in self.getchu, self.freem:
      if r and r.videos:
        for vid in r.videos:
          if vid not in vids:
            yield vid

class GameItem(object):
  __slots__ = (
    'id',
    'title',
    'romajiTitle',
    'brand',
    'series',
    'image',
    'banner',
    'wiki',
    'fileSize',
    'timestamp',
    'date',
    'otome',
    'ecchi',
    'okazu',
    'scapeMedian',
    'scapeCount',
    'topicCount',
    'annotCount',
    'subtitleCount',
    'playUserCount',
    'tags',
    'artists',
    'sdartists',
    'writers',
    'musicians',

    'overallScoreSum',
    'overallScoreCount',
    'ecchiScoreSum',
    'ecchiScoreCount',
    #'easyScoreSum',
    #'easyScoreCount',
  )

  def __init__(self, id=0,
      title="", romajiTitle="", brand="", series="", image="", banner="", wiki="",
      timestamp=0, fileSize=0, date=None, artists='', sdartists='', writers='', musicians='',
      otome=False, ecchi=True, okazu=False, scapeMedian=0, scapeCount=0, tags='',
      topicCount=0, annotCount=0, subtitleCount=0, playUserCount=0,
      overallScoreSum=0, overallScoreCount=0, ecchiScoreSum=0, ecchiScoreCount=0, #easyScoreSum=0, easyScoreCount=0,
    ):
    self.id = id # int
    self.title = title # unicode
    self.romajiTitle = romajiTitle # unicode
    self.brand = brand # unicode
    self.series = series # unicode
    self.image = image # str
    self.banner = banner # str
    self.wiki = wiki # unicode
    self.fileSize = fileSize # int
    self.timestamp = timestamp # int
    self.date = date # datetime or None
    self.otome = otome # bool
    self.ecchi = ecchi # bool
    self.okazu = okazu # int
    self.scapeMedian = scapeMedian # int
    self.scapeCount = scapeCount # int
    self.topicCount = topicCount # int
    self.annotCount = annotCount # int
    self.subtitleCount = subtitleCount # int
    self.playUserCount = playUserCount # int
    self.tags = tags # unicode not None
    self.artists = artists # unicode not None
    self.sdartists = sdartists # unicode not None
    self.writers = writers # unicode not None
    self.musicians = musicians # unicode not None

    self.overallScoreSum = overallScoreSum
    self.overallScoreCount = overallScoreCount
    self.ecchiScoreSum = ecchiScoreSum
    self.ecchiScoreCount = ecchiScoreCount
    #self.easyScoreSum = easyScoreSum
    #self.easyScoreCount = easyScoreCount

class Game(object):
  NAME_TYPES = 'window', 'file', 'link', 'folder', 'brand'
  LOADERS = 'none', 'apploc', 'ntlea', 'lsc', 'le'

  __slots__ = (
    'id',
    'md5',
    'itemId',
    'encoding',
    'language',
    'launchLanguage',
    'hook',
    'deletedHook',
    'hookDisabled',
    'threadKept',
    'threadName',
    'threadSignature',
    'keepsSpace',
    'removesRepeat',
    'ignoresRepeat',
    'timeZoneEnabled',
    'gameAgentDisabled',
    'nameThreadName',
    'nameThreadSignature',
    'nameThreadDisabled',
    'otherThreads',
    'userDefinedName',
    'names',
    'path',
    'launchPath',
    'visitTime',
    'visitCount',
    'commentCount',
    'commentsUpdateTime',
    'refsUpdateTime',
    'voiceDefaultEnabled',
    'loader',
  )

  @classmethod
  def createEmptyGame(cls, path="", md5=""):
    return cls(
        threadSignature=defs.NULL_THREAD_SIGNATURE,
        threadName=defs.NULL_THREAD_NAME,
        encoding=defs.NULL_THREAD_ENCODING,
        md5=md5,
        fileNames=[os.path.basename(path)] if path else [])

  def __init__(self, id=0, md5="", itemId=0,
      encoding="", hook="", deletedHook="", threadName="", threadSignature=0,
      removesRepeat=None, ignoresRepeat=None, keepsSpace=None,
      nameThreadName="", nameThreadSignature=0, nameThreadDisabled=None,
      windowNames=[], fileNames=[], linkNames=[], folderNames=[], brandNames=[],
      path="", launchPath="", otherThreads=None,
      loader="", hookDisabled=None, threadKept=None, timeZoneEnabled=None, gameAgentDisabled=False,
      language='', launchLanguage='',
      userDefinedName="", visitTime=0, visitCount=0, commentCount=0,
      **ignored):
    # Static
    self.id = id                # long
    self.md5 = md5              # str
    self.itemId = itemId        # long
    self.encoding = encoding    # str
    self.language = language    # str
    self.launchLanguage = launchLanguage # str
    self.hook = hook            # str
    self.deletedHook = deletedHook    # str
    self.hookDisabled = hookDisabled  # bool or None
    self.threadKept = threadKept  # bool or None
    self.threadName = threadName            # str
    self.threadSignature = threadSignature  # long
    self.keepsSpace = keepsSpace  # bool or None
    self.removesRepeat = removesRepeat  # bool or None
    self.ignoresRepeat = ignoresRepeat  # bool or None
    self.timeZoneEnabled = timeZoneEnabled # bool or None
    self.gameAgentDisabled = gameAgentDisabled # bool

    self.nameThreadName = nameThreadName    # str
    self.nameThreadSignature = nameThreadSignature  # long
    self.nameThreadDisabled  = nameThreadDisabled # bool or None

    # {long signature: str} not None
    self.otherThreads = otherThreads if otherThreads is not None else {}

    self.userDefinedName = userDefinedName

    self.names = { # {str type : [unicode name] or None}
      'window': windowNames, # [unicode] not None
      'file': fileNames,     # [unicode] not None
      'link': linkNames,     # [unicode] not None
      'folder': folderNames, # [unicode] not None
      'brand': brandNames,   # [unicode] not None
    }

    # Local
    self.path = path # unicode
    self.launchPath = launchPath # unicode

    self.visitTime = visitTime   # long
    self.visitCount = visitCount # int
    self.commentCount = commentCount # int

    self.commentsUpdateTime = 0  # long
    self.refsUpdateTime = 0  # long

    self.voiceDefaultEnabled = False

    self.loader = loader # "apploc" or "ntlea" or "le"

  #@property
  #def brand(self):
  #  try: return self.names['brand'][0]
  #  except: return ""

  @property
  def name(self):
    ret = self.userDefinedName
    if ret:
      return ret
    ret = manager().queryItemName(self.itemId)
    if ret:
      return ret
    for k in 'link', 'window', 'file', 'folder':
      if self.names.get(k):
        return self.names[k][0]
    return tr_("Unknown")

  def icon(self):
    """
    @return  QIcon or None
    """
    return rc.file_icon(self.path) if self.path else None

  #@property
  def gameType(self): # str not None, '' or 'otome' or 'junai' or 'nuki'
    if self.itemId and self.itemId >= defs.MIN_NORMAL_GAME_ITEM_ID:
      g = manager().queryGameItem(self.itemId)
      if g:
        return 'otome' if g.otome else 'nuki' if g.okazu else 'junai'
    return ''

class GameFile(object):
  __slots__ = (
    'id',
    'md5',
    'name',
    'itemId',
    'visitCount',
    'commentCount',
  )

  def __init__(self, id=0, itemId=0, visitCount=0, commentCount=0, md5="", name=""):
    self.id = id        # long
    self.md5 = md5      # str
    self.name = name    # unicode
    self.itemId = itemId # long
    self.visitCount = visitCount # int
    self.commentCount = commentCount # int

class _GameObject(object):
  __slots__ = [
    '_memoized', # @memoized

    'id',
    'md5',
    'name',
    'path',
    'launchPath',
    'language',
  ]

  @memoizedproperty
  def info(self):
    return manager().queryGameInfo(id=self.id) if self.id else None

  @memoizedproperty
  def brand(self): # unicode or None
    try: return self.info.brand0
    except AttributeError: pass

  @memoizedproperty
  def date(self): # long not None
    try: return self.info.date0
    except AttributeError: return 0

  @memoizedproperty
  def gameType(self): # unicode or None
    info = self.info
    if info and info.itemId >= defs.MIN_NORMAL_GAME_ITEM_ID: # skip emulator which is less than 100
      return 'otome' if info.otome0 else 'junai' if not info.okazu0 else 'nuki'
    return ''

  @memoizedproperty
  def fileSizeString(self): # str
    info = self.info
    return info.fileSizeString0 if info and info.fileSize0 else ''

  @memoizedproperty
  def tags(self): # unicode or None
    t = self.gameType
    if t:
      return (
          u"乙女" if t == 'otome' else
          u"抜き" if t == 'nuki' else
          u"純愛" if t == 'junai' else
          None)
      #if info.doujin:  # no offline version ><
      #  return u"同人"
      #if l:
      #  return ','.join(l)
      #l = []
      #if info.otome0:
      #  l.append(u"乙女")
      #else:
      #  l.append(u"抜き" if info.okazu0 else u"純愛")
      ##if info.doujin:
      ##  l.append(u"同人")
      #if l:
      #  return ','.join(l)

  def getGameItemProperty(self, key): # str ->
    try: return getattr(self.info.gameItem, key)
    except AttributeError: pass

class GameObject(QObject):
  def __init__(self, parent=None, game=None):
    """
    @param  game  GameObject or Game or GameFile
    """
    super(GameObject, self).__init__(parent)
    d = self.__d = _GameObject()
    d.id = 0 # long
    d.md5 = "" # str
    d.name = "" # unicode
    d.path = "" # unicode
    d.launchPath = "" # unicode
    d.language = "ja" # str

    if game:
      self.initWithGame(game)

  def initWithGame(self, game):
    """
    @param  game  GameObject or Game or GameFile
    """
    if game:
      d = self.__d
      d.id = game.id
      d.md5 = game.md5
      d.name = game.name
      try: # GameFile
        d.language = game.language
        d.path = game.path
        d.launchPath = game.launchPath
      except AttributeError: pass

  #qml = Property(unicode,
  #  lambda self:
  #    rc.jinja_template('qml/opengame').render({
  #      'path': QDir.fromNativeSeparators(self.path) if self.path else "",
  #      'launchPath': QDir.fromNativeSeparators(self.launchPath) if self.launchPath else "",
  #    }),
  #  )

  linkChanged = Signal(unicode)
  link = Property(unicode,
    lambda self: create_game_link(self.__d.path, self.__d.launchPath),
    notify=linkChanged)

  idChanged = Signal(int)
  id = Property(int,
    lambda self: self.__d.id,
    notify=idChanged)

  itemIdChanged = Signal(int)
  itemId = Property(int,
    lambda self: manager().queryGameItemId(id=self.__d.id),
    notify=itemIdChanged)

  md5Changed = Signal(str)
  md5 = Property(str,
    lambda self: self.__d.md5,
    notify=md5Changed)

  nameChanged = Signal(unicode)
  name = Property(unicode,
    lambda self: self.__d.name,
    notify=nameChanged)

  languageChanged = Signal(unicode)
  language = Property(unicode,
    lambda self: self.__d.language,
    notify=languageChanged)

  pathChanged = Signal(unicode)
  path = Property(unicode,
    lambda self: self.__d.path,
    notify=pathChanged)

  launchPathChanged = Signal(unicode)
  launchPath = Property(unicode,
    lambda self: self.__d.launchPath,
    notify=launchPathChanged)

  knownChanged = Signal(bool)
  known = Property(bool,
    lambda self: bool(self.__d.info),
    notify=knownChanged)

  brandChanged = Signal(unicode)
  brand = Property(unicode,
    lambda self: self.__d.brand,
    notify=brandChanged)

  tagsChanged = Signal(unicode)
  tags = Property(unicode,
    lambda self: self.__d.tags,
    notify=tagsChanged)

  fileSizeStringChanged = Signal(unicode)
  fileSizeString = Property(unicode,
    lambda self: self.__d.fileSizeString,
    notify=fileSizeStringChanged)

  dateChanged = Signal(long)
  date = Property(long,
    lambda self: self.__d.date,
    notify=dateChanged)

  overallScoreSumChanged = Signal(int)
  overallScoreSum = Property(int,
    lambda self: self.__d.getGameItemProperty('overallScoreSum') or 0,
    notify=overallScoreSumChanged)

  overallScoreCountChanged = Signal(int)
  overallScoreCount = Property(int,
    lambda self: self.__d.getGameItemProperty('overallScoreCount') or 0,
    notify=overallScoreCountChanged)

  ecchiScoreSumChanged = Signal(int)
  ecchiScoreSum = Property(int,
    lambda self: self.__d.getGameItemProperty('ecchiScoreSum') or 0,
    notify=ecchiScoreSumChanged)

  ecchiScoreCountChanged = Signal(int)
  ecchiScoreCount = Property(int,
    lambda self: self.__d.getGameItemProperty('ecchiScoreCount') or 0,
    notify=ecchiScoreCountChanged)

  topicCountChanged = Signal(int)
  topicCount = Property(int,
    lambda self: self.__d.getGameItemProperty('topicCount') or 0,
    notify=topicCountChanged)

  #@Slot(result=QIcon)
  def icon(self):
    """
    @return  QIcon or None
    """
    return (
      rc.file_icon(self.path) if self.path and os.path.exists(self.path) else
      rc.file_icon(self.launchPath) if self.launchPath else
      None)

  @Slot(result=str)
  def image(self):
    id = self.__d.id
    return manager().queryGameBackgroundImageUrl(id=id) if id else ''

class _Character:

  __slots__ = (
    'name',
    'gender',
    'ttsEngine',
    'ttsEnabled',
    'timestamp',
  )

  @staticmethod
  def synthesize(name, type):
    """
    @param  name  str
    @param  type  type
    @param  sync  bool  when true, save the changes on line
    return Property, Signal
    """
    signame = name + 'Changed'
    def getter(self):
      return getattr(self.__d, name)
    def setter(self, value):
      if getattr(self.__d, name) != value:
        setattr(self.__d, name, value)
        getattr(self, signame).emit(value)
        manager().touchCharacters()
    sig = Signal(type)
    return Property(type, getter, setter, notify=sig), sig

class Character(QObject):
  __D = _Character
  def __init__(self, parent=None,
      name='', gender='', ttsEngine='', ttsEnabled=False, timestamp=0,
      **ignored):
    super(Character, self).__init__(parent)
    d = self.__d = _Character()
    d.name = name
    d.gender = gender # 'm' or 'f'
    d.ttsEngine = ttsEngine # str  '' for default engine
    d.ttsEnabled = ttsEnabled # bool
    d.timestamp = timestamp or skdatetime.current_unixtime() # long

  @property
  def d(self): return self.__d

  name, nameChanged = __D.synthesize('name', unicode)
  gender, genderChanged = __D.synthesize('gender', unicode)
  ttsEngine, ttsEngineChanged = __D.synthesize('ttsEngine', unicode)
  ttsEnabled, ttsEnabledChanged = __D.synthesize('ttsEnabled', bool)
  timestamp, timestampChanged = __D.synthesize('timestamp', int)

class Subtitle(object):
  __slots__ = (
    #'__weakref__',

    'textId',
    'text',
    'textName',
    'textTime',
    'textLang',
    'sub',
    'subName',
    'subTime',
    'subLang',
    'userId',

    '_userName',
    '_q',
  )
  def __init__(self,
      textId=0, text='', textName='',
      textTime=0, subTime=0,
      sub='', subName='',
      userId=0, subLang='', textLang=''):
    self.textId = textId # long
    self.text = text # unicode
    self.textName = textName # unicode
    self.textLang = textLang # str
    self.textTime = textTime
    self.sub = sub # unicode
    self.subName = subName # unicode
    self.userId = userId # long
    self.subLang = subLang # str
    self.subTime = subTime

    self._userName = None # str  cached
    self._q = None # Qt

  def equalText(self, text, exact=False):
    """
    @param  text  unicode
    @param* exact  bool
    @return  bool
    """
    if not exact or not self.textName:
      diffcount = len(text) - len(self.text)
      if not diffcount:
        return text == self.text
      elif diffcount == 2:
        if text.startswith(u"「") and text.endswith(u"」"):
          return text[1:-1] == self.text
      elif not exact and diffcount == -2:
        if self.text.startswith(u"「") and self.text.endswith(u"」"):
          return self.text[1:-1] == text
    if self.textName:
      if not exact and text.startswith(u"「") and text.endswith(u"」"):
        text = text[1:-1]
      diffcount = len(text) - len(self.textName) - len(self.text)
      if not diffcount:
        return text.startswith(self.textName) and text.endswith(self.text)
        #return self.textName + self.text == text
      elif diffcount == 2:
        if text.startswith(u"【"):
          return text == (u"【%s】%s" % (self.textName, text))
        if text.startswith(u"「"):
          return text == (u"%s「%s」" % (self.textName, text))
      elif diffcount == 4:
        if text.startswith(u"【") and text.endswith(u"」"):
          return text == (u"【%s】「%s」" % (self.textName, text))
    return False

  def equalSub(self, text, exact=False): # unicode, bool -> bool
    """
    @param  text  unicode
    @param* exact  bool
    @return  bool
    """
    if not exact or not self.subName:
      diffcount = len(text) - len(self.sub)
      if not diffcount:
        return text == self.sub
      elif diffcount == 2:
        if text.startswith(u"「") and text.endswith(u"」"):
          return text[1:-1] == self.sub
      elif not exact and diffcount == -2:
        if self.sub.startswith(u"「") and self.sub.endswith(u"」"):
          return self.sub[1:-1] == text
      elif not exact and diffcount < 0: # sub is longer
        if self.sub.startswith(u"【") and self.sub.endswith(u"」"):
          if text.startswith(u"「") and text.endswith(u"」"):
            return self.sub.endswith(u"】" + text)
          else:
            return self.sub.endswith(u"】「%s」" % text)
    if self.subName:
      if not exact and text.startswith(u"「") and text.endswith(u"」"):
        text = text[1:-1]
      diffcount = len(text) - len(self.subName) - len(self.sub)
      if not diffcount:
        return text.startswith(self.subName) and text.endswith(self.sub)
        #return self.subName + self.sub == text
      elif diffcount == 2:
        if text.startswith(u"【"):
          return text == (u"【%s】%s" % (self.subName, sub))
        if text.startswith(u"「"):
          return text == (u"%s「%s」" % (self.subName, sub))
      elif diffcount == 4:
        if text.startswith(u"【") and text.endswith(u"」"):
          return text == (u"【%s】「%s」" % (self.subName, sub))
    return False

  @property
  def userName(self):
    if self._userName is None:
      self._userName = manager().queryUserName(self.userId) or ''
    return self._userName

  def getObject(self):
    if not self._q:
      self._q = SubtitleObject(self)
    return SubtitleObject(self)

  def releaseObject(self):
    q = self._q
    self._q = None
    if q and q.parent():
      q.setParent(None)

  def releaseObjectLater(self, interval=30000): # release aftre 30min
    q = self._q
    self._q = None
    if q and q.parent():
      #q.setParent(None)
      skevents.runlater(partial(q.setParent, None), interval)

class SubtitleObject(QObject):
  def __init__(self, d=None, parent=None):
    super(SubtitleObject, self).__init__(parent or manager()) # force having parent or it might crash after copy in QML
    self.d = d
    #self.dref = weakref.ref(d)

  #@property
  #def d(self): return self.dref()

  languageChanged = Signal(unicode)
  language = Property(unicode,
      lambda self: self.d.subLang,
      notify=languageChanged)

  textChanged = Signal(unicode)
  text = Property(unicode,
      lambda self: self.d.sub,
      notify=textChanged)

  userNameChanged = Signal(unicode)
  userName = Property(unicode,
      lambda self: self.d.userName,
      notify=userNameChanged)

  colorChanged = Signal(unicode)
  color = Property(unicode,
      lambda self: manager().queryUserColor(self.d.userId),
      notify=colorChanged)

  createTimeChanged = Signal(int)
  createTime = Property(int,
      lambda self: self.d.textTime,
      notify=createTimeChanged)

  updateTimeChanged = Signal(int)
  updateTime = Property(int,
      lambda self: self.d.subTime,
      notify=updateTimeChanged)

@Q_Q
class _Comment(object):

  __slots__ = (
    'q', 'qref', # Q_Q

    'init',
    'id',
    'gameId',
    '_gameMd5',
    'userId',
    'userHash',
    'type',
    'language',
    'timestamp',
    'updateTimestamp',
    'updateUserId',
    'text',
    'disabled',
    'deleted',
    'locked',
    'hash',
    'context',
    'contextSize',
    'comment',
    'updateComment',
    'likeCount',
    'dislikeCount',

    'selected',

    'dirtyProperties',
  )

  def __init__(self, q,
      id, gameId, gameMd5, userId, userHash, type, language, timestamp, updateTimestamp, updateUserId, text, hash, context, contextSize, comment, updateComment, likeCount, dislikeCount, disabled, deleted, locked):
    self.init = False           # bool
    self.id = id                # long
    self.gameId = gameId        # long
    self._gameMd5 = gameMd5     # str
    self.userId = userId        # int
    self.userHash = userHash    # int
    self.type = type            # 'comment' or 'subtitle'
    self.language = language    # str
    self.timestamp = timestamp  # long
    self.updateTimestamp = updateTimestamp  # long
    self.updateUserId = updateUserId    # int
    self.text = text            # unicode
    self.disabled = disabled    # bool
    self.deleted = deleted      # bool
    self.locked = locked        # bool
    #self.popup = popup          # bool
    self.hash = hash            # long
    self.context = context      # unicode
    self.contextSize = contextSize # int
    self.comment = comment
    self.updateComment = updateComment
    self.likeCount = likeCount
    self.dislikeCount = dislikeCount

    self.selected = False       # bool

    self.dirtyProperties = set() # set([str])

  def addDirtyProperty(self, name):
    if self.id:
      self.dirtyProperties.add(name)
    self.setDirty(True)
    if name == 'deleted':
      manager().removeComment(self.q)

  def setDirty(self, dirty):
    if dirty:
      manager().addDirtyComment(self.q)
    else:
      manager().removeDirtyComment(self.q)

  @property
  def userName(self): return _get_user_name(self.userId)
  @property
  def updateUserName(self): return _get_user_name(self.updateUserId)
  @property
  def protected(self): return _is_protected_data(self)

  @property
  def gameMd5(self):
    if not self._gameMd5 and self.gameId:
      self._gameMd5 = manager().queryGameMd5(self.gameId) or ""
    return self._gameMd5

  @gameMd5.setter
  def gameMd5(self, v): self._gameMd5 = v

  @staticmethod
  def synthesize(name, type, sync=False):
    """
    @param  name  str
    @param  type  type
    @param  sync  bool  when true, save the changes on line
    return Property, Signal
    """
    signame = name + 'Changed'
    def getter(self):
      return getattr(self.__d, name)
    def setter(self, value):
      if getattr(self.__d, name) != value:
        setattr(self.__d, name, value)
        getattr(self, signame).emit(value)
    def sync_setter(self, value):
      if getattr(self.__d, name) != value:
        setattr(self.__d, name, value)
        self.__d.addDirtyProperty(name)
        getattr(self, signame).emit(value)
    sig = Signal(type)
    return Property(type, getter, sync_setter if sync else setter, notify=sig), sig

  TYPES = 'subtitle', 'danmaku', 'comment', 'popup'
  TR_TYPES = tr_('Subtitle'), tr_('Danmaku'), tr_('Comment'), tr_("Pop-up")

class Comment(QObject):
  __D = _Comment

  TYPES = __D.TYPES
  TR_TYPES = __D.TR_TYPES
  TYPE_NAMES = dict(zip(_Comment.TYPES, _Comment.TR_TYPES))

  @classmethod
  def typeName(cls, t):
    """
    @param  t  unicode
    @return  unicode not None
    """
    return cls.TYPE_NAMES.get(t) or ""

  @property
  def d(self): return self.__d

  def __init__(self, init=True, parent=None,
      id=0, gameId=0, gameMd5="", userId=0, userHash=0,
      type="", language="", timestamp=0, text="",
      hash=0, context="", contextSize=0, comment="", updateComment="",
      disabled=False, deleted=False, locked=False,
      updateUserId=0, updateTimestamp=0,
      likeCount=0, dislikeCount=0,
      **ignored):
    self.__d = _Comment(self,
      id, gameId, gameMd5, userId, userHash, type, language, timestamp, updateTimestamp, updateUserId, text, hash, context, contextSize, comment, updateComment, likeCount, dislikeCount, disabled, deleted, locked)
    if init:
      self.init(parent)

  ## Construction ##

  def init(self, parent=None):
    """Invoke super __init__
    @param  parent  QObject
    """
    d = self.__d
    if not d.init:
      d.init = True
      super(Comment, self).__init__(parent)
      self.updateUserIdChanged.connect(lambda:
          self.updateUserNameChanged.emit(self.updateUserName))

  def isInitialized(self): return self.__d.init  # not used

  def clone(self, id=0, userId=0, userHash=None, timestamp=0, disabled=None, deleted=None, updateUserId=None, updateTimestamp=None):
    d = self.__d
    return Comment(parent=self.parent(), init=d.init,
      id=id if id else d.id,
      userId=userId if userId else d.userId,
      userHash=userHash if userHash is not None else userId,
      timestamp=timestamp if timestamp else d.timestamp,
      updateUserId=updateUserId if updateUserId is not None else d.updateUserId,
      updateTimestamp=updateTimestamp if updateTimestamp is not None else d.updateTimestamp,
      disabled=disabled if disabled is not None else d.disabled,
      deleted=deleted if deleted is not None else d.deleted,
      locked=d.locked,
      gameId=d.gameId, gameMd5=d.gameMd5,
      type=d.type, language=d.language, text=d.text,
      hash=d.hash, context=d.context, contextSize=d.contextSize,
      comment=d.comment, updateComment=d.updateComment)

  ## Dirty ##

  def isDirty(self): return bool(self.dirtyProperties)

  def dirtyProperties(self):
    """
    @return  set([str])  modified property names
    """
    return self.__d.dirtyProperties

  def clearDirtyProperties(self): self.__d.setDirty(False)

  ## Properties ##

  id, idChanged = __D.synthesize('id', long)
  #gameMd5, gameMd5Changed = __D.synthesize('gameMd5', str)
  #gameId, gameIdChanged = __D.synthesize('gameId', long)
  userId, userIdChanged = __D.synthesize('userId', int)
  userHash, userHashChanged = __D.synthesize('userHash', int)
  updateUserId, updateUserIdChanged = __D.synthesize('updateUserId', int)
  timestamp, timestampChanged = __D.synthesize('timestamp', int)
  updateTimestamp, updateTimestampChanged = __D.synthesize('updateTimestamp', int)

  type, typeChanged = __D.synthesize('type', str, sync=True)
  language, languageChanged = __D.synthesize('language', str, sync=True)
  text, textChanged = __D.synthesize('text', unicode, sync=True)
  context, contextChanged = __D.synthesize('context', unicode, sync=True)
  contextSize, contextSizeChanged = __D.synthesize('contextSize', int, sync=True)
  comment, commentChanged = __D.synthesize('comment', unicode, sync=True)
  updateComment, updateCommentChanged = __D.synthesize('updateComment', unicode, sync=True)
  likeCount, likeCountChanged = __D.synthesize('likeCount', int) # sync=False
  dislikeCount, dislikeCountChanged = __D.synthesize('dislikeCount', int) # sync=False
  disabled, disabledChanged = __D.synthesize('disabled', bool, sync=True)
  deleted, deletedChanged = __D.synthesize('deleted', bool, sync=True)
  locked, lockedChanged = __D.synthesize('locked', bool, sync=True)
  #popup, popupChanged = __D.synthesize('popup', bool, sync=True)

  selected, selectedChanged = __D.synthesize('selected', bool) # whether the item is selected in term table

  def setDeleted(self, t): self.deleted = t
  def setDisabled(self, t): self.disabled = t
  def setLocked(self, t): self.locked = t

  userNameChanged = Signal(unicode)
  userName = Property(unicode,
      lambda self: self.__d.userName,
      notify=userNameChanged)

  updateUserNameChanged = Signal(unicode)
  updateUserName = Property(unicode,
      lambda self: self.__d.updateUserName,
      notify=updateUserNameChanged)

  colorChanged = Signal(unicode)
  color = Property(unicode,
      lambda self: manager().queryUserColor(self.__d.userId),
      notify=colorChanged)

  proptectedChanged = Signal(bool)
  protected = Property(bool,
      lambda self: self.__d.protected,
      notify=proptectedChanged)

  @property
  def gameMd5(self): return self.__d.gameMd5
  @gameMd5.setter
  def gameMd5(self, val): self.__d.gameMd5 = val

  def setGameId(self, value):
    d = self.__d
    if d.gameId != value:
      d.gameId = value
      d.gameMd5 = ""
      #d.addDirtyProperty('gameId') # modify comment game id is not allowed
      self.gameIdChanged.emit(value)
      dprint("pass")
  gameIdChanged = Signal(int)
  gameId = Property(int,
      lambda self: self.__d.gameId,
      setGameId,
      notify=gameIdChanged)

  def setHash(self, value):
    if self.__d.hash != value:
      self.__d.hash = value
      self.__d.addDirtyProperty('hash')
      #self.hashObjectChanged.emit(value)
  hash = property(
      lambda self: self.__d.hash,
      setHash)

  @property
  def modifiedTimestamp(self):
    """
    @return  long  used for sorting
    """
    return max(self.__d.timestamp, self.__d.updateTimestamp)

  # Not used
  #def hashObject(self):
  #  d = self.__d
  #  if not hasattr(d, 'hashObject'):
  #    d.hashObject = c_longlong(d.hash)
  #  elif d.hashObject.value != d.hash:
  #    d.hashObject.value = d.hash
  #  return d.hashObject
  #hashObjectChanged = Signal(c_longlong)
  #hashObject = Property(c_longlong,
  #    hashObject,
  #    lambda self, obj: self.setHash(obj.value if obj else 0),
  #    notify=hashObjectChanged)

  #@Slot(result=c_longlong)
  #def getHash(self): return self.__d.hash

#class Context:
#  def __init__(self, text="", hash=0, count=0):
#    self.text = text
#    self.hash = hash
#    self.count = count

@Q_Q
class _Term(object):
  __slots__ = (
    'q', 'qref', # Q_Q

    'init',
    'id',
    'gameId',
    '_gameMd5',
    'userId',
    'userHash',
    'type',
    'host',
    'context',
    'language',
    'sourceLanguage',
    'timestamp',
    'updateTimestamp',
    'updateUserId',
    'text',
    'pattern',
    'ruby',
    'priority',
    'role',
    'comment',
    'updateComment',
    'regex',
    'phrase',
    'disabled',
    'deleted',
    'special',
    'private',
    'hentai',
    'icase',
    #'syntax',

    'selected',
    '_errorType',
    #'_errorString',

    'dirtyProperties',

    '_gameItemId',
  )

  # Aliases for share/trscript
  #@property
  #def fr(self): return self.sourceLanguage
  #@property
  #def to(self): return self.language

  def __init__(self, q,
      id, gameId, gameMd5, userId, userHash, type, host, context, language, sourceLanguage, timestamp, updateTimestamp, updateUserId, text, pattern, ruby, priority, role, comment, updateComment, regex, phrase, disabled, deleted, special, private, hentai, icase):
    self.init = False           # bool
    self.id = id                # long
    self.gameId = gameId        # long
    self._gameMd5 = gameMd5     # str
    self.userId = userId        # long
    self.userHash = userHash    # long
    self.type = type            # in TYPES
    self.host = host            # str
    self.context = context      # str
    self.language = language    # str
    self.sourceLanguage = sourceLanguage or 'ja' # str  default to Japanese
    self.timestamp = timestamp  # long
    self.updateTimestamp = updateTimestamp # long
    self.updateUserId = updateUserId   # long
    self.text = text            # unicode
    self.pattern = pattern      # unicode
    self.ruby = ruby            # unicode
    self.priority = priority    # float
    self.role = role            # unicode
    self.comment = comment      # unicode
    self.updateComment = updateComment  # unicode
    self.regex = regex          # bool
    self.phrase = phrase        # bool
    #self.bbcode = bbcode        # bool
    self.disabled = disabled    # bool
    self.deleted = deleted      # bool
    self.special = special      # bool
    self.private = private      # bool
    self.hentai = hentai        # bool
    self.icase = icase          # bool
    #self.syntax = syntax        # bool

    self.selected = False       # bool

    self._errorType = None      # None or int
    #self._errorString = None   # None or unicode

    #self.patternRe = None # compiled re or None
    #self.bbcodeText = None # unicode or None  cached BBCode

    #self.replace = None # multi-replacer function or none
    #self.prepareReplace = None # multi-replacer function or none
    #self.applyReplace = None # multi-replacer function or none

    self.dirtyProperties = set() # set([str])

    self._gameItemId = None # this value is cached

  def addDirtyProperty(self, name):
    if self.id:
      self.dirtyProperties.add(name)
    self.setDirty(True)

    if name not in ('private', 'selected', 'comment', 'updateComment', 'timestamp', 'updateTimestamp', 'updateUserId', 'updateUserHash'):
      termman.manager().invalidateCache() # invalidate term cache when any term is changed

    if self._errorType is not None and name in ('pattern', 'text', 'ruby', 'role', 'type', 'host', 'context', 'language', 'sourceLanguage', 'regex', 'special'):
      self.recheckError()

    #if name in ('pattern', 'private', 'special'): # since the terms are sorted by them
    #  manager().invalidateSortedTerms()
    #else:
    #if d.type == 'term'

    #self.clearCachedProperties()
    #manager().clearTermTitles()

    #if self.type == 'macro': # bug: change type to macro will not have effect at once
    #  manager().clearMacroCache() # might be slow, though

  #def clearCachedProperties(self):
  #  self.replace = self.prepareReplace = self.applyReplace = self.patternRe = None

  def setDirty(self, dirty):
    if dirty:
      manager().addDirtyTerm(self.q)
    else:
      manager().removeDirtyTerm(self.q)

  @property
  def gameMd5(self):
    if not self._gameMd5 and self.gameId:
      self._gameMd5 = manager().queryGameMd5(self.gameId) or ""
    return self._gameMd5
  @gameMd5.setter
  def gameMd5(self, val): self._gameMd5 = val

  @property
  def gameItemId(self): # cached
    if self._gameItemId is None:
      self._gameItemId = (manager().queryGameItemId(self.gameId) or 0) if self.gameId else 0
    return self._gameItemId
  @gameItemId.setter
  def gameItemId(self, val): self._gameItemId = val

  @property
  def userName(self): return _get_user_name(self.userId)
  @property
  def updateUserName(self): return _get_user_name(self.updateUserId)

  @property
  def protected(self): return _is_protected_data(self)

  def recheckError(self):
    v = self._getErrorType()
    if v != self._errorType:
      self._errorType = v
      if self.init:
        self.q.errorTypeChanged.emit(v)
    #v = self._getErrorString()
    #if v != self._errorString:
    #  self._errorString = v
    #  if self.init:
    #    self.q.errorStringChanged.emit(v)

  @property
  def errorType(self):
    if self._errorType is None:
      self._errorType = self._getErrorType()
    return self._errorType

  def getGameSeries(self): return manager().queryItemSeries(self.gameItemId)
  def getGameName(self): return manager().queryGameName(id=self.gameId)

  #@property
  #def errorString(self):
  #  if self._errorString is None:
  #    self._errorString = self._getErrorString()
  #  return self._errorString

  _RE_HIRAGANA = re.compile(u'[あ-ん]')
  _RE_LATIN_WORD = re.compile('^[0-9a-zA-Z ]+$')
  def _getErrorType(self): # -> int not None
    # E_EMPTY_PATTERN
    if not self.pattern:
      return self.E_EMPTY_PATTERN

    # E_EMPTY_TEXT
    if not self.text and self.type == 'proxy':
      return self.E_EMPTY_TEXT

    # E_NEWLINE
    # E_TAB
    for it in self.pattern, self.text, self.ruby, self.role:
      if it:
        if '\n' in it:
          return self.E_NEWLINE
        if '\t' in it:
          return self.E_TAB

    # E_BAD_RUBY
    if self.ruby and self.type not in self.RUBY_TYPES:
      return self.E_BAD_RUBY

    # E_BAD_ROLE
    if self.role and not textutil.validate_term_role(self.role):
      return self.E_BAD_ROLE
    if self.role and self.type not in self.ROLE_TYPES:
      return self.E_BAD_ROLE
    if not self.role and self.type == 'proxy':
      return self.E_BAD_ROLE

    # E_BAD_HOST
    if self.host and self.type not in self.HOST_TYPES:
      return self.E_BAD_HOST

    # E_BAD_CONTEXT
    if self.context and self.type not in self.CONTEXT_TYPES:
      return self.E_BAD_CONTEXT

    # E_USELESS
    if self.sourceLanguage == 'ja' and self.pattern == self.text and not self.ruby and (
        self.type not in ('trans', 'suffix', 'prefix', 'name', 'yomi', 'proxy')):
      return self.E_USELESS

    # E_USELESS
    if self.regex and self.type != 'macro' and not textutil.mightbe_regex(self.pattern):
      return self.E_USELESS_REGEX

    # W_BAD_REGEX
    if (self.regex and (
        not textutil.validate_regex(self.pattern)
        or not textutil.validate_macro(self.text))):
      return self.W_BAD_REGEX

    # W_NOT_INPUT
    if self.language == 'en' and self.type == 'input' and self.text and self._RE_LATIN_WORD.match(self.text):
      return self.W_NOT_INPUT

    # W_NOT_GAME
    if not self.regex and self.type == 'game' and self.text and unichars.isascii(self.text) and not unichars.isascii(self.pattern):
      return self.W_NOT_GAME

    # W_KANA_TEXT
    if self.sourceLanguage == 'ja' and self.type in ('name', 'suffix', 'trans', 'output') and jpchars.anykana(self.text):
      return self.W_KANA_TEXT

    # W_MISSING_TEXT
    if not self.text and len(self.pattern) > 3 and self.type in ('trans', 'name', 'yomi'):
      return self.W_MISSING_TEXT

    # W_SHORT
    if (self.type not in ('suffix', 'prefix', 'ocr', 'macro') and (
        len(self.pattern) == 1 and jpchars.iskana(self.pattern) or
        not self.special and len(self.pattern) == 2 and jpchars.iskana(self.pattern[0]) and jpchars.iskana(self.pattern[1]))):
      return self.W_SHORT

    # W_LONG
    if not self.regex and len(self.pattern) > 25:
      return self.W_LONG

    # W_CHINESE_KANJI
    if self.language.startswith('zh') and self.text:

      # W_CHINESE_SIMPLIFIED
      if self.language == 'zhs' and opencc.containszht(self.text):
        return self.W_CHINESE_SIMPLIFIED

      # W_CHINESE_TRADITIONAL
      if self.language == 'zht' and opencc.containszhs(self.text):
        return self.W_CHINESE_TRADITIONAL

      #if opencc.containsja(self.text): # not checked as it might have Japanese chars such as 桜
      #  return self.W_CHINESE_KANJI

    if self.sourceLanguage.startswith('zh') and self.pattern:

      # W_CHINESE_SIMPLIFIED
      if self.language == 'zhs' and not opencc.containszhs(self.pattern):
        return self.W_CHINESE_SIMPLIFIED

      # W_CHINESE_TRADITIONAL
      if self.language == 'zht' and opencc.containszhs(self.pattern):
        return self.W_CHINESE_TRADITIONAL

    return self.OK

  @staticmethod
  def synthesize(name, type, sync=False):
    """
    @param  name  str
    @param  type  type
    @param  sync  bool  when true, save the changes on line
    return Property, Signal
    """
    signame = name + 'Changed'
    def getter(self):
      return getattr(self.__d, name)
    def setter(self, value):
      if getattr(self.__d, name) != value:
        setattr(self.__d, name, value)
        getattr(self, signame).emit(value)
    def sync_setter(self, value):
      if getattr(self.__d, name) != value:
        setattr(self.__d, name, value)
        self.__d.addDirtyProperty(name)
        getattr(self, signame).emit(value)
    sig = Signal(type)
    return Property(type, getter, sync_setter if sync else setter, notify=sig), sig

  # Errors, the larger (warning) or smaller (error) the worse
  OK = 0
  W_CHINESE_TRADITIONAL = 5 # should not use traditional chinese
  W_CHINESE_SIMPLIFIED = 6  # should not use simplified chinese
  #W_CHINESE_KANJI = 7       # having Japanese characters in kanji
  W_LONG = 11               # being too long
  W_SHORT = 12              # being too short
  W_MISSING_TEXT = 20       # text is empty
  W_KANA_TEXT = 25          # Japanese characters in translation
  W_NOT_GAME = 30           # should not use game type
  W_NOT_INPUT = 31          # should not use input type
  W_BAD_REGEX = 100         # mismatch regex
  E_USELESS = -100          # translation has no effect
  E_USELESS_REGEX = -101    # regex flag is redundant
  E_BAD_HOST = -800         # invalid translation host
  E_BAD_ROLE = -801         # invalid role character
  E_BAD_RUBY = -802         # invalid ruby character
  E_BAD_CONTEXT = -803      # invalid context type
  E_NEWLINE = -900          # having new line characters in pattern or repl
  E_TAB = -901              # having tag characters in pattern or repl
  E_EMPTY_TEXT = -999       # translation text is empty
  E_EMPTY_PATTERN = -1000   # pattern is empty

  TYPES = 'trans', 'input', 'output', 'name', 'yomi', 'suffix', 'prefix', 'game', 'tts', 'ocr', 'macro', 'proxy'
  TR_TYPES = tr_("Translation"), mytr_("Input"), mytr_("Output"), mytr_("Name"), mytr_("Yomi"), mytr_("Suffix"), mytr_("Prefix"), tr_("Game"), mytr_("TTS"), mytr_("OCR"), tr_("Macro"), tr_("Proxy")

  HOSTS = 'bing', 'google', 'babylon', 'lecol', 'infoseek', 'excite', 'nifty', 'systran', 'transru', 'naver', 'baidu', 'youdao', 'jbeijing', 'fastait', 'dreye', 'eztrans', 'transcat', 'lec', 'atlas', 'hanviet', 'vtrans'
  TR_HOSTS = tuple(map(i18n.translator_name, HOSTS))

  CONTEXTS = 'scene', 'name', 'window', 'other'
  TR_CONTEXTS = tuple(map(i18n.game_context_name, CONTEXTS))
  HOST_TYPES = 'input', 'output', 'trans', 'suffix', 'prefix', 'name', 'yomi', 'proxy' # types allow host

  CONTEXT_TYPES = list(HOST_TYPES)
  CONTEXT_TYPES.append('game')
  CONTEXT_TYPES = tuple(CONTEXT_TYPES)

  ROLE_TYPES = 'trans', 'yomi', 'proxy' # types allow role
  RUBY_TYPES = 'trans', 'output', 'name', 'yomi', 'prefix', 'suffix' # types allow ruby

class Term(QObject):
  __D = _Term

  TYPES = __D.TYPES
  TR_TYPES = __D.TR_TYPES
  TYPE_NAMES = dict(zip(_Term.TYPES, _Term.TR_TYPES))

  HOSTS = __D.HOSTS
  TR_HOSTS = __D.TR_HOSTS
  HOST_NAMES = dict(zip(_Term.HOSTS, _Term.TR_HOSTS))
  HOST_TYPES = __D.HOST_TYPES

  CONTEXTS = __D.CONTEXTS
  TR_CONTEXTS = __D.TR_CONTEXTS
  CONTEXT_NAMES = dict(zip(_Term.CONTEXTS, _Term.TR_CONTEXTS))
  CONTEXT_TYPES = __D.CONTEXT_TYPES

  ROLE_TYPES = __D.ROLE_TYPES
  RUBY_TYPES = __D.RUBY_TYPES

  @classmethod
  def typeName(cls, t):
    """
    @param  t  unicode
    @return  unicode not None
    """
    return cls.TYPE_NAMES.get(t) or ""

  #@staticmethod
  #def typeAllowsHost(t): return t in self.HOST_TYPES

  #@classmethod
  #def hostName(cls, t):
  #  """
  #  @param  t  unicode
  #  @return  unicode not None
  #  """
  #  return cls.HOST_NAMES.get(t) or ""

  @property
  def d(self): return self.__d

  # FIXME: Term is not deleted when QObject is initialized
  #def __del__(self):  dprint("Term deleted")

  def __init__(self, init=True, parent=None,
      id=0, gameId=0, gameMd5="", userId=0, userHash=0,
      type="", host="", context="", language="", sourceLanguage="", timestamp=0, text="",
      pattern="", ruby="", priority=0.0, role="", comment="", updateComment="",
      updateUserId=0, updateTimestamp=0,
      regex=False, phrase=False,
      disabled=False, deleted=False, special=False, private=False, hentai=False, icase=False, #syntax=False,
      **ignored):
    self.__d = _Term(self,
      id, gameId, gameMd5, userId, userHash, type, host, context, language, sourceLanguage, timestamp, updateTimestamp, updateUserId, text, pattern, ruby, priority, role, comment, updateComment, regex, phrase, disabled, deleted, special, private, hentai, icase)
    if init:
      self.init(parent)

  ## Construction ##

  def init(self, parent=None):
    """Invoke super __init__
    @param  parent  QObject
    """
    d = self.__d
    if not d.init:
      d.init = True
      super(Term, self).__init__(parent)
      self.updateUserIdChanged.connect(lambda:
          self.updateUserNameChanged.emit(self.updateUserName))

  def isInitialized(self): return self.__d.init # -> bool

  def clone(self, id=0, userId=0, userHash=None, timestamp=0, disabled=None, deleted=None, updateUserId=None, updateTimestamp=None):
    d = self.__d
    return Term(parent=self.parent(), init=d.init,
      id=id if id else d.id,
      userId=userId if userId else d.userId,
      userHash=userHash if userHash is not None else userId,
      timestamp=timestamp if timestamp else d.timestamp,
      updateUserId=updateUserId if updateUserId is not None else d.updateUserId,
      updateTimestamp=updateTimestamp if updateTimestamp is not None else d.updateTimestamp,
      disabled=disabled if disabled is not None else d.disabled,
      deleted=deleted if deleted is not None else d.deleted,
      special=d.special,
      private=d.private,
      hentai=d.hentai,
      icase=d.icase,
      #syntax=d.syntax,
      regex=d.regex,
      phrase=d.phrase,
      gameId=d.gameId, gameMd5=d.gameMd5,
      comment=d.comment, updateComment=d.updateComment,
      type=d.type, host=d.host, context=d.context, language=d.language, sourceLanguage=d.sourceLanguage, text=d.text, pattern=d.pattern, ruby=d.ruby, priority=d.priority, role=d.role)

  ## Dirty ##

  def isDirty(self): return bool(self.dirtyProperties)

  def dirtyProperties(self):
    """
    @return  set([str])  modified property names
    """
    return self.__d.dirtyProperties

  def clearDirtyProperties(self): self.__d.setDirty(False)

  # Cache

  #def clearCache(self): self.__d.clearCachedProperties()

  ## Properties ##

  id, idChanged = __D.synthesize('id', long)
  #gameId, gameIdChanged = __D.synthesize('gameId', long)
  #gameMd5, gameMd5Changed = __D.synthesize('gameMd5', str)
  userId, userIdChanged = __D.synthesize('userId', int)
  userHash, userHashChanged = __D.synthesize('userHash', int)
  updateUserId, updateUserIdChanged = __D.synthesize('updateUserId', int)
  timestamp, timestampChanged = __D.synthesize('timestamp', int)
  updateTimestamp, updateTimestampChanged = __D.synthesize('updateTimestamp', int)

  type, typeChanged = __D.synthesize('type', str, sync=True)
  host, hostChanged = __D.synthesize('host', str, sync=True)
  context, contextChanged = __D.synthesize('context', str, sync=True)
  language, languageChanged = __D.synthesize('language', str, sync=True)
  sourceLanguage, sourceLanguageChanged = __D.synthesize('sourceLanguage', str, sync=True)
  role, roleChanged = __D.synthesize('role', unicode, sync=True)
  pattern, patternChanged = __D.synthesize('pattern', unicode, sync=True)
  text, textChanged = __D.synthesize('text', unicode, sync=True)
  ruby, rubyChanged = __D.synthesize('ruby', unicode, sync=True)
  priority, priorityChanged = __D.synthesize('priority', float, sync=True)
  comment, commentChanged = __D.synthesize('comment', unicode, sync=True)
  updateComment, updateCommentChanged = __D.synthesize('updateComment', unicode, sync=True)
  disabled, disabledChanged = __D.synthesize('disabled', bool, sync=True)
  deleted, deletedChanged = __D.synthesize('deleted', bool, sync=True)
  special, specialChanged = __D.synthesize('special', bool, sync=True)
  private, privateChanged = __D.synthesize('private', bool, sync=True)
  regex, regexChanged = __D.synthesize('regex', bool, sync=True)
  phrase, phraseChanged = __D.synthesize('phrase', bool, sync=True)
  hentai, hentaiChanged = __D.synthesize('hentai', bool, sync=True)
  icase, icaseChanged = __D.synthesize('icase', bool, sync=True)
  #syntax, syntaxChanged = __D.synthesize('syntax', bool, sync=True)

  selected, selectedChanged = __D.synthesize('selected', bool) # whether the item is selected in term table

  private_Changed = privateChanged
  private_ = private # needed for javascript as private is a keyword

  #def setBBCode(self, value):
  #  if self.__d.bbcode != value:
  #    self.__d.bbcode = value
  #    self.__d.bbcodeText = None
  #    self.__d.addDirtyProperty('bbcode')
  #    self.bbcodeChanged.emit(value)
  #    dprint("pass")
  #def isBBCode(self): return self.__d.bbcode
  #bbcodeChanged = Signal(bool)
  #bbcode = Property(bool, isBBCode, setBBCode, notify=bbcodeChanged)

  userNameChanged = Signal(unicode)
  userName = Property(unicode,
      lambda self: self.__d.userName,
      notify=userNameChanged)

  updateUserNameChanged = Signal(unicode)
  updateUserName = Property(unicode,
      lambda self: self.__d.updateUserName,
      notify=updateUserNameChanged)

  proptectedChanged = Signal(bool)
  protected = Property(bool,
      lambda self: self.__d.protected,
      notify=proptectedChanged)

  errorTypeChanged = Signal(int)
  errorType = Property(int,
      lambda self: self.__d.errorType,
      notify=errorTypeChanged)

  @property
  def gameMd5(self): return self.__d.gameMd5
  @gameMd5.setter
  def gameMd5(self, val): self.__d.gameMd5 = val

  @property
  def gameItemId(self): return self.__d.gameItemId

  @property
  def gameSeries(self): return self.__d.getGameSeries()

  @property
  def gameName(self): return self.__d.getGameName()

  def setGameId(self, value):
    d = self.__d
    if d.gameId != value:
      d.gameId = value
      d.gameMd5 = ""
      d.gameItemId = None
      d.addDirtyProperty('gameId')
      self.gameIdChanged.emit(value)
      dprint("pass")
  gameIdChanged = Signal(int)
  gameId = Property(int,
      lambda self: self.__d.gameId,
      setGameId,
      notify=gameIdChanged)

  @property
  def modifiedTimestamp(self):
    """
    @return  long  used for sorting
    """
    return max(self.__d.timestamp, self.__d.updateTimestamp)

  #@property
  #def bbcodeText(self):
  #  """
  #  @return  unicode
  #  """
  #  d = self.__d
  #  if d.bbcodeText is None:
  #    d.bbcodeText = bbcode.parse(d.text) if d.text else ""
  #  return d.bbcodeText

  #def setText(self, value):
  #  d = self.__d
  #  if d.text != value:
  #    d.text = value
  #    d.replace = d.prepareReplace = d.applyReplace = None
  #    d.addDirtyProperty('text')
  #    self.textChanged.emit(value)
  #    dprint("pass")
  #textChanged = Signal(unicode)
  #text = Property(unicode,
  #    lambda self: self.__d.text,
  #    setText,
  #    notify=textChanged)

  #def setRegex(self, value):
  #  d = self.__d
  #  if d.regex != value:
  #    d.regex = value
  #    d.patternRe = None
  #    d.addDirtyProperty('regex')
  #    self.regexChanged.emit(value)
  #    dprint("pass")
  #def isRegex(self): return self.__d.regex
  #regexChanged = Signal(bool)
  #regex = Property(bool, isRegex, setRegex, notify=regexChanged)

  #def setIgnoresCase(self, value):
  #  d = self.__d
  #  if d.ignoresCase != value:
  #    d.ignoresCase = value
  #    d.patternRe = None
  #    d.addDirtyProperty('ignoresCase')
  #    self.ignoresCaseChanged.emit(value)
  #    dprint("pass")
  #ignoresCaseChanged = Signal(bool)
  #ignoresCase = Property(bool,
  #    lambda self: self.__d.ignoresCase,
  #    setIgnoresCase,
  #    notify=ignoresCaseChanged)

  #@property
  #def patternRe(self):
  #  """
  #  @throw  re exception
  #  @return  re or None
  #  """
  #  d = self.__d
  #  if not d.patternRe and d.pattern:
  #    pattern = d.pattern
  #    if defs.TERM_MACRO_BEGIN in pattern:
  #      pattern = termman.manager().applyMacroTerms(pattern)
  #    if pattern:
  #      d.patternRe = (
  #        re.compile(pattern, re.DOTALL) if d.regex else
  #        re.compile(re.escape(pattern))
  #      )
  #  return d.patternRe

  #def patternNeedsRe(self):
  #  """
  #  @return  bool
  #  """
  #  return self.__d.regex #or self.__d.type == 'name'

  #def needsReplace(self):
  #  """
  #  @return  bool
  #  """
  #  return self.__d.type == 'name' #and bool(manager().termTitles())

  #def needsEscape(self):
  #  """
  #  @return  bool
  #  """
  #  return config.is_kanji_language(self.__d.language)

  #@property
  #def replace(self):
  #  """
  #  @return  multireplacer
  #  """
  #  d = self.__d
  #  if not d.replace and d.pattern:
  #    pattern = d.pattern
  #    if d.regex and defs.TERM_MACRO_BEGIN in pattern:
  #      pattern = termman.manager().applyMacroTerms(pattern)
  #    if pattern:
  #      titles = manager().termTitles()
  #      table = {k : d.text + v + ' ' for k,v in titles.iteritems()} # append space
  #      d.replace = skstr.multireplacer(table,
  #          prefix=pattern,
  #          escape=not d.regex)
  #  return d.replace

  #@replace.setter
  #def replace(self, v): self.__d.replace = v

  #@property
  #def prepareReplace(self):
  #  """
  #  @return  multireplacer
  #  """
  #  d = self.__d
  #  if not d.prepareReplace and d.pattern:
  #    pattern = d.pattern
  #    if d.regex and defs.TERM_MACRO_BEGIN in pattern:
  #      pattern = termman.manager().applyMacroTerms(pattern)
  #    if pattern:
  #      titles = manager().termTitles()
  #      #l = sorted(titles.iterkeys(), key=len) # already sorted
  #      esc = defs.NAME_ESCAPE + ' '
  #      h = self.priority or d.id or id(self)
  #      table = {k : esc%(h,i) for i,k in enumerate(titles)}
  #      d.prepareReplace = skstr.multireplacer(table,
  #          prefix=pattern,
  #          escape=not d.regex)
  #  return d.prepareReplace

  #@prepareReplace.setter
  #def prepareReplace(self, v): self.__d.prepareReplace = v

  #def convertsChinese(self):
  #  return manager().user().language == 'zht' and self.__d.language == 'zhs'

  #@property
  #def applyReplace(self):
  #  """
  #  @return  multireplacer
  #  """
  #  d = self.__d
  #  if not d.applyReplace and d.pattern:
  #    mark = termman.manager().markEscapeText
  #    titles = manager().termTitles()
  #    #l = sorted(titles.iterkeys(), key=len) already sorted
  #    esc = defs.NAME_ESCAPE
  #    #esc = defs.NAME_ESCAPE.replace('.', r'\.') # do not need
  #    h = self.priority or d.id or id(self)
  #    if self.convertsChinese():
  #      table = {esc%(h,i) : mark(zhs2zht(d.text) + titles[k]) for i,k in enumerate(titles)}
  #    else:
  #      table = {esc%(h,i) : mark(d.text + titles[k]) for i,k in enumerate(titles)}
  #    d.applyReplace = skstr.multireplacer(table) #escape=False
  #  return d.applyReplace

  #@applyReplace.setter
  #def applyReplace(self, v): self.__d.applyReplace = v

  #def setPattern(self, value):
  #  d = self.__d
  #  if d.pattern != value:
  #    d.pattern = value
  #    d.patternRe = None
  #    d.replace = d.prepareReplace = d.applyReplace = None
  #    d.addDirtyProperty('pattern')
  #    self.patternChanged.emit(value)
  #    dprint("pass")
  #patternChanged = Signal(unicode)
  #pattern = Property(unicode,
  #    lambda self: self.__d.pattern,
  #    setPattern,
  #    notify=patternChanged)

## Name ##

#class NameItem(object):
#
#  def __init__(self, id=0, text="", yomi=""):
#    self.id = id # long
#    self.text = text # unicode
#    self.yomi = yomi # unicode
#
#  #@staticmethod
#  #def needsEscape():
#  #  return not config.is_kanji_language(manager().user().language)
#
#  #@staticmethod
#  #def needsRomaji():
#  #  return not config.is_kanji_language(manager().user().language)
#
#  @memoizedproperty
#  def translation(self):
#    """
#    @return  unicode
#    """
#    lang = manager().user().language
#    if config.is_kanji_language(lang):
#      return self.text
#    if lang == 'ja':
#      return ''
#    yomi = self.yomi or self.text
#    if not textutil.match_kata_hira_punc(yomi):
#      return ''
#    if lang == 'ko': return cconv.kana2ko(yomi)
#    if lang == 'th': return cconv.kana2th(yomi)
#    return cconv.kana2romaji(yomi).title()
#
#  @memoizedproperty
#  def replace(self):
#    """
#    @return  multireplacer
#    """
#    titles = manager().termTitles()
#    # Append a space at the end
#    table = {k : self.translation + v + ' ' for k,v in titles.iteritems()}
#    return skstr.multireplacer(table, prefix=self.text, escape=True)
#
#  @memoizedproperty
#  def prepareReplace(self):
#    """
#    @return  multireplacer
#    """
#    titles = manager().termTitles()
#    #l = sorted(titles.iterkeys(), key=len) # already sorted
#    esc = defs.CHARA_ESCAPE + ' '
#    h = self.id or id(d)
#    table = {k : esc%(h,i) for i,k in enumerate(titles)}
#    return skstr.multireplacer(table, prefix=self.text, escape=True)
#
#  @memoizedproperty
#  def applyReplace(self):
#    """
#    @return  multireplacer
#    """
#    mark = termman.manager().markEscapeText
#    titles = manager().termTitles()
#    #l = sorted(titles.iterkeys(), key=len) # already sorted
#    esc = defs.CHARA_ESCAPE
#    #esc = defs.NAME_ESCAPE.replace('.', r'\.') # do not need
#    h = self.id or id(d)
#    table = {esc%(h,i) : mark(self.translation + titles[k]) for i,k in enumerate(titles)}
#    return skstr.multireplacer(table) #escape=False

## References ##

#class ReferenceDigest(object):
#  def __init__(self, id=0, type="", itemId=0, gameId=0, timestamp=0, date=0, key="", title="", brand="", image=""):
#    self.id = id        # long
#    self.type = type    # str
#    self.itemId = itemId # long
#    self.gameId = gameId # long
#    self.date = date
#    self.timestamp = timestamp
#    self.key = key # str
#    self.title = title    # unicode
#    self.brand = brand    # unicode
#    self.image = image    # unicode
#
#  @memoizedproperty
#  def url(self):
#    """
#    @return  str or None
#    """
#    if self.type == 'trailers':
#      return 'http://erogetrailers.com/soft/%s' % self.key
#    if self.type == 'amazon':
#      return 'http://amazon.co.jp/dp/%s' % self.key
#    #if self.type == 'getchu':
#    #  return 'http://getchu.com/soft.phtml?id=%s' % self.key

  #@memoizedproperty
  #def weight(self):
  #  """
  #  @return  float [0.0, 1.0]
  #  """
  #  return 1 - 1 / (1 + math.log10(1 + self.visitCount + self.commentCount))

@Q_Q
class _Reference(object):
  __slots__ = (
    'q', 'qref',  # Q_Q

    'init',
    'id',
    'itemId',
    'gameId',
    '_gameMd5',
    'userId',
    'userHash',
    'type',
    'timestamp',
    'updateTimestamp',
    'updateUserId',
    'updateUserHash',
    'key',
    'title',
    'brand',
    'url',
    'date',
    'comment',
    'updateComment',
    'disabled',
    'deleted',

    'dirtyProperties',
  )

  def __init__(self, q,
      id, itemId, gameId, gameMd5, userId, userHash, type, timestamp, updateTimestamp, updateUserId, key, title, brand, url, date, comment, updateComment, disabled, deleted):
    self.init = False           # bool
    self.id = id                # long
    self.itemId = itemId        # long
    self.gameId = gameId        # long
    self._gameMd5 = gameMd5     # str
    self.userId = userId        # long
    self.userHash = userHash    # long
    self.type = type            # in TYPES
    self.timestamp = timestamp  # long
    self.updateTimestamp = updateTimestamp  # long
    self.updateUserId = updateUserId        # long
    #self.updateUserHash = updateUserHash    # long
    self.key = key              # str
    self.title = title          # unicode
    self.brand = brand          # unicode
    self.url = url              # str
    self.date = date            # long
    self.comment = comment      # unicode
    self.updateComment = updateComment  # unicode
    self.disabled = disabled    # bool
    self.deleted = deleted      # bool

    self.dirtyProperties = set() # set([str])

  def addDirtyProperty(self, name):
    if self.id:
      self.dirtyProperties.add(name)
    self.setDirty(True)
    #if name == 'pattern':
    manager().touchReferences()

  def setDirty(self, dirty):
    if dirty:
      manager().addDirtyReference(self.q)
    else:
      manager().removeDirtyReference(self.q)

  @property
  def gameMd5(self):
    if not self._gameMd5 and self.gameId:
      self._gameMd5 = manager().queryGameMd5(self.gameId) or ""
    return self._gameMd5

  @gameMd5.setter
  def gameMd5(self, val): self._gameMd5 = val

  @property
  def userName(self): return _get_user_name(self.userId)
  @property
  def updateUserName(self): return _get_user_name(self.updateUserId)
  @property
  def protected(self): return _is_protected_data(self)

  @staticmethod
  def synthesize(name, type, sync=False):
    """
    @param  name  str
    @param  type  type
    @param  sync  bool  when true, save the changes on line
    return Property, Signal
    """
    signame = name + 'Changed'
    def getter(self):
      return getattr(self.__d, name)
    def setter(self, value):
      if getattr(self.__d, name) != value:
        setattr(self.__d, name, value)
        getattr(self, signame).emit(value)
    def sync_setter(self, value):
      if getattr(self.__d, name) != value:
        setattr(self.__d, name, value)
        self.__d.addDirtyProperty(name)
        getattr(self, signame).emit(value)
    sig = Signal(type)
    return Property(type, getter, sync_setter if sync else setter, notify=sig), sig

  TYPES = 'trailers', 'scape', 'holyseal', 'getchu', 'melon', 'gyutto', 'amazon', 'dmm', 'digiket', 'dlsite', 'freem', 'steam'
  TR_TYPES = 'Trailers', 'ErogameScape', 'Holyseal', 'Getchu', 'Melon', 'Gyutto', 'Amazon', 'DMM', 'DiGiket', 'DLsite', 'FreeM', 'Steam'

class Reference(QObject):
  __D = _Reference

  TYPES = __D.TYPES
  TR_TYPES = __D.TR_TYPES
  TYPE_NAMES = dict(zip(_Reference.TYPES, _Reference.TR_TYPES))

  @classmethod
  def typeName(cls, t):
    """
    @param  t  unicode
    @return  unicode not None
    """
    return cls.TYPE_NAMES.get(t) or ""

  @property
  def d(self): return self.__d

  def __init__(self, init=True, parent=None,
      id=0, itemId=0, gameId=0, gameMd5="", userId=0, userHash=0,
      type="", key="", timestamp=0, title="", brand="", url="", date=0,
      comment="", updateComment="",
      updateUserId=0, updateTimestamp=0,
      disabled=False, deleted=False,
      **ignored):
    self.__d = _Reference(self,
        id, itemId, gameId, gameMd5, userId, userHash, type, timestamp, updateTimestamp, updateUserId, key, title, brand, url, date, comment, updateComment, disabled, deleted)
    if init:
      self.init(parent)

  @property
  def queryKey(self): return self.key # str

  ## Construction ##

  @staticmethod
  def create(type, **kwargs):
    """
    @param  type  str
    @return  Reference
    """
    if type == 'trailers':
      cls = TrailersReference
    elif type == 'scape':
      cls = ScapeReference
    elif type == 'holyseal':
      cls = HolysealReference
    elif type == 'getchu':
      cls = GetchuReference
    elif type == 'gyutto':
      cls = GyuttoReference
    elif type == 'digiket':
      cls = DiGiketReference
    elif type == 'melon':
      cls = MelonReference
    elif type == 'amazon':
      cls = AmazonReference
    elif type == 'dmm':
      cls = DmmReference
    elif type == 'dlsite':
      cls = DLsiteReference
    elif type == 'freem':
      cls = FreemReference
    elif type == 'steam':
      cls = SteamReference
    else:
      dwarn("unknown type: %s" % type)
      cls = Reference
    return cls(type=type, **kwargs)

  def init(self, parent=None):
    """Invoke super __init__
    @param  parent  QObject
    """
    d = self.__d
    if not d.init:
      super(Reference, self).__init__(parent)
      d.init = True
      self.updateUserIdChanged.connect(lambda:
          self.updateUserNameChanged.emit(self.updateUserName))

  def isInitialized(self): return self.__d.init  # not used

  def clone(self, id=0, userId=0, userHash=None, timestamp=0, disabled=None, deleted=None, updateUserId=None, updateTimestamp=None):
    d = self.__d
    return Reference(parent=self.parent(), init=d.init,
      id=id if id else d.id,
      userId=userId if userId else d.userId,
      userHash=userHash if userHash is not None else userId,
      timestamp=timestamp if timestamp else d.timestamp,
      updateUserId=updateUserId if updateUserId is not None else d.updateUserId,
      updateTimestamp=updateTimestamp if updateTimestamp is not None else d.updateTimestamp,
      disabled=disabled if disabled is not None else d.disabled,
      deleted=deleted if deleted is not None else d.deleted,
      gameId=d.gameId, gameMd5=d.gameMd5, itemId=d.itemId,
      comment=d.comment, updateComment=d.updateComment,
      type=d.type, key=d.key, title=d.title, brand=d.brand, url=d.url, date=d.date)

  ## Dirty ##

  def isDirty(self): return bool(self.dirtyProperties)

  def dirtyProperties(self):
    """
    @return  set([str])  modified property names
    """
    return self.__d.dirtyProperties

  def clearDirtyProperties(self): self.__d.setDirty(False)

  ## Properties ##

  id, idChanged = __D.synthesize('id', long)
  itemId, itemIdChanged = __D.synthesize('itemId', long)
  type, typeChanged = __D.synthesize('type', str)
  #gameId, gameIdChanged = __D.synthesize('gameId', long)
  #gameMd5, gameMd5Changed = __D.synthesize('gameMd5', str)
  userId, userIdChanged = __D.synthesize('userId', int)
  userHash, userHashChanged = __D.synthesize('userHash', int)
  updateUserId, updateUserIdChanged = __D.synthesize('updateUserId', int)
  #updateUserHash, updateUserHashChanged = __D.synthesize('updateUserHash', int)
  timestamp, timestampChanged = __D.synthesize('timestamp', int)
  updateTimestamp, updateTimestampChanged = __D.synthesize('updateTimestamp', int)

  key, keyChanged = __D.synthesize('key', str)
  title, titleChanged = __D.synthesize('title', unicode)
  brand, brandChanged = __D.synthesize('brand', unicode)
  url, urlChanged = __D.synthesize('url', str)
  date, dateChanged = __D.synthesize('date', long)

  comment, commentChanged = __D.synthesize('comment', unicode, sync=True)
  updateComment, updateCommentChanged = __D.synthesize('updateComment', unicode, sync=True)
  disabled, disabledChanged = __D.synthesize('disabled', bool, sync=True)
  deleted, deletedChanged = __D.synthesize('deleted', bool, sync=True)

  userNameChanged = Signal(unicode)
  userName = Property(unicode,
      lambda self: self.__d.userName,
      notify=userNameChanged)

  updateUserNameChanged = Signal(unicode)
  updateUserName = Property(unicode,
      lambda self: self.__d.updateUserName,
      notify=updateUserNameChanged)

  proptectedChanged = Signal(bool)
  protected = Property(bool,
      lambda self: self.__d.protected,
      notify=proptectedChanged)

  @property
  def gameMd5(self): return self.__d.gameMd5
  @gameMd5.setter
  def gameMd5(self, val): self.__d.gameMd5 = val

  def setGameId(self, value):
    d = self.__d
    if d.gameId != value:
      d.gameId = value
      d.gameMd5 = ""
      d.addDirtyProperty('gameId')
      self.gameIdChanged.emit(value)
      dprint("pass")
  gameIdChanged = Signal(int)
  gameId = Property(int,
      lambda self: self.__d.gameId,
      setGameId,
      notify=gameIdChanged)

  @property
  def modifiedTimestamp(self):
    """
    @return  long  used for sorting
    """
    return max(self.__d.timestamp, self.__d.updateTimestamp)

  @property
  def image(self):
    """
    @return  str
    """
    try: return self.largeImage or self.mediumImage or self.smallImage
    except AttributeError: return ''

  @property
  def imageUrl(self, cache=True):
    ret = self.image
    if ret and cache:
      ret = cacheman.cache_image_url(ret)
    return ret

  def hasSampleImages(self): return bool(getattr(self, 'sampleImages'))

  def iterSampleImageUrls(self, cache=True):
    """
    @yield  str  url
    """
    #if self.hasSampleImages():
    for it in self.sampleImages:
      yield cacheman.cache_image_url(it) if cache else it

class TrailersItem(object):
  __slots__ = (
    'series',
    'banner',
    'otome',
    'brands',
    'videos',

    'artists', 'sdartists', 'writers', 'musicians',
  )

  def __init__(self,
      series="", banner="",
      otome=False,
      brands=[], videos=[],
      **kwargs):
    self.series = series # unicode
    self.banner = banner # str url
    self.otome = otome   # bool
    self.brands = brands    # [kw]
    self.videos = videos    # [kw]

    for k in 'artists', 'sdartists', 'writers', 'musicians':
      v = kwargs.get(k)
      v = [it['name'] for it in v] if v else []
      setattr(self, k, v)
    if self.musicians:
      self.musicians = uniquelist(self.musicians)

  def iterVideoIdsWithImage(self, cache=True):
    """
    @param  cache  bool
    @yield  (str vid, str url)
    """
    if self.videos:
      host = proxy.manager().ytimg_i
      for it in self.videos:
        vid = it['vid']
        img = host + '/vi/' + vid + '/maxresdefault.jpg' # http://stackoverflow.com/questions/2068344/how-do-i-get-a-youtube-video-thumbnail-from-the-youtube-api
        yield vid, cacheman.cache_image_url(img) if cache else img

class ScapeReference(Reference):
  def __init__(self, parent=None,
      type='scape',
      banner_url=None,
      okazu=None,
      genre=None,
      trial_url=None, trial_h=None,
      median=None, count=None,
      funtime=None, playtime=None,
      twitter_data_widget_id=None,
      twitter_data_widget_id_official=None,
      twitter_data_widget_id_before=None,
      shoukai='',
      **kwargs):
    super(ScapeReference, self).__init__(parent=parent,
        type=type, **kwargs)
    self.bannerUrl = banner_url # str url or None
    self.trialUrl = trial_url   # str or None
    self.trialH = trial_h       # bool or None
    self.okazu = okazu          # bool or None
    self.median = median        # int or None
    self.medianCount = count    # int or None
    self.funTime = funtime or 0   # int
    self.playTime = playtime or 0 # int
    self.slogan = genre or '' # unicode
    self.homepage = shoukai or '' # str
    self.twitterWidgets = []
    for it in twitter_data_widget_id, twitter_data_widget_id_official, twitter_data_widget_id_before:
      if it:
        self.twitterWidgets.append(it)

    self.dmm = kwargs.get('dmm') or '' # str

    self.trailers = kwargs.get('erogetrailers') or kwargs.get('trailers') or ''  # str
    self.gyutto = kwargs.get('gyutto_id') or ''
    self.tokuten = kwargs.get('erogametokuten') or ''

    self.dlsite = kwargs.get('dlsite_id') or ''
    self.dlsiteDomain = kwargs.get('dlsite_domain') or ''

    k = kwargs.get('digiket') or '' # starts with ITM
    if k:
      k = k.replace('ITM', '').lstrip('0')
    self.digiket = k

  @property
  def tokutenUrl(self):
    return 'http://erogame-tokuten.com/title.php?title_id=%s' % self.tokuten if self.tokuten else ''

  #@property
  #def digiketUrl(self): # such as: http://www.digiket.com/work/show/_data/ID=ITM0097342/
  #  return 'http://www.digiket.com/work/show/_data/ID=%s/' % self.digiket if self.digiket else ''

  @property
  def dlsiteUrl(self):
    return 'http://www.dlsite.com/%s/work/=/product_id/%s.html' % (self.dlsiteDomain, self.dlsite) if self.dlsite and self.dlsiteDomain else ''

  #@property
  #def gyuttoUrl(self):
  #  return 'http://gyutto.com/i/item%s' % self.gyutto if self.gyutto else ''

  @property
  def erogetrailersUrl(self):
    return 'http://erogetrailers.com/soft/%s' % self.trailers if self.trailers else ''

  def hasReview(self):
    return bool(self.medianCount)

  def queryReviews(self, **kwargs):
    """
    @param*  offset  int
    @param*  limit  int
    @return  [kw]
    """
    return refman.scape().queryReviews(self.key, **kwargs)

class DLsiteReference(Reference): #(object):
  def __init__(self, parent=None,
      type='dlsite',
      image='', price=0, ecchi=True, otome=False, homepage='',
      artist='', writer='', musician='',
      description='', characterDescription='', review='', filesize=0,
      sampleImages=[], tags=[], rpg=False,
      **kwargs):
    super(DLsiteReference, self).__init__(parent=parent,
        type=type, **kwargs)
    self.largeImage = image # str
    self.price = price # int
    self.ecchi = ecchi # bool
    self.otome = otome # bool
    self.homepage = homepage # str
    self.description = description # unicode
    self.characterDescription = characterDescription # unicode
    self.review = review # unicode
    self.sampleImages = sampleImages # [str url]
    self.rpg = rpg # bool
    self.fileSize = filesize # int

    #self.genres = []
    #if rpg:
    #  self.genres.append('RPG')

    self.tags = tags # [unicode]
    #if rpg:
    #  self.tags.append('RPG')

    self.creators = []
    if artist:
      self.creators.append({'name':artist, 'roles':['artist']})
    if writer:
      self.creators.append({'name':writer, 'roles':['writer']})
    if musician:
      self.creators.append({'name':musician, 'roles':['musician']})

  def hasReview(self): return bool(self.review)

  def renderReview(self):
    """
    @return  unicode not None
    """
    return skstr.unescapehtml(self.review) if self.review else ''

  @property
  def queryKey(self):
    """@reimp"""
    return self.url

  def hasSampleImages(self): return bool(self.sampleImages)

  def iterSampleImageUrls(self, cache=True):
    """
    @yield  str  url
    """
    #if self.hasSampleImages():
    for it in self.sampleImages:
      it = proxy.get_dlsite_url(it)
      yield cacheman.cache_image_url(it) if cache else it

  _rx_desc_size = re.compile(r'width="[0-9]+" height="[0-9]+"')  # remove image size, use large image
  def hasDescriptions(self): return bool(self.description)
  def iterDescriptions(self):
    t = self.description
    if t:
      t = proxy.replace_dlsite_html(t)
      t = t.replace("<h2>", "<b>").replace("</h2>", "</b>") # reduce font size
      t = self._rx_desc_size.sub('', t)
      yield cacheman.cache_html(t)

  # Example: <a href="//img.dlsite.jp/modpub/images2/parts/RJ080000/RJ079473/RJ079473_PTS0000000168_3.jpg"
  def renderCharacterDescription(self): # -> unicode
    t = self.characterDescription
    if not t:
      return ''
    t = proxy.replace_dlsite_html(t)
    return cacheman.cache_html(t)

class FreemReference(Reference): #(object):
  def __init__(self, parent=None,
      type='freem',
      image="", slogan="",
      otome=False, ecchi=True,
      description='',
      videos=[],
      sampleImages=[],
      filesize=0,
      **kwargs):
    super(FreemReference, self).__init__(parent=parent,
        type=type, **kwargs)
    self.largeImage = image # str
    self.otome = otome # bool
    self.ecchi = ecchi # bool
    self.slogan = slogan or '' # str
    self.description = description # unicode
    self.sampleImages = sampleImages # [str url]
    self.videos = videos    # [str]
    self.fileSize = filesize # int

  def iterVideoIdsWithImage(self, cache=True):
    """
    @param  cache  bool
    @yield  (str vid, str url)
    """
    if self.videos:
      host = proxy.manager().ytimg_i
      for vid in self.videos:
        img = host + '/vi/' + vid + '/0.jpg'
        yield vid, cacheman.cache_image_url(img) if cache else img

  def hasDescriptions(self): return bool(self.description)
  def iterDescriptions(self):
    t = self.description
    if t:
      yield t

  def hasSampleImages(self): return bool(self.sampleImages)

  def iterSampleImageUrls(self, cache=True):
    """
    @yield  str  url
    """
    #if self.hasSampleImages():
    for it in self.sampleImages:
      yield cacheman.cache_image_url(it) if cache else it

class SteamReference(Reference): #(object):
  def __init__(self, parent=None,
      type='steam',
      image="",
      otome=False,
      homepage='',
      description='', review='',
      sampleImages=[],
      **kwargs):
    super(SteamReference, self).__init__(parent=parent,
        type=type, **kwargs)
    self.largeImage = image # str
    self.otome = otome # bool
    self.homepage = homepage # str
    self.description = description # unicode
    self.review = review # unicode
    self.sampleImages = sampleImages # [str url]

  def hasSampleImages(self): return bool(self.sampleImages)

  def iterSampleImageUrls(self, cache=True):
    """
    @yield  str  url
    """
    #if self.hasSampleImages():
    for it in self.sampleImages:
      yield cacheman.cache_image_url(it) if cache else it

  def hasDescriptions(self): return bool(self.description)
  def iterDescriptions(self):
    t = self.description
    if t:
      yield t

  def hasReview(self): return bool(self.review)
  def renderReview(self): return self.review

class GetchuReference(Reference): #(object):
  def __init__(self, parent=None,
      type='getchu',
      image="",
      price=0,
      #writers[], artists=[], sdartists=[], musicians=[],
      otome=False, genre='', categories=[], subgenres=[],
      characters=[],
      descriptions=[], characterDescription='',
      videos=[],
      sampleImages=[], comics=[], banners=[],
      writers=[], artists=[], sdartists=[], musicians=[],
      **kwargs):
    super(GetchuReference, self).__init__(parent=parent,
        type=type, **kwargs)
    self.largeImage = image # str
    self.otome = otome # bool
    self.price = price # int
    self.characters = characters    # [kw]
    self.slogan = genre or '' # str
    self.tags = subgenres + categories # [unicode] not None
    self.descriptions = descriptions # [unicode]
    self.comics = comics # [str url]
    self.sampleImages = sampleImages # [str url]
    self.bannerImages = banners # [str url]
    self.videos = videos    # [str]

    self.artists = artists # [unicode name]
    self.sdartists = sdartists # [unicode name]
    self.writers = writers # [unicode name]
    self.musicians = musicians # [unicode name]

    self.characterDescription = characterDescription # unicode

  def iterVideoIdsWithImage(self, cache=True):
    """
    @param  cache  bool
    @yield  (str vid, str url)
    """
    if self.videos:
      host = proxy.manager().ytimg_i
      for vid in self.videos:
        img = host + '/vi/' + vid + '/0.jpg'
        yield vid, cacheman.cache_image_url(img) if cache else img

  def hasBannerImages(self): return bool(self.bannerImages)

  def iterBannerImageUrls(self, cache=True):
    """
    @yield  str  url
    """
    #if self.hasSampleImages():
    for it in self.bannerImages:
      it = proxy.get_image_url(it)
      #it = proxy.get_getchu_url(it)
      yield cacheman.cache_image_url(it) if cache else it

  #def hasReview(self): return True # not implemented
  #@property
  #def reviewUrl(self): # str
  #  # Example: http://www.getchu.com/review/item_review.php?action=list&id=756396
  #  domain = proxy.manager().getchu_domain
  #  return '%s/review/item_review.php?action=list&id=%s' % (domain, self.key)

  @memoizedproperty
  def review(self):
    """
    @return  unicode  HTML not None
    """
    h = refman.getchu().queryReview(self.key)
    return skstr.unescapehtml(h) if h else ''

  def hasReview(self): return bool(self.review)
  def renderReview(self): return self.review

  def hasSampleImages(self): return bool(self.sampleImages or self.bannerImages)

  def iterSampleImageUrls(self, cache=True):
    """
    @yield  str  url
    """
    #if self.hasSampleImages():
    l = self.sampleImages
    if l:
      for it in l:
        it = proxy.get_getchu_url(it)
        yield cacheman.cache_image_url(it) if cache else it
    l = self.bannerImages
    if l:
      for it in l:
        it = proxy.get_getchu_url(it)
        it = proxy.get_image_url(it)
        yield cacheman.cache_image_url(it) if cache else it

  def hasDescriptions(self):
    """
    @return  bool
    """
    return bool(self.descriptions)

  def iterDescriptions(self):
    """
    @yield  unicode
    """
    return itertools.imap(self._renderDescription, self.descriptions)

  _rx_desc_title = re.compile(r'<div class="tabletitle">.(.+?)</div>') # first dot to skip the leading space. not sure why \s does not work
  _rx_desc_size = re.compile(r'width="[0-9]+" height="[0-9]+"')  # remove image size, use large image
  @classmethod
  def _renderDescription(cls, t):
    """
    @param  unicode
    @return  unicode
    """
    t = cls._rx_desc_title.sub(ur'<div class="tabletitle">【\1】</div>', t)
    t = cls._rx_desc_size.sub('', t)
    t = t.replace('_s.jpg', '.jpg')
    t = proxy.replace_getchu_html(t)
    return cacheman.cache_html(t)

  def renderCharacterDescription(self): # -> unicode
    t = self.characterDescription
    if not t:
      return ''
    t = self._rx_desc_title.sub('', t)
    t = self._rx_desc_size.sub('', t)
    t = t.replace('_s.jpg', '.jpg')
    t = t.replace('width="1%"', 'width="25%"') # <TD valign="middle" width="1%"> for img
    t = t.replace('valign="middle"', 'valign="top"')
    t = t.replace('vertical-align:middle', 'vertical-align:top')
    t = proxy.replace_getchu_html(t)
    return cacheman.cache_html(t)

  def iterNameYomi(self):
    """
    yield (unicode name, unicode yomi)
    """
    if self.characters:
      for it in self.characters:
        yield it['name'], it['yomi']

class DiGiketReference(Reference): #(object):
  def __init__(self, parent=None,
      type='digiket',
      image="",
      price=0, # not exist price though
      #writers[], artists=[], musicians=[],
      otome=False, ecchi=True, genre='', keywords=[],
      filesize=0,
      anime=False,
      characters=[],
      description='', characterDescription='', review='', event='',
      screenshots=[], ev='',
      artists=[], writers=[], musicians=[],
      **kwargs):
    super(DiGiketReference, self).__init__(parent=parent,
        type=type, **kwargs)
    self.largeImage = image # str
    self.otome = otome # bool
    self.price = price # int
    self.characters = characters    # [kw]
    self.slogan = genre or '' # str
    self.description = description # unicode
    self.characterDescription = characterDescription # unicode
    self.review = review # unicode
    self.fileSize = filesize # int
    self.event = event # unicode

    self.tags = keywords or []
    if anime:
      self.tags.append(u'アニメ')

    self.sampleImages = []
    if image:
      self.sampleImages.append(image)
    if ev:
      self.sampleImages.append(ev)
    if screenshots:
      self.sampleImages.extend(screenshots)

    self.artists = artists # [unicode name]
    self.writers = writers # [unicode name]
    self.musicians = musicians # [unicode name]

  def hasSampleImages(self): return bool(self.sampleImages)

  def iterSampleImageUrls(self, cache=True):
    """
    @yield  str  url
    """
    #if self.hasSampleImages():
    for it in self.sampleImages:
      yield cacheman.cache_image_url(it) if cache else it

  def hasDescriptions(self):
    """
    @return  bool
    """
    return bool(self.description)

  def iterDescriptions(self):
    """
    @yield  unicode
    """
    if self.description:
      yield cacheman.cache_html(self.description)

  def renderCharacterDescription(self): return self.characterDescription

  def hasReview(self): return bool(self.review)
  def renderReview(self): return self.review

class MelonReference(Reference): #(object):
  def __init__(self, parent=None,
      type='melon',
      image="",
      price=0,
      sampleImages = [],
      doujin=False, ecchi=True,
      intro='', event='', artists=[], writers=[],
      **kwargs):
    super(MelonReference, self).__init__(parent=parent,
        type=type, **kwargs)
    self.largeImage = image # str
    self.ecchi = ecchi # bool
    self.doujin = doujin # bool
    self.price = price # int
    self.description = intro # unicode
    self.event = event # unicode

    self.sampleImages = sampleImages

    self.artists = artists
    self.writers = writers

  def hasSampleImages(self): return bool(self.sampleImages)

  def iterSampleImageUrls(self, cache=True):
    """
    @yield  str  url
    """
    #if self.hasSampleImages():
    for it in self.sampleImages:
      yield cacheman.cache_image_url(it) if cache else it

  def hasDescriptions(self):
    """
    @return  bool
    """
    return bool(self.description)

  def iterDescriptions(self):
    """
    @yield  unicode
    """
    if self.description:
      yield self.description
      #yield cacheman.cache_html(self.description)

class AmazonReference(Reference):
  def __init__(self, parent=None,
      type='amazon',
      price=0, ecchi=True,
      largeImage="", mediumImage="", smallImage="",
      sampleImages=[],
      descriptions=[],
      review="",
      **kwargs):
    super(AmazonReference, self).__init__(parent=parent,
        type=type, **kwargs)
    self.price = price  # int yen
    self.ecchi = ecchi # bool
    self.largeImage = largeImage # str url
    self.mediumImage = mediumImage # str url
    self.smallImage = smallImage # str url
    self.sampleImages = sampleImages # [str url] not None
    self.reviewUrl = review # str url
    self.descriptions =  descriptions # [unicode] not None, contains HTML tags

  def hasDescriptions(self):
    """
    @return  bool
    """
    return bool(self.descriptions)

  def iterDescriptions(self):
    """
    @yield  unicode
    """
    for it in self.descriptions:
      yield self._renderDescription(it)

  @memoizedproperty
  def review(self):
    """
    @return  unicode  HTML not None
    """
    if self.reviewUrl:
      h = refman.amazon().queryReview(self.reviewUrl)
      if h:
        # extract <body>
        START = '<body>'
        STOP = '</body>'
        start = h.find(START)
        if start != -1:
          start += len(START)
          stop = h.find(STOP, start)
          if stop != -1:
            h = h[start:stop]

        # remove <script>
        START = '<script'
        STOP = '</script>'
        start = h.find(START)
        if start != -1:
          stop = h.rfind(STOP)
          if stop != -1:
            h = h[:start] + h[stop+len(STOP):]
        return h
    return ''

  def hasReview(self): return bool(self.reviewUrl)
  def renderReview(self):
    # TODO: Fetch data online
    return self.review

  #_story_rx = re.compile(r"%s" % '|'.join([
  #  u"<b>■ストーリー</b>",
  #  u"■ストーリー<br>",
  #  u"■ストーリー",
  #  u"<b>【ストーリー】</b>",
  #  u"【ストーリー】",
  #  "<b>【商品概要.*",
  #  "【商品概要.*",
  #]), re.DOTALL)
  @staticmethod
  def _renderDescription(t):
    """
    @param  unicode
    @return  unicode
    """
    if t:
      return cacheman.cache_html(skstr.uniqbr(skstr.stripbr(t), repeat=3) )
    return ''

class GyuttoReference(Reference): #(object), images will crash Python2
  def __init__(self, parent=None,
      type='gyutto',
      series="",
      image="", # not used
      #price=0, # not exist price though
      #writers[], artists=[], musicians=[],
      filesize=0,
      #description='',  # not used
      theme='',
      doujin=False, otome=False,
      tags=[], sampleImages=[],
      writers=[], artists=[], musicians=[],
      **kwargs):
    super(GyuttoReference, self).__init__(parent=parent,
        type=type, **kwargs)
    self.largeImage = image # str
    self.series = series
    self.slogan = theme
    self.fileSize = filesize
    self.tags = tags # [unicode] not None
    self.sampleImages = sampleImages # [str URL]
    self.otome = otome
    self.doujin = doujin

    self.artists = artists # [unicode name]
    self.writers = writers # [unicode name]
    self.musicians = musicians # [unicode name]

  @memoizedproperty
  def review(self):
    """
    @return  unicode  HTML not None
    """
    h = refman.getchu().queryReview(self.key)
    return skstr.unescapehtml(h) if h else ''

  def hasReview(self): return bool(self.review)
  def renderReview(self): return self.review

  #@property
  #def reviewUrl(self):
  #  return 'http://gyutto.com/item/item_review.php?id=%s' % self.key

  def hasSampleImages(self): return bool(self.sampleImages)

  def iterSampleImageUrls(self, cache=True):
    """@reimp
    @yield  str  url
    """
    for it in self.sampleImages:
      return cacheman.cache_image_url(it) if cache else it

class HolysealReference(Reference): #(object):
  def __init__(self, parent=None,
      type='holyseal',
      #writers[], artists=[],
      otome=False,
      ecchi=True,
      banner='',
      genre='',
      writers=[], artists=[],
      **kwargs):
    super(HolysealReference, self).__init__(parent=parent,
        type=type, **kwargs)
    self.otome = otome # bool
    self.ecchi = ecchi # bool
    self.banner = banner # unicode or None
    self.slogan = genre or '' # str

    self.artists = artists # [unicode name]
    self.writers = writers # [unicode name]

class TokutenItem(object): # erogame-tokuten webpage, images will crash Python2
  __slots__ = (
    'key',
    'url',
    'images',
    'image',
  )

  type = 'tokuten'
  def __init__(self, key="", url="", images=[], **kwargs):
    self.key = key # str
    self.url = url # str
    self.images = images # [str]
    self.image = '' # placeholder, cover is not fetched

  def hasSampleImages(self): return bool(self.images)

  def iterSampleImageUrls(self, cache=True):
    """@reimp
    @yield  str  url
    """
    for it in self.images:
      return cacheman.cache_image_url(it) if cache else it

class DmmPage(object): # DMM webpage
  __slots__ = (
    'description',
    'review',
  )
  def __init__(self, url="",
      description="", review="",
      **kwargs):
    self.description = description # unicode html or None
    self.review = review # unicode html or None

class DmmReference(Reference):
  def __init__(self, parent=None,
      type='dmm', # dmm
      price=0, doujin=False, ecchi=True, otome=False,
      series="", keywords=[], authors=[], #genres=[],
      largeImage="", mediumImage="", smallImage="",
      sampleImages=[],
      **kwargs):
    super(DmmReference, self).__init__(parent=parent,
        type=type, **kwargs)
    self.price = price  # int yen
    self.series = series  # unicode
    self.doujin = doujin # bool
    self.ecchi = ecchi # bool
    self.otome = otome # bool
    #self.genres = genres # [str]
    self.tags = keywords  # [unicode] not None
    self.artists = authors  # [unicode] not None
    self.largeImage = largeImage # str url
    self.mediumImage = mediumImage # str url
    self.smallImage = smallImage # str url
    self.sampleImages = sampleImages # [str url] not None

  @memoizedproperty
  def page(self):
    """Online
    @return  {kw} or None
    """
    kw = refman.dmm().query(self.url)
    if kw:
      return DmmPage(**kw)

  def hasReview(self): return bool(self.page and self.page.review)
  def renderReview(self):
    return self.page.review if self.page else ''

  @property
  def description(self): # -> str
    page = self.page
    return page.description if page else ''

  def hasDescriptions(self): # -> bool
    page = self.page
    return bool(page and page.description)

  def iterDescriptions(self): # yield unicode
    page = self.page
    if page and page.description:
      yield cacheman.cache_html(page.description)

  @memoized
  def hasSampleImages(self):
    """@reimp
    @return  bool
    """
    if self.sampleImages:
      url = self.sampleImages[0]
      path = cacheman.cache_image_path(url)
      if self._isBadImage(path):
        return False
    return True

  def iterSampleImageUrls(self, cache=True):
    """@reimp
    @yield  str  url
    """
    for it in self.sampleImages:
      if not cache:
        yield it
      else:
        path = cacheman.cache_image_url(it)
        if path == it or not self._isBadImage(cacheman.cache_image_path(it)):
          yield path

  @staticmethod
  def _isBadImage(path):
    """
    @param  path  unicode
    @return  bool
    """
    return not path or os.path.exists(path + '.bad')
    #if path and os.path.exists(path):
    #  np = osutil.normalize_path(path)
    #  import hashutil
    #  md5 = hashutil.md5sum(np)
    #  # http://pics.dmm.com/mono/movie/n/now_printing/now_printing.jpg
    #  BAD_MD5 = 'f591f3826a1085af5cdeeca250b2c97a'
    #  if md5 == BAD_MD5: # now printing
    #    return True
    #return False

class TrailersReference(Reference):
  def __init__(self, parent=None,
      type='trailers', # trailers
      ecchi=True, doujin=False, **kwargs):
    super(TrailersReference, self).__init__(parent=parent,
        type=type, **kwargs)
    self.ecchi = ecchi # bool
    self.doujin = doujin # bool
    self.videoCount = kwargs.get('videoCount') or kwargs.get('totalVideos') or 0
    self.dmm = kwargs.get('dmm2') or kwargs.get('dmm') or '' # str
    for k in (
        'amazon', 'getchu', 'holyseal', 'erogamescape', 'gyutto',
        'homepage', 'romanTitle',
        ):
      setattr(self, k, kwargs.get(k) or '')

  @property
  def amazonUrl(self):
    return 'http://amazon.co.jp/dp/' + self.amazon if self.amazon else ''

  #@property
  #def dmmUrl(self):

  @property
  def getchuUrl(self):
    return 'http://getchu.com/soft.phtml?id=%s' % self.getchu if self.getchu else ''

  #@property
  #def gyuttoUrl(self):
  #  return 'http://gyutto.com/i/item%s' % self.gyutto if self.gyutto else ''

  @property
  def holysealUrl(self):
    return 'http://holyseal.net/cgi-bin/mlistview.cgi?prdcode=%s' % self.holyseal if self.holyseal else ''

  @property
  def erogamescapeUrl(self):
    return 'http://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/game.php?game=%s' % self.erogamescape if self.erogamescape else ''

## Game model ##

# See: https://groups.google.com/forum/?fromgroups=#!topic/pyside/zGsHyJ3We-A
# See; http://pastebin.com/VMeg4isb

GAME_ICON_ROLE = Qt.DecorationRole
GAME_NAME_ROLE = Qt.DisplayRole
GAME_TOOLTIP_ROLE = Qt.ToolTipRole
GAME_MD5_ROLE = Qt.UserRole
GAME_LINK_ROLE = Qt.UserRole +1
GAME_SEARCHTEXT_ROLE = Qt.UserRole +2
GAME_STYLEHINT_ROLE = Qt.UserRole +3
GAME_ROLES = {
  GAME_ICON_ROLE: 'icon',
  GAME_NAME_ROLE: 'name',
  GAME_TOOLTIP_ROLE: 'toolTip',
  GAME_MD5_ROLE: 'md5',
  GAME_LINK_ROLE: 'link',
  GAME_SEARCHTEXT_ROLE: 'searchText',
  GAME_STYLEHINT_ROLE: 'styleHint',
}

@Q_Q
class _GameModel(object):
  def __init__(self):
    self.currentGameObject = None # GameObject
    #self.refresh()
    #q.destroyed.connect(self._onDestroyed)

    self.filterGameType = '' # empty, 'otome', 'junai', or 'nuki'

    self._filterText = "" # unicode
    self._filterRe = None # compiled re
    self._filterData = None # [Character]

    self._sourceData = None # [Reference] or None
    self._sortedData = None
    #self.md5 = "" # str
    #self._gameId = 0
    #self.sortingReverse = False
    #self.sortingColumn = 0

  def resetSourceData(self): self._sourceData = None

  @property
  def sourceData(self): # -> list not None
    if self._sourceData is None:
      #q = self.q
      #q.beginResetModel()
      data = [{
        'id': g.id,
        'md5': g.md5,
        'time': g.visitTime,
        'name': g.name,
        'path': QDir.fromNativeSeparators(g.path),
        'launchPath': QDir.fromNativeSeparators(g.launchPath) if g.launchPath else "",
        'gameType': g.gameType(),
      } for g in manager().games()]
      #if g.path and (
      #  os.path.exists(g.path) or
      #  g.launchPath and os.path.exists(g.launchPath)
      #)]

      if data:
        data.sort(reverse=True, key=operator.itemgetter('time'))
      self._sourceData = data
      #q.endResetModel()
    return self._sourceData

  @property
  def data(self):
    """
    @return  [Character]
    """
    #return self.sortedData if self.sortingColumn or self.sortingReverse else self.filterData if self.filterText else self.sourceData
    return self.sortedData

  @property
  def sortedData(self): # -> list not None
    if self._sortedData is None:
      self._sortedData = self.filterData if self.filterText or self.filterGameType else self.sourceData
      #if not self.sortingColumn:
      #  if self.sortingReverse:
      #    self._sortedData = list(reversed(data))
      #  else:
      #    self._sortedData = data
      #else:
      #col = self.COLUMNS[self.sortingColumn]
      #self._sortedData = sorted(data,
      #    key=operator.attrgetter(col),
      #    reverse=self.sortingReverse)
    return self._sortedData
  @sortedData.setter
  def sortedData(self, value): self._sortedData = value

  @property
  def filterText(self): return self._filterText
  @filterText.setter
  def filterText(self, value):
    self._filterText = value
    self._filterRe = None
    self._filterData = None
    self._sortedData = None

  @property
  def filterData(self):
    if self._filterData is None:
      self._filterData = filter(self._searchData, self.sourceData)
    return self._filterData
  @filterData.setter
  def filterData(self, value): self._filterData = value

  @property
  def filterRe(self):
    """
    @throw  re exception
    """
    if not self._filterRe and self.filterText:
      self._filterRe = re.compile(self.filterText, re.IGNORECASE|re.DOTALL)
    return self._filterRe

  def _searchData(self, entry):
    """
    @param  entry  Character
    @return  bool
    """
    if not self.filterGameType or self.filterGameType == entry['gameType']:
      if not self.filterText:
        return True
      else:
        try:
          rx = self.filterRe
          for it in entry['name'], entry['path'], entry['launchPath']:
            if it and rx.search(it):
              return True
        except Exception, e:
          dwarn(e)
          #message = e.message or "%s" % e
          #growl.warn(message)
    return False

#@QmlObject
class GameModel(QAbstractListModel):
  """Constructed by SpringBoard QML"""
  def __init__(self, parent=None):
    super(GameModel, self).__init__(parent)
    self.setRoleNames(GAME_ROLES)
    self.__d = _GameModel(self)

    dm = manager()
    dm.gamesChanged.connect(self.__d.resetSourceData)
    dm.gamesChanged.connect(self.reset)

    for sig in self.filterTextChanged, self.filterGameTypeChanged: #self.sortingColumnChanged, self.sortingReverseChanged:
      sig.connect(self.reset)

    #changed = manager().gamesChanged
    #changed.connect(self.__d.refresh)
    #changed.connect(self.reset)
    #changed.connect(lambda:
    #    self.countChanged.emit(self.count))

  #@Slot()
  def reset(self):
    d = self.__d
    d.filterData = None
    d.sortedData = None
    super(GameModel, self).reset()
    self.countChanged.emit(self.count)
    self.currentCountChanged.emit(self.currentCount)

  def rowCount(self, parent=QModelIndex()):
    """@reimp @public"""
    return len(self.__d.data)

  def data(self, index, role):
    """@reimp @public"""
    if not index.isValid():
      return
    row = index.row()
    if row < 0:
      return
    data = self.__d.data
    if row >= len(data):
      return

    game = data[row]

    if role in (GAME_NAME_ROLE, GAME_MD5_ROLE):
      return game[GAME_ROLES[role]]

    if role == GAME_ICON_ROLE:
      return "image://file/" + game['path'] # = FileImageProvider.PROVIDER_ID

    if role == GAME_TOOLTIP_ROLE:
      return game['launchPath'] or game['path']

    if role == GAME_STYLEHINT_ROLE:
      return game['gameType']

    if role == GAME_LINK_ROLE:
      return create_game_link(game['path'], game['launchPath'])

    if role == GAME_SEARCHTEXT_ROLE:
      return "\n".join(game[key] or ''
          for key in ('name', 'path', 'launchPath'))

  @Slot(int, result=QObject)
  def get(self, row):
    try: md5 = self.__d.data[row]['md5']
    except IndexError: return
    d = self.__d
    g = manager().queryGameObject(md5=md5)
    if g:
      #if d.currentGameObject:
      #  skevents.runlater(d.currentGameObject.deleteLater)
      d.currentGameObject = g # keep reference
      return g

  countChanged = Signal(int)
  count = Property(int,
      lambda self: len(self.__d.sourceData),
      notify=countChanged)

  currentCountChanged = Signal(int)
  currentCount = Property(int,
      lambda self: len(self.__d.data),
      notify=currentCountChanged)

  def setFilterText(self, value):
    if value != self.__d.filterText:
      self.__d.filterText = value
      self.filterTextChanged.emit(value)
  filterTextChanged = Signal(unicode)
  filterText = Property(unicode,
      lambda self: self.__d.filterText,
      setFilterText,
      notify=filterTextChanged)

  def setFilterGameType(self, value):
    if value != self.__d.filterGameType:
      self.__d.filterGameType = value
      self.filterGameTypeChanged.emit(value)
  filterGameTypeChanged = Signal(unicode)
  filterGameType = Property(unicode,
      lambda self: self.__d.filterGameType,
      setFilterGameType,
      notify=filterGameTypeChanged)

  #def setSortingColumn(self, value):
  #  if value != self.__d.sortingColumn:
  #    self.__d.sortingColumn = value
  #    self.sortingColumnChanged.emit(value)
  #sortingColumnChanged = Signal(int)
  #sortingColumn = Property(int,
  #    lambda self: self.__d.sortingColumn,
  #    setSortingColumn,
  #    notify=sortingColumnChanged)

  #def setSortingReverse(self, value):
  #  if value != self.__d.sortingReverse:
  #    self.__d.sortingReverse = value
  #    self.sortingReverseChanged.emit(value)
  #sortingReverseChanged = Signal(bool)
  #sortingReverse = Property(bool,
  #    lambda self: self.__d.sortingReverse,
  #    setSortingReverse,
  #    notify=sortingReverseChanged)

## Voice model ##

VOICE_OBJECT_ROLE = Qt.UserRole
VOICE_NUM_ROLE = Qt.UserRole +1
VOICE_ROLES = {
  VOICE_OBJECT_ROLE: 'object', # Character, object
  VOICE_NUM_ROLE: 'number', # int, 番号
}
class _VoiceModel(object):
  COLUMNS = [ # MUST BE CONSISTENT WITH voicetable.qml
    'timestamp', # row
    'ttsEnabled',
    'ttsEngine',
    'gender',
    'name',
    'timestamp',
  ]
  def __init__(self):
    self._filterText = "" # unicode
    self._filterRe = None # compiled re
    self._filterData = None # [Character]
    self._sortedData = None

    self.sortingColumn = 0
    self.sortingReverse = False

  @property
  def data(self):
    """
    @return  [Character]
    """
    #return self.sortedData if self.sortingColumn or self.sortingReverse else self.filterData if self.filterText else self.sourceData
    return self.sortedData

  @staticproperty
  def sourceData(): return manager().characters() # -> list not None

  @property
  def sortedData(self): # -> list not None
    if self._sortedData is None:
      data = self.filterData if self.filterText else self.sourceData
      #if not self.sortingColumn:
      #  if self.sortingReverse:
      #    self._sortedData = list(reversed(data))
      #  else:
      #    self._sortedData = data
      #else:
      #if not self.sortingColumn: # first column is timestamp
      #  reverse = not reverse
      col = self.COLUMNS[self.sortingColumn]
      self._sortedData = sorted(data,
          key=operator.attrgetter(col),
          reverse=self.sortingReverse)
    return self._sortedData
  @sortedData.setter
  def sortedData(self, value): self._sortedData = value

  @property
  def filterText(self): return self._filterText
  @filterText.setter
  def filterText(self, value):
    self._filterText = value
    self._filterRe = None
    self._filterData = None
    self._sortedData = None

  @property
  def filterData(self):
    if self._filterData is None:
      self._filterData = filter(self._searchData, self.sourceData)
    return self._filterData
  @filterData.setter
  def filterData(self, value): self._filterData = value

  @property
  def filterRe(self):
    """
    @throw  re exception
    """
    if not self._filterRe and self.filterText:
      self._filterRe = re.compile(self.filterText, re.IGNORECASE|re.DOTALL)
    return self._filterRe

  def _searchData(self, entry):
    """
    @param  entry  Character
    @return  bool
    """
    try:
      rx = self.filterRe
      for it in entry.name, i18n.gender_name(entry.gender):
        if it and rx.search(it):
          return True
    except Exception, e:
      dwarn(e)
      #message = e.message or "%s" % e
      #growl.warn(message)
    return False

#@QmlObject
class VoiceModel(QAbstractListModel):
  """Constructed by VoiceView QML"""

  def __init__(self, parent=None):
    super(VoiceModel, self).__init__(parent)
    self.setRoleNames(VOICE_ROLES)
    d = self.__d = _VoiceModel()

    for sig in self.filterTextChanged, self.sortingColumnChanged, self.sortingReverseChanged:
      sig.connect(self.reset)

    manager().charactersChanged.connect(self.reset)

  #@Slot()
  def reset(self):
    d = self.__d
    d.filterData = None
    d.sortedData = None
    super(VoiceModel, self).reset()
    self.countChanged.emit(self.count)
    self.currentCountChanged.emit(self.currentCount)

  def rowCount(self, parent=QModelIndex()):
    """@reimp @public"""
    return len(self.__d.data)

  def data(self, index, role):
    """@reimp @public"""
    if index.isValid():
      row = index.row()
      if row >= 0 and row < self.rowCount():
        if role == VOICE_NUM_ROLE:
          return row + 1
        elif role == VOICE_OBJECT_ROLE:
          return self.get(row)

  @Slot(int, result=QObject)
  def get(self, row):
    # Revert the list
    try: return self.__d.data[-row -1]
    except IndexError: pass

  countChanged = Signal(int)
  count = Property(int,
      lambda self: len(self.__d.sourceData),
      notify=countChanged)

  currentCountChanged = Signal(int)
  currentCount = Property(int,
      lambda self: len(self.__d.data),
      notify=currentCountChanged)

  def setFilterText(self, value):
    if value != self.__d.filterText:
      self.__d.filterText = value
      self.filterTextChanged.emit(value)
  filterTextChanged = Signal(unicode)
  filterText = Property(unicode,
      lambda self: self.__d.filterText,
      setFilterText,
      notify=filterTextChanged)

  def setSortingColumn(self, value):
    if value != self.__d.sortingColumn:
      self.__d.sortingColumn = value
      self.sortingColumnChanged.emit(value)
  sortingColumnChanged = Signal(int)
  sortingColumn = Property(int,
      lambda self: self.__d.sortingColumn,
      setSortingColumn,
      notify=sortingColumnChanged)

  def setSortingReverse(self, value):
    if value != self.__d.sortingReverse:
      self.__d.sortingReverse = value
      self.sortingReverseChanged.emit(value)
  sortingReverseChanged = Signal(bool)
  sortingReverse = Property(bool,
      lambda self: self.__d.sortingReverse,
      setSortingReverse,
      notify=sortingReverseChanged)

  @Slot(QObject)
  def removeItem(self, c):
    if prompt.confirmDeleteCharacter(c):
      manager().removeCharacter(c)

  @Slot()
  def clearItems(self):
    if prompt.confirmClearEntries():
      manager().clearCharacters()

  @Slot()
  def purgeItems(self):
    manager().purgeCharacters()

## Term model ##

TERM_OBJECT_ROLE = Qt.UserRole
TERM_NUM_ROLE = Qt.UserRole + 1
TERM_ID_ROLE = Qt.UserRole + 2
TERM_ROLES = {
  TERM_OBJECT_ROLE: 'object', # Term, object
  TERM_NUM_ROLE: 'number', # int, 番号
  TERM_ID_ROLE: 'id', # object id
}
class _TermModel(object):
  COLUMNS = [ # MUST BE CONSISTENT WITH termtable.qml
    'selected',
    'modifiedTimestamp', # row, default
    'id',
    'errorType',
    'disabled',
    'private',
    'sourceLanguage',
    'language',
    'type',
    'context',
    'host',
    #'syntax',
    'regex',
    'phrase',
    'icase',
    'hentai',
    'special',
    'gameId',
    'role',
    'priority',
    'pattern',
    'text',
    'ruby',
    'comment',
    'userName',
    'timestamp',
    'updateUserName',
    'updateTimestamp',
    'updateComment',
  ]
  DEFAULT_SORTING_COLUMN = COLUMNS.index('modifiedTimestamp') # int = 1, the second column

  def __init__(self):
    self.filterSourceLanguage = "" # str
    self.filterLanguage = ""    # str
    self.filterHost = ""        # str
    self.filterTypes = ""       # str
    self.filterColumn = ""      # str
    self._filterText = ""       # unicode
    self._filterRe = None       # compiled re
    self._filterData = None     # [Term]
    self._sortedData = None     # [Term]
    self._duplicateData = None  # [Term]

    self.sortingColumn = self.DEFAULT_SORTING_COLUMN
    self.sortingReverse = False

    self.pageNumber = 1 # starts at 1
    self.pageSize = 50 # read-only, number of items per page, smaller enough to speed up scrolling

    self.duplicate = False # bool

    self.selectionCount = 0 # int, cached

  @memoizedproperty
  def commentDialog(self):
    import commentinput, windows
    parent = windows.top()
    return commentinput.CommentInputDialog(parent)

  def pageIndex(self): return max(0, self.pageSize * (self.pageNumber - 1)) # -> int

  def get(self, row): # int -> QObject
    try:
      ret = self.data[- # Revert the list
        (self.pageIndex() + row +1)]
      if ret:
        ret.init() # this is the only place that the object is initialized
      return ret
    except IndexError: pass

  @property
  def data(self):
    """
    @return  [Term]
    """
    return (self.sortedData if self.sortingReverse or self.sortingColumn != self.DEFAULT_SORTING_COLUMN
        else self.filterData if any((self.filterText, self.filterTypes, self.filterLanguage, self.filterSourceLanguage, self.filterHost))
        else self.duplicateData if self.duplicate else self.sourceData)

  @staticproperty
  def sourceData(): return manager().terms() # -> list not None

  @property
  def duplicateData(self):
    """
    @return  [Term]
    """
    if self._duplicateData is None:
      l = self.sourceData
      if l:
        l = (t for t in l if not t.d.disabled and not t.d.deleted) # filter
        l = sorted(l, key=self._duplicateSortKey)
        dups = []
        lastTerm = None
        found = False
        for t in l:
          if lastTerm is not None and self._equivalent(t, lastTerm):
            if not found:
              dups.append(lastTerm)
              found = True
            dups.append(t)
          elif found:
            found = False
          lastTerm = t
        l = dups
      self._duplicateData = l
    return self._duplicateData
  @duplicateData.setter
  def duplicateData(self, value): self._duplicateData = value

  @staticmethod
  def _duplicateSortKey(t):
    """Used only by duplicateData
    @param  t  Term
    @return  any tuple consistent with _equivalent()
    """
    td = t.d
    return td.pattern, td.language[:2], td.special, t.gameSeries or td.gameItemId, td.type

  @staticmethod
  def _equivalent(x, y):
    """Used only by duplicateData
    @param  x  Term
    @param  y  Term
    @return  bool  if they are duplicate
    """
    xd = x.d
    yd = y.d
    return (xd.pattern == yd.pattern
      and (
        xd.language == 'ja'
        or yd.language == 'ja'
        or xd.language[:2] == yd.language[:2]
      )
      and (
        xd.type == yd.type
        or xd.type in ('name', 'yomi', 'trans', 'input') and yd.type in ('name', 'yomi', 'trans', 'input')
      )
      and not (xd.type == 'yomi' and yd.type == 'name' and yd.language.startswith('zh') and not ja2zh_name_test(xd.pattern))
      and not (yd.type == 'yomi' and xd.type == 'name' and xd.language.startswith('zh') and not ja2zh_name_test(xd.pattern))
      #and xd.text == yd.text
      and (
        not xd.special
        or xd.gameItemId == yd.gameItemId
        or x.gameSeries and x.gameSeries == y.gameSeries
      )
   )

  @property
  def sortedData(self): # -> list not None
    if self._sortedData is None:
      data = (self.filterData if any((self.filterText, self.filterTypes, self.filterLanguage, self.filterSourceLanguage, self.filterHost))
          else self.duplicateData if self.duplicate
          else self.sourceData)
      if not data:
        self._sortedData = []
      elif self.sortingColumn == self.DEFAULT_SORTING_COLUMN:
        if self.sortingReverse:
          self._sortedData = list(reversed(data))
        else:
          self._sortedData = data
      else:
        col = self.COLUMNS[self.sortingColumn]
        self._sortedData = sorted(data,
            key=lambda it:getattr(it.d, col),
            reverse=self.sortingReverse)
    return self._sortedData
  @sortedData.setter
  def sortedData(self, value): self._sortedData = value

  @property
  def filterText(self): return self._filterText
  @filterText.setter
  def filterText(self, value):
    self._filterText = value
    self._filterRe = None
    self._filterData = None
    self._sortedData = None

  @property
  def filterData(self):
    if self._filterData is None:
      data = self.duplicateData if self.duplicate else self.sourceData
      self._filterData = filter(self._searchData, data) if data else []
    return self._filterData
  @filterData.setter
  def filterData(self, value): self._filterData = value

  @property
  def filterRe(self):
    """
    @throw  re exception
    """
    if not self._filterRe and self.filterText:
      self._filterRe = re.compile(self.filterText, re.IGNORECASE|re.DOTALL)
    return self._filterRe

  def _searchData(self, term):
    """
    @param  term  Term
    @return  bool
    """
    td = term.d
    filters = [self.filterText, self.filterHost, self.filterSourceLanguage, self.filterLanguage, self.filterTypes]

    filters.pop()
    if self.filterTypes:
      if td.type not in self.filterTypes:
        return False
      if not any(filters):
        return True

    filters.pop()
    if self.filterLanguage:
      if not td.language.startswith(self.filterLanguage):
        return False
      if not any(filters):
        return True

    filters.pop()
    if self.filterSourceLanguage:
      if not td.sourceLanguage.startswith(self.filterSourceLanguage):
        return False
      if not any(filters):
        return True

    filters.pop()
    if self.filterHost:
      if td.host != self.filterHost:
        return False
      if not any(filters):
        return True

    t = self.filterText
    if not t:
      return False
    dm = manager()
    try:
      q = None # [str] or None
      if self.filterColumn:
        col = self.filterColumn
        if col == 'id':
          try: return int(t) == td.id
          except ValueError: return False
        elif col == 'role':
          return t == td.role
        elif col == 'user':
          q = td.userName,
        elif col == 'game':
          try:
            tid = int(t)
            if tid == td.gameId or tid == term.gameItemId:
              return True
            if len(t) >= 4:
              return False
          except ValueError: pass
          q = term.gameSeries, term.gameName
        #elif col == 'language':
        #  q = td.language, i18n.language_name(td.language)
        #elif col == 'type':
        #  q = td.type, Term.typeName(td.type)
        elif col == 'pattern':
          q = td.pattern,
        elif col == 'text':
          q = td.text,
        elif col == 'ruby':
          q = td.ruby,
        elif col == 'comment':
          q = td.comment, td.updateComment
      else: # search all columns
        if len(t) > 2:
          try:
            tid = int(t)
            if tid and tid == td.id:
              return True
          except ValueError:
            pass
        if len(t) > 1:
          if t[0] == '@':
            t = t[1:]
            rx = re.compile(t, re.IGNORECASE)
            for it in td.userName, td.updateUserName:
              if it and rx.match(it):
                return True
            return False
          if t[0] == '#':
            t = t[1:]
            try:
              tid = int(t)
              if tid == td.gameId or tid == term.gameItemId:
                return True
              if len(t) >= 4:
                return False
            except ValueError: pass

            rx = re.compile(t, re.IGNORECASE)
            it = term.gameSeries or term.gameName
            return bool(it and (t in it or rx.search(it))) # check t in it in case of escape
        q = td.pattern, td.text, td.ruby, td.language, i18n.language_name(td.language), td.userName, td.updateUserName, Term.typeName(td.type), td.comment, td.updateComment, term.gameSeries, term.gameName
      if q:
        rx = self.filterRe
        for it in q:
          if it and (t in it or rx.search(it)): # check t in it in case of escape
            return True
    except Exception, e:
      dwarn(e)
      #message = e.message or "%s" % e
      #growl.warn(message)
    return False

#@QmlObject
class TermModel(QAbstractListModel):
  """Constructed by TermView QML"""

  def __init__(self, parent=None):
    super(TermModel, self).__init__(parent)
    self.setRoleNames(TERM_ROLES)
    d = self.__d = _TermModel()

    for sig in (
        self.filterTypesChanged, #self.filterLanguageChanged, self.filterHostChanged, self.filterTextChanged,
        self.sortingColumnChanged, self.sortingReverseChanged,
        self.pageSizeChanged, self.pageNumberChanged,
        self.duplicateChanged
      ):
      sig.connect(self.reset)

    manager().termsChanged.connect(lambda:
        manager().isTermsEditable() and self.reset())
    manager().termsEditableChanged.connect(lambda t:
        t and self.reset())

  @Slot()
  def refresh(self): self.reset()

  def reset(self):
    d = self.__d
    d.filterData = None
    d.sortedData = None
    d.duplicateData = None
    super(TermModel, self).reset()
    self.countChanged.emit(self.count)
    self.currentCountChanged.emit(self.currentCount)
    self.refreshSelection()

  def rowCount(self, parent=QModelIndex()):
    """@reimp @public"""
    d = self.__d
    totalSize = len(d.data)
    return min(self.__d.pageSize, max(totalSize - d.pageIndex(), 0))

  def data(self, index, role):
    """@reimp @public"""
    if index.isValid():
      row = index.row()
      if row >= 0 and row < self.rowCount():
        if role == TERM_NUM_ROLE:
          return self.__d.pageIndex() + row +1
        elif role == TERM_OBJECT_ROLE:
          return self.__d.get(row)
        elif role == TERM_ID_ROLE:
          obj = self.__d.get(row)
          if obj:
            return obj.d.id

  @Slot(int, result=QObject)
  def get(self, row): return self.__d.get(row)

  countChanged = Signal(int)
  count = Property(int,
      lambda self: len(self.__d.sourceData),
      notify=countChanged)

  currentCountChanged = Signal(int)
  currentCount = Property(int,
      lambda self: len(self.__d.data),
      notify=currentCountChanged)

  def setFilterTypes(self, value):
    if value != self.__d.filterTypes:
      self.__d.filterTypes = value
      d = self.__d
      self.filterTypesChanged.emit(value)
  filterTypesChanged = Signal(str)
  filterTypes = Property(str,
      lambda self: self.__d.filterTypes,
      setFilterTypes,
      notify=filterTypesChanged)

  def setFilterHost(self, value):
    if value != self.__d.filterHost:
      self.__d.filterHost = value
      d = self.__d
      self.filterHostChanged.emit(value)
  filterHostChanged = Signal(str)
  filterHost = Property(str,
      lambda self: self.__d.filterHost,
      setFilterHost,
      notify=filterHostChanged)

  def setFilterLanguage(self, value):
    if value != self.__d.filterLanguage:
      self.__d.filterLanguage = value
      d = self.__d
      self.filterLanguageChanged.emit(value)
  filterLanguageChanged = Signal(str)
  filterLanguage = Property(str,
      lambda self: self.__d.filterLanguage,
      setFilterLanguage,
      notify=filterLanguageChanged)

  def setFilterSourceLanguage(self, value):
    if value != self.__d.filterSourceLanguage:
      self.__d.filterSourceLanguage = value
      d = self.__d
      self.filterSourceLanguageChanged.emit(value)
  filterSourceLanguageChanged = Signal(str)
  filterSourceLanguage = Property(str,
      lambda self: self.__d.filterSourceLanguage,
      setFilterSourceLanguage,
      notify=filterSourceLanguageChanged)

  def setFilterColumn(self, value):
    if value != self.__d.filterColumn:
      self.__d.filterColumn = value
      self.filterColumnChanged.emit(value)
  filterColumnChanged = Signal(str)
  filterColumn = Property(str,
      lambda self: self.__d.filterColumn,
      setFilterColumn,
      notify=filterColumnChanged)

  def setFilterText(self, value):
    if value != self.__d.filterText:
      self.__d.filterText = value
      self.filterTextChanged.emit(value)
  filterTextChanged = Signal(unicode)
  filterText = Property(unicode,
      lambda self: self.__d.filterText,
      setFilterText,
      notify=filterTextChanged)

  def setSortingColumn(self, value):
    if value != self.__d.sortingColumn:
      self.__d.sortingColumn = value
      self.sortingColumnChanged.emit(value)
  sortingColumnChanged = Signal(int)
  sortingColumn = Property(int,
      lambda self: self.__d.sortingColumn,
      setSortingColumn,
      notify=sortingColumnChanged)

  def setSortingReverse(self, value):
    if value != self.__d.sortingReverse:
      self.__d.sortingReverse = value
      self.sortingReverseChanged.emit(value)
  sortingReverseChanged = Signal(bool)
  sortingReverse = Property(bool,
      lambda self: self.__d.sortingReverse,
      setSortingReverse,
      notify=sortingReverseChanged)

  selectionCountChanged = Signal(int)
  selectionCount = Property(int,
      lambda self: self.__d.selectionCount,
      notify=selectionCountChanged)

  def setPageNumber(self, value):
    if value != self.__d.pageNumber:
      self.__d.pageNumber = value
      self.pageNumberChanged.emit(value)
  pageNumberChanged = Signal(int)
  pageNumber = Property(int,
      lambda self: self.__d.pageNumber,
      setPageNumber,
      notify=pageNumberChanged)

  def setPageSize(self, value):
    if value != self.__d.pageSizeumber:
      self.__d.pageSize = value
      self.pageSizeChanged.emit(value)
  pageSizeChanged = Signal(int)
  pageSize = Property(int,
      lambda self: self.__d.pageSize,
      #setPageSize, # not used
      notify=pageSizeChanged)

  def setDuplicate(self, value):
    if value != self.__d.duplicate:
      self.__d.duplicate = value
      self.duplicateChanged.emit(value)
  duplicateChanged = Signal(bool) # only display duplicate items
  duplicate = Property(bool,
      lambda self: self.__d.duplicate,
      setDuplicate,
      notify=duplicateChanged)

  @Slot()
  def refreshSelection(self):
    #self.__d.updateSelectionCount()

    d = self.__d
    count = 0
    for c in d.sourceData:
      if c.d.selected:
        count += 1
    if count != d.selectionCount:
      d.selectionCount = count
      self.selectionCountChanged.emit(count)

  @Slot()
  def clearSelection(self): # set selected = False
    d = self.__d
    if d.selectionCount:
      for c in d.sourceData:
        if c.d.selected:
          c.selected = False
      d.selectionCount = 0
      self.selectionCountChanged.emit(0)

  @Slot()
  def deleteSelection(self): # delete selected entries
    d = self.__d
    if d.selectionCount and netman.manager().isOnline():
      comment = prompt.getDeleteSelectionComment(d.selectionCount)
      if comment:
        manager().deleteSelectedTerms(updateComment=comment)

  @Slot()
  def enableSelection(self): # delete selected entries
    d = self.__d
    if d.selectionCount and netman.manager().isOnline():
      comment = prompt.getEnableSelectionComment(d.selectionCount)
      if comment:
        manager().updateSelectedTermsEnabled(True, updateComment=comment)

  @Slot()
  def disableSelection(self): # delete selected entries
    d = self.__d
    if d.selectionCount and netman.manager().isOnline():
      comment = prompt.getDisableSelectionComment(d.selectionCount)
      if comment:
        manager().updateSelectedTermsEnabled(False, updateComment=comment)

  @Slot()
  def commentSelection(self): # delete selected entries
    d = self.__d
    if d.selectionCount and netman.manager().isOnline():
      ok, comment, opt = d.commentDialog.get()
      if ok and comment:
        manager().commentSelectedTerms(
          value=comment,
          type=opt['type'],
          append=opt['method'] == 'append',
        )

## Comment model ##

COMMENT_OBJECT_ROLE = Qt.UserRole
COMMENT_NUM_ROLE = Qt.UserRole + 1
COMMENT_ROLES = {
  COMMENT_OBJECT_ROLE: 'object', # Comment, object
  COMMENT_NUM_ROLE: 'number', # int, 番号
}
@Q_Q
class _CommentModel(object):
  COLUMNS = [ # MUST BE CONSISTENT WITH subtable.qml
    'selected',
    'modifiedTimestamp', # row
    'disabled',
    'type',
    'language',
    'locked',
    'likeCount',
    'dislikeCount',
    'text',
    'context',
    'contextSize',
    'gameId',
    'comment',
    'userName',
    'timestamp',
    'updateUserName',
    'updateTimestamp',
    'updateComment',
  ]
  DEFAULT_SORTING_COLUMN = COLUMNS.index('modifiedTimestamp') # int = 1, the second column

  def __init__(self, q):
    self._dirty = False  # bool
    self._filterText = "" # unicode
    self._filterRe = None # compiled re
    self._filterData = None # [Comment]
    self._sourceData = None # [Comment]
    self._sortedData = None # [Comment]
    self._duplicateData = None # [Comment]
    self.md5 = "" # str
    self._gameId = 0
    self.sortingReverse = False
    self.sortingColumn = self.DEFAULT_SORTING_COLUMN

    self.pageNumber = 1 # starts at 1
    self.pageSize = 100 # read-only, number of items per page, smaller enough to speed up scrolling

    self.selectionCount = 0 # int, cached

    self.duplicate = False # bool

    q.gameMd5Changed.connect(self._invalidate)

    for sig in q.filterTextChanged, q.sortingColumnChanged, q.sortingReverseChanged, q.pageSizeChanged, q.pageNumberChanged, q.duplicateChanged:
      sig.connect(self._refresh)

    dm = manager()
    dm.commentsChanged.connect(lambda md5:
      md5 == self.md5 and self._invalidate())
    dm.commentAdded.connect(self._addComment)
    dm.commentRemoved.connect(self._removeComment)
    #dm.aboutToExportComments.connect(self._save)

    QCoreApplication.instance().aboutToQuit.connect(self._save)

  @memoizedproperty
  def commentDialog(self):
    import commentinput, windows
    parent = windows.top()
    return commentinput.CommentInputDialog(parent)

  def pageIndex(self): return max(0, self.pageSize * (self.pageNumber - 1)) # -> int

  # @Slot(int, result=QObject)
  def get(self, row):
    try:
      ret = self.data[- # Revert the list
        (self.pageIndex() + row +1)]
      if ret:
        ret.init()
      return ret
    except IndexError: pass

  def _addComment(self, c):
    try:
      if c.d.gameId == self.gameId:
        self.sourceData.append(c)
        self._refresh()
    except ValueError: pass

  def _removeComment(self, c):
    try:
      #if c.gameId == self.gameId:
      # As the comment could has different gameId but the same itemId
      self.sourceData.remove(c)
      self._refresh()
    except ValueError: pass

  def _invalidate(self):
    self._sourceData = None
    self._refresh()

  def _refresh(self):
    self._filterData = None
    self._sortedData = None
    self._duplicateData = None
    q = self.q
    q.reset()
    q.countChanged.emit(q.count)
    q.currentCountChanged.emit(q.currentCount)
    q.refreshSelection()

  @property
  def data(self):
    """
    @return  [Comment]
    """
    return self.sortedData if self.sortingColumn != self.DEFAULT_SORTING_COLUMN or self.sortingReverse else self.filterData if self.filterText else self.duplicateData if self.duplicate else self.sourceData

  @property
  def duplicateData(self):
    """
    @return  [Comment]
    """
    if self._duplicateData is None:
      l = self.sourceData
      if l:
        l = (c for c in l if not c.d.disabled and not c.d.deleted) # filter
        l = sorted(l, key=self._duplicateSortKey)
        dups = []
        lastComment = None
        found = False
        for c in l:
          if lastComment is not None and self._equivalent(c, lastComment):
            if not found:
              dups.append(lastComment)
              found = True
            dups.append(c)
          elif found:
            found = False
          lastComment = c
        l = dups
      self._duplicateData = l
    return self._duplicateData
  @duplicateData.setter
  def duplicateData(self, value): self._duplicateData = value

  @staticmethod
  def _duplicateSortKey(c):
    """Used only by duplicateData
    @param  t  Comment
    @return  any tuple consistent with _equivalent()
    """
    cd = c.d
    return cd.text, cd.hash, cd.language[:2], cd.type

  @staticmethod
  def _equivalent(x, y):
    """Used only by duplicateData
    @param  x  Comment
    @param  y  Comment
    @return  bool  if they are duplicate
    """
    xd = x.d
    yd = y.d
    return (
        xd.hash == yd.hash and
        xd.type == yd.type and
        xd.language[:2] == yd.language[:2] and
        xd.text == yd.text)

  @property
  def sortedData(self): # -> list not None
    if self._sortedData is None:
      data = self.filterData if self.filterText else self.duplicateData if self.duplicate else self.sourceData
      if not data:
        self._sortedData = []
      #elif not self.sortingColumn == self.DEFAULT_SORTING_COLUMN:
        #if self.sortingReverse:
          #self._sortedData = list(reversed(data))
        #else:
          #self._sortedData = data
      else:
        col = self.COLUMNS[self.sortingColumn]
        self._sortedData = sorted(data,
            key=lambda it:getattr(it.d, col),
            reverse=self.sortingReverse)
    return self._sortedData
  @sortedData.setter
  def sortedData(self, value): self._sortedData = value

  @property
  def gameId(self):
    if not self._gameId and self.md5:
      self._gameId = manager().queryGameId(self.md5) or 0
    return self._gameId

  @gameId.setter
  def gameId(self, val): self._gameId = val

  def _saveLater(self):
    try: self._saveTimer.start()
    except AttributeError:
      t = self._saveTimer = QTimer(self.q)
      t.setInterval(90 * 1000) # in 1.5 minute
      t.setSingleShot(True)
      t.timeout.connect(self._save)
      t.start()

  def _save(self):
    if not self.md5 or not self._dirty:
      return
    if self.md5 == manager().currentGameMd5():
      self._dirty = False
      return
    xmlfile = rc.comments_xml_path(md5=self.md5)
    if not self.sourceData:
      if os.path.exists(xmlfile):
        try: os.path.remove(xmlfile)
        except Exception, e: dwarn(e)
      self._dirty = False
      return
    if manager().savingComments():
      self._saveLater()
    else:
      ok = rc.jinja_template_write(xmlfile, 'xml/comments',
        now=datetime.now(),
        comments=(it.d for it in self.sourceData),
      )
      if ok:
        dprint("pass: xml = %s" % xmlfile)
      else:
        dwarn("failed: xml = %s" % xmlfile)
      self._dirty = False

  @property
  def sourceData(self): # -> list not None
    if self._sourceData is None:
      CommentModel.locked = True
      l = manager().queryComments(md5=self.md5)
      CommentModel.locked = False
      if l: # Make a copy of l
        self._sourceData = sorted(l, key=operator.attrgetter('modifiedTimestamp'))
        #growl.msg(my.tr("Found {0} comments").format(len(l)))
      else:
        self._sourceData = []
        #growl.msg(my.tr("No user-contributed subtitles found"))
    return self._sourceData
  @sourceData.setter
  def sourceData(self, value): self._sourceData = value

  def _updateSourceData(self):
    growl.msg(my.tr("Reload user-contributed comments"))
    l = manager().queryComments(md5=self.md5, online=True)
    if l: # Make a copy of l
      self._sourceData = sorted(l, key=operator.attrgetter('modifiedTimestamp'))
      self._dirty = True
      self._save()
      self._refresh()
      growl.msg(my.tr("Found {0} comments").format(len(l)))
    else:
      growl.msg(my.tr("No user-contributed subtitles found"))

  def confirmUpdate(self):
    dm = manager()
    g = dm.queryGame(md5=self.md5)
    if prompt.confirmUpdateComments(g):
      if g:
        g.commentsUpdateTime = skdatetime.current_unixtime()
      skevents.runlater(dm.submitDirtyComments, 200)
      skevents.runlater(self._updateSourceData, 500)

      # Secretly update game references
      #gameId = dm.queryGameId(self.md5)
      #if gameId:
      #  skevents.runlater(partial(
      #      dm.updateReferences, gameId),
      #      1000)

  @property
  def filterText(self): return self._filterText
  @filterText.setter
  def filterText(self, value):
    self._filterText = value
    self._filterRe = None
    self._filterData = None

  @property
  def filterData(self):
    if self._filterData is None:
      data = self.duplicateData if self.duplicate else self.sourceData
      self._filterData = filter(self._searchData, data) if data else []
    return self._filterData
  @filterData.setter
  def filterData(self, value): self._filterData = value

  @property
  def filterRe(self):
    """
    @throw  re exception
    """
    if not self._filterRe and self.filterText:
      self._filterRe = re.compile(self.filterText, re.IGNORECASE|re.DOTALL)
    return self._filterRe

  def _searchData(self, c):
    """
    @param  c  Comment
    @return  bool
    """
    t = self.filterText
    if not t:
      return False
    dm = manager()
    cd = c.d # Performance reasion
    try:
      if len(t) > 1:
        if t[0] == '@':
          t = t[1:]
          rx = re.compile(t, re.IGNORECASE)
          for it in cd.userName, cd.updateUserName:
            if it and rx.match(it):
              return True
          return False
        if t[0] == '#':
          t = t[1:]
          if t == str(cd.gameId):
            return True
          rx = re.compile(t, re.IGNORECASE)
          it = dm.queryGameName(id=cd.gameId)
          return bool(it and rx.search(it))
      rx = self.filterRe
      for it in cd.text, cd.context, i18n.language_name(cd.language), cd.userName, cd.updateUserName, Comment.typeName(cd.type), cd.comment, cd.updateComment, dm.queryGameName(id=cd.gameId):
        if it and rx.search(it):
          return True
    except Exception, e:
      dwarn(e)
      #message = e.message or "%s" % e
      #growl.warn(message)
    return False

  def deleteSelectedItems(self, updateComment='', append=True):
    """
    @param* updateComment  unicode
    @param* append  bool
    """
    user = manager().user()
    userId = user.id
    if not userId:
      return
    data = list(self.sourceData) # back up source data so that it won't change after deletion
    if not data:
      return

    userLevel = user.commentLevel

    count = 0

    for c in data:
      cd = c.d
      if cd.selected and not cd.deleted:
        if not ( # the same as canEdit permission in qml
          userId == ADMIN_USER_ID or
          cd.userId == userId and not cd.protected or
          cd.userId == GUEST_USER_ID and userLevel > 0):
          growl.warn('<br/>'.join((
            my.tr("Editing other's entry is not allowed"),
            tr_("User") + ": " + cd.userName,
            tr_("Text") + ": " + cd.text,
          )))
          continue
        count += 1
        if updateComment:
          c.updateComment = "%s // %s" % (updateComment, cd.updateComment) if (append and
            cd.updateComment and cd.updateComment != updateComment and not cd.updateComment.startswith(updateComment + ' //')
          ) else updateComment
        c.deleted = True
        #if c.parent():
        #  skevents.runlater(partial(c.setParent, None), 120000) # after 2 min

    if count:
      #d.terms = [t for t in d.terms if not (t.d.selected and t.d.deleted)]
      #if d._sortedTerms:
      #  d._sortedTerms = [t for t in d._sortedTerms if not (t.d.selected and t.d.deleted)]

      #d.invalidateTerms()
      #d.touchTerms()

      growl.msg(my.tr("{0} items updated").format(count))

  def updateSelectedItemsEnabled(self, value, updateComment='', append=True):
    """
    @param  value  bool
    @param* updateComment  unicode
    @param* append  bool
    """
    user = manager().user()
    userId = user.id
    if not userId:
      return
    data = self.sourceData
    if not data:
      return

    userLevel = user.commentLevel
    userAccess = []
    if user.access:
        userAccessMass = user.access.split(',')
        for a in userAccessMass:
            userAccess.append(a)
    
    now = skdatetime.current_unixtime()

    count = 0
    for c in data:
      cd = c.d
      if cd.selected and cd.disabled == value:
        if not ( # the same as canImprove permission in qml
          userId != GUEST_USER_ID and not cd.locked or
          (str(cd.userId) + ":" + str(cd.itemId)) in userAccess or
          cd.userId == userId and not cd.protected or
          cd.userId == GUEST_USER_ID and userLevel > 0):
          growl.warn('<br/>'.join((
            my.tr("Editing other's entry is not allowed"),
            tr_("User") + ": " + cd.userName,
            tr_("Text") + ": " + cd.text,
          )))
          continue
        count += 1
        c.updateUserId = userId
        c.updateTimestamp = now
        c.disabled = not value
        if updateComment:
          c.updateComment = "%s // %s" % (updateComment, cd.updateComment) if (append and
            cd.updateComment and cd.updateComment != updateComment and not cd.updateComment.startswith(updateComment + ' //')
          ) else updateComment

    if count:
      growl.msg(my.tr("{0} items updated").format(count))

  def commentSelectedItems(self, value, type='comment', append=True):
    """
    @param  value  unicode
    @param* type  'comment' or 'updateComment'
    @param* append  bool
    """
    user = manager().user()
    userId = user.id
    if not userId:
      return
    data = self.sourceData
    if not data:
      return

    userLevel = user.commentLevel

    now = skdatetime.current_unixtime()

    count = 0

    for c in data:
      cd = c.d
      if cd.selected:
        if type == 'comment':
          if not ( # the same as canEdit permission in qml
            userId == ADMIN_USER_ID or
            cd.userId == userId and not cd.protected or
            cd.userId == GUEST_USER_ID and userLevel > 0):
            growl.warn('<br/>'.join((
              my.tr("Editing other's entry is not allowed"),
              tr_("User") + ": " + cd.userName,
              tr_("Text") + ": " + cd.text,
            )))
            continue
          count += 1
          c.updateUserId = userId
          c.updateTimestamp = now
          c.comment = "%s // %s" % (value, cd.comment) if (append and
            cd.comment and cd.comment != value and not cd.comment.startswith(value + ' //')
          ) else value

        elif type == 'updateComment':
          if not ( # the same as canImprove permission in qml
            userId != GUEST_USER_ID and not cd.locked or
            cd.userId == userId and not cd.protected or
            cd.userId == GUEST_USER_ID and userLevel > 0):
            growl.warn('<br/>'.join((
              my.tr("Editing other's entry is not allowed"),
              tr_("User") + ": " + cd.userName,
              tr_("Text") + ": " + cd.text,
            )))
            continue
          count += 1
          c.updateUserId = userId
          c.updateTimestamp = now
          c.updateComment = "%s // %s" % (value, cd.updateComment) if (append and
            cd.updateComment and cd.updateComment != value and not cd.updateComment.startswith(value + ' //')
          ) else value

    if count:
      growl.msg(my.tr("{0} items updated").format(count))

#@QmlObject
class CommentModel(QAbstractListModel):
  """Constructed by SubtitleView QML"""

  locked = False # whether the model is loading references

  def __init__(self, parent=None):
    super(CommentModel, self).__init__(parent)
    self.setRoleNames(COMMENT_ROLES)
    self.__d = _CommentModel(self)

  def rowCount(self, parent=QModelIndex()):
    """@reimp @public"""
    d = self.__d
    totalSize = len(d.data)
    return min(self.__d.pageSize, max(totalSize - d.pageIndex(), 0))

  def data(self, index, role):
    """@reimp @public"""
    if index.isValid():
      row = index.row()
      if row >= 0 and row < self.rowCount():
        if role == COMMENT_NUM_ROLE:
          return self.__d.pageIndex() + row +1
        elif role == COMMENT_OBJECT_ROLE:
          return self.__d.get(row)

  @Slot(int, result=QObject)
  def get(self, row): return self.__d.get(row)

  @Slot()
  def update(self):
    md5 = self.__d.md5
    if not md5:
      return
    if md5 == manager().currentGameMd5():
      import textman
      textman.manager().confirmReload()
    elif netman.manager().isOnline():
      self.__d.confirmUpdate()
    else:
      growl.warn(my.tr("Cannot connect to the Internet"))

  @Slot()
  def export_(self):
    manager().exportComments(it.d for it in self.__d.sourceData)
    #md5 = self.__d.md5
    #if md5:
    #  manager().exportComments(md5=md5)

  @Slot()
  def showChart(self):
    d = self.__d
    main.manager().showCommentChart(d.sourceData, d.md5)

  countChanged = Signal(int)
  count = Property(int,
      lambda self: len(self.__d.sourceData),
      notify=countChanged)

  gameMd5Changed = Signal(str)
  def setGameMd5(self, v):
    d = self.__d
    if d.md5 != v:
      d.md5 = v
      d.gameId = 0
      self.gameMd5Changed.emit(v)
  gameMd5 = Property(str,
      lambda self: self.__d.md5,
      setGameMd5,
      notify=gameMd5Changed)

  currentCountChanged = Signal(int)
  currentCount = Property(int,
      lambda self: len(self.__d.data),
      notify=currentCountChanged)

  def setFilterText(self, value):
    if value != self.__d.filterText:
      self.__d.filterText = value
      self.filterTextChanged.emit(value)
  filterTextChanged = Signal(unicode)
  filterText = Property(unicode,
      lambda self: self.__d.filterText,
      setFilterText,
      notify=filterTextChanged)

  def setSortingColumn(self, value):
    if value != self.__d.sortingColumn:
      self.__d.sortingColumn = value
      self.sortingColumnChanged.emit(value)
  sortingColumnChanged = Signal(int)
  sortingColumn = Property(int,
      lambda self: self.__d.sortingColumn,
      setSortingColumn,
      notify=sortingColumnChanged)

  def setSortingReverse(self, value):
    if value != self.__d.sortingReverse:
      self.__d.sortingReverse = value
      self.sortingReverseChanged.emit(value)
  sortingReverseChanged = Signal(bool)
  sortingReverse = Property(bool,
      lambda self: self.__d.sortingReverse,
      setSortingReverse,
      notify=sortingReverseChanged)

  selectionCountChanged = Signal(int)
  selectionCount = Property(int,
      lambda self: self.__d.selectionCount,
      notify=selectionCountChanged)

  def setPageNumber(self, value):
    if value != self.__d.pageNumber:
      self.__d.pageNumber = value
      self.pageNumberChanged.emit(value)
  pageNumberChanged = Signal(int)
  pageNumber = Property(int,
      lambda self: self.__d.pageNumber,
      setPageNumber,
      notify=pageNumberChanged)

  def setPageSize(self, value):
    if value != self.__d.pageSize:
      self.__d.pageSize = value
      self.pageSizeChanged.emit(value)
  pageSizeChanged = Signal(int)
  pageSize = Property(int,
      lambda self: self.__d.pageSize,
      #setPageSize, # not used
      notify=pageSizeChanged)

  def setDuplicate(self, value):
    if value != self.__d.duplicate:
      self.__d.duplicate = value
      self.duplicateChanged.emit(value)
  duplicateChanged = Signal(bool) # only display duplicate items
  duplicate = Property(bool,
      lambda self: self.__d.duplicate,
      setDuplicate,
      notify=duplicateChanged)

  @Slot()
  def refreshSelection(self):
    #self.__d.updateSelectionCount()

    d = self.__d
    count = 0
    for t in d.sourceData:
      if t.d.selected:
        count += 1
    if count != d.selectionCount:
      d.selectionCount = count
      self.selectionCountChanged.emit(count)

  @Slot()
  def clearSelection(self): # set selected = False
    d = self.__d
    if d.selectionCount:
      for t in d.sourceData:
        if t.d.selected:
          t.selected = False
      d.selectionCount = 0
      self.selectionCountChanged.emit(0)

  @Slot()
  def deleteSelection(self): # delete selected entries
    d = self.__d
    if d.selectionCount and netman.manager().isOnline():
      comment = prompt.getDeleteSelectionComment(d.selectionCount)
      if comment:
        d.deleteSelectedItems(updateComment=comment)

  @Slot()
  def enableSelection(self): # delete selected entries
    d = self.__d
    if d.selectionCount and netman.manager().isOnline():
      comment = prompt.getEnableSelectionComment(d.selectionCount)
      if comment:
        d.updateSelectedItemsEnabled(True, updateComment=comment)

  @Slot()
  def disableSelection(self): # delete selected entries
    d = self.__d
    if d.selectionCount and netman.manager().isOnline():
      comment = prompt.getDisableSelectionComment(d.selectionCount)
      if comment:
        d.updateSelectedItemsEnabled(False, updateComment=comment)

  @Slot()
  def commentSelection(self): # delete selected entries
    d = self.__d
    if d.selectionCount and netman.manager().isOnline():
      ok, comment, opt = d.commentDialog.get()
      if ok and comment:
        d.commentSelectedItems(
          value=comment,
          type=opt['type'],
          append=opt['method'] == 'append',
        )

## Reference  model ##

REF_OBJECT_ROLE = Qt.UserRole
REF_NUM_ROLE = Qt.UserRole +1
REF_ROLES = {
  REF_OBJECT_ROLE: 'object', # Comment, object
  REF_NUM_ROLE: 'number', # int, 番号
}
@Q_Q
class _ReferenceModel(object):
  COLUMNS = [ # MUST BE CONSISTENT WITH reftable.qml
    'modifiedTimestamp', # row
    'disabled',
    'gameId',
    'itemId',
    'type',
    'title',
    'brand',
    'date',
    'comment',
    'userName',
    'timestamp',
    'updateUserName',
    'updateTimestamp',
    'updateComment',
  ]

  def __init__(self, q):
    self._dirty = False  # bool
    self._filterText = "" # unicode
    self._filterRe = None # compiled re
    self._filterData = None # [Reference] or None
    self._sourceData = None # [Reference] or None
    self._sortedData = None
    #self.md5 = "" # str
    #self._gameId = 0
    self.gameId = 0
    self.sortingReverse = False
    self.sortingColumn = 0

    q.gameIdChanged.connect(self._invalidate)

    for sig in q.filterTextChanged, q.sortingColumnChanged, q.sortingReverseChanged:
      sig.connect(self.refresh)

    dm = manager()
    dm.referencesTouched.connect(self.touch)

    dm.referencesChanged.connect(lambda gameId:
      gameId == self.gameId and self._invalidate())

    QCoreApplication.instance().aboutToQuit.connect(self._save)

  def touch(self):
    self._dirty = True
    self._saveLater()

  #def _addComment(self, c):
  #  try:
  #    if c.d.gameId == self.gameId:
  #      self.sourceData.append(c)
  #      self.refresh()
  #  except ValueError: pass

  #def _removeComment(self, c):
  #  try:
  #    if c.d.gameId == self.gameId:
  #      self.sourceData.remove(c)
  #      self.refresh()
  #  except ValueError: pass

  def _invalidate(self):
    self._sourceData = None
    self.refresh()

  def refresh(self):
    self._filterData = None
    self._sortedData = None
    q = self.q
    q.reset()
    q.countChanged.emit(q.count)
    q.currentCountChanged.emit(q.currentCount)

    q.trailersItemChanged.emit(q.trailersItem)
    q.scapeItemChanged.emit(q.scapeItem)
    q.holysealItemChanged.emit(q.holysealItem)
    q.getchuItemChanged.emit(q.getchuItem)
    q.gyuttoItemChanged.emit(q.gyuttoItem)
    q.digiketItemChanged.emit(q.digiketItem)
    q.melonItemChanged.emit(q.melonItem)
    q.dmmItemChanged.emit(q.dmmItem)
    q.amazonItemChanged.emit(q.amazonItem)
    q.dlsiteItemChanged.emit(q.dlsiteItem)
    q.freemItemChanged.emit(q.freemItem)
    q.steamItemChanged.emit(q.steamItem)

    self.invalidateActiveItem()

  def invalidateActiveItem(self):
    q = self.q
    q.activeItemChanged.emit(q.activeItem)

  @property
  def data(self):
    """
    @return  [Reference]
    """
    return self.sortedData if self.sortingColumn or self.sortingReverse else self.filterData if self.filterText else self.sourceData

  @property
  def sortedData(self):
    if self._sortedData is None:
      data = self.filterData if self.filterText else self.sourceData
      if not self.sortingColumn:
        if self.sortingReverse:
          self._sortedData = list(reversed(data))
        else:
          self._sortedData = data
      else:
        col = self.COLUMNS[self.sortingColumn]
        self._sortedData = sorted(data,
            key=operator.attrgetter(col),
            reverse=self.sortingReverse)
    return self._sortedData
  @sortedData.setter
  def sortedData(self, value): self._sortedData = value

  #@property
  #def gameId(self):
  #  if not self._gameId and self.md5:
  #    self._gameId = manager().queryGameId(self.md5) or 0
  #  return self._gameId

  #@gameId.setter
  #def gameId(self, val): self._gameId = val

  def _saveLater(self):
    try: self._saveTimer.start()
    except AttributeError:
      t = self._saveTimer = QTimer(self.q)
      t.setInterval(90 * 1000) # in 1.5 minute
      t.setSingleShot(True)
      t.timeout.connect(self._save)
      t.start()

  def _save(self):
    if not self.gameId or not self._dirty:
      return
    manager().saveReferences(self.sourceData, self.gameId)
    self._dirty = False

  @property
  def sourceData(self): # -> list not None
    if self._sourceData is None:
      #CommentModel.locked = True
      l = manager().queryReferences(gameId=self.gameId, online=False)
      #CommentModel.locked = False
      if l:
        l.sort(key=operator.attrgetter('modifiedTimestamp'))
        self._sourceData =l
        #growl.msg(my.tr("Found {0} comments").format(len(l)))
      else:
        self._sourceData = []
        #growl.msg(my.tr("No user-contributed subtitles found"))
    return self._sourceData
  @sourceData.setter
  def sourceData(self, value): self._sourceData = value

  def _updateSourceData(self):
    growl.msg(my.tr("Update game information"))
    l = manager().queryReferences(gameId=self.gameId, online=True)
    if l:
      l.sort(key=operator.attrgetter('modifiedTimestamp'))
      self._sourceData = l
      self._dirty = True
      self._save()
      self.refresh()
      growl.msg(my.tr("Found {0} references").format(len(l)))
    else:
      growl.msg(my.tr("No game references found"))

  def confirmUpdate(self):
    g = manager().queryGame(id=self.gameId)
    if prompt.confirmUpdateRefs(g):
      if g:
        g.refsUpdateTime = skdatetime.current_unixtime()
      skevents.runlater(manager().submitDirtyReferences, 200)
      skevents.runlater(self._updateSourceData, 500)

  @property
  def filterText(self): return self._filterText
  @filterText.setter
  def filterText(self, value):
    self._filterText = value
    self._filterRe = None
    self._filterData = None

  @property
  def filterData(self):
    if self._filterData is None:
      self._filterData = filter(self._searchData, self.sourceData)
    return self._filterData
  @filterData.setter
  def filterData(self, value): self._filterData = value

  @property
  def filterRe(self):
    """
    @throw  re exception
    """
    if not self._filterRe and self.filterText:
      self._filterRe = re.compile(self.filterText, re.IGNORECASE|re.DOTALL)
    return self._filterRe

  def _searchData(self, r):
    """
    @param  r  Reference
    @return  bool
    """
    t = self.filterText
    if not t:
      return False
    dm = manager()
    rd = r.d
    try:
      if len(t) > 1:
        if t[0] == '@':
          t = t[1:]
          rx = re.compile(t, re.IGNORECASE)
          for it in r.userName, r.updateUserName:
            if it and rx.match(it):
              return True
          return False
        if t[0] == '#':
          t = t[1:]
          if t == str(rd.gameId):
            return True
          if t == str(rd.itemId):
            return True
          rx = re.compile(t, re.IGNORECASE)
          it = dm.queryGameName(id=rd.gameId)
          if bool(it and rx.search(it)):
            return True
          it = dm.queryItemName(id=rd.itemId)
          return bool(it and rx.search(it))
      rx = self.filterRe
      for it in rd.title, rd.brand, r.userName, r.updateUserName, rd.comment, rd.updateComment, dm.queryGameFileName(id=rd.gameId):
        if it and rx.search(it):
          return True
    except Exception, e:
      dwarn(e)
      #message = e.message or "%s" % e
      #growl.warn(message)
    return False

  def findItem(self, type=None):
    if type:
      for it in self.sourceData:
        if it.type == type and not it.disabled and not it.deleted:
          return it

#@QmlObject
class ReferenceModel(QAbstractListModel):
  """Constructed by ReferenceView QML"""

  def __init__(self, parent=None):
    super(ReferenceModel, self).__init__(parent)
    self.setRoleNames(REF_ROLES)
    self.__d = _ReferenceModel(self)

  def rowCount(self, parent=QModelIndex()):
    """@reimp @public"""
    return len(self.__d.data)

  def data(self, index, role):
    """@reimp @public"""
    if index.isValid():
      row = index.row()
      if row >= 0 and row < self.rowCount():
        if role == REF_NUM_ROLE:
          return row + 1
        elif role == REF_OBJECT_ROLE:
          return self.get(row)

  @Slot(int, result=QObject)
  def get(self, row):
    # Revert the list
    try: return self.__d.data[-row -1]
    except IndexError: pass

  def activeItem(self):
    for it in self.__d.sourceData:
      if not it.disabled and not it.deleted:
        return it
  activeItemChanged = Signal(QObject)
  activeItem = Property(QObject, activeItem, notify=activeItemChanged)

  ## Properties ##

  #@Slot()
  #def export_(self):
  #  gameId = self.__d.gameId
  #  if gameId:
  #    manager().exportReferences(gameId=gameId)

  #@Slot()
  #def showChart(self):
  #  d = self.__d
  #  main.manager().showReferenceChart(d.sourceData, d.md5)

  steamItemChanged = Signal(QObject)
  steamItem = Property(QObject,
      lambda self: self.__d.findItem(type='steam'),
      notify=steamItemChanged)

  freemItemChanged = Signal(QObject)
  freemItem = Property(QObject,
      lambda self: self.__d.findItem(type='freem'),
      notify=freemItemChanged)

  getchuItemChanged = Signal(QObject)
  getchuItem = Property(QObject,
      lambda self: self.__d.findItem(type='getchu'),
      notify=getchuItemChanged)

  gyuttoItemChanged = Signal(QObject)
  gyuttoItem = Property(QObject,
      lambda self: self.__d.findItem(type='gyutto'),
      notify=gyuttoItemChanged)

  digiketItemChanged = Signal(QObject)
  digiketItem = Property(QObject,
      lambda self: self.__d.findItem(type='digiket'),
      notify=digiketItemChanged)

  melonItemChanged = Signal(QObject)
  melonItem = Property(QObject,
      lambda self: self.__d.findItem(type='melon'),
      notify=melonItemChanged)

  holysealItemChanged = Signal(QObject)
  holysealItem = Property(QObject,
      lambda self: self.__d.findItem(type='holyseal'),
      notify=holysealItemChanged)

  amazonItemChanged = Signal(QObject)
  amazonItem = Property(QObject,
      lambda self: self.__d.findItem(type='amazon'),
      notify=amazonItemChanged)

  dmmItemChanged = Signal(QObject)
  dmmItem = Property(QObject,
      lambda self: self.__d.findItem(type='dmm'),
      notify=dmmItemChanged)

  dlsiteItemChanged = Signal(QObject)
  dlsiteItem = Property(QObject,
      lambda self: self.__d.findItem(type='dlsite'),
      notify=dlsiteItemChanged)

  scapeItemChanged = Signal(QObject)
  scapeItem = Property(QObject,
      lambda self: self.__d.findItem(type='scape'),
      notify=scapeItemChanged)

  trailersItemChanged = Signal(QObject)
  trailersItem = Property(QObject,
      lambda self: self.__d.findItem(type='trailers'),
      notify=trailersItemChanged)

  countChanged = Signal(int)
  count = Property(int,
      lambda self: len(self.__d.sourceData),
      notify=countChanged)

  gameIdChanged = Signal(int)
  def setGameId(self, v):
    d = self.__d
    if d.gameId != v:
      d.gameId = v
      self.gameIdChanged.emit(v)
  gameId = Property(int,
      lambda self: self.__d.gameId,
      setGameId,
      notify=gameIdChanged)

  currentCountChanged = Signal(int)
  currentCount = Property(int,
      lambda self: len(self.__d.data),
      notify=currentCountChanged)

  def setFilterText(self, value):
    if value != self.__d.filterText:
      self.__d.filterText = value
      self.filterTextChanged.emit(value)
  filterTextChanged = Signal(unicode)
  filterText = Property(unicode,
      lambda self: self.__d.filterText,
      setFilterText,
      notify=filterTextChanged)

  def setSortingColumn(self, value):
    if value != self.__d.sortingColumn:
      self.__d.sortingColumn = value
      self.sortingColumnChanged.emit(value)
  sortingColumnChanged = Signal(int)
  sortingColumn = Property(int,
      lambda self: self.__d.sortingColumn,
      setSortingColumn,
      notify=sortingColumnChanged)

  def setSortingReverse(self, value):
    if value != self.__d.sortingReverse:
      self.__d.sortingReverse = value
      self.sortingReverseChanged.emit(value)
  sortingReverseChanged = Signal(bool)
  sortingReverse = Property(bool,
      lambda self: self.__d.sortingReverse,
      setSortingReverse,
      notify=sortingReverseChanged)

  ## Slots ##

  @Slot()
  def update(self):
    if netman.manager().isOnline():
      self.__d.confirmUpdate()
    else:
      growl.warn(my.tr("Cannot connect to the Internet"))

  @Slot(QObject)
  def submitItem(self, ref):
    """
    @param  ref  Reference
    """
    dm = manager()
    user = dm.user()
    if not user.name:
      return
    md5 = dm.queryGameMd5(ref.gameId)
    if not md5:
      return
    d = self.__d

    # Avoid duplicated items
    for it in d.sourceData:
      if (it.type == ref.type and it.key == ref.key and
          not it.deleted and not it.disabled):
        dwarn("duplicated")
        t = Reference.typeName(it.type)
        u = _get_user_name(it.userId)
        info = "@%s: %s" % (u, t)
        growl.notify('<br/>'.join((
            my.tr("Reference already existed"),
            info)))
        return

    # Enforce one site one reference
    for it in d.sourceData:
      if (#it.id != ref.id and
          it.gameId == ref.gameId and
          it.type == ref.type and
          not it.deleted and not it.disabled):
        it.disabled = True
    d.sourceData.append(ref)
    dm.submitReference(ref)
    d.refresh()
    d.touch()

  @Slot(QObject)
  def removeItem(self, ref):
    if prompt.confirmDeleteRef(ref):
      #manager().removeReference(ref)
      ref.deleted = True
      d = self.__d
      try:
        d.sourceData.remove(ref)
        d.refresh()
      except ValueError: pass
      #d.touch()  # already touch

  @Slot(QObject)
  def toggleItemEnabled(self, ref):
    gameId = self.gameId
    if not gameId:
      return
    userId = manager().user().id
    if not userId:
      return
    comment = ""
    if userId != ref.userId:
      comment = prompt.getUpdateComment(ref.updateComment)
      if not comment:
        return

    d = self.__d
    # Enforce one site one reference
    if ref.disabled:
      for it in d.sourceData:
        if (it.id != ref.id and
            it.gameId == ref.gameId and
            it.type == ref.type and
            not it.deleted and not it.disabled):
          it.disabled = True

    ref.disabled = not ref.disabled
    ref.updateUserId = userId
    ref.updateTimestamp = skdatetime.current_unixtime()
    if comment:
      ref.updateComment = comment

    d.invalidateActiveItem()

## Manager ##

@Q_Q
class _DataManager(object):
  def __init__(self):
    # Game texts of current game, indexed by hash, nullable
    self.contexts = {}    # {str:str}, not None

    # Comments of current game, indexed by hash, nullable
    self.comments = {}                # {long hash:[Comment]}, not None
    self.comments2 = {}               # {long hash:[Comment]}, not None
    self._commentsDirty = False       # bool
    self.dirtyComments = set()        # set(Comment)
    self.dirtyCommentsLocked = False  # bool
    #self.dirtyCommentsMutex = QMutex()

    # Terms
    self.terms = []                 # [Term], not None
    #self._sortedTerms = None
    self._termsDirty = False
    self.dirtyTerms = set()         # set(Term)
    self.dirtyTermsLocked = False   # bool
    self.updateTermsLocked = False  # bool

    self.termsEditable = False # disable editable by default
    #self.termsInitialized = False # if the terms has initialized

    #self._termTitles = None  # OrderedDict{unicode from:unicode to} or None
    #self._termMacros = None  # {unicode pattern:unicode repl} or None   indexed macros

    # References to modify
    #self._referencesDirty = False    # bool
    self.dirtyReferences = set()      # set(Reference)
    self.dirtyReferencesLocked = False  # bool
    #self.dirtyReferencesMutex = QMutex()

    self.characters = {} # [unicode name: Character} not None
    self._charactersDirty = False       # bool

    # Current game
    self.currentGame = None # class Game
    self.currentGameIds = [] # [long gameId] not None
    self._currentGameObject = None # QObject

    # Game library, which is a list of games indexed by their md5, not null
    self.games = {} # {str:Game}
    self._gamesDirty = False

    self._gameFilesDirty = False
    self.gameFiles = {} # {long id:GameFile}
    self.gameFilesByMd5 = {} # {str md5:GameFile}

    #self._referenceDigestsDirty = False
    #self.referenceDigests = {} # {long itemId:[ReferenceDigest]} not None

    self.gameItems = {} # {long itemId:GameItem} not None

    self._gameInfo = [] # [GameInfo]

    #self.nameItems = [] # [NameItem]

    # Subtitles for the current game
    #self.resetSubtitles()
    self.subtitles = [] # [Subtitle]
    self.subtitleIndex = {} # {long hash:[Subtitle]}
    self.subtitleItemId = 0 # long
    self.subtitleTimestamp = 0 # long


    # Users
    self.users = {} # {long id:UserDigest}

    # Load user profile
    self._loadUser()

  def resetSubtitles(self):
    self.subtitleIndex = {} # {long hash:[Subtitle]}
    self.subtitleItemId = 0 # long
    self.subtitleTimestamp = 0 # long
    self._clearSubtitles()

  def _clearSubtitles(self):
    if self.subtitles:
      l = self.subtitles
      self.subtitles = [] # [Subtitle]
      if l:
        for it in l:
          it.releaseObject()

  def resetCharacters(self):
    self.characters = {'':Character(parent=self.q, ttsEnabled=True)}

  def clearCharacters(self):
    if self.characters:
      for it in self.characters.itervalues():
        if it.parent():
          it.setParent(None)
      self.characters = {}

  def needsPurgeCharacters(self):
    for it in self.characters.itervalues():
      if not (it.ttsEnabled or it.ttsEngine or it.gender or not it.name):
        return True
    return False

  def purgeCharacters(self):
    changed = False
    for it in self.characters.itervalues():
      if not (it.ttsEnabled or it.ttsEngine or it.gender or not it.name):
        if it.parent():
          it.setParent(None)
        changed = True
    if changed:
      self.characters = {k:v
          for k,v in self.characters.iteritems()
          if v.ttsEnabled or v.ttsEngine or v.gender or not v.name}

  def clearTerms(self):
    if self.terms:
      self.terms = []                 # [Term], not None
      #if self.termsInitialized:
      #  for t in self.terms:
      #    if t.isInitialized():
      #      try:
      #        if t.parent():
      #          t.setParent(None) # might raise if QObject has been deleted
      #      except Exception, e:
      #        dwarn(e)
      #self.sortedTerms = None

  #def clearNameItems(self): self.nameItems = [] #; mecabman.manager().clearDictionary()

  #@property
  #def sortedTerms(self):
  #  if self._sortedTerms is None:
  #    if not self.terms:
  #      self._sortedTerms = []
  #    else:
  #      l = (it for it in self.terms if not it.d.disabled and not it.d.deleted) # filtered
  #      l = sorted(l, reverse=True, key=lambda it:
  #            (len(it.d.pattern), it.d.private, it.d.special, it.d.id)) # it.regex  true is applied first
  #      count = len(l)
  #      for index, it in enumerate(l):
  #        it.priority = count - index
  #      self._sortedTerms = l
  #  return self._sortedTerms

  #@sortedTerms.setter
  #def sortedTerms(self, v):
  #  self._sortedTerms = v
  #  self.clearTermTitles()
  #  self.clearTermMacros()

  #@property
  #def termTitles(self):
  #  if self._termTitles is None:
  #    self._termTitles = self._queryTermTitles()
  #  return self._termTitles

  #@termTitles.setter
  #def termTitles(self, v): self._termTitles = v

  #def clearTermTitles(self): self._termTitles = None

  #def _queryTermTitles(self):
  #  """Terms sorted by length and id
  #  @return  OrderedDict{unicode from:unicode to} not None not empty
  #  """
  #  lang = self.user.language
  #  zht = lang == 'zht'
  #  q = termman.manager().filterTerms(self.q.iterTitleTerms(), lang)
  #  l = [] # [long id, unicode pattern, unicode replacement]
  #  ret = OrderedDict({'':''})
  #  for t in q:
  #    td = t.d
  #    pat = td.pattern
  #    repl = td.text
  #    if zht and td.language == 'zhs':
  #      pat = zhs2zht(pat)
  #      if repl: # and self.convertsChinese:
  #        repl = zhs2zht(repl)
  #    l.append((td.id, pat, repl))
  #  l.sort(key=lambda it:
  #      (len(it[1]), it[0]))
  #  for id,pat,repl in l:
  #    ret[pat] = repl
  #  return ret

  # Macros

  #@property
  #def termMacros(self):
  #  if self._termMacros is None:
  #    self._termMacros = self._queryTermMacros()
  #  return self._termMacros

  #def _queryTermMacros(self):
  #  """
  #  @return  {unicode pattern:unicode repl} not None
  #  """
  #  ret = {t.d.pattern:t.d.text for t in
  #    termman.manager().filterTerms(self.q.iterMacroTerms(), self.user.language)}
  #  MAX_COUNT = 1000
  #  for count in xrange(1, MAX_COUNT):
  #    dirty = False
  #    for pattern,text in ret.iteritems(): # not iteritems as I will modify ret
  #      if text and defs.TERM_MACRO_BEGIN in text:
  #        dirty = True
  #        ok = False
  #        for m in termman.RE_MACRO.finditer(text):
  #          macro = m.group(1)
  #          repl = ret.get(macro)
  #          if repl:
  #            text = text.replace("{{%s}}" % macro, repl)
  #            ok = True
  #          else:
  #            dwarn("missing macro", macro, text)
  #            ok = False
  #            break
  #        if ok:
  #          ret[pattern] = text
  #        else:
  #          ret[pattern] = None # delete this pattern
  #    if not dirty:
  #      break
  #  if count == MAX_COUNT - 1:
  #    dwarn("recursive macro definition")
  #  return {k:v for k,v in ret.iteritems() if v is not None}

  #def clearTermMacros(self): self._termMacros = None

  ## User ##

  def _loadUser(self):
    ss  = settings.global_()
    if ss.userName() and ss.userId():
      self.user = User(
        id = ss.userId(),
        name = ss.userName(),
        password = ss.userPassword(),
        language = ss.userLanguage(),
        gender = ss.userGender(),
        homepage = ss.userHomepage(),
        color = ss.userColor(),
        avatar = ss.userAvatar(),
        termLevel = ss.userTermLevel(),
        commentLevel = ss.userCommentLevel(),
      )
    else:
      self.user = GUEST.clone()

  def _saveUser(self):
    ss = settings.global_()
    ss.setUserId(self.user.id)
    ss.setUserName(self.user.name)
    ss.setUserPassword(self.user.password)
    ss.setUserGender(self.user.gender)
    ss.setUserHomepage(self.user.homepage)
    ss.setUserAvatar(self.user.avatar)
    ss.setUserColor(self.user.color)
    ss.setUserTermLevel(self.user.termLevel)
    ss.setUserCommentLevel(self.user.commentLevel)
    ss.setUserAccess(self.user.access)

  def reloadUser(self):
    if not self.user.isLoginable() or self.user.isGuest():
      self.user = GUEST.clone(language=self.user.language)
      self._saveUser()

    # Here, userId is not used, which is not accurate
    if not self.user.isGuest() and netman.manager().isOnline():
      #skevents.runlater(self._updateUser)
      self._updateUser()
    elif self.user.name and self.user.language:
      growl.msg('<br/>'.join((
        my.tr("Sign in as '{0}'").format(self.user.name),
        my.tr("User language is '{0}'").format(i18n.language_name(self.user.language)),
      )))

    self.q.loginChanged.emit(self.user.name, self.user.password)

  def _updateUser(self):
    if not self.user.isLoginable() or not netman.manager().isOnline():
      return
    
    user = netman.manager().queryUser(self.user.name, self.user.password)
    if user:
      #if not user.name:
      #  dwarn("warning: missing user name! Something is wrong here!");
      #if not user.language:
      #  user.language = 'en'
      self.user = user.clone(language=self.user.language)
      self._saveUser()

      growl.msg('<br/>'.join((
        my.tr("Sign in as '{0}'").format(self.user.name),
        my.tr("User language is '{0}'").format(i18n.language_name(self.user.language)),
      )))

    else:
      dwarn("login failed")
      growl.error(my.tr("Sign in failed as '{0}'").format(self.user.name))

  ## Game ##

  @property
  def currentGameObject(self):
    if not self._currentGameObject and self.currentGame:
      self._currentGameObject = GameObject(game=self.currentGame)
    return self._currentGameObject

  @currentGameObject.setter
  def currentGameObject(self, v): self._currentGameObject = v

  @property
  def gameInfo(self):
    if not self._gameInfo:
      self._gameInfo = [GameInfo(itemId=itemId) for itemId in self.gameItems]
    return self._gameInfo

  def containsGameInfo(self, itemId): return itemId in self.gameItems

  def repairGameItems(self):
    for g in self.games.itervalues():
      if self.gameFilesByMd5:
        if g.md5:
          f = self.gameFilesByMd5.get(g.md5)
          if f:
            g.itemId = f.itemId
            g.id = f.id
      if self.gameFiles:
        if g.id:
          f = self.gameFiles.get(g.id)
          if f:
            g.itemId = f.itemId
            #g.md5 = f.md5
    self.touchGames()
    dprint("pass")

  def repairCurrentGame(self):
    g = self.currentGame
    if g:
      if g.md5:
        if self.gameFilesByMd5:
          f = self.gameFilesByMd5.get(g.md5)
          if f:
            g.itemId = f.itemId
            g.id = f.id
      if g.id:
        if self.gameFiles:
          f = self.gameFiles.get(g.id)
          if f:
            g.itemId = f.itemId
            #g.md5 = f.md5
      self.currentGameObject = None
      self.currentGameIds = self.q.querySeriesGameIds(itemId=g.itemId) if g.itemId else [g.id] if g.id else []

  def updateGame(self, game, deleteHook=False, online=True):
    """
    @param[inout]  game  Game  id/md5 will be updated after submission
    @param  deleteHook  bool
    @param  online  bool  if enable online access
    @return  bool

    Note: user-define name and loader in game are NOT updated.
    """
    if not game or not (game.id or game.md5):
      return
    if not game.id:
      try: game.id = self.games[game.md5].id
      except KeyError: pass
    if deleteHook and not game.hook:
      try: game.hook = self.games[game.md5].hook
      except KeyError: pass
    if online:
      nm = netman.manager()
      if nm.isOnline() and self.user.isLoginable():
        ok = nm.updateGame(game, self.user.name, self.user.password,
            deleteHook=deleteHook)

    if game.md5 not in self.games:
      game.visitCount += 1
      self.games[game.md5] = game
      #self.backupGamesXmlLater()
    else:
      g = self.games[game.md5]
      g.visitCount += 1
      g.md5 = game.md5 # enforce md5

      for pty in 'id', 'itemId', 'encoding', 'language', 'launchLanguage', 'commentCount', 'visitTime', 'path', 'launchPath':
        v = getattr(game, pty)
        if v:
          setattr(g, pty, v)

      for pty in 'nameThreadDisabled', 'hookDisabled', 'threadKept', 'removesRepeat', 'ignoresRepeat', 'keepsSpace', 'timeZoneEnabled', 'gameAgentDisabled':
        v = getattr(game, pty)
        if v is not None:
          setattr(g, pty, v)

      if game.threadSignature:
        g.threadSignature = game.threadSignature
        g.threadName = game.threadName

      if game.nameThreadSignature:
        g.nameThreadSignature = game.nameThreadSignature
        g.nameThreadName = game.nameThreadName

      if game.deletedHook:
        g.deletedHook = game.deletedHook
      elif deleteHook and not g.deletedHook:
        g.deletedHook = g.hook

      if deleteHook:
        g.hook = None
      elif game.hook:
        g.hook = game.hook

      #g.otherThreads = game.otherThreads if game.otherThreads is not None else {}
      #elif game.otherThreads: # merge thread
      #  g.otherThreads.update(game.otherThreads)

      for t in game.names:
        if game.names[t]:
          if g.names[t] is None:
            g.names[t] = []
          for n in game.names[t]:
            if n not in g.names[t]:
              g.names[t].append(n)

    self.touchGames()

    return True

  def touchGames(self):
    self._gamesDirty = True
    self._saveGamesLater()

    self.q.gamesChanged.emit()

  def touchGameFiles(self):
    self._gameFilesDirty = True
    self._saveGameFilesLater()

  #def updateGame(self, game):
  #  """
  #  @param[inout]  game  Game  id/md5 will be updated after submission
  #  @return  bool
  #  """
  #  if not game or not game.md5:
  #    return False
  #  if not game.id:
  #    try: game.id = self.games[game.md5].id
  #    except: pass
  #  nm = netman.manager()
  #  if nm.isOnline() and self.user.isLoginable():
  #    ok = nm.updateGame(game, self.user.name, self.user.password)
  #  if not game.md5:
  #    return False

  #  self.games[game.md5] = game
  #  self._gamesDirty = True
  #  self._saveGamesLater()

  #  self.q.gamesChanged.emit()
  #  return True

  def removeGame(self, md5):
    try: del self.games[md5]
    except KeyError: return
    self.touchGames()

  #def backupGamesXmlLater(self):
    #pass
    # Game xml backup is disabled
    #xmlfile = rc.xml_path('games')
    #osutil.backup_file_later(xmlfile)

  def saveGames(self):
    if not self._gamesDirty:
      return
    xmlfile = rc.xml_path('games')
    dprint("enter: xml = %s" % xmlfile)
    if not self.games:
      if os.path.exists(xmlfile):
        skfileio.removefile(xmlfile)
    else: # Game saved in traditional way so that it will not get corrupted
      data = rc.jinja_template('xml/games').render({
        'now': datetime.now(),
        'games': self.games.itervalues(),
      })
      ok = skfileio.writefile(xmlfile, data)
      if ok:
        dprint("pass")
      else:
        dwarn("failed: xml = %s" % xmlfile)
    dprint("leave")

  def _saveGameFilesLater(self):
    try: self._saveGameFilesTimer.start()
    except AttributeError:
      t = self._saveGameFilesTimer = QTimer(self.q)
      t.setInterval(5 * 1000) # in 5 seconds
      t.setSingleShot(True)
      t.timeout.connect(self.saveGameFiles)
      t.start()

  def _saveGamesLater(self):
    try: self._saveGamesTimer.start()
    except AttributeError:
      t = self._saveGamesTimer = QTimer(self.q)
      t.setInterval(60 * 1000) # in 1 minute
      t.setSingleShot(True)
      t.timeout.connect(self.saveGames)
      t.start()

  def reloadGameItems(self):
    xmlfile = rc.xml_path('gameitems')
    self.gameItems = {}
    self._gameInfo = []
    if not os.path.exists(xmlfile):
      dprint("pass: xml not found, %s" % xmlfile)
      return
    try:
      context = etree.iterparse(xmlfile, events=('start', 'end'))
      items = {} # {long itemId:GameItem}
      path = 0
      for event, elem in context:
        if event == 'start':
          path += 1
          if path == 3: # grimoire/references/reference
            e = GameItem(id=int(elem.get('id')))
        else:
          path -= 1
          if path == 3: # grimoire/references/reference
            tag = elem.tag
            text = elem.text
            if tag in ('title', 'romajiTitle', 'brand', 'series', 'image', 'banner', 'wiki', 'tags', 'artists', 'sdartists', 'writers', 'musicians'):
              setattr(e, tag, text)
            elif tag == 'keywords': # backward compatibility since 1386059148
              e.tags = text
            elif tag in ('otome', 'ecchi', 'okazu'):
              setattr(e, tag, text == 'true')
            elif tag in ('timestamp', 'fileSize', 'topicCount', 'annotCount', 'playUserCount', 'subtitleCount', 'scapeMedian', 'scapeCount', 'overallScoreSum', 'overallScoreCount', 'ecchiScoreSum', 'ecchiScoreCount'):
              setattr(e, tag, int(text))
            elif tag == 'date':
              e.date = datetime.strptime(text, '%Y%m%d')
          elif path == 2: # grimoire/games
            items[e.id] = e

      self.gameItems = items

      dprint("pass: load %i items from %s" % (len(self.gameItems), xmlfile))
      return

    except etree.ParseError, e:
      dwarn("xml parse error", e.args)
    except (TypeError, ValueError, AttributeError), e:
      dwarn("xml malformat", e.args)
    except Exception, e:
      derror(e)

    dwarn("warning: failed to load xml from %s" % xmlfile)

  #def reloadReferenceDigests(self):
  #  xmlfile = rc.xml_path('refdigest')
  #  self.referenceDigests = {}
  #  self._gameInfo = []
  #  if not os.path.exists(xmlfile):
  #    dprint("pass: xml not found, %s" % xmlfile)
  #    return

  #  try:
  #    context = etree.iterparse(xmlfile, events=('start', 'end'))
  #    digests = {} # {long itemId:ReferenceDigest}
  #    path = 0
  #    for event, elem in context:
  #      if event == 'start':
  #        path += 1
  #        if path == 3: # grimoire/references/reference
  #          r = ReferenceDigest(
  #              id=int(elem.get('id')),
  #              type=elem.get('type'))
  #      else:
  #        path -= 1
  #        if path == 3: # grimoire/references/reference
  #          tag = elem.tag
  #          text = elem.text
  #          if tag in ('key', 'title', 'brand', 'image'):
  #            setattr(r, tag, text)
  #          elif tag.endswith('Id') or tag.endswith('Count') or tag in ('date', 'timestamp'):
  #            setattr(r, tag, int(text))
  #        elif path == 2: # grimoire/games
  #          if r.type in Reference.TYPES:
  #            try: digests[r.itemId].append(r)
  #            except KeyError: digests[r.itemId] = [r]

  #    self.referenceDigests = digests

  #    dprint("pass: load %i refs from %s" % (len(self.referenceDigests), xmlfile))
  #    return

  #  except etree.ParseError, e:
  #    dwarn("xml parse error", e.args)
  #  except (TypeError, ValueError, AttributeError), e:
  #    dwarn("xml malformat", e.args)
  #  except Exception, e:
  #    derror(e)

  #  dwarn("warning: failed to load xml from %s" % xmlfile)

  def reloadGameFiles(self):
    xmlfile = rc.xml_path('gamefiles')
    self.gameFiles = {}
    self.gameFilesByMd5 = {}
    if not os.path.exists(xmlfile):
      dprint("pass: xml not found, %s" % xmlfile)
      return

    try:
      context = etree.iterparse(xmlfile, events=('start', 'end'))
      files = {}
      path = 0
      for event, elem in context:
        if event == 'start':
          path += 1
          if path == 3: # grimoire/games/game
            g = GameFile(id=int(elem.get('id')))
        else:
          path -= 1
          if path == 4: # grimoire/games/game/names
            if elem.tag == 'name':
              g.name = elem.text
          elif path == 3: # grimoire/games/game
            tag = elem.tag
            text = elem.text
            if tag == 'md5':
              g.md5 = text
            elif tag.endswith('Id') or tag.endswith('Count') or tag.endswith('Time'):
              setattr(g, tag, int(text))
          elif path == 2: # grimoire/games
            files[g.id] = g

      self.gameFilesByMd5 = {v.md5:v for v in files.itervalues()}
      self.gameFiles = files

      dprint("pass: load %i games from %s" % (len(self.gameFiles), xmlfile))
      return

    except etree.ParseError, e:
      dwarn("xml parse error", e.args)
    except (TypeError, ValueError, AttributeError), e:
      dwarn("xml malformat", e.args)
    except Exception, e:
      derror(e)

    dwarn("warning: failed to load xml from %s" % xmlfile)
    #datafile = rc.data_path('gamefiles')
    #self.gameFiles = {}
    #self.gameFilesByMd5 = {}
    #if not os.path.exists(datafile):
    #  dprint("pass: file not found, %s" % datafile)
    #  return
    #
    # In Python3, only binary file is allowed for picking.
    # Either save game md5 in binary, or switch back to portable text file (i.e. list of md5)
    # See: http://regding.is-programmer.com/posts/31734
    #try:
    #  with open(datafile, 'r') as f:
    #    #l = f.readlines()
    #    data = pickle.load(f)
    #
    #    self.gameFilesByMd5 = {v.md5:v for v in data.itervalues()}
    #    self.gameFiles = data
    #    dprint("count = %i" % len(self.gameFiles))
    #except (IOError, pickle.UnpicklingError), e:
    #  dwarn(e)
    #except Exception, e:
    #  dwarn(e)

  def saveGameFiles(self):
    if not self._gameFilesDirty or not self.gameFiles:
      return

    ok = rc.jinja_template_write_xml('gamefiles',
      now=datetime.now(),
      files=self.gameFiles.itervalues(),
    )
    if ok:
      settings.global_().setGameFilesTime(skdatetime.current_unixtime())
      dprint("pass: xml = gamefiles")
    else:
      dwarn("failed: xml = gamefiles")

    #if self.gameFiles:
    #  dprint("enter")
    #  datafile = rc.data_path('gamefiles')
    #  try:
    #    with open(datafile, 'w') as f:
    #      pickle.dump(self.gameFiles, f)
    #    settings.global_().setGameFilesTime(skdatetime.current_unixtime())
    #  except (IOError, pickle.PicklingError), e:
    #    dwarn(e)
    #  dprint("leave")

  def reloadGames(self): # not writing stream template to security reason, so that games xml will not corrupted
    self._gamesDirty = False
    self.games = {}

    xmlfile = rc.xml_path('games')
    xmlfile_bak = rc.xml_path('games', backup=True)

    self._reloadGames(xmlfile)
    if self.games:
      dprint("backup game profile")
      skfileio.copyfile(xmlfile, xmlfile_bak)
    else:
      dprint("try recovering backup profile")
      self._reloadGames(xmlfile_bak)
      if self.games:
        growl.notify(my.tr("VNR's game profile (%s) was corrupted. Recovered from backup.") % "games.xml")
        skfileio.copyfile(xmlfile_bak, xmlfile)
      else:
        dprint("failed to recover from backup file")
    self.q.gamesChanged.emit()

    # If games, backup games

  def _reloadGames(self, xmlfile):
    """This function is only called by reloadGames!
    @param  xmlfile  str  path
    """
    if not os.path.exists(xmlfile):
      dprint("pass: xml not found, %s" % xmlfile)
      return

    try:
      tree = etree.parse(xmlfile)
      root = tree.getroot()

      e_games = root.find('./games')
      for game in e_games:
        text = game.get('id')
        #if not text:
        #  continue
        g = Game(id=int(text))

        for e in game:
          tag = e.tag
          if tag in ('md5', 'path', 'launchPath', 'language', 'launchLanguage', 'loader', 'encoding', 'userDefinedName', 'deletedHook'):
            setattr(g, tag, e.text or '')
          #elif tag in ('itemId', 'commentsUpdateTime', 'refsUpdateTime', 'visitTime', 'visitCount', 'commentCount'):
          elif tag.endswith('Id') or tag.endswith('Count') or tag.endswith('Time'):
            setattr(g, tag, int(e.text))
          elif tag in ('timeZoneEnabled', 'gameAgentDisabled', 'removesRepeat', 'ignoresRepeat', 'keepsSpace', 'threadKept', 'voiceDefaultEnabled'):
            setattr(g, tag, e.text == 'true')
          elif tag == 'hook':
            g.hook = e.text
            g.hookDisabled = e.get('disabled') == 'true'
            b = e.get('kept') == 'true' # for backward compatibility
            if b:
              g.threadKept = b
          elif tag == 'threads':
            thread = e.find('./thread[@type="scene"]')
            g.threadName = thread.find('./name').text
            g.threadSignature = long(thread.find('./signature').text)

            thread = e.find('./thread[@type="name"]')
            if thread is not None:
              # FIXME: this might cause issue that online namethraed overwrite local one?
              #attr = thread.get('disabled')
              #if attr is not None:
              #  g.nameThreadDisabled = tag == 'true'
              g.nameThreadName = thread.find('./name').text
              g.nameThreadSignature = long(thread.find('./signature').text)

            threads = e.iterfind('./thread[@type="other"]')
            if threads:
              g.otherThreads = {
                long(e.find('./signature').text) : e.find('./name').text
                for e in threads
              }
          elif tag == 'names':
            l = {
              t: [it.text for it in e.iterfind('./name[@type="%s"]' % t)]
              for t in g.NAME_TYPES
            }
            try: l['window'] = filter(sjis_encodable, l['window'])
            except KeyError: pass
            g.names = l

        if not g.language: g.language = 'ja'

        # Error checking
        #if g.loader == 'lsc':
        #  dwarn("change game loader from LocaleSwitch to AppLocale")
        #  g.loader = 'apploc'

        if g.language in ('ja', 'zhs', 'zht') and g.keepsSpace:
          dwarn("ignore keeping spaces: id=%s" % g.id)
          g.keepsSpace = False
          growl.notify('<br/>'.join((
            my.tr("Disable keeping space for Kanji language") + " (%s)" % g.language ,
            g.name,
          )))

        # Change game engines
        if g.threadName:
          v = config.RENAMED_GAME_ENGINES.get(g.threadName)
          if v:
            g.threadName = v
        if g.nameThreadName:
          v = config.RENAMED_GAME_ENGINES.get(g.nameThreadName)
          if v:
            g.nameThreadName = v

        if g.hook and g.threadName != defs.HCODE_THREAD_NAME:
          dwarn("ignore bad hook: id=%s, code=%s" % (g.id, g.hook))
          growl.notify('<br/>'.join((
            my.tr("Remove bad user-defined hcode"),
            g.hook,
            g.name,
          )))
          g.hook = ''
          g.hookDisabled = None
          #g.hookKept = None

        #if g.threadName in config.SINGLE_GAME_ENGINES and g.threadSignature != defs.SINGLE_ENGINE_SIGNATURE:
        #  g.threadSignature = defs.SINGLE_ENGINE_SIGNATURE
        #  dwarn("correct signature for single game engine: %s" % g.threadName)
        #  growl.notify('<br/>'.join((
        #    my.tr("Automatically correct text settings"),
        #    "%s: %s" % (tr_("Engine"), g.threadName),
        #    "%s: %s" % (tr_("Game"), g.name),
        #  )))

        if (g.removesRepeat or g.ignoresRepeat) and g.threadName in config.NOREPEAT_GAME_ENGINES:
          g.removesRepeat = g.ignoresRepeat = None
          dwarn("ignore bad repetition: thread name = %s" % g.threadName)
          growl.notify('<br/>'.join((
            my.tr("Ignore repetition filters in text settings"),
            "%s: %s" % (tr_("Engine"), g.threadName),
            "%s: %s" % (tr_("Game"), g.name),
          )))

        if g.threadKept and g.threadName in config.NOFLOAT_GAME_ENGINES:
          g.threadKept = None
          dwarn("ignore non-floating engine: %s" % g.threadName)
          growl.notify('<br/>'.join((
            my.tr("Do not keep all scenario threads in text settings"),
            "%s: %s" % (tr_("Engine"), g.threadName),
            "%s: %s" % (tr_("Game"), g.name),
          )))

        if g.path and os.path.exists(g.path) or g.launchPath and os.path.exists(g.launchPath):
          self.games[g.md5] = g
        else:
          growl.notify('<br/>'.join((
            my.tr("Remove non-existed game"),
            g.name,
            g.path,
          )))

      dprint("pass: load %i games from %s" % (len(self.games), xmlfile))
      return

    except etree.ParseError, e:
      dwarn("xml parse error", e.args)
    except (TypeError, ValueError, AttributeError), e:
      dwarn("xml malformat", e.args)
    except Exception, e:
      derror(e)

    dwarn("warning: failed to load xml from %s" % xmlfile)

  ## User ##

  def saveUsers(self):
    if self.users:
      ok = rc.jinja_template_write_xml('users',
        now=datetime.now(),
        users=self.users.itervalues(),
      )
      if ok:
        settings.global_().setUserDigestsTime(skdatetime.current_unixtime())
        dprint("pass: xml = users")
      else:
        dwarn("failed: xml = users")

  def reloadUsers(self):
    xmlfile = rc.xml_path('users')
    self.users = {}
    if not os.path.exists(xmlfile):
      dprint("pass: xml not found, %s" % xmlfile)
      #self.q.usersChanged.emit()
      return

    try:
      context = etree.iterparse(xmlfile, events=('start', 'end'))

      users = {}
      path = 0
      for event, elem in context:
        if event == 'start':
          path += 1
          if path == 3: # grimoire/users/user
            u = UserDigest(id=int(elem.get('id')))
        else:
          path -= 1
          if path == 3: # grimoire/users/user
            tag = elem.tag
            text = elem.text
            setattr(u, tag, text or '')

          elif path == 4: # grimoire/users/user/levels
            tag = elem.tag
            text = elem.text
            setattr(u, tag, int(text))

          elif path == 2:
            users[u.id] = u

      if users:
        self.users = users
        #self.invalidateUsers()

        dprint("pass: load users from %s" % xmlfile)
        return

    except etree.ParseError, e:
      dwarn("xml parse error", e.args)
    except (TypeError, ValueError, AttributeError), e:
      dwarn("xml malformat", e.args)
    except Exception, e:
      derror(e)
    finally:
      self.q.gamesChanged.emit()

    dwarn("warning: failed to load xml from %s" % xmlfile)

  ## Character ##

  def _saveCharactersLater(self):
    try: self._saveCharactersTimer.start()
    except AttributeError:
      t = self._saveCharactersTimer = QTimer(self.q)
      t.setInterval(30 * 1000) # in 30 second
      t.setSingleShot(True)
      t.timeout.connect(self.saveCharacters)
      t.start()

  def iterCharacters(self):
    """
    @yield  Character
    """
    if self.characters:
      for it in self.characters.itervalues():
        yield it

  def iterCharacterData(self):
    """
    @yield  _Character
    """
    for it in self.iterCharacters():
      yield it.d

  ## Comment ##

  def _saveCommentsLater(self):
    try: self._saveCommentsTimer.start()
    except AttributeError:
      t = self._saveCommentsTimer = QTimer(self.q)
      t.setInterval(30 * 1000) # in 30 second
      t.setSingleShot(True)
      t.timeout.connect(self.saveComments)
      t.start()

  def iterComments(self):
    """
    @yield  Comment  which is not deleted
    """
    if self.comments:
      for l in self.comments.itervalues():
        for c in l:
          if not c.d.deleted:
            yield c

  def iterCommentData(self):
    """
    @yield  _Comment
    """
    for it in self.iterComments():
      yield it.d

  def iterTermData(self):
    """
    @yield  _Term
    """
    for it in self.terms:
      yield it.d

  #def iterTermsWithType(self, type):
  #  """
  #  @param  type  str
  #  @yield  Term
  #  """
  #  ids = self.currentGameIds # 8/27/2013: Why AttributeError?!
  #  for t in self.sortedTerms:
  #    td = t.d # To improve performance
  #    if not td.disabled and not td.deleted and td.type == type and (not td.special or
  #        ids and td.gameId and td.gameId in ids):
  #      yield t

  #def iterTermsWithTypes(self, types):
  #  """
  #  @param  types  [str]
  #  @yield  Term
  #  """
  #  ids = self.currentGameIds # 8/27/2013: Why AttributeError?!
  #  for t in self.sortedTerms:
  #    td = t.d # To improve performance
  #    if not td.disabled and not td.deleted and td.type in types and (not td.special or
  #        ids and td.gameId and td.gameId in ids):
  #      yield t

  ## Character name ##

  #def updateNameItems(self):
  #  #if not gid or gameId and gameId != gid:
  #  #  dwarn("game changed")
  #  #  return
  #  if self.nameItems:
  #    dwarn("name items already exist")
  #    return
  #  mm = mecabman.manager()
  #  if not mm.isEnabled():
  #    dwarn("mecab is not enabled")
  #    return
  #  dprint("enter")
  #  growl.msg(my.tr("Searching for game character names") + " ...")
  #  game = self.currentGame
  #  if game and game.itemId:
  #    info = self.q.currentGameInfo()
  #    if info and info.itemId == game.itemId:
  #      l = info.characters # may surrender event cycles
  #      if l:
  #        if self.nameItems:
  #          dwarn("leave: name items already exist")
  #          return
  #        growl.msg(my.tr("Found {0} game characters").format(len(l)))
  #        #names = ((kw['name'],kw['yomi']) for kw in l)
  #        names = [(kw['name'],kw['yomi']) for kw in l]
  #        nm = nameman.manager()
  #        self.nameItems = nm.parseNameItems(names)
  #
  #        itemId = game.itemId
  #        dicpath = nm.cachedMeCabDic(itemId)
  #        if not dicpath:
  #          dicpath = skthreads.runsync(partial(
  #              nm.compileMeCabDic,
  #              names,
  #              itemId))
  #        if dicpath and not mm.userDictionary():
  #          mm.setUserDictionary(dicpath)
  #        dprint("leave: item count = %i" % len(self.nameItems))
  #        return
  #  growl.msg(my.tr("Game character names not found"))
  #  dprint("leave: no items")

  def _updateContexts(self):
    self.contexts = {h:c[0].context for h,c in self.comments.iteritems()} if self.comments else {}

  def _updateComments2(self):
    dprint("enter")
    d = {}
    if self.comments:
      for c in self.iterComments():
        context = c.d.context
        if context:
          h = hashutil.hashcontexts(context)
          l = d.get(h)
          if l:
            l.append(c)
          else:
            d[h] = [c]
    self.comments2 = d
    dprint("leave: len = %i" % len(d))

  # Subtitles

  def updateSubtitles(self, itemId, reset=False):
    """
    @param  itemId  long
    @param* reset  bool
    """
    #self.resetSubtitles()
    if self.subtitles:
      subTimestamp = self.subtitleTimestamp
    else:
      subTimestamp = 0
    now = self.subtitleTimestamp = skdatetime.current_unixtime()
    self.subtitleItemId = itemId
    skthreads.runasynclater(
        partial(self._updateSubtitles, itemId, now, self.subtitles, subTimestamp, reset),
        100) # reload subtitles after 100 ms

  def _updateSubtitles(self, itemId, timestamp, subs, subTimestamp, reset):
    """This function runs in parallel
    @param  itemId  long
    @param  timestamp  long  now
    @param  subs  [Subtitle]
    @param  subTimestamp  long
    @param  reset bool
    @return  {long:Subtitle}
    """
    if itemId != self.subtitleItemId or timestamp != self.subtitleTimestamp:
      return

    lang = self.user.language

    langs = ['zht', 'zhs'] if lang.startswith('zh') else [lang]
    if langs[0] != 'en' and 'en' not in settings.global_().blockedLanguages():
      langs.append('en')

    gameLang = 'ja' # TODO: allow change gamelang

    changed = False
    if reset or not subTimestamp:
      growl.msg(my.tr("Updating online subtitles") + " ...", async=True)
      subs = netman.manager().querySubtitles(itemId=itemId, langs=langs, async=False)
      if itemId != self.subtitleItemId or timestamp != self.subtitleTimestamp:
        return
      changed = True
      subTimestamp = timestamp
    else:
      growl.msg(my.tr("Updating online subtitles") + " ...", async=True)
      newsubs = netman.manager().querySubtitles(itemId=itemId, langs=langs, time=subTimestamp, async=False)
      if itemId != self.subtitleItemId or timestamp != self.subtitleTimestamp:
        return
      if newsubs:
        changed = True
        subTimestamp = timestamp
        self._mergeSubtitles(subs, newsubs)

    if itemId != self.subtitleItemId or timestamp != self.subtitleTimestamp:
      return

    if subs:
      self._clearSubtitles()
      self.subtitles = subs
      self.subtitleIndex = self._createSubtitleIndex(subs)
      growl.msg(my.tr("Found {0} subtitles").format(len(subs)), async=True)
    else:
      growl.msg(my.tr("Subtitles not found"), async=True)
    if changed:
      self._saveXmlSubtitles(subs, subTimestamp, itemId, lang, gameLang)
      self._saveYamlSubtitles(subs, timestamp, itemId, lang, gameLang)

  def reloadSubtitles(self, itemId):
    """
    @param  itemId  long
    """
    self.resetSubtitles()
    if itemId:
      item = manager().queryGameItem(id=itemId)
      if item and item.subtitleCount:
        now = self.subtitleTimestamp = skdatetime.current_unixtime()
        self.subtitleItemId = itemId
        skthreads.runasync(partial(self._reloadSubtitles, itemId, now))

  def _reloadSubtitles(self, itemId, timestamp):
    """This function runs in parallel
    @param  itemId  long
    @param  timestamp  long
    @return  {long:Subtitle}
    """
    if itemId != self.subtitleItemId or timestamp != self.subtitleTimestamp:
      return

    lang = self.user.language

    langs = ['zht', 'zhs'] if lang.startswith('zh') else [lang]
    if langs[0] != 'en' and 'en' not in settings.global_().blockedLanguages():
      langs.append('en')

    gameLang = 'ja' # TODO: allow change gamelang

    subs, subTimestamp = self._loadXmlSubtitles(itemId, lang, gameLang)
    if itemId != self.subtitleItemId or timestamp != self.subtitleTimestamp:
      return

    changed = False
    if not subs or not subTimestamp:
      growl.msg(my.tr("Updating online subtitles") + " ...", async=True)
      subs = netman.manager().querySubtitles(itemId=itemId, langs=langs, async=False)
      if itemId != self.subtitleItemId or timestamp != self.subtitleTimestamp:
        return
      changed = True
      subTimestamp = timestamp
    elif timestamp > config.APP_UPDATE_SUBS_INTERVAL + subTimestamp:
      growl.msg(my.tr("Updating online subtitles") + " ...", async=True)
      newsubs = netman.manager().querySubtitles(itemId=itemId, langs=langs, time=subTimestamp, async=False)
      if itemId != self.subtitleItemId or timestamp != self.subtitleTimestamp:
        return
      if newsubs:
        changed = True
        subTimestamp = timestamp
        self._mergeSubtitles(subs, newsubs)

    if itemId != self.subtitleItemId or timestamp != self.subtitleTimestamp:
      return

    subIndex = self._createSubtitleIndex(subs)

    if itemId != self.subtitleItemId or timestamp != self.subtitleTimestamp:
      return

    self._clearSubtitles()
    self.subtitles = subs or []
    self.subtitleIndex = subIndex
    self.subtitleTimestamp = subTimestamp

    if subs:
      growl.msg(my.tr("Found {0} subtitles").format(len(subs)), async=True)
    else:
      growl.msg(my.tr("Subtitles not found"), async=True)
    if changed and subs:
      self._saveXmlSubtitles(subs, subTimestamp, itemId, lang, gameLang)
      self._saveYamlSubtitles(subs, subTimestamp, itemId, lang, gameLang)

  @staticmethod
  def _createSubtitleIndex(subs):
    """
    @param  subs  [Subtitle]
    @return  {long hash:[Subtitle]}
    """
    ret = {}
    if subs:
      for s in subs:
        h = hashutil.hashcontext(s.text)
        l = ret.get(h)
        if l:
          l.append(s)
        else:
          ret[h] = [s]
    return ret

  @staticmethod
  def _saveXmlSubtitles(subs, timestamp, itemId, subLang, gameLang):
    """
    @param  subs  [Subtitle]
    @param  itemId  long
    @param  subLang  str
    @param* gameLang  str
    @return  [Subtitle], timestamp
    """
    xmlfile = rc.subs_yaml_path(itemId, subLang, gameLang, fmt='xml')
    dprint("save modified subtitles to %s" % xmlfile)

    ok = rc.jinja_template_write(xmlfile, 'xml/subs',
      subs=subs,
      timestamp=timestamp,
      now=skdatetime.timestamp2datetime(timestamp),
    )
    if ok:
      dprint("pass: xml = %s" % xmlfile)
    else:
      dwarn("failed: xml = %s" % xmlfile)

  @staticmethod
  def _saveYamlSubtitles(subs, timestamp, itemId, subLang, gameLang):
    """
    @param  subs  [Subtitle]
    @param  itemId  long
    @param  subLang  str
    @param* gameLang  str
    @return  [Subtitle], timestamp
    """
    from jinjay.escape import ystr
    yamlfile = rc.subs_yaml_path(itemId, subLang, gameLang)
    dprint("save modified subtitles to %s" % yamlfile)

    ok = rc.jinja_template_write(yamlfile, 'yaml/subs',
      ys=ystr,
      subs=subs,
      subCount=len(subs),
      timestamp=timestamp,
      now=skdatetime.timestamp2datetime(timestamp),
      gameId=itemId,
      options={
        'subLang': subLang,
        'textLang': gameLang,
      }
    )
    if ok:
      dprint("pass: yaml = %s" % yamlfile)
    else:
      dwarn("failed: yaml = %s" % yamlfile)

    # Python yaml is using too many memory +100MB

    #lines = [{
    #  'gameId': itemId,
    #  'textLang': gameLang,
    #  'subLang': subLang,
    #  'timestamp': timestamp,
    #}]
    #for s in subs:
    #  l = {} # enforce order
    #  l['id'] = s.textId
    #  for k in (
    #      'text', 'textName', 'textLang', 'textTime',
    #      'sub', 'subName', 'subLang', 'subTime',
    #      'userId', 'userName',
    #    ):
    #    v = getattr(s, k)
    #    if v:
    #      l[k] = v
    #  lines.append(l)
    #skyaml.writefile(lines, path)

  @staticmethod
  def _mergeSubtitles(subs, newsubs):
    """
    @param  subs  [Subtitle]
    @param  newsubs  [Subtitle]
    """
    index = {it.textId:i for i,it in enumerate(subs)}
    for s in newsubs:
      i = index.get(s.textId)
      if i:
        t = subs[i]
        subs[i] = s
        t.releaseObjectLater()
      else:
        subs.append(s)

  @staticmethod
  def _loadXmlSubtitles(itemId, subLang, gameLang):
    """
    @param  itemId  long
    @param  subLang  str
    @param* gameLang  str
    @return  [Subtitle], timestamp
    """
    xmlfile = rc.subs_yaml_path(itemId, subLang, gameLang, fmt='xml')
    if not os.path.exists(xmlfile):
      #dprint("pass: xml not found, %s" % xmlfile)
      dprint("pass: xml not found")
      return (), 0

    try:
      timestamp = 0
      context = etree.iterparse(xmlfile, events=('start', 'end'))
      ret = []
      path = 0
      for event, elem in context:
        if event == 'start':
          path += 1
          if path == 2: # grimoire/trs
            timestamp = elem.get('timestamp')
            if not timestamp:
              raise ValueError("missing xml timestamp")
            timestamp = int(timestamp)
          elif path == 3: # grimoire/trs/tr
            kw = {}
        else:
          path -= 1
          if path == 3: # grimoire/trs/tr
            tag = elem.tag
            text = elem.text
            if tag in ('text', 'textName', 'textLang', 'sub', 'subName', 'subLang', 'itemId'):
              kw[tag] = text or ''
            elif tag in ('userId', 'textId', 'textTime', 'subTime'):
              kw[tag] = int(text)
            #else:
            #  kw[tag] = text or ''

          elif path == 2: # grimoire/trs
            s = Subtitle(**kw)
            ret.append(s)

      #self.comments, self.context = comments, contexts
      dprint("pass: load %i characters from %s" % (len(ret), xmlfile))
      return ret, timestamp

    except etree.ParseError, e:
      dwarn("xml parse error", e.args)
    except (TypeError, ValueError, AttributeError), e:
      dwarn("xml malformat", e.args)
    except Exception, e:
      derror(e)

    dwarn("warning: failed to load xml from %s" % xmlfile)
    return (), 0

  #@staticmethod
  #def _loadYamlSubtitles(itemId, subLang, gameLang): # too slow to use
  #  """
  #  @param  itemId  long
  #  @param  subLang  str
  #  @param* gameLang  str
  #  @return  [Subtitle], timestamp
  #  """
  #  path = rc.subs_yaml_path(itemId, subLang, gameLang)
  #  if os.path.exists(path):
  #    try:
  #      l = yaml.load(file(path, 'r'))
  #      options = l.pop(0)
  #      subs = []
  #      for it in l:
  #        s = Subtitle(
  #          userId=it.get('userId') or 0,
  #          textId=it.get('id') or 0,
  #          text=it.get('text') or '',
  #          textName=it.get('textName') or '',
  #          textLang=it.get('textLang') or '',
  #          textTime=it.get('textTime') or 0,
  #          sub=it.get('sub') or '',
  #          subName=it.get('subName') or '',
  #          subLang=it.get('subLang') or '',
  #          subTime=it.get('subTime') or 0,
  #        )
  #        if s.text and s.sub:
  #          subs.append(s)
  #
  #      dprint("pass: load %i subs from %s" % (len(subs), path))
  #      return subs, options.get('timestamp') or 0
  #    except Exception, e:
  #      dwarn(e)
  #  return (), 0

  def reloadComments(self, online=True):
    self.contexts = {}
    self.comments = {}
    self.comments2 = {}
    g = self.currentGame
    if not g or not g.md5:
      return

    nm = netman.manager()
    if online and nm.isOnline():
      cursor = skcursor.SkAutoBusyCursor()
      self.touchComments()

      growl.msg(my.tr("Fetching comments") + " ...")
      r = nm.queryComments(gameId=g.id, md5=g.md5)
      if not r and r is not None:
        _DataManager.removeComments(md5=g.md5)
      self.comments = r or {}
      self._updateContexts()
      self._updateComments2()
      if self.comments:
        g.commentsUpdateTime = skdatetime.current_unixtime()
        self._saveCommentsLater()
    else:
      growl.msg(my.tr("Loading offline comments") + " ...")
      self.comments = _DataManager.loadComments(md5=g.md5, hash=True) or {}
      self._updateContexts()
      self._updateComments2()
      self._commentsDirty = False

    if self.comments:
      count = 0
      for c in self.comments.itervalues():
        count += len(c)
      growl.msg(my.tr("Found {0} comments").format(count))
    # Already growled in main window for credits
    #else:
    #  growl.msg(my.tr("No user-contributed subtitles found"))
    self.invalidateComments(g.md5)
    dprint("comments count = %i" % len(self.comments) if self.comments else 0)

  def saveComments(self):
    if not self._commentsDirty or not self.comments:
      return
    if self.dirtyCommentsLocked:
      dprint("warning: dirty comments are locked, save later")
      self._saveCommentsLater()
      return
    md5 = self.q.currentGameMd5()
    if not md5:
      return
    xmlfile = rc.comments_xml_path(md5=md5)
    ok = rc.jinja_template_write(xmlfile, 'xml/comments',
      now=datetime.now(),
      comments=self.iterCommentData(),
      contexts=self.contexts,
    )
    if ok:
      dprint("pass: xml = %s" % xmlfile)
    else:
      dwarn("failed: xml = %s" % xmlfile)

  def saveCharacters(self):
    if not self._charactersDirty: #or not self.characters:
      return
    md5 = self.q.currentGameMd5()
    if not md5:
      return
    xmlfile = rc.voices_xml_path(md5=md5)
    if not self.characters and os.path.exists(xmlfile):
      dprint("remove xml = %s" % xmlfile)
      skfileio.removefile(xmlfile)
      return
    ok = rc.jinja_template_write(xmlfile, 'xml/voices',
      now=datetime.now(),
      voices=self.iterCharacterData(),
    )
    if ok:
      dprint("pass: xml = %s" % xmlfile)
    else:
      dwarn("failed: xml = %s" % xmlfile)

  def reloadCharacters(self, online=True):
    self.clearCharacters()
    g = self.currentGame
    if not g or not g.md5:
      return
    l = _DataManager._loadCharacters(g.md5, parent=self.q)
    if l:
      self.characters = l
    else:
      self.resetCharacters()
    assert self.characters
    self.invalidateCharacters()

  @staticmethod
  def _loadCharacters(md5, parent=None):
    """
    @param  md5  str
    @return {unicode name:Character}
    """
    xmlfile = rc.voices_xml_path(md5=md5)

    #self.comments = {}
    #self.contexts = {}
    if not os.path.exists(xmlfile):
      #dprint("pass: xml not found, %s" % xmlfile)
      dprint("pass: xml not found")
      return

    try:
      context = etree.iterparse(xmlfile, events=('start', 'end'))

      ret = {} #if hash else []
      path = 0
      for event, elem in context:
        if event == 'start':
          path += 1
          if path == 3: # grimoire/voices/voice
            kw = {
              'ttsEnabled': elem.get('disabled') != 'true',
            }
        else:
          path -= 1
          if path == 3: # grimoire/voices/voice
            tag = elem.tag
            text = elem.text
            if tag in ('name', 'gender', 'ttsEngine'):
              kw[tag] = text or ''
            elif tag == 'timestamp':
              kw[tag] = int(text)
            #else:
            #  kw[tag] = text or ''

          elif path == 2: # grimoire/voices
            c = Character(parent=parent, **kw)
            ret[c.name] = c

      #self.comments, self.context = comments, contexts
      dprint("pass: load %i characters from %s" % (len(ret), xmlfile))
      return ret

    except etree.ParseError, e:
      dwarn("xml parse error", e.args)
    except (TypeError, ValueError, AttributeError), e:
      dwarn("xml malformat", e.args)
    except Exception, e:
      derror(e)

    dwarn("warning: failed to load xml from %s" % xmlfile)

  #def iterReferenceDigests(self):
  #  """
  #  @yield  ReferenceDigest
  #  """
  #  for it in self.referenceDigests.itervalues():
  #    for r in it:
  #      yield r

  def saveGameItems(self):
    if not self.gameItems: #or not self._gameItemsDirty:
      return
    ok = rc.jinja_template_write_xml('gameitems',
      now=datetime.now(),
      items=self.gameItems.itervalues(),
    )
    if ok:
      settings.global_().setGameItemsTime(skdatetime.current_unixtime())
      dprint("pass: xml = gameitems")
    else:
      dwarn("failed: xml = gameitems")

  #def saveReferenceDigests(self):
  #  if not self.referenceDigests: #or not self._referenceDigestsDirty:
  #    return

  #  xmlfile = rc.xml_path('refdigest')
  #  data = rc.jinja_template('xml/refdigest').render({
  #    'now': datetime.now(),
  #    'digests': self.iterReferenceDigests(),
  #  })
  #  ok = skfileio.writefile(xmlfile, data)
  #  if ok:
  #    #settings.global_().setReferenceDigestsTime(skdatetime.current_unixtime())
  #    dprint("pass: xml = %s" % xmlfile)
  #  else:
  #    dwarn("failed: xml = %s" % xmlfile)

  @staticmethod
  def loadReferences(gameId, parent=None, init=True):
    """
    @param  gameId  int
    @return [Reference]
    """
    xmlfile = rc.refs_xml_path(gameId=gameId)

    #self.comments = {}
    #self.contexts = {}
    if not os.path.exists(xmlfile):
      #dprint("pass: xml not found, %s" % xmlfile)
      dprint("pass: xml not found")
      return

    try:
      context = etree.iterparse(xmlfile, events=('start', 'end'))

      ret = [] #if hash else []
      path = 0
      for event, elem in context:
        if event == 'start':
          path += 1
          if path == 3: # grimoire/references/reference
            kw = {
              #'comment': "",
              #'updateComment': "",
              #'updateTimestamp':  0,
              #'updateUserId': 0,
              'disabled': elem.get('disabled') == 'true',
              'id': int(elem.get('id')),
              'type': elem.get('type'),
            }
        else:
          path -= 1
          if path == 3: # grimoire/voices/voice
            tag = elem.tag
            text = elem.text
            if tag in ('key', 'title', 'brand', 'url', 'comment', 'updateComment'):
              kw[tag] = text or ''
            #if tag in ('itemId', 'gameId', 'userId', 'timestamp', 'updateUserId', 'updateTimestamp', 'date'):
            elif tag == 'date' or tag.endswith('Id') or tag.endswith('Hash') or tag.endswith('Count') or tag.endswith('imestamp'):
              kw[tag] = int(text)
            #elif tag == 'disabled':
            #  kw[tag] = text == 'true'

          elif path == 2 and kw['type'] in Reference.TYPES: # grimoire/references
            #if not kw.get('userHash'):
            #  kw['userHash'] = kw['userId']
            ret.append(Reference(parent=parent, **kw))

      #self.comments, self.context = comments, contexts
      dprint("pass: load %i refs from %s" % (len(ret), xmlfile))
      return ret

    except etree.ParseError, e:
      dwarn("xml parse error", e.args)
    except (TypeError, ValueError, AttributeError), e:
      dwarn("xml malformat", e.args)
    except Exception, e:
      derror(e)

    dwarn("warning: failed to load xml from %s" % xmlfile)

  @staticmethod
  def removeReferences(gameId):
    if gameId:
      xmlfile = rc.refs_xml_path(gameId=gameId)
      if os.path.exists(xmlfile):
        skfileio.removefile(xmlfile)

  ## Comments ##

  @staticmethod
  def removeComments(md5):
    if md5:
      xmlfile = rc.comments_xml_path(md5=md5)
      if os.path.exists(xmlfile):
        skfileio.removefile(xmlfile)

  @classmethod
  def loadComments(cls, md5, hash=True, async=True):
    """
    @param  md5  str
    @param  hash  bool
    @return ({long hash:Comment} if hash else [Comment]) or None
    """
    xmlfile = rc.comments_xml_path(md5=md5)

    #self.comments = {}
    #self.contexts = {}
    if not os.path.exists(xmlfile):
      #dprint("pass: xml not found, %s" % xmlfile)
      dprint("pass: xml not found")
      return

    if async:
      try: sz = os.path.getsize(xmlfile)
      except os.error: sz = 0
      if sz < 2000000: # max file size, around 2MB
        async = False

    dprint("pass: async = %s" % async)
    if not async:
      cursor = skcursor.SkAutoWaitCursor()
      return cls._loadComments(xmlfile, hash)
    else:
      cursor = skcursor.SkAutoBusyCursor()
      return skthreads.runsync(partial(
          cls._loadComments, xmlfile, hash, checkexit=True))

  @staticmethod
  def _loadComments(xmlfile, hash, checkexit=False):
    """
    @param  xmlfile  unicode  path to xml
    @param  hash  bool
    @param  checkexit  bool  weather check quit
    @return ({long hash:Comment} if hash else [Comment]) or None
    """
    blans = settings.global_().blockedLanguages()
    try:
      context = etree.iterparse(xmlfile, events=('start', 'end'))

      ret = {} if hash else []
      path = 0
      for event, elem in context:
        if checkexit and main.EXITED:
          return
        if event == 'start':
          path += 1
          if path == 3: # grimoire/comments/comment
            kw = {
              #'comment': "",
              #'updateComment': "",
              #'updateTimestamp':  0,
              #'updateUserId': 0,
              'id': int(elem.get('id')),
              'type': elem.get('type'),
              'disabled': elem.get('disabled') == 'true',
              'locked': elem.get('locked') == 'true',
              'language': '', # language not null
            }
        else:
          path -= 1
          if path == 3: # grimoire/comments/comment
            tag = elem.tag
            text = elem.text
            if tag in ('language', 'text', 'comment', 'updateComment', 'itemId'):
              kw[tag] = text or ''
            #elif tag in ('gameId', 'userId', 'timestamp', 'updateUserId', 'updateTimestamp'):
            elif tag.endswith('Id') or tag.endswith('Hash') or tag.endswith('Count') or tag.endswith('imestamp'):
              kw[tag] = int(text)
            elif tag == 'context':
              kw['context'] = text or ''
              kw['hash'] = long(elem.get('hash'))
              kw['contextSize'] = int(elem.get('size'))

          elif path == 2 and kw['type'] in Comment.TYPES and kw['language'][:2] not in blans: # grimoire/comments
            #if not kw.get('userHash'):
            #  kw['userHash'] = kw['userId']
            c = Comment(init=False, **kw)
            if not hash:
              ret.append(c)
            else:
              h = kw['hash']
              if h in ret:
                ret[h].append(c)
              else:
                ret[h] = [c]

      #self.comments, self.context = comments, contexts
      dprint("pass: load %i comments from %s" % (len(ret), xmlfile))
      return ret

    except etree.ParseError, e:
      dwarn("xml parse error", e.args)
    except (TypeError, ValueError, AttributeError), e:
      dwarn("xml malformat", e.args)
    except Exception, e:
      derror(e)

    dwarn("warning: failed to load xml from %s" % xmlfile)

  def backupCommentsXmlLater(self):
    pass
    #md5 = self.q.currentGameMd5()
    #if not md5:
    #  return
    #xmlfile = rc.comments_xml_path(md5=md5)
    #osutil.backup_file_later(xmlfile)

  def submitDirtyComments(self):
    if (not self.user.isLoginable() or
        not self.dirtyComments or
        not netman.manager().isOnline()):
      return
    dprint("enter")
    #if not self.dirtyCommentsMutex.tryLock():
    if self.dirtyCommentsLocked:
      self.submitDirtyCommentsLater()
    else:
      cursor = skcursor.SkAutoBusyCursor()
      self.dirtyCommentsLocked = True
      nm = netman.manager()
      for c in tuple(self.dirtyComments): # copy dirty comments into a new list
        cd = c.d
        async = not main.EXITED
        ok = True
        if cd.id:
          ok = nm.updateComment(c, self.user.name, self.user.password, async=async)
        elif not cd.deleted:
          ok = nm.submitComment(c, self.user.name, self.user.password, md5=c.gameMd5, async=async)
        if ok:
          c.clearDirtyProperties()
        else:
          growl.warn('<br/>'.join((
            my.tr("Failed to save changes, will try later"),
            cd.text,
          )))
      #self.dirtyCommentsMutex.unlock()
      self.dirtyCommentsLocked = False
    dprint("leave")

  def submitDirtyCommentsLater(self):
    try: self._submitCommentsTimer.start()
    except AttributeError:
      t = self._submitCommentsTimer = QTimer(self.q)
      t.setInterval(SUBMIT_INTERVAL)
      t.setSingleShot(True)
      t.timeout.connect(self.submitDirtyComments)
      t.start()
    #dprint("pass")

  def touchCharacters(self):
    self._charactersDirty = True
    self._saveCharactersLater()

  def touchComments(self):
    self._commentsDirty = True
    self._saveCommentsLater()

  def invalidateComments(self, md5): self.q.commentsChanged.emit(md5)

  def invalidateCharacters(self): self.q.charactersChanged.emit()

  #def _invalidateReferences(self, gameId):
  #  self.referencesChanged.emit(gameId)

  ## References ##

  def submitDirtyReferencesLater(self):
    try: self._submitRefsTimer.start()
    except AttributeError:
      t = self._submitRefsTimer = QTimer(self.q)
      t.setInterval(REF_SUBMIT_INTERVAL)
      t.setSingleShot(True)
      t.timeout.connect(self.submitDirtyReferences)
      t.start()

  def _updateGameItem(gameId, itemId):
    g = self.currentGame
    if g and g.id == gameId:
      g.itemId = itemId

    try:
      g = self.gameFiles[id]
      g.itemId = itemId
      self.touchGameFiles()
    except KeyError: pass

    if g:
      try:
        g = self.games[g.md5]
        g.itemId = itemId
        self.touchGames()
      except KeyError: pass
    else:
      for g in self.games.itervalues():
        if id == g.id:
          g.itemId = itemId
          self.touchGames()

    g = self.currentGame
    if g:
      self.currentGameIds = self.q.querySeriesGameIds(itemId=g.itemId) if g.itemId else [g.id] if g.id else []
    # need to invalidate translation cache here

  def submitDirtyReferences(self):
    if (not self.user.isLoginable() or
        not self.dirtyReferences or
        not netman.manager().isOnline()):
      return
    dprint("enter")
    #if not self.dirtyRefsMutex.tryLock():
    if self.dirtyReferencesLocked:
      self.submitDirtyReferencesLater()
    else:
      cursor = skcursor.SkAutoBusyCursor()
      self.dirtyRefererencesLocked = True
      nm = netman.manager()
      for t in tuple(self.dirtyReferences): # copy dirty terms into a new list
        async = not main.EXITED
        ok = True
        if t.id:
          ok = nm.updateReference(t, self.user.name, self.user.password, async=async)
        elif not t.deleted:
          ok = nm.submitReference(t, self.user.name, self.user.password, async=async)
        if ok and isinstance(ok, tuple):
          t.clearDirtyProperties()
          gameId, itemId = ok
          if gameId:
            self._updateGameItem(gameId=gameId, itemId=itemId)
        else:
          growl.warn('<br/>'.join((
            my.tr("Failed to save changes, will try later"),
            t.title,
          )))
      #self.dirtyReferencesMutex.unlock()
      self.dirtyReferencesLocked = False
    dprint("leave")

  ## Translation scripts ##

  #@staticmethod
  #def saveTranslationScripts(kw):
  #  """
  #  @param  kw  {str key:unicode data]
  #  @return  bool
  #  """
  #  try:
  #    for lang,path in config.TAHSCRIPT_LOCATIONS.iteritems():
  #      data = kw.get(lang)
  #      if data:
  #        dir = os.path.dirname(path)
  #        if not os.path.exists(dir):
  #          os.makedirs(dir)
  #        skfileio.removefile(path)
  #        if not skfileio.writefile(path, data):
  #          return False
  #    return True
  #  except Exception, e:
  #    dwarn(e)
  #  return False

  ## Terminologies ##

  def invalidateTerms(self): self.q.termsChanged.emit()

  def touchTerms(self):
    self._termsDirty = True
    self._saveTermsLater()

  def _saveTermsLater(self):
    try: self._saveTermsTimer.start()
    except AttributeError:
      t = self._saveTermsTimer = QTimer(self.q)
      t.setInterval(30 * 1000) # in 30 seconds
      t.setSingleShot(True)
      t.timeout.connect(self.saveTerms)
      t.start()

  def submitDirtyTermsLater(self):
    try: self._submitTermsTimer.start()
    except AttributeError:
      t = self._submitTermsTimer = QTimer(self.q)
      t.setInterval(SUBMIT_INTERVAL)
      t.setSingleShot(True)
      t.timeout.connect(self.submitDirtyTerms)
      t.start()
    #dprint("pass")

  def submitDirtyTerms(self):
    if (not self.user.isLoginable() or
        not self.dirtyTerms or
        not netman.manager().isOnline()):
      return
    dprint("enter")
    #if not self.dirtyTermsMutex.tryLock():
    if self.dirtyTermsLocked:
      self.submitDirtyTermsLater()
    else:
      cursor = skcursor.SkAutoBusyCursor()
      self.dirtyTermsLocked = True
      nm = netman.manager()
      for t in tuple(self.dirtyTerms): # copy dirty terms into a new list
        td = t.d
        async = not main.EXITED
        ok = True
        if td.id:
          ok = nm.updateTerm(t, self.user.name, self.user.password, async=async)
        elif not td.deleted:
          ok = nm.submitTerm(t, self.user.name, self.user.password, async=async)
        if ok:
          t.clearDirtyProperties()
        else:
          growl.warn('<br/>'.join((
            my.tr("Failed to save changes, will try later"),
            td.text,
          )))
      #self.dirtyTermsMutex.unlock()
      self.dirtyTermsLocked = False
    dprint("leave")

  def saveTerms(self): # -> bool
    if not self._termsDirty or not self.terms:
      return False
    if self.dirtyTermsLocked:
      dprint("warning: dirty terms are locked, save later")
      self._saveTermsLater()
      return False
    ok = rc.jinja_template_write_xml('terms',
      now=datetime.now(),
      timestamp=settings.global_().termsTime(),
      terms=self.iterTermData(),
    )
    if ok:
      dprint("pass: xml = terms")
    else:
      dwarn("failed: xml = terms")
    return ok

  def reloadTerms(self):
    """
    @return  long  timestamp or None
    """
    xmlfile = rc.xml_path('terms')
    self._termsDirty = False
    self.clearTerms()

    blans = settings.global_().blockedLanguages()

    if not os.path.exists(xmlfile):
      dprint("pass: xml not found, %s" % xmlfile)
      #self.q.gamesChanged.emit()
      return

    OLD_TYPES = {
      'escape': 'trans',
      'source': 'input',
      'target': 'output',
      #'name': 'name',
      #'yomi': 'yomi',
      'title': 'suffix',
      'origin': 'game',
      'speech': 'tts',
      'ocr': 'ocr',
      #'macro': 'macro',
    }

    try:
      #tree = etree.parse(xmlfile)
      #root = tree.getroot()
      #init = self.termsEditable # bool

      context = etree.iterparse(xmlfile, events=('start', 'end'))

      terms = []
      path = 0
      now = skdatetime.current_unixtime()
      timestamp = 0
      outdate_interval = 40 * 86400 # 1.5 month
      outdate_time = now - outdate_interval
      for event, elem in context:
        if event == 'start':
          path += 1
          if path == 1: # grimoire
            timestamp = elem.get('timestamp')
            #if timestamp:
            #  outdate_time = now - outdate_interval
          elif path == 3: # grimoire/terms/term
            type_ = elem.get('type')
            if type_:
              type_ = OLD_TYPES.get(type_) or type_
            kw = {
              #'gameId': 0,
              #'text': "",
              #'pattern': "",
              #'special': False,
              #'regex': False,
              #'icase': False,
              ##'bbcode': False,
              #'comment': "",
              #'updateComment': "",
              #'updateTimestamp':  0,
              #'updateUserId': 0,

              'id': int(elem.get('id')),
              'type': type_,
              'disabled': elem.get('disabled') == 'true',
              'language': '', # language not null
            }
        else:
          path -= 1
          if path == 3: # grimoire/terms/term
            tag = elem.tag
            text = elem.text
            if tag == 'priority':
              kw[tag] = float(text)
            elif tag in ('language', 'sourceLanguage', 'host', 'context', 'pattern', 'text', 'ruby', 'role', 'comment', 'updateComment'):
              kw[tag] = text or ''
            #if tag in ('gameId', 'userId', 'timestamp', 'updateUserId', 'updateTimestamp'):
            elif tag.endswith('Id') or tag.endswith('Hash') or tag.endswith('Count') or tag.endswith('imestamp'):
              kw[tag] = int(text)
            elif tag in ('special', 'private', 'hentai', 'regex', 'phrase', 'icase'):
              kw[tag] = text == 'true'

          elif path == 2 and kw['type'] in Term.TYPES and kw['language'][:2] not in blans:
            #if not kw.get('userHash'):
            #  kw['userHash'] = kw['userId']
            if kw.get('disabled'):
              t = kw.get('updateTimestamp') or kw.get('timestamp')
              if t and t < outdate_time:
                dprint("ignore outdated term: id = %s" % kw.get('id'))
                continue
            terms.append(Term(
                init=False,
                parent=self.q, # FIXME: increase PySide reference count
                **kw))

      if terms:
        self.terms = terms
        #self.termsInitialized = init
        #self.sortedTerms = None    # already cleared by clearTerms

        if timestamp:
          settings.global_().setTermsTime(timestamp)

        self.invalidateTerms()

        dprint("pass: load %i terms from %s" % (len(self.terms), xmlfile))
        return timestamp

    except etree.ParseError, e:
      dwarn("xml parse error", e.args)
    except (TypeError, ValueError, AttributeError), e:
      dwarn("xml malformat", e.args)
    except Exception, e:
      derror(e)
    #finally:
    #  self.q.termsChanged.emit()

    dwarn("warning: failed to load xml from %s" % xmlfile)

  # Update user
  def saveUserLanguage(self, language):
    """
    @param  language  unicode
    """
    u = self.user
    if language and u.language != language:
      u.language = language
      growl.msg(my.tr("Your {0} is '{1}'").format(
        tr_("language"), i18n.language_name(language)
      ))

      nm = netman.manager()
      if not u.isGuest() and nm.isOnline():
        skevents.runlater(partial(nm.updateUser,
            u.name, u.password, language=language))

  def saveUserGender(self, gender):
    """
    @param  gender  unicode
    """
    u = self.user
    if gender and u.gender != gender:
      u.gender = gender
      growl.msg(my.tr("Your {0} is '{1}'").format(
        tr_("gender"), i18n.gender_name(gender)
      ))

      nm = netman.manager()
      if not u.isGuest() and nm.isOnline():
        skevents.runlater(partial(nm.updateUser,
            u.name, u.password, gender=gender))

  def saveUserColor(self, color):
    """
    @param  color unicode
    """
    u = self.user
    if color and u.color != color:
      growl.msg(my.tr("Your {0} is '{1}'").format(
        tr_("color"),
        '<span style="color:%s">%s</span>' % (color, color),
      ))

      if color == defs.USER_DEFAULT_COLOR:
        color = ''
      u.color = color
      nm = netman.manager()
      if not u.isGuest() and nm.isOnline():
        skevents.runlater(partial(nm.updateUser,
            u.name, u.password, color=color))

class DataManager(QObject):

  termsChanged = Signal()
  termsEditableChanged = Signal(bool)
  gameFilesChanged = Signal()
  gameItemsChanged = Signal()
  #translationScriptsChanged = Signal()

  ## Construction ##

  #def iterReferenceDigests(self): return self.__d.iterReferenceDigests()

  def __init__(self, parent=None):
    super(DataManager, self).__init__(parent)
    d = self.__d = _DataManager(self)

    self.commentsChanged.connect(lambda md5:
      md5 == self.currentGameMd5() and self.commentCountChanged.emit(
          self.commentCount()))

    for sig in self.commentAdded, self.commentRemoved:
      sig.connect(lambda c:
        c.d.gameId == self.currentGameId() and self.commentCountChanged.emit(
            self.commentCount()))

    ss = settings.global_()
    ss.loginChanged.connect(self.login)
    ss.userLanguageChanged.connect(d.saveUserLanguage)
    ss.userGenderChanged.connect(d.saveUserGender)
    ss.userColorChanged.connect(d.saveUserColor)

    #ss.userLanguageChanged.connect(d.clearTermTitles)
    #ss.userLanguageChanged.connect(d.clearNameItems)

    qApp = QCoreApplication.instance()
    qApp.aboutToQuit.connect(d.submitDirtyComments)
    qApp.aboutToQuit.connect(d.submitDirtyTerms)
    qApp.aboutToQuit.connect(d.saveGames)
    qApp.aboutToQuit.connect(d.saveTerms)
    qApp.aboutToQuit.connect(d.saveComments)
    qApp.aboutToQuit.connect(d.saveCharacters)
    #qApp.aboutToQuit.connect(d.saveUsers)
    qApp.aboutToQuit.connect(d.saveGameFiles)

  """Emit when games changed"""
  gamesChanged = Signal()

  """Emit when login user changed"""
  loginChanged = Signal(unicode, unicode) # username, password

  """Emit when current comments are reloaded"""
  currentGameChanged = Signal()
  commentsChanged = Signal(str) # md5
  commentAdded = Signal(QObject) # Comment
  commentRemoved = Signal(QObject) # Comment

  referencesTouched = Signal()
  referencesChanged = Signal(int) # gameId

  #aboutToExportComments = Signal()

  def games(self):
    """Games in the library
    @yield  Game
    """
    return self.__d.games.itervalues()

  def user(self):
    """Should be const"""
    return self.__d.user

  def gamesByMd5(self):
    """Game dictionary indexed by md5 digest
    @return  {md5:Game}
    """
    return self.__d.games

  def comments(self):
    """Current comments
    @return  [Comment]
    """
    return list(self.__d.iterComments())

  def iterContextComments(self):
    """Game dictionary indexed by md5 digest
    @yeild  context, [comments]
    """
    d = self.__d
    if d.comments:
      for h, comments in d.comments.iteritems():
        try: context = d.contexts[h]
        except (TypeError, KeyError, OverflowError): context = ""
        yield context, comments

  #def refresh(self):
  #  """Synchronize the data with the online database"""
  #  self.__d.reloadUser()
  #  self.__d.reloadGames()

  def savingComments(self): return self.__d.dirtyCommentsLocked

  def reloadGames(self): self.__d.reloadGames()
  def reloadGameFiles(self): self.__d.reloadGameFiles()
  #def reloadReferenceDigests(self): self.__d.reloadReferenceDigests()
  def reloadGameItems(self): self.__d.reloadGameItems()
  def reloadUsers(self): self.__d.reloadUsers()

  def reloadTerms(self):
    """
    @return  long  timestamp or None
    """
    return self.__d.reloadTerms()

  def reloadUser(self): self.__d.reloadUser()

  def isGuest(self): return self.__d.user.isGuest()

  def isLogin(self): return self.__d.user.isLoginable()

  def login(self, userName, password):
    d = self.__d
    if d.user.name != userName or d.user.password != password:
      d.user.name = userName
      d.user.password = password
      d.reloadUser()

  def currentGame(self):
    return self.__d.currentGame
  def currentGameId(self):
    return self.__d.currentGame.id if self.__d.currentGame else 0
  def currentGameMd5(self):
    return self.__d.currentGame.md5 if self.__d.currentGame else ""
  def currentGameLanguage(self):
    return self.__d.currentGame.language if self.__d.currentGame else ''
  def currentGameIds(self):
    return self.__d.currentGameIds
  def currentGameItemId(self):
    return self.__d.currentGame.itemId if self.__d.currentGame else 0
  def currentGameObject(self):
    return self.__d.currentGameObject
  def currentGameName(self):
    md5 = self.currentGameMd5()
    return self.queryGameName(md5=md5) if md5 else ''
  def currentGameSeries(self):
    itemId = self.currentGameItemId()
    return self.queryItemSeries(itemId)
  def currentGameInfo(self):
    g = self.__d.currentGame
    if g:
      return self.queryGameInfo(id=g.id, md5=g.md5)

  def hasGames(self): return bool(self.__d.games)
  def hasGameFiles(self): return bool(self.__d.gameFiles)

  #def hasReferenceDigests(self): return bool(self.__d.referenceDigests)

  def hasGameItems(self): return bool(self.__d.gameItems)

  def hasUsers(self): return bool(self.__d.users)

  def containsGameMd5(self, md5, online=True):
    """
    @param  md5  str
    @param  online  whether query online database
    @return  bool
    """
    return online and md5 in self.__d.gameFilesByMd5 or md5 in self.__d.games

  def updateGameDatabase(self):
    if netman.manager().isOnline():
      self.updateGameFiles()
      self.updateGameItems()
      #self.updateReferenceDigests()
      self.updateUsers()
      # Disable caching images
      #self.updateGameImages()
    else:
      growl.warn(my.tr("Cannot connect to the Internet"))

  # Cache game images
  #def updateGameImages(self):
  #  dprint("enter")
  #  for it in self.__d.gameInfo:
  #    if it.image0:
  #      it.imageUrl0
  #    #if it.image:
  #    #  it.imageUrl
  #  dprint("leave")

  # Subtitles

  def clearSubtitles(self):
    self.__d.resetSubtitles()

  def querySubtitles(self, hash):
    """
    @param  hash  long
    @return  [Subtitle] or None
    """
    return self.__d.subtitleIndex.get(hash)

  def queryBestSubtitle(self, hash, text=""):
    """
    @param  hash  long
    @param* text  unicode
    @return  Subtitle or None
    """
    l = self.__d.subtitleIndex.get(hash)
    if l:
      for sub in l:
        if sub.equalText(text, exact=True):
          return sub
      return l[0]

  def hasSubtitles(self): # -> bool
    return bool(self.__d.subtitleIndex)

  def updateSubtitles(self, reset=False):
    itemId = self.currentGameItemId()
    if itemId:
      item = self.queryGameItem(id=itemId)
      if item and item.subtitleCount:
        self.__d.updateSubtitles(itemId, reset=reset)
        return
    growl.notify(my.tr("Subtitles not found"))

  # Users

  def queryUser(self, id=0, name=''):
    """
    @param* id  int
    @param* name  unicode
    @return  User or None
    """
    d = self.__d
    if id == GUEST_USER_ID:
      return GUEST
    elif id and id == d.user.id or name and name == d.user.name:
      return d.user
    elif id:
      return d.users.get(id)
    elif name:
      for it in d.users.itervalues():
        if it.name == name:
          return it

  def queryUserName(self, id):
    """
    @param* id  int
    @return  name  str or None
    """
    d = self.__d
    if id == GUEST_USER_ID:
      return GUEST.name
    elif id and id == d.user.id:
      return d.user.name
    else:
      u = d.users.get(id)
      if u:
        return u.name

  def queryUserColor(self, *args, **kwargs):
    """
    @return  unicode not None
    """
    u = self.queryUser(*args, **kwargs)
    return u.color if u else ""

  def _queryUserAvatar(self, id=0, name='', cache=False):
    """
    @param* id  int
    @param* name  unicode
    @param* cache  bool
    @return  unicode not None
    """
    u = self.queryUser(id=id, name=name)
    ret = u.avatar if u else ""
    if ret and cache:
      #skevents.runlater(partial(cacheman.manager().updateAvatar, ret))
      cacheman.manager().cacheAvatar(ret)
    return ret

  def queryUserAvatarUrl(self, id=0, hash=0, name='', cache=False):
    """
    @param* id  int
    @param* hash  int
    @param* name  unicode
    @param* size  str
    @param* cache  bool
    @return  unicode not None
    """
    av = self._queryUserAvatar(id, name=name, cache=cache)
    if not av:
      path = rc.random_avatar_path(hash or id)
      return osutil.path_url(path)
    path = rc.avatar_image_path(av)
    if os.path.exists(path):
      return osutil.path_url(path)
    else:
      return cacheman.avatarurl(av)

  def queryGameItem(self, id):
    """
    @param* id  long
    @return  GameItem or None
    """
    return self.__d.gameItems.get(id)

  def queryItemName(self, id):
    """
    @param* id  long
    @return  unicode not None
    """
    if id:
      g = self.__d.gameItems.get(id)
      if g:
        return g.title
    return ""

  def queryItemSeries(self, id):
    """
    @param* id  long
    @return  unicode not None
    """
    if id:
      g = self.__d.gameItems.get(id)
      if g:
        return g.series
    return ""

  def _iterItemGameIds(self, id):
    """
    @param* id  long  itemId
    @yield  long gameId
    """
    for g in self.__d.gameFiles.itervalues():
      if g.itemId == id:
        yield g.id

  def _iterSeriesItemIds(self, series):
    """
    @param  series  unicode
    @yield  long itemId
    """
    for g in self.__d.gameItems.itervalues():
      if g.series == series:
        yield g.id

  def querySeriesGameIds(self, itemId):
    """
    @param  itemId  long
    @return  set(long gameId) not None
    """
    dig = self.queryGameItem(itemId)
    if dig and dig.series:
      ret = set()
      for seriesItemId in self._iterSeriesItemIds(dig.series):
        for it in self._iterItemGameIds(seriesItemId):
          ret.add(it)
      return ret
    return set(self._iterItemGameIds(itemId))

  def queryItemGame(self, id):
    """
    @param* id  long  itemId
    @return  Game or None
    """
    for it in self.__d.games.itervalues():
      if it.itemId == id:
        return it

  def queryGameSeries(self, id=None, md5=None, itemId=None):
    """
    @param* id  long
    @param* md5  str
    @param* itemId  long
    @return  unicode or ''
    """
    if not itemId and (id or md5):
      itemId = self.queryGameItemId(id=id, md5=md5)
    if itemId:
      dig = self.queryGameItem(itemId)
      if dig:
        return dig.series
    return ''

  def queryGameName(self, id=None, md5=None):
    """
    @param* id  long
    @param* md5  str
    @return  unicode not None
    """
    if not id and not md5:
      return ""
    d = self.__d
    itemId = self.queryGameItemId(id=id, md5=md5)
    if itemId:
      g = self.__d.gameItems.get(itemId)
      if g:
        return g.title
      #digs = self.queryReferenceDigests(itemId=itemId)
      #if digs:
      #  for t in 'trailers', 'amazon', 'dmm':
      #    for r in digs:
      #      if r.type == t:
      #        return r.title
    if md5:
      try: return d.games[md5].name
      except KeyError: pass
      try: return d.gameFilesByMd5[md5].name
      except KeyError: pass
    elif id:
      for g in d.games.itervalues():
        if g.id == id:
          return g.name
      try: return d.gameFiles[id].name
      except KeyError: pass
    return ""

  def queryGameIcon(self, **kwargs):
    """
    @return  QIcon or None
    """
    g = self.queryGame(**kwargs)
    if g:
      return g.icon()

  def queryGameImageUrl(self, **kwargs):
    """
    @return  str not None
    """
    g = self.queryGameInfo(**kwargs)
    return g.imageUrl0 if g else ''

  def queryGameBackgroundImageUrl(self, **kwargs):
    """
    @return  str not None
    """
    g = self.queryGameInfo(**kwargs)
    return g.imageUrl0 if g and g.imageFitsBackground0() else ''

  def queryGameFileName(self, id=None, md5=None):
    """
    @param* id  long
    @param* md5  str
    @return  unicode not None
    """
    if id or md5:
      d = self.__d
      if md5:
        try: return d.games[md5].names['file'][0]
        except: pass
        try: return d.gameFilesByMd5[md5].name
        except KeyError: pass
      elif id:
        try:
          for g in d.games.itervalues():
            if g.id == id:
              return g.names['file'][0]
        except: pass
        try: return d.gameFiles[id].name
        except KeyError: pass
    return ''

  def queryGameId(self, md5):
    """
    @param  md5  str
    @return  long or None
    """
    try: return self.__d.games[md5].id
    except KeyError: pass
    try: return self.__d.gameFilesByMd5[md5].id
    except KeyError: pass

  def queryGameMd5(self, id):
    """
    @param  id  long
    @return  str or None
    """
    try: return self.__d.gameFiles[id].md5
    except KeyError: pass
    for g in self.__d.games.itervalues():
      if id == g.id:
        return g.md5

  def updateUsers(self):
    if netman.manager().isOnline():
      #growl.msg(my.tr("Updating user database online") + " ...")
      dprint("enter")
      users = netman.manager().getUsers()
      d = self.__d
      if not users:
        dwarn("failed to get user digests")
        #growl.warn('<br/>'.join((
        #  my.tr("Failed to update user database"),
        #  my.tr("Something might be wrong with the Internet connection"),
        #)))
      #elif d.users and len(users) == len(d.users):
      #  #growl.msg(my.tr("Game database is updated"))
      #  dprint("user digests are not changed")
      else:
        try:
          #d.userDigestsByName = {v.name:v for v in digests.itervalues()}
          d.users = users
          #dprint("digest count = %i" % len(d.users))
          dprint("succeed")
          d.saveUsers()
          #growl.msg(my.tr("Game database is updated"))
        except Exception, e:
          dwarn(e)
          #growl.warn('<br/>'.join((
          #  my.tr("Failed to update user database"),
          #  my.tr("Something might be wrong with the Internet connection"),
          #)))
      dprint("leave")

  def updateGameFiles(self):
    if netman.manager().isOnline():
      dprint("enter")
      growl.msg(my.tr("Updating game database online") + " ...")
      files = netman.manager().getGameFiles()
      d = self.__d
      if not files:
        growl.warn('<br/>'.join((
          my.tr("Failed to update game database"),
          my.tr("Something might be wrong with the Internet connection"),
        )))
      #elif d.gameFiles and len(files) == len(d.gameFiles):
      #  growl.msg(my.tr("Game database is updated"))
      else:
        try:
          d.gameFilesByMd5 = {v.md5:v for v in files.itervalues()}
          d.gameFiles = files
          d.repairGameItems()
          dprint("digest count = %i" % len(d.gameFiles))
          d._gameFilesDirty = True
          d._saveGameFilesLater()
          self.gameFilesChanged.emit()
          #growl.msg(my.tr("Game database is updated"))
        except Exception, e:
          dwarn(e)
          growl.warn('<br/>'.join((
            my.tr("Failed to update game database"),
            my.tr("Something might be wrong with the Internet connection"),
          )))
      dprint("leave")

  def updateGameItems(self):
    if netman.manager().isOnline():
      dprint("enter")
      #growl.msg(my.tr("Updating game database online") + " ...")
      items = netman.manager().getGameItems()
      d = self.__d
      if items:
        d.gameItems = items
        d._gameInfo = []
        dprint("digest count = %i" % len(d.gameItems))
        d.repairCurrentGame()
        d.saveGameItems()
        growl.msg(my.tr("Game database is updated"))
        self.gameItemsChanged.emit()
      dprint("leave")

  #def updateReferenceDigests(self):
  #  if netman.manager().isOnline():
  #    #growl.msg(my.tr("Updating game database online") + " ...")
  #    digests = netman.manager().getReferenceDigests()
  #    d = self.__d
  #    #if not digests:
  #    #  growl.warn('<br/>'.join((
  #    #    my.tr("Failed to update game database"),
  #    #    my.tr("Something might be wrong with the Internet connection"),
  #    #  )))
  #    #elif d.gameFiles and len(digests) == len(d.gameFiles):
  #    #  growl.msg(my.tr("Game database is updated"))
  #    if digests:
  #      try:
  #        d.referenceDigests = digests
  #        d._gameInfo = []
  #        dprint("digest count = %i" % len(d.referenceDigests))
  #        d.saveReferenceDigests()
  #        #growl.msg(my.tr("Game database is updated"))
  #      except Exception, e:
  #        dwarn(e)
  #        #growl.warn('<br/>'.join((
  #        #  my.tr("Failed to update game database"),
  #        #  my.tr("Something might be wrong with the Internet connection"),
  #        #)))

  def isTermsEditable(self): return self.__d.termsEditable

  def setTermsEditable(self, t):
    d = self.__d
    if d.termsEditable != t:
      d.termsEditable = t
      #if t and d.terms and not d.termsInitialized:
      #  dprint("initialize terms")
      #  d.termsInitialized = True
      #  for it in d.terms:
      #    it.init(self)
      self.termsEditableChanged.emit(t)

  def updateTerms(self, reset=False):
    """
    @param* reset  whether do incremental update
    """
    d = self.__d
    if d.updateTermsLocked:
      growl.notify(my.tr("Waiting for dictionary update") + " ...")
    elif netman.manager().isOnline():
      d.updateTermsLocked = True
      dprint("enter")
      if reset:
        growl.msg(my.tr("Redownload the entire dictionary terms") + " ...")
      else:
        growl.msg(my.tr("Update dictionary terms incrementally") + " ...")

      #editable = d.termsEditable
      ss = settings.global_()
      updateTime = ss.termsTime()
      now = skdatetime.current_unixtime()

      l = d.terms
      nm = netman.manager()
      incremental = bool(not reset and updateTime and l) # bool
      if incremental:
        result = nm.mergeTerms(l, updateTime,
            d.user.name, d.user.password, init=False) #, parent=self)
        if not result:
          l = None
        else:
          l, now = result
      else:
        result = nm.getTerms(d.user.name, d.user.password, init=False) #, parent=self)
        if not result:
          l = None
        else:
          l, now = result
          result = nm.mergeTerms(l, now,
              d.user.name, d.user.password, init=False) #, parent=self)
          if result:
            l, now = result
      if l:
        #if not editable and editable != d.termsEditable:
        #  for it in l:
        #    it.init(self)

        d.clearTerms()

        d.terms = l
        #d.termsInitialized = d.termsEditable

        dprint("term count = %i" % len(d.terms))
        d.touchTerms()
        d.invalidateTerms()
        #with SkProfiler(): # 12/8/2014: 0.7240298 seconds
        if d.saveTerms():
          ss.setTermsTime(now)
        growl.msg(my.tr("Found {0} terms").format(len(d.terms)))
      elif incremental and l == []:
        growl.msg(my.tr("No changes found for Shared Dictionary"))
        ss.setTermsTime(now)
      else:
        growl.warn('<br/>'.join((
          my.tr("Failed to download terms online"),
          my.tr("Something might be wrong with the Internet connection"),
        )))
      d.updateTermsLocked = False
      dprint("leave")

  #def updateTranslationScripts(self):
  #  if netman.manager().isOnline():
  #    dprint("enter")
  #    growl.msg(my.tr("Updating translation scripts online") + " ...")
  #
  #    data = netman.manager().getTranslationScripts()
  #    if not data:
  #      growl.warn('<br/>'.join((
  #        my.tr("Failed to download translation scripts online"),
  #        my.tr("Something might be wrong with the Internet connection"),
  #      )))
  #    elif not self.__d.saveTranslationScripts(data):
  #      growl.warn(my.tr("Failed to save translation scripts to the disk"))
  #    else:
  #      self.translationScriptsChanged.emit()
  #      import trscriptman
  #      count = trscriptman.manager().scriptCount()
  #      if not count:
  #        growl.warn(my.tr("Failed to save translation scripts to the disk"))
  #      else:
  #        settings.global_().setTranslationScriptTime(skdatetime.current_unixtime())
  #        growl.msg(my.tr("Found {0} translation rules").format(count))
  #    dprint("leave")

  def queryReferences(self, gameId=0, init=True, online=False, onlineLater=False):
    """
    @param  gameId  long
    @param* init  bool
    @param* online  bool  check online first
    @param* onlineLater  bool  check online later
    @return  [Reference] or [], not None
    """
    if online:
      ret = netman.manager().queryReferences(gameId=gameId, init=init)
    else: # parent is None ^^
      ret = _DataManager.loadReferences(gameId=gameId, init=init)
      if not ret and onlineLater:
        ret = netman.manager().queryReferences(gameId=gameId, init=init)
    if online or onlineLater:
      if ret:
        self.saveReferences(ret, gameId)
      elif ret is not None:
        _DataManager.removeReferences(gameId=gameId)
    return ret or []

  def containsReferences(self, gameId=None, md5=None):
    """
    @param  gameId  int
    @param  md5
    @return bool
    """
    if not gameId and md5:
      gameId = self.queryGameId(md5)
    if not gameId:
      return False
    xmlfile = rc.refs_xml_path(gameId=gameId)
    return os.path.exists(xmlfile)

  def queryReferenceData(self, gameId, **kwargs):
    """
    @param  gameId  long
    @param* online  bool
    @param* onlineLater  bool
    @yield  _Reference
    """
    l = self.queryReferences(gameId=gameId, init=False, **kwargs)
    for ref in l:
      rd = ref.d
      #if rd.gameId == gameId and not rd.disabled:
      if not rd.disabled:
        yield rd

  #def queryReferenceDigests(self, itemId):
  #  """
  #  @param  itemId  long
  #  @return  [ReferenceDigest] not None
  #  """
  #  return self.__d.referenceDigests.get(itemId) or []

  def getGameInfo(self):
    """
    @return  [GameInfo] not None
    """
    return self.__d.gameInfo

  #def hasNameItems(self):
  #  """
  #  @return  bool
  #  """
  #  return bool(self.__d.nameItems)

  #def iterNameItems(self):
  #  """
  #  @return  [NameItems] not None
  #  """
  #  return self.__d.nameItems

  def queryGameInfo(self, id=None, md5=None, itemId=None, cache=True):
    """
    @param* id  long
    @param* md5  unicode
    @param* itemId  long
    @param* cache
    @return  Game or None
    """
    ret = None
    if not id and md5:
      id = self.queryGameId(md5)
    if not itemId:
      itemId = self.queryGameItemId(id=id, md5=md5)
    d = self.__d
    if itemId and cache and d.containsGameInfo(itemId=itemId):
      for it in d.gameInfo:
        if itemId == it.itemId:
          ret = it
          if ret.empty:
            ret = None
    if not ret and (id or itemId):
      ret = GameInfo(gameId=id, itemId=itemId)
      if ret.empty:
        ret = None
    return ret

  def queryGameFile(self, id=0, md5=""):
    """
    @param* gameId
    @param* md5  str
    @return  GameFile or None
    """
    for it in self.__d.gameFiles.itervalues():
      if id and id == it.id or md5 and md5 == it.md5:
        return it

  def queryGameObject(self, parent=None, digest=False, id=None, md5=None, **kwargs):
    """
    @param  parent  QObject
    @param  local  bool
    @param* gameId  long
    @param* md5  str
    @return  gameman.GameObject or None
    """
    g = self.queryGame(id=id, md5=md5, **kwargs)
    if g:
      return GameObject(parent=parent, game=g)
    if digest:
      dig = self.queryGameFile(id=id, md5=md5)
      if dig:
        return GameObject(parent=parent, game=dig)

  def queryGame(self, id=None, md5=None, itemId=None, online=False):
    """
    @param* id  long
    @param* md5  unicode
    @param* online  whether query online
    @return  Game or None
    """
    if not id and not md5 and itemId:
      return self.queryItemGame(itemId)
    if not id and md5:
      id = self.queryGameId(md5)
    elif not md5 and id:
      md5 = self.queryGameMd5(id)
    return self.__d.games.get(md5) or (
        netman.manager().queryGame(id=id, md5=md5) if online and netman.manager().isOnline() else
        None)

  def queryGameItemId(self, id=None, md5=None):
    """
    @param* id  long
    @param* md5  unicode
    @return  long or None
    """
    if not id and not md5:
      return
    d = self.__d
    if id:
      g = d.gameFiles.get(id)
    else:
      g = d.gameFilesByMd5.get(md5)
    if not g:
      if not md5:
        md5 = self.queryGameMd5(id)
      g = d.games.get(md5)
    if g:
      return g.itemId

  def queryGameFiles(self, itemId):
    """
    @param  itemId  long
    @return  [GameFile] not None
    """
    ret = []
    if itemId:
      for it in self.__d.gameFiles.itervalues():
        if itemId == it.itemId:
          ret.append(it)
    return ret

  def queryGameFile(self, id=None, md5=None, itemId=None):
    """
    @param* id  long
    @param* md5  unicode
    @param* itemId  long
    @return  GameFile or None
    """
    d = self.__d
    if itemId:
      ret = GameFile(itemId=itemId)
      for it in d.gameFiles.itervalues():
        if itemId == it.itemId:
          ret.visitCount += it.visitCount
          ret.commentCount += it.commentCount
      return ret
    if id: return d.gameFiles.get(id)
    if md5: return d.gameFilesByMd5.get(md5)

  def removeGame(self, md5):
    self.__d.removeGame(md5)

  def addGame(self, path, md5=None):
    """
    @param  path  unicode
    @param  md5  str
    """
    nm = netman.manager()
    #if not nm.isOnline():
    #  dwarn("cannot add new game when offline");
    #  return
    if not path:
      dwarn("missing path");
      return

    import procutil
    if procutil.is_blocked_process_path(path):
      dwarn("blocked file name")
      growl.warn(my.tr("Please do not add non-game program to VNR!"))
      return

    if not md5:
      np = osutil.normalize_path(path)
      md5 = hashutil.md5sum(np)
      if not md5:
        dwarn("failed to hash game executable")
        growl.warn(my.tr("Failed to read game executable"))
        return
    d = self.__d
    if md5 in d.games:
      dwarn("game md5 already exists")
      growl.notify(my.tr("The game already exists"))
      return

    g = None
    if nm.isOnline():
      growl.msg(my.tr("Searching game information online") + " ...")
      g = nm.queryGame(md5=md5)
    if not g:
      growl.notify("<br/>".join((
          my.tr("It seems to be an unknown game."),
          my.tr("Please manually adjust Text Settings after launching the game."))))
      g = Game.createEmptyGame()

    g.md5 = md5

    fileName = os.path.basename(path)
    if not g.names['file']:
      g.names['file'].append(fileName)

    g.visitTime = skdatetime.current_unixtime()
    g.visitCount = 1

    growl.msg(my.tr("Found new game") + ":" "<br/>" + g.name)
    g.path = path
    d.games[md5] = g
    d.touchGames()

  def increaseGameTopicCount(self, itemId):
    """
    @param  itemId  long
    """
    item = self.queryGameItem(id=itemId)
    if item:
      item.topicCount += 1
      self.__d.touchGameFiles()

  def addGameScore(self, itemId, ecchiScore=None, overallScore=None):
    """
    @param  itemId  long
    @param* ecchiScore  int or None
    @param* overallScore  int or None
    """
    item = self.queryGameItem(id=itemId)
    if item:
      if ecchiScore is not None:
        item.ecchiScoreCount += 1
        item.ecchiScoreSum += ecchiScore
      if overallScore is not None:
        item.overallScoreCount += 1
        item.overallScoreSum += overallScore
      self.__d.touchGameFiles()

  def loadGame(self, game):
    d = self.__d
    d.saveComments()
    d.currentGame = None
    d.currentGameObject = None
    d.currentGameIds = []
    #d.clearTermTitles()
    #d.clearNameItems()
    #mecabman.manager().clearDictionary()
    if not game:
      return
    if not game.id and not game.md5:
      dwarn("error: missing game id and md5 digest")
      return

    if not game.id:
      game.id = self.queryGameId(game.md5) or 0
    elif not game.md5:
      game.md5 = self.queryGameMd5(game.id) or ""

    g = d.games.get(game.md5)
    oldCommentCount = g.commentCount if g else 0

    # Update twice as updateGame might be blocked when online
    dprint("change current game")
    g = d.currentGame = d.games.get(game.md5)
    d.currentGameObject = None
    d.currentGameIds = self.querySeriesGameIds(itemId=g.itemId) if g and g.itemId else [g.id] if g and g.id else []

    if not d.updateGame(game):
      growl.warn(my.tr("Failed to get game information"))
      return

    # Update twice as updateGame might be blocked when online
    dprint("update current game")
    g = d.currentGame = d.games.get(game.md5)
    d.currentGameObject = None
    d.currentGameIds = self.querySeriesGameIds(itemId=g.itemId) if g.itemId else [g.id] if g.id else []

    if not g.id:
      dwarn("missing game ID!")

    t = g.refsUpdateTime
    if t + config.APP_UPDATE_REFS_INTERVAL < skdatetime.current_unixtime():
      if g.itemId and g.itemId < defs.MIN_NORMAL_GAME_ITEM_ID:
        dprint("found non-normal game, ignore refs")
      else:
        dprint("schedule to update game refs")
        skevents.runlater(self.updateReferences, 5000)

    commentCount = g.commentCount

    #if commentCount and commentCount != oldCommentCount:
    t = g.commentsUpdateTime
    online = not t or t + config.APP_UPDATE_COMMENTS_INTERVAL < skdatetime.current_unixtime()
    #else:
    #  online = False

    dprint("load comment online = %s" % online)
    d.reloadCharacters()
    d.reloadComments(online=online)
    d.reloadSubtitles(g.itemId)
    self.currentGameChanged.emit()

    #gid = self.currentGameId()
    #if gid:
    #if mecabman.manager().isEnabled() and mecabman.manager().supportsUserDic():
    #  dprint("update game-specicfic translation")
    #  skevents.runlater(d.updateNameItems, 3000) # delay a little

  def reloadComments(self):
    d = self.__d
    if d.currentGame:
      d.saveComments()
      d.reloadComments()

  def updateGame(self, game, deleteHook=False, online=True):
    """
    @param[inout]  game  Game  id/md5 will be updated after submission
    @param  deleteHook  bool
    @param  online  bool  if enable online access
    """
    if not game:
      return
    if not game.id and not game.md5:
      dwarn("error: missing game id and md5 digest")
      return
    d = self.__d
    if not d.updateGame(game, deleteHook=deleteHook, online=online):
      growl.warn(my.tr("Failed to get game information"))
      return

    if (game.id and game.id == self.currentGameId() or
        game.md5 and game.md5 == self.currentGameMd5()):
      g = d.currentGame = d.games[game.md5]
      d.currentGameObject = None
      d.currentGameIds = self.querySeriesGameIds(itemId=g.itemId) if g.itemId else [g.id]
      #d.backupGamesXmlLater()

  def setGameName(self, name, md5):
    """Either id or md5 should be given
    @param  name unicode
    @param  md5  str
    """
    g = self.__d.games.get(md5)
    if not g:
      growl.warn('<br/>'.join((
        my.tr("The game does not exist. Did you delete it?"),
        name,
      )))
      return
    if g.name == name:
      return
    g.userDefinedName = name
    self.__d.touchGames()
    #self.__d.backupGamesXmlLater()

  def setGameLocation(self, path, md5):
    """Either id or md5 should be given
    @param  path unicode not None
    @param  md5  str
    """
    g = self.__d.games.get(md5)
    if not g:
      growl.warn('<br/>'.join((
        my.tr("The game does not exist. Did you delete it?"),
        path,
      )))
      return
    if g.path == path:
      return
    g.path = path
    self.__d.touchGames()
    #self.__d.backupGamesXmlLater()

  def setGameLanguage(self, language, md5):
    """Either id or md5 should be given
    @param  language  str not None
    @param  md5  str
    """
    g = self.__d.games.get(md5)
    if not g:
      growl.warn('<br/>'.join((
        my.tr("The game does not exist. Did you delete it?"),
        path,
      )))
      return
    if g.language == language:
      return
    g.language = language
    self.__d.touchGames()

  def setGameLaunchLanguage(self, language, md5):
    """Either id or md5 should be given
    @param  language  str not None
    @param  md5  str
    """
    g = self.__d.games.get(md5)
    if not g:
      growl.warn('<br/>'.join((
        my.tr("The game does not exist. Did you delete it?"),
        path,
      )))
      return
    if g.launchLanguage == language:
      return
    g.launchLanguage = language
    self.__d.touchGames()

  def setGameLaunchPath(self, path, md5):
    """Either id or md5 should be given
    @param  path  unicode not None
    @param  md5  str
    """
    g = self.__d.games.get(md5)
    if not g:
      growl.warn('<br/>'.join((
        my.tr("The game does not exist. Did you delete it?"),
        path,
      )))
      return
    if g.launchPath == path:
      return
    g.launchPath = path
    self.__d.touchGames()
    #self.__d.backupGamesXmlLater()

  def setGameLoader(self, loader, md5):
    """Either id or md5 should be given
    @param  loader  unicode
    @param  md5  str
    """
    #dprint(loader)
    g = self.__d.games.get(md5)
    if not g:
      growl.warn('<br/>'.join((
        my.tr("The game does not exist. Did you delete it?"),
        loader,
      )))
      return
    if g.loader == loader:
      return
    g.loader = loader
    self.__d.touchGames()
    #self.__d.backupGamesXmlLater()

  def setGameTimeZone(self, value, md5):
    """Either id or md5 should be given
    @param  value  bool or None
    @param  md5  str
    """
    #dprint(value)
    g = self.__d.games.get(md5)
    if not g:
      growl.warn('<br/>'.join((
        my.tr("The game does not exist. Did you delete it?"),
        loader,
      )))
      return
    if g.timeZoneEnabled == value:
      return
    g.timeZoneEnabled = value
    self.__d.touchGames()
    #self.__d.backupGamesXmlLater()

  def setGameAgentDisabled(self, t, md5):
    """Either id or md5 should be given
    @param  t  bool
    @param  md5  str
    """
    dprint(t)
    g = self.__d.games.get(md5)
    if not g:
      growl.warn('<br/>'.join((
        my.tr("The game does not exist. Did you delete it?"),
        loader,
      )))
      return
    if g.gameAgentDisabled == t:
      return
    g.gameAgentDisabled = t
    self.__d.touchGames()
    #self.__d.backupGamesXmlLater()

  def setGameHookEnabled(self, enabled, md5):
    """Either id or md5 should be given
    @param  enabled  bool or None
    @param  md5  str
    """
    dprint(enabled)
    g = self.__d.games.get(md5)
    if not g:
      growl.warn(my.tr("The game does not exist. Did you delete it?"))
      return
    disabled = not enabled
    if g.hookDisabled == disabled:
      return
    g.hookDisabled = disabled
    self.__d.touchGames()
    #self.__d.backupGamesXmlLater()

  #def setGameHookKept(self, kept, md5):
  #  """Either id or md5 should be given
  #  @param  kept  bool or None
  #  @param  md5  str
  #  """
  #  g = self.__d.games.get(md5)
  #  if not g:
  #    growl.warn(my.tr("The game does not exist. Did you delete it?"))
  #    return
  #  if g.hookKept == kept:
  #    return
  #  g.hookKept = kept
  #  self.__d.touchGames()
  #  #self.__d.backupGamesXmlLater()

  def setGameVoiceDefaultEnabled(self, enabled, md5):
    """Either id or md5 should be given
    @param  enabled  bool
    @param  md5  str
    """
    dprint(enabled)
    g = self.__d.games.get(md5)
    if not g:
      growl.warn(my.tr("The game does not exist. Did you delete it?"))
      return
    if g.voiceDefaultEnabled == enabled:
      return
    g.voiceDefaultEnabled = enabled
    self.__d.touchGames()
    #self.__d.backupGamesXmlLater()

  def setGameOtherThreads(self, threads, md5):
    """Either id or md5 should be given
    @param  name unicode
    @param  md5  str
    """
    g = self.__d.games.get(md5)
    if not g:
      growl.warn('<br/>'.join((
        my.tr("The game does not exist. Did you delete it?"),
        name,
      )))
      return
    g.otherThreads = threads
    self.__d.touchGames()
    #self.__d.backupGamesXmlLater()

  #def disableGameNameThread(self, md5, online=True):
  #  """Either id or md5 should be given
  #  @param  md5  str
  #  """
  #  g = self.__d.games.get(md5)
  #  if not g:
  #    growl.warn('<br/>'.join((
  #      my.tr("The game does not exist. Did you delete it?"),
  #      name,
  #    )))
  #    return
  #  if not g.nameThreadDisabled:
  #    g.nameThreadDisabled = True
  #    self.__d.touchGames()
  #    if online:
  #      game = Game(nameThreadDisabled=True)
  #      ok = nm.updateGame(game, self.user.name, self.user.password)
  #    #self.__d.backupGamesXmlLater()

  #def setGameHook(self, hcode, md5):
  #  """Either id or md5 should be given
  #  @param  hcode unicode not None
  #  @param  md5  str
  #  """
  #  g = self.__d.games.get(md5)
  #  if not g:
  #    growl.warn('<br/>'.join((
  #      my.tr("The game does not exist. Did you delete it?"),
  #      hcode,
  #    )))
  #    return
  #  if g.hook == hcode:
  #    return
  #  g.hook = hcode
  #  self.__d.touchGames()
  #  #self.__d.backupGamesXmlLater()

  def hasComments(self): return bool(self.__d.comments)

  commentCountChanged = Signal(int)
  def commentCount(self): return len(self.__d.comments)

  def queryComments(self, hash=None, hash2=None, md5=None, online=False):
    """
    @param  hash  long  data hash
    @param  hash2  long  text hash
    @param  md5  unicode
    @param* online  bool
    @return  [Comment] or [], not None
    """
    if md5:
      if hash:
        derror("This code path should never happen")
      if online:
        if md5 == self.currentGameMd5():
          derror("This code path should never happen")
          self.reloadComments()
          return self.comments()
        else:
          gameId = self.queryGameId(md5)
          ret = netman.manager().queryComments(gameId=gameId, md5=md5, hash=False)
          if not ret and ret is not None:
            _DataManager.removeComments(md5=md5)
          return ret or []
      else:
        if md5 == self.currentGameMd5(): return self.comments()
        return _DataManager.loadComments(md5=md5, hash=False) or []
    elif hash:
      return self.__d.comments.get(hash) or []
    elif hash2:
      return self.__d.comments2.get(hash2) or []
    return []

  def queryContext(self, hash=None):
    """
    @return  str or None
    """
    try: return self.__d.contexts[hash]
    except (KeyError, TypeError, AttributeError): pass

  def updateContext(self, hash, text):
    """
    @param  hash  long not c_longlong
    @param  text  unicode
    """
    if hash and text:
      try: self.__d.contexts[hash] = text
      except (KeyError, TypeError, AttributeError): pass

  charactersChanged = Signal()

  def characters(self): return self.__d.characters.values()
  def queryCharacter(self, name):
    """
    @param  name  unicode
    @return  Character or None
    """
    return self.__d.characters.get(name or '')

  def addCharacter(self, name):
    """
    @param  name  unicode
    """
    d = self.__d
    if name not in d.characters:
      g = d.currentGame
      enabled = g.voiceDefaultEnabled if g else False
      d.characters[name] = Character(parent=self, name=name, ttsEnabled=enabled)
      d.touchCharacters()
      d.invalidateCharacters()

  def touchCharacters(self): self.__d.touchCharacters()

  ## References ##

  def addDirtyReference(self, ref):
    d = self.__d
    d.dirtyReferences.add(ref)
    d.submitDirtyReferencesLater()
    #d.touchReferences()

  def removeDirtyReference(self, ref):
    try: self.__d.dirtyReferences.remove(ref)
    except KeyError: pass

  def submitDirtyReferences(self): self.__d.submitDirtyReferences()

  def submitReference(self, ref, commit=True):
    """
    @param[inout]  ref  Reference
    @param  commit  bool  submit now!
    @return  bool  if succeed
    """
    if not ref:
      return False
    ref.id = 0 # reset reference ID

    gameId = ref.gameId #or self.currentGameId()
    if not gameId:
      growl.warn(my.tr("Unknown game. Please try updating the database."))
      dwarn("warning: no game ID")
      return False

    d = self.__d
    if not d.user.isLoginable():
      growl.warn(my.tr("Please sign in to submit reference"))
      dwarn("failed: not login")
      return False

    if commit:
      d.dirtyReferences.add(ref)
      d.submitDirtyReferencesLater()
      #d.touchReferences()
      #d.backupReferencesXmlLater()

    nm = netman.manager()
    if not nm.isOnline():
      nm.updateOnline()
      if not nm.isOnline():
        growl.warn(my.tr("Cannot connect to the Internet"))

    refman.manager().cache(type=ref.type, key=ref.queryKey)

    #self.referenceAdded.emit(ref)
    #self.invalidateReferences(md5)
    return True

  @staticmethod
  def saveReferences(refs, gameId):
    """
    @param  refs  [References]
    @param  gameId  long
    """
    if not gameId:
      return

    xmlfile = rc.refs_xml_path(gameId=gameId)
    if not refs:
      if os.path.exists(xmlfile):
        try: os.path.remove(xmlfile)
        except Exception, e: dwarn(e)
      return
    ok = rc.jinja_template_write(xmlfile, 'xml/refs',
      now=datetime.now(),
      refs=(it.d for it in refs),
    )
    if ok:
      dprint("pass: xml = %s" % xmlfile)

      g = manager().queryGame(id=gameId)
      if g:
        g.refsUpdateTime = skdatetime.current_unixtime()
    else:
      dwarn("failed: xml = %s" % xmlfile)

  def touchGames(self): self.__d.touchGames()

  def updateReferences(self, gameId=0):
    """
    @param* gameId  long
    @return  [Reference] or None
    """
    if not gameId:
      gameId = self.currentGameId()
      if not gameId:
        return
    if not netman.manager().isOnline():
      return
    l = manager().queryReferences(gameId=gameId, online=True)
    if l:
      l.sort(key=operator.attrgetter('modifiedTimestamp'))
      self.saveReferences(l, gameId=gameId)
      self.referencesChanged.emit(gameId)
      dprint("found %s game references" % len(l))
      return l
    else:
      dprint("no game references")

  def touchReferences(self):
    self.referencesTouched.emit()

  ## Comments ##

  def invalidateComments(self, md5):
    """Notify the dataman that the comment count is Changed
    @param  md5  str
    """
    self.__d.invalidateComments(md5)

  def removeComment(self, c):
    """
    @param  c  Comment
    """
    self.commentRemoved.emit(c)

  def submitComment(self, comment, commit=True):
    """
    @param[inout]  comment Comment
    @param  commit  bool  submit now!
    @return  bool  if succeed
    """
    if not comment:
      return False
    comment.id = 0 # reset comment ID

    md5 = comment.gameMd5 or self.currentGameMd5()
    if not md5:
      growl.warn(my.tr("Please start the game to submit comment"))
      dwarn("warning: no running game")
      return False

    d = self.__d
    if not d.user.isLoginable():
      growl.warn(my.tr("Please sign in to submit comment"))
      dwarn("failed: not login")
      return False

    if comment.context:
      d.contexts[comment.hash] = comment.context

    if comment.hash in d.comments:
      d.comments[comment.hash].append(comment)
    else:
      d.comments[comment.hash] = [comment]

    if commit:
      d.dirtyComments.add(comment)
      d.submitDirtyCommentsLater()
      d.touchComments()
      d.backupCommentsXmlLater()

    nm = netman.manager()
    if not nm.isOnline():
      nm.updateOnline()
      if not nm.isOnline():
        growl.warn(my.tr("Cannot connect to the Internet"))

    self.commentAdded.emit(comment)
    #self.invalidateComments(md5)
    return True

  def touchComments(self): self.__d.touchComments()

  def addDirtyComment(self, comment):
    d = self.__d
    d.dirtyComments.add(comment)
    d.submitDirtyCommentsLater()
    d.touchComments()

  def removeDirtyComment(self, comment):
    try: self.__d.dirtyComments.remove(comment)
    except KeyError: pass

  def submitDirtyComments(self): self.__d.submitDirtyComments()

  ## Terminologies ##

  def hasTerms(self): return bool(self.__d.terms)

  def terms(self):
    """Used by TermModel
    @return  [Term]
    """
    return self.__d.terms

  def queryTerm(self, id):
    """
    @param  id  long
    @return  Term
    """
    for it in self.__d.terms:
      if it.d.id == id:
        return it

  def queryTermData(self, *args, **kwargs):
    """
    @param  id  long
    @return  _Term
    """
    t = self.queryTerm(*args, **kwargs)
    if t:
      return t.d

  def removeTerm(self, term):
    """
    @param  term  Term
    """
    d = self.__d
    try: d.terms.remove(term)
    except ValueError:
      dwarn("failed to remove term")
      return

    #term.deleted = True
    #try: d._sortedTerms.remove(term)
    #except: pass

    #if term.isInitialized():
    #  try:
    #    if term.parent():
    #      skevents.runlater(partial(term.setParent, None), 90000) # after 1.5 min
    #  except Exception, e:
    #    dwarn(e)

    d.invalidateTerms()
    d.touchTerms()

  def deleteSelectedTerms(self, updateComment='', append=True):
    """
    @param* updateComment  unicode
    @param* append  bool
    """
    d = self.__d
    userId = d.user.id
    if not userId:
      return
    data = d.terms
    if not data:
      return

    userLevel = d.user.termLevel

    count = 0

    for t in data:
      td = t.d
      if td.selected and not td.deleted:
        if not ( # the same as canEdit permission in qml
          userId == ADMIN_USER_ID or
          td.userId == userId and not td.protected or
          td.userId == GUEST_USER_ID and userLevel > 0):
          growl.warn('<br/>'.join((
            my.tr("Editing other's entry is not allowed"),
            tr_("User") + ": " + td.userName,
            tr_("Pattern") + ": " + td.pattern,
            tr_("Text") + ": " + td.text,
          )))
          continue
        count += 1
        if updateComment:
          t.updateComment = "%s // %s" % (updateComment, td.updateComment) if (append and
            td.updateComment and td.updateComment != updateComment and not td.updateComment.startswith(updateComment + ' //')
          ) else updateComment
        t.deleted = True
        #if t.isInitialized():
        #  try:
        #    if t.parent():
        #      skevents.runlater(partial(t.setParent, None), 120000) # after 2 min
        #  except Exception, e:
        #    dwarn(e)

    if count:
      d.terms = [t for t in d.terms if not (t.d.selected and t.d.deleted)]
      #if d._sortedTerms:
      #  d._sortedTerms = [t for t in d._sortedTerms if not (t.d.selected and t.d.deleted)]

      d.invalidateTerms()
      d.touchTerms()

      growl.msg(my.tr("{0} items updated").format(count))

  def updateSelectedTermsEnabled(self, value, updateComment='', append=True):
    """
    @param  value  bool
    @param* updateComment  unicode
    @param* append  bool
    """
    d = self.__d
    userId = d.user.id
    if not userId:
      return
    data = d.terms
    if not data:
      return

    userLevel = d.user.termLevel

    now = skdatetime.current_unixtime()

    count = 0
    for t in data:
      td = t.d
      if td.selected and td.disabled == value:
        if not ( # the same as canImprove permission in qml
          userId != GUEST_USER_ID or
          td.userId == userId and not td.protected or
          td.userId == GUEST_USER_ID and userLevel > 0):
          growl.warn('<br/>'.join((
            my.tr("Editing other's entry is not allowed"),
            tr_("User") + ": " + td.userName,
            tr_("Pattern") + ": " + td.pattern,
            tr_("Text") + ": " + td.text,
          )))
          continue
        count += 1
        t.updateUserId = userId
        t.updateTimestamp = now
        t.disabled = not value
        if updateComment:
          t.updateComment = "%s // %s" % (updateComment, td.updateComment) if (append and
            td.updateComment and td.updateComment != updateComment and not td.updateComment.startswith(updateComment + ' //')
          ) else updateComment

    if count:
      growl.msg(my.tr("{0} items updated").format(count))

    #d.terms = [t for t in d.terms if not (t.d.selected and t.d.deleted)]
    #if d._sortedTerms:
    #  d._sortedTerms = [t for t in d._sortedTerms if not (t.d.selected and t.d.updateTimestamp == now)]

    #d.invalidateTerms()
    #d.touchTerms()

  def commentSelectedTerms(self, value, type='comment', append=True):
    """
    @param  value  unicode
    @param* type  'comment' or 'updateComment'
    @param* append  bool
    """
    d = self.__d
    userId = d.user.id
    if not userId:
      return
    data = d.terms
    if not data:
      return

    userLevel = d.user.termLevel

    now = skdatetime.current_unixtime()

    count = 0

    for t in data:
      td = t.d
      if td.selected:
        if type == 'comment':
          if not ( # the same as canEdit permission in qml
            userId == ADMIN_USER_ID or
            td.userId == userId and not td.protected or
            td.userId == GUEST_USER_ID and userLevel > 0):
            growl.warn('<br/>'.join((
              my.tr("Editing other's entry is not allowed"),
              tr_("User") + ": " + td.userName,
              tr_("Pattern") + ": " + td.pattern,
              tr_("Text") + ": " + td.text,
            )))
            continue
          count += 1
          t.updateUserId = userId
          t.updateTimestamp = now
          t.comment = "%s // %s" % (value, td.comment) if (append and
            td.comment and td.comment != value and not td.comment.startswith(value + ' //')
          ) else value

        elif type == 'updateComment':
          if not ( # the same as canImprove permission in qml
            userId != GUEST_USER_ID or
            td.userId == userId and not td.protected or
            td.userId == GUEST_USER_ID and userLevel > 0):
            growl.warn('<br/>'.join((
              my.tr("Editing other's entry is not allowed"),
              tr_("User") + ": " + td.userName,
              tr_("Pattern") + ": " + td.pattern,
              tr_("Text") + ": " + td.text,
            )))
            continue
          count += 1
          t.updateUserId = userId
          t.updateTimestamp = now
          t.updateComment = "%s // %s" % (value, td.updateComment) if (append and
            td.updateComment and td.updateComment != value and not td.updateComment.startswith(value + ' //')
          ) else value

    if count:
      growl.msg(my.tr("{0} items updated").format(count))

    #d.terms = [t for t in d.terms if not (t.d.selected and t.d.deleted)]
    #if d._sortedTerms:
    #  d._sortedTerms = [t for t in d._sortedTerms if not (t.d.selected and t.d.updateTimestamp == now)]

    #d.invalidateTerms()
    #d.touchTerms()

  def removeCharacter(self, c):
    """
    @param  Character
    """
    d = self.__d
    try: del d.characters[c.name]
    except KeyError:
      dwarn("failed to remove character")
      return

    d.touchCharacters()
    d.invalidateCharacters()
    if c.parent():
      c.setParent(None)

  def clearCharacters(self):
    d = self.__d
    if d.characters:
      d.clearCharacters()
      d.resetCharacters()
      d.touchCharacters()
      d.invalidateCharacters()

  def purgeCharacters(self):
    d = self.__d
    if d.characters and d.needsPurgeCharacters():
      d.purgeCharacters()
      #d.resetCharacters()
      d.touchCharacters()
      d.invalidateCharacters()

  def submitTerm(self, term, commit=True):
    """
    @param[inout]  term  Term
    @param  commit  bool
    @return  bool  if succeed
    """
    if not term:
      return False
    term.id = 0 # reset comment ID

    #md5 = self.currentGameMd5()
    #if not md5:
    #  dprint("no running game")
    #  #return False

    d = self.__d
    if not d.user.isLoginable():
      growl.warn(my.tr("Please sign in to submit comment"))
      dwarn("failed: not login")
      return False

    d.terms.append(term)
    #self.invalidateSortedTerms()

    if commit:
      d.dirtyTerms.add(term)
      d.submitDirtyTermsLater()
      d.touchTerms()
      #d.backupTermsXmlLater()

    nm = netman.manager()
    if not nm.isOnline():
      nm.updateOnline()
      if not nm.isOnline():
        growl.warn(my.tr("Cannot connect to the Internet"))

    d.invalidateTerms()
    return True

  def addDirtyTerm(self, term):
    d = self.__d
    d.dirtyTerms.add(term)
    d.submitDirtyTermsLater()
    d.touchTerms()

  #def queryTermMacro(self, pattern):
  #  """
  #  @param  unicode
  #  @return  unicode or None
  #  """
  #  return self.__d.termMacros.get(pattern)

  #def clearMacroCache(self):
  #  d = self.__d
  #  d.clearTermMacros()
  #  for t in d.terms:
  #    td = t.d
  #    if td.regex and not td.disabled and defs.TERM_MACRO_BEGIN in td.pattern:
  #      t.clearCache()

  #def invalidateSortedTerms(self): self.__d.sortedTerms = None
  #def clearTermTitles(self): self.__d.clearTermTitles()

  def removeDirtyTerm(self, term):
    try: self.__d.dirtyTerms.remove(term)
    except KeyError: pass

  def submitDirtyTerms(self): self.__d.submitDirtyTerms()

  def exportTerms(self):
    if not self.hasTerms():
      growl.warn(my.tr("Shared dictionary is empty"))
      return

    if not prompt.confirmExportCsv():
      return

    #d = self.__d
    #d.submitDirtyTerms()
    #d.saveTerms()
    #xmlfile = rc.xml_path('terms')

    ts = datetime.now().strftime("%y%m%d")
    fileName = "vnr-dict-%s.csv" % ts
    path = os.path.join(skpaths.DESKTOP, fileName)
    import csvutil
    ok = csvutil.saveterms(path, self.__d.iterTermData())
    if ok:
      growl.msg(my.tr("Dictionary entries are saved to the desktop"))
      osutil.open_location(path)
    else:
      growl.warn(my.tr("Shared dictionary is empty"))
    #try:
    #  shutil.copyfile(xmlfile, path)
    #  growl.msg(my.tr("Dictionary entries are saved to the desktop"))
    #except IOError, e:
    #  dwarn(e)
    #  growl.warn(my.tr("Shared dictionary is empty"))

  def exportComments(self, data=None):
    """
    @param  data  [Comment] or None
    """
    #if not md5:
    #  md5 = self.currentGameMd5()
    #if not md5:
    #  growl.warn(my.tr("There are no subtitles"))
    #  return

    #d = self.__d
    #d.submitDirtyComments()
    #d.saveComments()
    #self.aboutToExportComments.emit()

    #xmlfile = rc.comments_xml_path(md5=md5)
    #if not os.path.exists(xmlfile):
    #  growl.warn(my.tr("There are no subtitles"))
    #  return

    #ts = datetime.now().strftime("%y%m%d")
    #gameId = self.queryGameId(md5)
    #fileName = "vnr-sub-%i.xml" % gameId
    if not prompt.confirmExportCsv():
      return
    if not data:
      data = self.__d.iterCommentData()
    ts = datetime.now().strftime("%y%m%d")
    fileName = "vnr-sub-%s.csv" % ts
    path = os.path.join(skpaths.DESKTOP, fileName)
    import csvutil
    ok = csvutil.savecomments(path, data)
    if ok:
      growl.msg(my.tr("Subtitles are saved to the desktop"))
      osutil.open_location(path)
    else:
      growl.warn(my.tr("There are no subtitles"))
    #try:
    #  shutil.copyfile(xmlfile, path)
    #  growl.msg(my.tr("Subtitles are saved to the desktop"))
    #except IOError, e:
    #  dwarn(e)
    #  growl.warn(my.tr("There are no subtitles"))

@memoized
def manager(): return DataManager()

## QML plugin ##

#@QmlObject
class DataManagerProxy(QObject):
  def __init__(self, parent=None):
    super(DataManagerProxy, self).__init__(parent)
    dm = manager()
    dm.commentCountChanged.connect(self.commentCountChanged)
    dm.currentGameChanged.connect(lambda:
        self.gameMd5Changed.emit(self.gameMd5))
    # Not used
    #dm.currentGameChanged.connect(lambda:
    #    self.gameIdChanged.emit(self.gameId))
    dm.currentGameChanged.connect(lambda:
        self.gameItemIdChanged.emit(self.gameItemId))

    gm = gameman.manager()
    gm.focusEnabledChanged.connect(self.currentGameFocusEnabledChanged)

  # Game thread

  currentGameFocusEnabledChanged = Signal(bool)
  currentGameFocusEnabled = Property(bool,
      lambda _: gameman.manager().isFocusEnabled(),
      notify=currentGameFocusEnabledChanged)

  ## Translation scripts ##

  #@Slot()
  #def updateTranslationScripts(self):
  #  if prompt.confirmUpdateTranslationScripts():
  #    manager().updateTranslationScripts()

  #@Slot()
  #def reloadTranslationScripts(self):
  #  if prompt.confirmReloadTranslationScripts():
  #    import trscriptman
  #    sm = trscriptman.manager()
  #    sm.reloadScripts()
  #    count = sm.scriptCount()
  #    growl.msg(my.tr("Found {0} translation rules").format(count))

  ## Games ##

  @Slot()
  def updateGameDatabase(self):
    if prompt.confirmUpdateGameFiles():
      manager().updateGameDatabase()

  ## Comments ##

  commentCountChanged = Signal(int)
  commentCount = Property(int,
      lambda _: manager().commentCount(),
      notify=commentCountChanged)

  gameItemIdChanged = Signal(long)
  gameItemId = Property(long,
      lambda _: manager().currentGameItemId(),
      notify=gameItemIdChanged)

  # Not used
  #gameIdChanged = Signal(long)
  #gameId = Property(long,
  #    lambda _: manager().currentGameId(),
  #    notify=gameIdChanged)

  gameMd5Changed = Signal(str)
  gameMd5 = Property(str,
      lambda _: manager().currentGameMd5(),
      notify=gameMd5Changed)

  @Slot(result=unicode)
  def getCurrentGameName(self): return manager().currentGameName()

  @Slot(result=unicode)
  def getCurrentGameSeries(self): return manager().currentGameSeries()

  #@Slot(result=unicode)
  #def getCurrentUserName(self):
  #  return manager().user().name

  @Slot(QObject, int)
  def likeComment(self, c, value):
    user = manager().user()
    userId = user.id
    if not userId or userId == c.d.userId:
      return
    dprint(value)
    manager().touchComments()
    netman.manager().likeComment(c.d.id, value, user.name, user.password)

  @Slot(QObject, bool)
  def enableComment(self, c, t):
    userId = manager().user().id
    if not userId:
      return
    comment = ""
    if userId != c.d.userId:
      comment = prompt.getUpdateComment(c.d.updateComment)
      if not comment:
        return

    timestamp = skdatetime.current_unixtime()

    c.disabled = not t
    c.updateUserId = userId
    c.updateTimestamp = timestamp
    if comment:
      c.updateComment = comment

  @Slot(QObject)
  def duplicateComment(self, c):
    userId = manager().user().id
    if not userId:
      return
    needsConfirm = userId == GUEST_USER_ID or userId != term.userId
    if needsConfirm and not prompt.confirmDuplicateEntry():
      return
    timestamp = skdatetime.current_unixtime()
    ret = c.clone(
        id=0, userId=userId, timestamp=timestamp, disabled=False, deleted=False,
        updateTimestamp=0, updateUserId=0)
    manager().submitComment(ret)

  @Slot(QObject)
  def deleteComment(self, c):
    if prompt.confirmDeleteComment(c):
      c.deleted = True

  @Slot(QObject, result=QObject)
  def improveComment(self, comment):
    """
    @param[in]  comment  Comment
    @return Comment
    """
    userId = manager().user().id
    if not userId:
      return
    updateComment = ""
    if userId != comment.userId:
      updateComment = prompt.getUpdateComment(comment.updateComment)
      if not updateComment:
        return
    timestamp = skdatetime.current_unixtime()
    ret = comment.clone(
        id=0, userId=userId, timestamp=timestamp, disabled=False, deleted=False,
        updateTimestamp=0, updateUserId=0)
    manager().submitComment(ret)
    comment.disabled = True
    comment.updateUserId = userId
    comment.updateTimestamp = timestamp
    if updateComment:
      comment.updateComment = updateComment
    return ret

  @Slot(unicode, unicode, c_longlong, int, result=QObject)
  def createComment(self, text, type, ctxhash, ctxsize):
    """
    @return  Comment
    """
    ctxhash = long(ctxhash)
    dm = manager()
    user = dm.user()
    if not user.name:
      return
    gameId = dm.currentGameId()
    md5 = dm.currentGameMd5()
    if not gameId and not md5:
      return
    ctx = dm.queryContext(hash=ctxhash)
    timestamp = skdatetime.current_unixtime()
    ret = Comment(gameId=gameId, gameMd5=md5,
        userId=user.id, language=user.language,
        text=text, type=type, timestamp=timestamp,
        hash=ctxhash, context=ctx, contextSize=ctxsize)
    dm.submitComment(ret, commit=False)
    return ret

  ## Subtitles ##

  @Slot()
  def updateSubtitles(self):
    sel = prompt.confirmUpdateSubs()
    if sel:
      manager().updateSubtitles(**sel)

  ## Terms ##

  @Slot(unicode, unicode, unicode)
  def createTerm(self, type, pattern, text):
    dm = manager()
    user = dm.user()
    if not user.name:
      return
    gameId = dm.currentGameId()
    md5 = dm.currentGameMd5()
    #if not gameId and not md5:
    #  return
    ret = Term(gameId=gameId, gameMd5=md5,
        userId=user.id, language=user.language,
        timestamp=skdatetime.current_unixtime(),
        pattern=pattern, text=text, type=type)
    dm.submitTerm(ret, commit=False)
    #return ret

  @Slot(QObject)
  def deleteTerm(self, term):
    if prompt.confirmDeleteTerm(term):
      manager().removeTerm(term)
      term.deleted = True

  @Slot()
  def updateTerms(self):
    sel = prompt.confirmUpdateTerms()
    if sel:
      manager().submitDirtyTerms()
      manager().updateTerms(**sel)

  @Slot(QObject)
  def replicateTerm(self, term):
    userId = manager().user().id
    if not userId:
      return
    needsConfirm = userId == GUEST_USER_ID or userId != term.userId
    if needsConfirm and not prompt.confirmDuplicateEntry():
      return
    ret = term.clone(
        id=0, userId=userId, disabled=False, deleted=False,
        timestamp=skdatetime.current_unixtime(),
        updateTimestamp=0, updateUserId=0)
    manager().submitTerm(ret)

  @Slot(QObject, bool)
  def enableTerm(self, term, t):
    userId = manager().user().id
    if not userId:
      return
    comment = ""
    if userId != term.userId:
      comment = prompt.getUpdateComment(term.updateComment)
      if not comment:
        return

    term.disabled = not t
    term.updateUserId = userId
    term.updateTimestamp = skdatetime.current_unixtime()
    if comment:
      term.updateComment = comment

  @Slot(QObject)
  def improveTerm(self, term):
    userId = manager().user().id
    if not userId:
      return
    comment = ""
    if userId != term.userId:
      comment = prompt.getUpdateComment(term.updateComment)
      if not comment:
        return
    timestamp = skdatetime.current_unixtime()
    ret = term.clone(
        id=0, userId=userId, timestamp=timestamp, disabled=False, deleted=False,
        updateTimestamp=0, updateUserId=0)
    manager().submitTerm(ret)
    term.disabled = True
    term.updateUserId = userId
    term.updateTimestamp = timestamp
    if comment:
      term.updateComment = comment
    #return ret

  ## Game queries ##

  @Slot(long, result=unicode)
  def queryItemName(self, id):
    return manager().queryItemName(id=id)

  @Slot(long, result=unicode)
  def queryItemSeries(self, id):
    return manager().queryItemSeries(id=id)

  @Slot(long, result=long)
  def queryGameItemId(self, id):
    return manager().queryGameItemId(id=id)

  @Slot(long, result=unicode)
  def queryGameName(self, id):
    return manager().queryGameName(id=id)

  @Slot(long, result=unicode)
  def queryGameSeries(self, id):
    return manager().queryGameSeries(id=id)

  @Slot(long, result=unicode)
  def queryGameFileName(self, id):
    return manager().queryGameFileName(id=id)

  @Slot(long, long, result=unicode)
  def queryGameImage(self, tokenId, itemId): # uncached
    return manager().queryGameImageUrl(id=tokenId, itemId=itemId)

  @Slot(long, result=unicode)
  def queryUserAvatarUrl(self, id):
    ret = manager().queryUserAvatarUrl(id, cache=True)
    if ret and not netman.manager().isOnline() and ret.startswith("http://"):
      ret = ""
    return ret

  @Slot(long, long, result=unicode)
  def queryUserAvatarUrlWithHash(self, id, hash):
    ret = manager().queryUserAvatarUrl(id, hash=hash, cache=True)
    if ret and not netman.manager().isOnline() and ret.startswith("http://"):
      ret = ""
    return ret

  @Slot(long, result=unicode)
  def queryUserColor(self, id):
    return manager().queryUserColor(id)

  @Slot(result=long)
  def currentGameId(self):
    return manager().currentGameId()

  @Slot()
  def exportTerms(self): manager().exportTerms()
  #@Slot(str)
  #def exportComments(self, md5): manager().exportComments(md5=md5)

  @Slot(str, bool)
  def setGameVoiceDefaultEnabled(self, md5, val):
    if md5:
      manager().setGameVoiceDefaultEnabled(val, md5=md5)

  @Slot(str, result=bool)
  def queryGameVoiceDefaultEnabled(self, md5):
    g = manager().queryGame(md5=md5)
    return bool(g) and g.voiceDefaultEnabled

# EOF

#  @staticmethod
#  def _loadComments(xmlfile, hash, checkexit=False):
#    """
#    @param  xmlfile  unicode  path to xml
#    @param  hash  bool
#    @param  checkexit  bool  weather check quit
#    @return ({long hash:Comment} if hash else [Comment]) or None
#    """
#    try:
#      tree = etree.parse(xmlfile)
#      root = tree.getroot()
#
#      #root = etree.fromstring(
#      #    skfileio.readfile(xmlfile))
#
#      ret = {} if hash else []
#      #contexts = {}
#      comments = root.find('./comments')
#      for comment in comments.iterfind('./comment'):
#        if checkexit and main.EXITED:
#          return
#        kw = {
#          'comment': "",
#          'updateComment': "",
#          'updateTimestamp':  0,
#          'updateUserName': "",
#
#          'id': long(comment.get('id')),
#          'type': comment.get('type'),
#          'disabled': (comment.get('disabled') or comment.get('hidden')) == 'true',
#          'locked': comment.get('locked') == 'true',
#        }
#
#        it = comment.iter()
#        it.next() # skip the root, which conflict with 'comment'
#        for elem in it:
#          tag = elem.tag
#          text = elem.text
#
#          if tag in ('gameId', 'timestamp', 'updateTimestamp'):
#            kw[tag] = long(text)
#          else:
#            kw[tag] = text
#
#          if tag == 'context':
#            kw['hash'] = long(elem.get('hash'))
#            kw['contextSize'] = int(elem.get('size'))
#
#        #if c_hash and c_text:
#        c = Comment(**kw)
#        if not hash:
#          ret.append(c)
#        else:
#          h = kw['hash']
#          if h in comments:
#            ret[h].append(c)
#          else:
#            ret[h] = [c]
#
#      #self.comments, self.context = comments, contexts
#      dprint("pass: load %i comments from %s" % (len(ret), xmlfile))
#      return ret
#
#    except etree.ParseError, e:
#      dwarn("xml parse error", e.args)
#    except (TypeError, ValueError, AttributeError), e:
#      dwarn("xml malformat", e.args)
#    except Exception, e:
#      derror(e)
#
#    dwarn("warning: failed to load xml from %s" % xmlfile)
