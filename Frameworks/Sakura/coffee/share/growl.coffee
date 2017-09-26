###
growl.coffee
8/30/2014 jichi
###

#define 'bootstrap.growl'

log = (t) -> $.growl t, type: 'success'
warn = (t) -> $.growl t, type: 'warning'
error = (t) -> $.growl t, type: 'error'

r = log
r.log = log
r.warn = warn
r.error = error

@growl = r

# EOF
