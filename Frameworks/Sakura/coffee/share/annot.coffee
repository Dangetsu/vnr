# annot.coffee
# 3/28/2014 jichi
# Needed beans:
# - jlpBean
#   - parse: string -> string
# - ttsBean
#   - speak: string ->
# - trBean
#   - translators: -> string
#   - translate: string, string -> string
# Export functions
# - annotate: (el)->
# Style classes after injection
# - annot-root
#   - annot-src
#   - annot-ruby

# Underscore

WHITE_SPACES = [
  ' ', '\n', '\r', '\t', '\f', '\v', '\u00A0', '\u1680', '\u180E',
  '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', '\u2006',
  '\u2007', '\u2008', '\u2009', '\u200A', '\u2028', '\u2029', '\u202F',
  '\u205F', '\u3000'
]

toString = (val) -> if val? then val.toString() else ''

ltrim = (str, chars=WHITE_SPACES) ->
  str = toString str

  start = 0
  len = str.length
  charLen = chars.length
  found = true

  while found and start < len
    found = false
    i = -1
    c = str.charAt start

    while ++i < charLen
      if c is chars[i]
        found = true
        ++start
        break

  if start >= len then '' else str.substr(start, len)

rtrim = (str, chars=WHITE_SPACES) ->
  str = toString str

  end = str.length - 1
  charLen = chars.length
  found = true

  while found and end >= 0
    found = false
    i = -1
    c = str.charAt end

    while ++i < charLen
      if c is chars[i]
        found = true
        --end
        break

  if end >= 0 then str.substring(0, end + 1) else ''

trim = (str, chars=WHITE_SPACES) ->
  str = toString str
  ltrim(rtrim(str, chars), chars)

## Helpers

tr = (t) -> t # TODO: Not implemented, supposed to return the translated string

# half-width/full-width letters, numbers, and some half-width punctuations
isalnum = (ch) -> /[0-9a-zA-Z０-９ａ-ｚＡ-Ｚ]/.test ch # string ->bool

# half-width punctuations
#ispunct = (ch) -> /['"?!,\.]/.test ch # string -> bool

