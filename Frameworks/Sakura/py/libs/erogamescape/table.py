# coding: utf8
# table.py
# 8/18/2013 jichi
#
# See: http://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/select.php
# See: http://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/tablelist.php
# See (characters from twitter): http://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/doc/erogamescape_er_20110723.pdf
# See: http://tsubame30.exblog.jp/19548740/
# See: SELECT * from gamelist limit 1
# See: SELECT * from brandlist limit 1
#
# Example: SELECT * from gamelist limit 1
#    id	gamename	furigana	sellday	brandname	median	stdev	creater	kansouurl	checked	hanbaisuu	average2	median2	count2	comike	shoukai	model	checked2	erogame	galge	elfics	banner_url	admin_checked	max2	min2	gyutto_enc	gyutto_id	dmm	dmm_genre	dmm_genre_2	erogametokuten	total_play_time_median	time_before_understanding_fun_median	dlsite_id	dlsite_domain	the_number_of_uid_which_input_pov	the_number_of_uid_which_input_play	total_pov_enrollment_of_a	total_pov_enrollment_of_b	total_pov_enrollment_of_c	trial_url	trial_h	http_response_code	okazu	axis_of_soft_or_hard	trial_url_update_time	genre	twitter	erogetrailers	tourokubi	digiket	dmm_sample_image_count	dlsite_sample_image_count	gyutto_sample_image_count	digiket_sample_image_count	twitter_search	tgfrontier	gamemeter	twitter_data_widget_id	twitter_data_widget_id_before	twitter_data_widget_id_official
#    9426	青のはる。	アオノハル	2007-04-23	1881					t						http://www107.sakura.ne.jp/~nyannyan/aono_haru/aono_haru_main.htm	MOBILE	t	f																	0	0	0	0	0			200			0001-01-01 00:00:00			0			-1	-1	-1	-1		0
#
# Example: SELECT * from userreview where memo is not null and game = 19919 limit 1
#    game	uid	tokuten	tourokubi	hitokoto	memo	netabare	id	giveup	possession	play	reserve	outline	before_hitokoto	before_tokuten	before_tourokubi	outline_hitokoto	display	play_tourokubi	outline_netabare	outline_tourokubi	display_unique_count	sage	before_purchase_will	before_sage	total_play_time	time_before_understanding_fun	okazu_tokuten	trial_version_hitokoto	trial_version_hitokoto_sage	trial_version_hitokoto_tourokubi	timestamp	modified
#    19919	もっこりん	86	2014-07-01 03:11:37.042071+09	何も考えず適当にギャグに笑っておけばいいゲーム。相変わらず盛り上げるのはお上手だなぁと。点数は相当贔屓目	ケツの穴に修正がないのと、（起承転結の）結がないのは掛けているのか……？	t	1411808	f	f	t	f						f	2014-07-01 03:11:37.042071	f			f		f			-999		f		2014-07-01 10:42:17.88611	2014-07-01 10:42:17.88611

__all__ = 'Api',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from datetime import datetime
from sakurakit.skstr import unescapehtml

## Types ##

def t_unicode(t):
  """
  @param  t  str
  @return  unicode or None
  """
  return unescapehtml(t).decode('utf8', errors='ignore').strip() if t else None

def t_str(t):
  """
  @param  t  str
  @return  str or None
  """
  return unescapehtml(t).strip() if t else None

def t_int(t):
  """
  @param  t  str
  @return  int or None
  """
  if t:
    try: return int(t)
    except ValueError: pass

def t_long(t):
  """
  @param  t  str
  @return  long or None
  """
  if t:
    try: return long(t)
    except ValueError: pass

def t_bool(t):
  """
  @param  t  str
  @return  bool or None
  """
  return True if t == 't' else False if t == 'f' else None

def t_date(t):
  """
  @param  t  str  such as '2014-07-01'
  @return  datetime or None
  """
  if t and t != '2030-01-01':
    try: return datetime.strptime(t, '%Y-%m-%d')
    except: pass
    #except ValueError: pass

def t_datetime(t):
  """
  @param  t  str  such as '2014-07-01 10:42:17.8861'
  @return  datetime or None
  """
  if t:
    i = t.rfind('.')
    if i != -1:
      t = t[:i] # trim the text after '.'
    try: return datetime.strptime(t, '%Y-%m-%d\t%H:%M:%S')
    except: pass

## Tables ##

gamelist = {
  'id': t_long,         # game id
  #'brandname': t_int,  # brand id
  'gamename': t_unicode, # title
  'furigana': t_unicode, # katagana
  'sellday': t_date,
  'erogame': t_bool,    # アダルト
  'okazu': t_bool,      # 抜きゲー
  'genre': t_unicode,   # getchu slogan

  'banner_url': t_str,
  'trial_url': t_str,
  'trial_h': t_bool,

  'total_play_time_median': t_int,               # hours
  'time_before_understanding_fun_median': t_int, # hours
  #'stdev': t_int,
  'median': t_int,      # absolute median
  #'median2': t_int,    # after filtering
  #'average2': t_int,
  'count2': t_int,      # data count
  #'min2': t_int,
  #'max2': t_int,

  'twitter': t_unicode, # twitter user name
  'twitter_search': t_unicode,  # twitter search key words
  'twitter_data_widget_id': t_long,
  'twitter_data_widget_id_before': t_long, # before release
  'twitter_data_widget_id_official': t_long,

  'erogetrailers': t_long,

  'gyutto_id': t_long,
  'gyutto_enc': t_str,

  'dlsite_id': t_str,
  'dlsite_domain': t_str,

  'dmm': t_str,
  'dmm_genre': t_str,
  'dmm_genre_2': t_str,

  'digiket': t_str, # such as: ITM0072787
  'erogametokuten': t_long,

  'shoukai': t_str,    # homepage

  #'tgfrontier': t_long, # such as: http://tg-frontier.jp/soft.aspx?s=6668
  #'gamemeter': t_str,   # such as: http://gamemeter.net/g/b5885fc65b

  #'model': t_str,      # platform
  #'comike': t_long,
  #'galge': TODO,
  #'elfics': TODO,
}

userreview = {
  'id': t_long,     # review id
  'game': t_long,   # game id, such as: 19919
  'uid': t_unicode, # user name, such as: もっこりん
  'tokuten': t_int, # score, [0-100]
  'okazu_tokuten': t_int, # score, [-999,-1]
  'hitokoto': t_unicode, # title
  'memo': t_unicode,    # content
  'netabare': t_bool,   # ネタバレ 
  'timestamp': t_datetime, # create time
  'modified': t_datetime,  # update time
  #'play_tourokubi': t_datetime, # play start time
  #'giveup': t_bool,    # user give up
  #'play': t_bool,      # playすみ
  #'reserve': t_bool,   # 購入
}

# EOF
