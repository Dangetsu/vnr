# coding: utf8
# _dictman.py
# 10/10/2012 jichi

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import re
from sakurakit import skstr
from unitraits import jpmacros, cyrilchars
import convutil

#RIGHT_ARROW = u"→" # みぎ
RIGHT_ARROW = u"⇒" # みぎ

# KanjiDic

def render_kanji(text):
  """
  @param  text  unicode
  @return  unicode  html

  Add class before and after {}
  """
  text = text.replace('{', '<span class="def">{')
  text = text.replace('}', '}</span>')
  return text

# EDICT

def render_edict(text):
  """
  @param  text  unicode
  @return  unicode  html

  Example: /(n,adj-no) (1) center/centre/middle/heart/core/focus/pivot/emphasis/balance/(suf) (2) -centered/-centred/-focussed/-oriented/centered on/focussed on/(P)/
  """
  # Example: /EntL1390270X/
  text = re.sub(r'/[0-9a-zA-Z]+/$', '/', text) # remove trailing ref
  if text.startswith('/'):
    text = text[1:]
  if text.endswith('/'):
    text = text[:-1]
  role = ''
  if text.startswith('('): # extract leading word role
    i = text.find(')')
    if i != -1:
      role = text[1:i]
      text = text[i+1:]
  popular = text.endswith('(P)') # deal with trailing (popular) mark
  if popular:
    text = text[:-3]
  if text.endswith('/'): # replace (1) (2) ... by html list
    text = text[:-1]
  # Render list
  t = re.sub(r'\s?\(\d+\)\s?', '<li>', text)
  if t == text: # ul
    text = "<ul><li>%s</ul>" % text
  else: # ol
    if not t.startswith('<li>'):
      i = t.find('<li>')
      if i != -1:
        if role:
          role += ' ' + RIGHT_ARROW
        role += t[:i]
        t = t[i:]
    t = t.replace('/<', '<')
    text = "<ol>%s</ol>" % t
  # Render heading
  head = ''
  if role:
    head = '<span class="role">[%s]</span>' % role
  if popular:
    if head:
      head += ' '
    head += '<span class="flag">(common usage)</span>'
  if head:
    head = '<div class="head">%s</div>' % head
    text = head + text
  return text

# Lingoes

def _sub_roman(m): # re.match -> unicode
  t = m.group(2)
  r = convutil.kana2romaji(t)
  if r and r != t:
    t = "%s, %s" % (t, r)
  return '<span class="reading">(%s)</span>' % t

