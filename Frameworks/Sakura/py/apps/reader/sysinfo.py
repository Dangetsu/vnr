# coding: utf8
# sysinfo.py
# 8/2/2013 jichi

from sakurakit import skdatetime, skos, skwin

## Display ##

DISPLAY_RESOLUTION = skwin.get_display_resolution() if skos.WIN else (0,0)

## Time ##

NOW = skdatetime.NOW
#TIMESTAMP = skdatetime.CURRENT_UNIXTIME

def timestamp_jst_diff():
  # http://stackoverflow.com/questions/12015170/how-do-i-automatically-get-the-timezone-offset-for-my-local-time-zone
  # pytz.timezone('Japan').utcoffset(datetime.datetime.now()).seconds
  # = 32400 = 9 * 3600
  from dateutil import tz
  delta = tz.tzlocal().utcoffset(NOW)
  return 9*3600 - delta.seconds * (delta.days * 2 + 1) # +-1

TIMESTAMP_JST_DIFF = timestamp_jst_diff()
def timestamp2jst(seconds):
  return seconds + TIMESTAMP_JST_DIFF

# EOF
