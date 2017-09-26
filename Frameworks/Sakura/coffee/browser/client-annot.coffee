# client-annot.coffee
# 3/28/2014 jichi
# This file must be merged with annot.coffee.
## Main

do ->
  if document.body?
    annotate document.body
  else
    window.onload = -> annotate document.body
  #if @$
  #  $ ->
  #    #// jQuery plugin, example:
  #    $.fn.inject = ->
  #        @each -> inject @
  #    $('body').inject()

# EOF
