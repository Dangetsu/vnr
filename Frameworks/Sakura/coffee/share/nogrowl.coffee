###
nogrowl.coffee
8/30/2014 jichi

Dummy.
###

log = (t) ->
warn = (t) ->
error = (t) ->

r = log
r.log = log
r.warn = warn
r.error = error

@growl = r

# EOF
