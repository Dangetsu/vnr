# coding: utf8
# jsonman.py
# 8/10/2013 jichi

import json, re
from datetime import datetime
from operator import attrgetter
from sakurakit.skdebug import dprint, dwarn
import dataman

KEYS = (
  'itemId',
  'timestamp',
  'local',
  'visitCount', 'commentCount', 'playUserCount', 'subtitleCount',

  'title0',
  'romajiTitle0',
  'brand0',
  'date0',
  'fileSize0',
  'imageUrl0',
  'series0',
  'okazu0',
  'otome0',
  'tags0',
  'artists0',
  'sdartists0',
  'writers0',
  'musicians0',
  'scapeMedian0',
  'scapeCount0',
  'overallScore0',
  'overallScoreCount0',
  'overallScoreSum0',
  'ecchiScore0',
  'ecchiScoreCount0',
  'ecchiScoreSum0',
)

class GameInfoEncoder(json.JSONEncoder):

  def default(self, obj):
    """@reimp
    @param  obj  GameInfo
    @return  dict
    """
    return {k.replace('0',''):getattr(obj,k) for k in KEYS}

def gameinfo(start=0, count=100, sort=None, reverse=None, filters=None):
  """
  @param* start  int
  @param* count  int
  @param* sort  str
  @param* reverse  bool
  @param* filters  unicode  JSON
  @return  unicode json, int left, int total
  """
  dprint("enter: start = %i, count = %i, sort = %s, reverse = %s, filters =" % (start, count, sort, reverse), filters)
  dm = dataman.manager()
  data = dm.getGameInfo()
  if filters:
    try:
      params = json.loads(filters)

      error = False
      searchRe = searchDate = searchId = None
      search = params.get('search') # unicode
      searchLargeSize = None # bool or None
      if search:
        if (search.startswith('20') or search.startswith('19')) and search.isdigit():
          searchDate = search
        elif search.startswith('#') and search[1:].isdigit():
          searchId = int(search[1:])
        elif search in ('GB', 'gb'):
          searchLargeSize = True
        elif search in ('MB', 'mb'):
          searchLargeSize = False
        if not searchDate and not searchId and searchLargeSize is None:
          try: searchRe = re.compile(search, re.IGNORECASE)
          except Exception, e:
            dwarn(e)
            error = True
      if error:
        data = []
      else:
        l = []
        year = params.get('year')   # int
        month = params.get('month') # int
        local = params.get('local') # bool
        genre = params.get('genre') # str
        t = params.get('time')      # str
        upcoming = t == 'upcoming'  # bool
        recent = t == 'recent'      # bool
        okazu = otome = None        # bool
        if genre is not None:
          otome = genre == 'otome'
          if not otome:
            okazu = genre == 'nuki'  # bool
        tags = params.get('tags') # unicode
        if tags:
          tags = map(unicode.lower, tags)
        for it in data:
          if searchLargeSize is not None:
            if not it.fileSize0 or it.fileSize0 < 1024 * 1024: continue
            if searchLargeSize:
              if it.fileSize0 < 1024 * 1024 * 1024: continue
            else:
              if it.fileSize0 >= 1024 * 1024 * 1024: continue

          if otome is not None and otome != it.otome0: continue
          if okazu is not None and okazu != it.okazu0: continue
          if local is not None and local != it.local: continue
          if upcoming and not it.upcoming0: continue
          if recent and not it.recent0: continue

          dt = None
          if year or month:
            if not it.dateObject0: continue
            dt = it.dateObject0
            if month and month != dt.month: continue
            if year:
              if year < 2000: # aggregate 199x together
                if dt.year >= 2000 or dt.year < 1990: continue
              elif year != dt.year: continue
          if search:
            if searchRe:
              matched = False
              for k in 'title0', 'romajiTitle0', 'brand0', 'series0', 'tags0', 'artists0', 'sdartists0', 'writers0', 'musicians0':
                v = getattr(it, k)
                if v and searchRe.search(v):
                  matched = True
                  break
              if not matched:
                continue
            elif searchDate:
              if not dt:
                if not it.dateObject0: continue
                dt = it.dateObject0
              if not dt.strftime("%Y%m%d").startswith(searchDate): continue
            elif searchId:
              if searchId != it.itemId: continue
          if tags:
            t = it.tags0
            if not t: continue
            t = t.lower()
            contd = False
            for k in tags:
              if k not in t:
                contd = True
                break
            if contd: continue
          l.append(it)
        data = l
    except ValueError, e: dwarn(e)
  total = len(data)
  if data:
    if not sort and reverse:
      data.reverse()
    elif sort:
      k = sort if sort in KEYS else sort + '0'
      data.sort(key=attrgetter(k), reverse=bool(reverse))
    if start:
      data = data[start:]
    if count and count < len(data):
      data = data[:count]
  left = len(data)
  dprint("leave: count = %i/%i" % (left, total))
  return json.dumps(data, #[it for it in data if it.image], # Generator not supported
      cls=GameInfoEncoder), left, total

# EOF