def _render_lingoes(text, dic):
  """Render lingoes ja-zh dictionary.
  @param  text  unicode
  @param* dic  str  'ovdp', 'naver', 'vicon'
  @return  unicode  html

  Example ja-zh:
  <C><F><H /><I><N><P><U>否定助动</U></P><Q>[接动词及动词型活用的助动词 「れる·られる，せる·させる」的未然形， 「する」 后接 「ない」 时要变成 「し」。</Q><Q>「ない」 的活用形式与形容词相同，但未然形 「なかろ」+「う」 的用法不常见，一般表示否定的推测时用 「ないだろう」]</Q><Q>[表示对前面(动词所表示的)动作或作用(的状态)的否定]不，没。<T><W>押して開かなければ引いてごらん</W><X>如果推不开，拉拉看。</X></T></Q><Q>→「…てはいけない」、「…てはならない」。</Q><Q>→「なければならない」、「なくてはならない」、「ないといけない」。</Q><Q>→ 「なくてもよい」。</Q><Q>以 「…ないか」 的形式，或向对方询问，确认，或征求对方同意，或劝诱对方，或表示说话人的愿望(省略 「か」 时句尾读升调)。<T><W>早く雪が降らないかなあ</W><X>怎幺还不快点儿下雪啊!</X></T></Q><Q>[以 「…ないで」 的形式向对方表示说话人否定的愿望或委婉的禁止。</Q><Q>这种用法类似终助词，可以认为后面省略了 「くれ」 或 「ください」] 别。<T><W>約束の時間に遅れないでよ</W><X>约好的时间可别晚了啊!</X></T></Q></N></I></F></C><br class="xml"/><C><F><H /><I><N><Y>ある</Y><Q /></N></I></F></C>

  Example ja-vi:
  <C><F><H /><K><![CDATA[<ul><li><font color='#cc0000'><b> {ちょっといっぱい}</b></font></li></ul><ul><li><font color='#cc0000'><b> {let's have quick drink}</b></font></li></ul>]] > </K></F></C>
  """
  #if dic == 'ovdp':
  #  text = (text
  #    .replace('<![CDATA[', '').replace(']] >', '').replace(']]>', '')
  #    .replace('{', '').replace('}', '')
  #    .replace("<font color='#cc0000'>", '').replace('</font>', '')
  #    .replace('<b>', '').replace('</b>', '')
  #    #.replace('<ul>', '').replace('</ul>', '')
  #    #.replace('<li>', '<br/>').replace('</li>', '<br/>')
  #  )
  #  #if text.count('<li>') > 1:
  #  #  text = text.replace('ul>', 'ol>') # change to ordered list
  text = re.sub(r'(\[.*?\])', r'<span class="hl">\1</span> ', text) # highlight text in []
  text = text.replace('<T>', '<div>').replace('</T>', '</div>') # example sentence
  text = text.replace('</W><X>', '</W> %s <X>' % RIGHT_ARROW)
  #text = text.replace('<W>', '<div>').replace('</W>', '</div>') # example sentence text
  #text = text.replace('<X>', '<div>').replace('</X>', '</div>') # example sentence translation
  # Reading
  #text = text.replace('<M>', ' <span class="reading">(')
  #text = text.replace('</M>', ')</span> ')
  #text = text.replace('<g>', ' <span class="reading">(')
  #text = text.replace('</g>', ')</span> ')
  if '<M>' in text or '<g>' in text:
    text = re.sub(r'<([Mg])>(.+?)</\1>', _sub_roman, text)
  qc = text.count('<Q>')
  if qc > 1: # skip only 1 quote case
    text = text.replace('<Q>','<li>').replace('</Q>', '</li>') # quote => list
    #if qc == 1: # ul
    #  text = text.replace('<li>', '<ul><li>', 1)
    #  text = skstr.rreplace(text, '</li>', '</li></ul>', 1)
    #else: # ol
    text = text.replace('<li>', '<ol><li>', 1)
    text = skstr.rreplace(text, '</li>', '</li></ol>', 1)
  #return text
  if dic == 'naver':
    text = text.replace('<n />', '<br/>') # new line
    # Disabled as the original colors are ugly
    #text = text.replace('</x>', '</font>')
    #text = text.replace('<x>', '<font>')
    #text = text.replace('<x K=', '<font color=')
    text = text.replace('<E>', '<p class="entry">')
    text = text.replace('</E> ', '</p>')
  elif dic == 'vicon':
    text = text.replace('<N>', '<br/>') # new line
  # Recovered kanji
  return text
  #return skstr.escapehtml(text) + '<br/>' + text

def render_lingoes(text, dic=None):
  """Render lingoes ja-zh dictionary.
  @param  text  unicode
  @param* dic  str
  @return  unicode  html
  """
  return _render_lingoes(text, dic)

# OVDP

def _ovdp_romaji_replace(m):
  kana = m.group(1)
  return "%s (%s)" % (kana, convutil.kana2romaji(kana))
_rx_ovdp_kana = re.compile(jpmacros.applymacros(r'(?<=[{@])({{kana}}+)'))
def _ovdp_add_romaji(text):
  """Add romaji for kana in {}
  @param  text  unicode
  @return  unicode
  """
  if '@' in text or '{' in text:
    text = _rx_ovdp_kana.sub(_ovdp_romaji_replace, text)
  return text

