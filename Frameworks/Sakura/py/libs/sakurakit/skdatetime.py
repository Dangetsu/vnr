# coding: utf8
# skdatetime.py
# 11/3/2012 jichi

import time
from datetime import datetime

def current_unixtime():
  """Unix time in seconds
  @return  long  seconds
  """
  return long(time.time())

NOW = datetime.now()
CURRENT_UNIXTIME = current_unixtime()

# See: http://stackoverflow.com/questions/2775864/python-datetime-to-unix-timestamp
def datetime2timestamp(date):
  """Unix time in seconds
  @param  datetime  datetime.datetime not None
  @return  long  seconds
  @throw  when datetime is not valid or less than unixtime 0
  """
  return int(time.mktime(date.timetuple()))

date2timestamp = datetime2timestamp

def timestamp2datetime(seconds):
  """Unix time in seconds
  @param  seconds  float
  @return  datetime
  @throw  when datetime is not valid or less than unixtime 0
  """
  return datetime.fromtimestamp(seconds)

def timestamp2date(seconds):
  """Unix time in seconds
  @param  seconds  float
  @return  date
  @throw  when datetime is not valid or less than unixtime 0
  """
  return datetime.fromtimestamp(seconds).date()

# EOF
