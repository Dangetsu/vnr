###
linkify.coffee
1/27/2014 jichi

http://stackoverflow.com/questions/4504853/how-do-i-extract-a-url-from-plain-text-using-jquery
http://stackoverflow.com/questions/1500260/detect-urls-in-text-with-javascript
https://npmjs.org/package/html-linkify
https://raw.github.com/parshap/html-linkify/master/index.js

android.text.util.Linkify
http://grepcode.com/file/repository.grepcode.com/java/ext/com.google.android/android/2.0_r1/android/text/util/Regex.java#Regex.0WEB_URL_PATTERN
###

RE_YT = /[?&]v=([0-9a-zA-Z_-]+)/
RE_LINK = /(^|[^=\]])(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig

#YT_WIDTH = 640
#YT_HEIGHT = 480
YT_WIDTH = 400
YT_HEIGHT = 300

@linkify = (t) -> # string -> string
  t.replace RE_LINK, (all, prefix, url) ->
    #url = _.escape url
    ret = """<a target="_blank" href="#{url}">#{url}</a>"""
    if ~url.indexOf 'youtube.com'
      m = url.match RE_YT
      if m
        vid = m[1]
        #url = _.escape url
        #yturl = 'http://www.youtube.com/watch?v=' + vid
        ret += """<br/><iframe width="#{YT_WIDTH}" height="#{YT_HEIGHT}" src="http://youtube.com/embed/#{vid}" frameborder="0" allowfullscreen />"""
    prefix + ret

# EOF