def _render_ovdp(text):
  """Render OVDP ja-vi dictionary.
  @param  text  unicode
  @return  unicode  html

  Example ja-zh:
  @yomi
  - {hello}
  - {world}
  """
  text = _ovdp_add_romaji(text)
  if '}' in text:
    text = text.replace('} ,', '}:') # trim space after }
    text = text.replace('}', '</span>')
    text = text.replace('{', '<span class="hl">')
  if '@' in text:
    text = re.sub(r'@(.*?)\n', r'<u>\1</u><br/>', text)
  if text.count('- ') > 1:
    text = text.replace(r'- ', '<li>')
    text = "<ol>%s</ol>" % text
  else:
    text.replace('\n', '<br/>')
  return text

def _render_hanjadic(text):
  """Render hanjadic.
  @param  text  unicode
  @return  unicode  html

  Example:
【애】사랑(하다); 그리워하다; 아끼다
受(줄수)의 줄임 + 心(마음심) + (천천히걸을쇠)
心부 9획 (총13획)
[1] [v] love; be fond of; like; be kind to [2] love; affection; kindness; benevolence; likes [3] [v] be apt to
兼愛(겸애) 친불친(親不親)을 가리지 않고 모든 사람을 한결같이 사랑함
敬愛(경애) 존경하고 사랑함
敬天愛人(경천애인) 하늘을 공경하고 인류를 사랑함.
  """
  text = text.replace('\n', '<br/>')
  text = re.sub(ur'(【.*?】)', r'<span class="hl">\1</span> ', text)
  #text = re.sub(r'(\[.*?\])', r'<span class="hl">\1</span> ', text) # highlight text in []
  return text

def render_stardict(text, dic=None):
  """Render ovdp ja-vi dictionary.
  @param  text  unicode
  @param* dic  str
  @return  unicode  html
  """
  if dic == 'ovdp':
    return _render_ovdp(text)
  if dic == 'hanja':
    return _render_hanjadic(text)
  return text

# JMDict

def _render_jmdict_nl(text):
  """Render JMDict ja-nl dictionary.
  @param  t  unicode
  @return  unicode  html
  """
  if '(1)' in text:
    text = text.replace('(1)', '<ol>(1)')
    text = text.replace('<br/><ol>', '<ol>')
    text = re.sub(r'\s?\(\d+\)\s?', '<li>', text)
    text += '</ol>'
  text = text.replace(' }', '}') # trim space
  return text

def _render_jmdict_ru(text):
  """Render JMDict ja-ru dictionary.
  @param  t  unicode
  @return  unicode  html
  """
  text = text.replace(u'?', '') # remove question mark
  i = cyrilchars.findcyril(text)
  if i > 0 and text[i-1] != '>':
    text = text[:i] + '<br/>' + text[i:]
  return text

#def _render_jmdict_fr(text):
#  """Render JMDict ja-fr dictionary.
#  @param  t  unicode
#  @return  unicode  html
#  """
#  return text

def render_jmdict(text, language=None):
  """Render ovdp ja-vi dictionary.
  @param  text  unicode
  @param* language  str
  @return  unicode  html
  """
  if language == 'ru':
    text = _render_jmdict_ru(text)
  elif language == 'nl':
    text = _render_jmdict_nl(text)
  #elif language == 'fr':
  #  text = _render_jmdict_fr(text)

  BR = '<br/>'
  text = text.replace(u'【', BR + u'【') # break new line
  if text.startswith(BR):
    text = text[len(BR):]
  if text.endswith(BR):
    text = text[:-len(BR)]

  COMMON = '(common)'
  if COMMON in text:
    left, flag, right = text.partition(COMMON)
    if '>' in left:
      left, mid, role = left.rpartition('>')
      if ';' not in role:
        role = '<span class="role">[%s]</span> ' % role.strip()
        flag = '<span class="flag">%s</span>' % flag
        text = left + mid + role + flag + right
  return text

if __name__ == '__main__':
  t = u'/(n) tank (military vehicle)/(P)/EntL1390270X/'
  print render_edict(t)

# EOF
