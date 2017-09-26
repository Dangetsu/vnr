# coding: utf8
# dbutil.py
# 4/5/2015

# http://stackoverflow.com/questions/3785294/best-way-to-iterate-through-all-rows-in-a-db-table
def fetchsome(cursor, some):
  """
  @param  cursor
  @param  some  int
  @raise
  """
  fetch = cursor.fetchmany
  while True:
    rows = fetch(some)
    if not rows:
      break
    for row in rows:
      yield row

# EOF