isalphapunct = (ch) -> /[a-zA-Zａ-ｚＡ-Ｚ'"?!,\.]/.test ch # string ->bool

## Handlers

isRubyEnabled = -> document.body.classList.contains 'annot-opt-ruby'
isTtsEnabled = -> document.body.classList.contains 'annot-opt-tts'
isTranslationTipEnabled = -> document.body.classList.contains 'annot-opt-tr-tip'
isFullTranslationEnabled = -> document.body.classList.contains 'annot-opt-tr'

onSpeak = -> # this = element
  ttsBean.speak @getAttribute 'annot-text' if isTtsEnabled()

onTranslateTip = -> # this = element
  return if not isTranslationTipEnabled() or @classList.contains('annot-locked') or @classList.contains('annot-translated')

  @classList.add 'annot-locked'
  @classList.add 'annot-translated'

  text = @getAttribute 'annot-text'
  tip = @title
  @title = tr 'ちょっとまってて ...'
  s = trBean.translators()
  if s
    for key in s.split ','
      trans = trBean.translate(text, key) or "#{tr 'failed'}!"
      if tip
        tip += '\n' # does NOT work on windows, though
      tip += key + ': ' + trans
      @title = tip

  @classList.remove 'annot-locked'

## Render

# %span sentence
#   %ruby(class=word#{number})
#     %rb text
#     %rt ruby
_renderRubyElement = (text, ruby, feature, className) -> # must be consistent with parseparagraph in mecabrender.py
  rb = document.createElement 'rb'
  rb.textContent = text
  rt = document.createElement 'rt'
  rt.textContent = ruby
  ret = document.createElement 'ruby'
  ret.className = className
  ret.appendChild rb
  ret.appendChild rt
  ret.ondblclick = ->
    ttsBean.speak text if text and isTtsEnabled()

  #ret.title = feature if feature
  if feature
    ret.onmouseover = do (feature) ->-> # bind
      @title = feature unless isTranslationTipEnabled()
    ret.onmouseout = ->
      @removeAttribute 'title' if @title
  ret

renderRuby = (text) -> # string -> node  the target node to replace source
  data = jlpBean.parse text
  if data
    ret = document.createDocumentFragment()
    for sentence in JSON.parse data
      seg = document.createElement 'span'
      seg.className = 'annot-ruby'
      segtext = ''
      firstletter = lastletter = false
      for word in sentence # word = [surf, ruby, feature, className]
        surf = word[0]

        firstletter = isalnum surf[0]
        if firstletter and lastletter
          segtext += ' ' # not needed, but there is no drawbacks
          space = document.createTextNode ' '
          #space.class = 'annot-space' # not needded
          seg.appendChild space
        lastletter = isalphapunct surf.slice -1

        segtext += surf
        ruby = _renderRubyElement.apply @, word
        seg.appendChild ruby
      if segtext
        seg.setAttribute 'annot-text',  segtext
        #seg.onclick = do (segtext) ->-> # bind
        #  ttsBean.speak segtext if isTtsEnabled()
        seg.onclick = onSpeak
        seg.onmouseover = onTranslateTip

      ret.appendChild seg
    ret

_renderTranslationElement = (trans, text) -> # string, string -> node  the second text could be null
  ret = document.createElement 'span'
  ret.className = 'annot-tr'
  #ret.className = if el.className? then el.className + ' annot-tr' else 'annot-tr'
  #ret.title = if el.title then el.title + '\n' + text else text
  #ret.id = el.id if el.id
  ret.title = text # duplicate
  if text?
    ret.textContent = trans
    ret.setAttribute 'annot-text', text
    ret.onclick = onSpeak
    #ret.onmouseover = onTranslateTip
  else
    ret.title = trans
  ret

PARAGRAPH_SPLIT_STR = '【】「」『』♪'
PARAGRAPH_SPLIT_RE = /([【】「」『』♪])/

SENTENCE_SPLIT_RE = /(.*?[…‥！？。?!]+)/

renderTranslation = (text) -> # string -> node  node of the translated text
  ret = document.createDocumentFragment()
  for p in text.split PARAGRAPH_SPLIT_RE
    if text.length == 1 and text in PARAGRAPH_SPLIT_RE
      ret.appendChild _renderTranslationElement p
    else
      for q in p.split SENTENCE_SPLIT_RE # ?! to keep delim with previous text
        if q isnt ''
          trans = trBean.translate q, null # engine is null, use default engine
          if trans?
            ret.appendChild _renderTranslationElement trans, q
  ret

_renderSourceElement = (text, active) -> # string, bool -> node
  ret = document.createElement 'span'
  ret.className = 'annot-src'
  ret.textContent = text
  if active
    ret.setAttribute 'annot-text', text
    ret.onclick = onSpeak
    ret.onmouseover = onTranslateTip
  ret

renderSource = (text, el) -> # string, node -> node  input node is #text node which does not have class and id
  ret = document.createDocumentFragment()
  for p in text.split PARAGRAPH_SPLIT_RE
    if text.length == 1 and text in PARAGRAPH_SPLIT_RE
      ret.appendChild _renderSourceElement p, false # active = false
    else
      for q in p.split SENTENCE_SPLIT_RE # ?! to keep delim with previous text
        if q isnt ''
          ret.appendChild _renderSourceElement q, true # active = false
  ret

createContainer = (x, y) -> # node, node -> node  container of the replaced text
  #if el.nodeName is '#text' # '#text' does not has class, have to replace with span
  ret = document.createElement 'div'
  ret.className = 'annot-container'

  c = document.createElement 'div'
  c.className = 'annot-child'
  c.appendChild x
  ret.appendChild c

  c = document.createElement 'div'
  c.className = 'annot-child'
  c.appendChild y
  ret.appendChild c

  ret

## Inject

# http://stackoverflow.com/questions/9452340/iterating-through-each-text-element-in-a-page
# http://javascript.info/tutorial/traversing-dom
#itertextnodes = (node, callback) -> # DocumentElement, function(DocumentElement) ->
#  node = node.firstChild
#  while node?
#    if node.nodeType is 3
#      callback node
#    else if node.nodeType is 1
#      itertextnodes node, callback
#    node = node.nextSibling

# Node type: https://developer.mozilla.org/en-US/docs/Web/API/Node.nodeType
#   ELEMENT_NODE 	1
#   ATTRIBUTE_NODE 	2
#   TEXT_NODE 	3
#   CDATA_SECTION_NODE 	4
#   ENTITY_REFERENCE_NODE 	5
#   ENTITY_NODE 	6
#   PROCESSING_INSTRUCTION_NODE 	7
#   COMMENT_NODE 	8
#   DOCUMENT_NODE 	9
#   DOCUMENT_TYPE_NODE 	10
#   DOCUMENT_FRAGMENT_NODE 	11
#   NOTATION_NODE 	12
collecttextnodes = (node, ret) -> # DocumentElement, [] ->
  node = node.firstChild
  while node?
    if node.nodeType is 3
      ret.push node #if node.nodeName is '#text' # only deal with #text
    else if node.nodeType is 1
      collecttextnodes node, ret
    node = node.nextSibling

inject = (el) -> # DocumentElement ->
  el.className += ' annot-root' # root class for all elements
  nodes = []
  collecttextnodes el, nodes

  enable_ruby = isRubyEnabled()
  enable_trans = isFullTranslationEnabled()
  repl = ruby = trans = null
  for node in nodes
    text = trim node.textContent
    if text
      if enable_ruby
        ruby = renderRuby text #, node
      if enable_trans
        trans = renderTranslation text, node
      src = renderSource text, node
      if ruby? or trans?
        repl = document.createDocumentFragment()
        repl.appendChild src #if src?
        if ruby and trans
          repl.appendChild createContainer ruby, trans
        else
          repl.appendChild ruby if ruby?
          repl.appendChild trans if trans?
      else
        repl = src
      node.parentNode.replaceChild repl, node
      #node.className += ' annot-src'
      #node.parentNode.insertBefore repl, node

# Export the inject function
@annotate = inject

# EOF

## Main

#do ->
#  if document.body?
#    inject document.body
#  else
#    window.onload = -> inject document.body
#  #if @$
#  #  $ ->
#  #    #// jQuery plugin, example:
#  #    $.fn.inject = ->
#  #        @each -> inject @
#  #    $('body').inject()
