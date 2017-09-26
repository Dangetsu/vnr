###
rest.coffee
1/5/2014 jichi
This file is stand-alone
###

#define 'jquery'

# libs/ajax.coffee

VERSION = 1404193846
AGENT = 'vnr'

postJSON = ({data:data, url:url, success:success, error:error}) ->
  data.version = VERSION
  data.agent = AGENT
  console.log url
  $.ajax
    type: 'POST'
    contentType: 'application/json;charset=utf-8'
    dataType: 'json'
    data: JSON.stringify data
    url: url
    success: success
    error: error

growl =
  showInternetError: ->
  showSignInError: ->
  showDupError: ->

defs =
  STATUS_OK: 0
  STATUS_ERR: 1      # unknown error
  STATUS_USER_ERR: 2 # user does not exist
  STATUS_DUP_ERR: 3  # duplicate entry

# HOST is defined in defs.coffee
#HOST = 'http://sakuradite.com'
#HOST = 'http://localhost:8080'
#HOST = 'http://153.121.54.194'

@rest = # export
  forum: # ajax/forum.coffee
    list: (type, {data:data, success:success, error:error}) ->
      postJSON
        url: "#{HOST}/api/json/#{type}/list"
        data: data
        success: (res) ->
          if res.status is 0 and res.data
            list = res.data
            console.log type, 'list: count =', list.length
            #growl.showEmptyList type unless list.length
            success? list
            return
          growl.showInternetError type
          error?()
        error: (xhr) ->
          console.warn type, 'error:', JSON.stringify xhr
          growl.showInternetError type
          error?()

    query: (type, {data:data, success:success, error:error}) ->
      postJSON
        url: "#{HOST}/api/json/#{type}/query"
        data: data
        success: (res) ->
          if res.status is 0 and res.data?.id
            obj = res.data
            console.log type, 'query: id =', obj.id
            success? obj
            return
          growl.showInternetError type
          error?()
        error: (xhr) ->
          console.warn type, 'error:', JSON.stringify xhr
          growl.showInternetError type
          error?()

    create: (type, {data:data, success:success, error:error}) ->
      postJSON
        url: "#{HOST}/api/json/#{type}/create"
        data: data
        success: (res) ->
          if res.status is 0 and res.data?.id
            obj = res.data
            console.log type, 'create: id =', obj.id
            success? obj
            return
          switch res.status
            when defs.STATUS_USER_ERR then growl.showSignInError()
            when defs.STATUS_DUP_ERR then growl.showDupError type
            else growl.showInternetError type
          error?()
        error: (xhr) ->
          console.warn type, 'error:', JSON.stringify xhr
          growl.showInternetError type
          error?()

    update: (type, {data:data, success:success, error:error}) ->
      postJSON
        url: "#{HOST}/api/json/#{type}/update"
        data: data
        success: (res) ->
          if res.status is 0 and res.data?.id
            obj = res.data
            console.log type, 'update: id =', obj.id
            success? obj
            return
          if res.status is defs.STATUS_USER_ERR
            growl.showSignInError()
          else
            growl.showInternetError type
          error?()
        error: (xhr) ->
          console.warn type, 'error:', JSON.stringify xhr
          growl.showInternetError type
          error?()

@ticket =
  update: ({data:data, success:success, error:error}) ->
    ID = 'ticket'
    #if LOCKED
    #  growl.showInternetBusy data.type
    #else
    #  LOCKED = true # prevent massive ticket
    postJSON
      url: "#{HOST}/api/json/#{ID}/update"
      data: data
      success: (res) ->
        #LOCKED = false
        if res.status is 0 and res.id
          console.log ID, 'update: id =', res.id
          success?()
          return
        if res.status is defs.STATUS_USER_ERR
          growl.showSignInError()
        else
          growl.showInternetError data.type
        error?()
      error: (xhr) ->
        #LOCKED = false
        console.warn ID, 'error:', JSON.stringify xhr
        growl.showInternetError data.type
        error?()

  list: ({data:data, success:success, error:error}) ->
    ID = 'ticket'
    postJSON
      url: "#{HOST}/api/json/#{ID}/list"
      data: data
      success: (res) ->
        if res.status is 0 and res.data
          list = res.data
          console.log ID, 'list: count =', list.length
          #growl.showEmptyList type unless list.length
          success? list
          return
        growl.showInternetError data.type
        error?()
      error: (xhr) ->
        console.warn ID, 'error:', JSON.stringify xhr
        growl.showInternetError data.type
        error?()

# EOF
