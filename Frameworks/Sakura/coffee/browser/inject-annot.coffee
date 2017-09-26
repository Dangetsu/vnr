# inject-annot.coffee
# 3/28/2014 jichi
# Invoked by QWebFrame::evaluaeJavaScript
# Beans:
# - cdnBean: coffeebean.CdnBean
# - settingsBean: coffeebean.SettingsBean

#repaint = -> # ->
#  # http://stackoverflow.com/questions/3485365/how-can-i-force-webkit-to-redraw-repaint-to-propagate-style-changes
#  v = document.body.className
#  document.body.className += ' inject-dummy'
  #  document.body.className = v

#getdataset = -> # -> string  the value of %body[data-inject[
#  ret = if settingsBean.isJlpEnabled() then ['enabled'] else ['disabled']
#  ret.push 'tts' if settingsBean.isTtsEnabled()
#  ret.push 'tr' if settingsBean.isTranslationEnabled()
#  ret.join ' '
#document.body.dataset.annot = getdataset()

(->
  toggleclass = (el, cls, t) -> # element, string, booleaan
    if t then el.classList.add cls else el.classList.remove cls

  toggleclass @, 'annot-opt-tr', settingsBean.isFullTranslationEnabled()
  toggleclass @, 'annot-opt-ruby', settingsBean.isRubyEnabled()
  toggleclass @, 'annot-opt-tts', settingsBean.isTtsEnabled()
  toggleclass @, 'annot-opt-tr-tip', settingsBean.isTranslationTipEnabled()
).apply document.body

# Make sure this script is only evaluated once
unless @ANNOT_INJECTED
  @ANNOT_INJECTED = true

  linkcss = (url) -> # string -> el  return the inserted element
    el = document.createElement 'link'
    #el.type = 'text/css'
    el.rel = 'stylesheet'
    el.href = url #+ '.css'
    document.head.appendChild el
    el

  linkjs = (url) -> # string -> el  return the inserted element
    el = document.createElement 'script'
    el.src = url #+ '.js'
    document.body.appendChild el
    el

  linkcss cdnBean.url 'client-annot.css'
  linkjs cdnBean.url 'client-annot'

# EOF

#repaint = -> # Force a repaint
#  # http://stackoverflow.com/questions/3485365/how-can-i-force-webkit-to-redraw-repaint-to-propagate-style-changes
#  # http://stackoverflow.com/questions/8840580/force-dom-redraw-refresh-on-chrome-mac
#  if document.body
#    v = document.body.style.display
#    v = 'block'
#    if v isnt 'none'
#      document.body.style.display = 'none'
#      h = document.body.offsetHeight
#      document.body.style.display = v
