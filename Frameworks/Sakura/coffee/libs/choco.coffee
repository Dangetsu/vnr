###
choco.coffee
1/26/2013 jichi
A C++/Qt-like suger to CoffeeScript.
See: https://gitorious.org/qmlweb
- Signal bindings
- Anchors
- Class hierarchy
###

#define = @define ? require 'amdefine', @module
#define ['underscore', 'underscore.string', 'jquery'], (_, _s, $) ->
  #_bind = (fn, self) ->-> fn.apply self, arguments # the same as coffeescript __bind
  #  new class
((_, _s) ->
  @choco = new class
    ###
    Mixin
    ###

    #_.mixin = function(obj) {
    #  each(_.functions(obj), function(name){
    #    var func = _[name] = obj[name];
    #    _.prototype[name] = function() {
    #      var args = [this._wrapped];
    #      push.apply(args, arguments);
    #      return result.call(this, func.apply(_, args));
    #    };
    #  });
    #};
    @mixin: => (obj) -> @prototype[k] = v for k,v of obj

    #@mixin require 'sprintf'

    ###
    Algebra
    ###

    # http://en.wikipedia.org/wiki/Machine_epsilon
    epsilon = _epsilon = 5.96e-08 * 2 # epsilon nfor single precision
    feq: _feq = (x, y) -> _epsilon > Math.abs x - y

    ###
    Basic types
    ###

    nop: _nop = ->
    Nop: _Nop = -> _nop

    Undefined: _Undefined = ->
    Null: _Null = -> null
    True: _True = -> true
    False: _False = -> false

    List: _List =
      # http://stackoverflow.com/questions/3954438/remove-item-from-array-by-value
      remove: (a, el) -> # Array, HTMLElement
        while ~(i=_.indexOf a, el)
            a.splice i, 1

      removeFirst: (a, el) -> # Array, HTMLElement
        a.splice i,1 if ~(i=_.indexOf a, el)

      removeLast: (a, el) -> # Array, HTMLElement
        a.splice i,1 if ~(i=_.lastIndexOf a, el)

    ###
    DOM
    ###

    # int length=8, return string
    #randomId: (length=8, C='abcdefghijklmnopqrstuvwxyz0123456789') ->
    #  (C.charAt(_.random 0,C.length-1) for [1..length]).join ''
    #createId: =>
    #  while (id = "choco_#{@randomId()}") in @ids then undefined
    #  @ids.push id
    #  id
    #containsId: (id) => id in @ids
    #createId: -> _.uniqueId '__choco_'

    ###
    String:
    ###

    # http://d.hatena.ne.jp/reinyannyan/20060711/p1
    # http://stackoverflow.com/questions/6020714/escape-html-using-jquery
    # Difference from _.escape that '/' and quotes are not escaped
    escape: (str) ->
      str.replace /[&"<>]/g, (c) ->
        {
          '&': '&amp;'
          '"': '&quot;'
          '<': '&lt;'
          '>': '&gt;'
        }[c]

    ###
    Core objects
    ###

    @defineClass: (name, Name=null, cls) =>
      Name ?= _s.capitalize name
      cls.className = Name
      cls.prototype?.className = Name
      @prototype[name] = -> new cls _.values(arguments) ...
      @prototype[Name] = cls

    @defineClass 'prototype', null, class _Prototype extends Object
      @propdef: (prop, desc) -> # not =>, so that the @prototype is bounded to caller
        # https://developer.mozilla.org/en-US/docs/JavaScript/Reference/Global_Objects/Object/defineProperty
        #desc.configurable = true
        #desc.enumerable = true
        Object.defineProperty @prototype, prop, desc

        # defineProperty has higher priority than @prototype.value, and it is difficult to redefine
        #  if desc.get? and desc.set?
        #    -> if arguments.length then desc.set.apply @, arguments else desc.get.apply @
        #  else
        #    desc.get ? desc.set ? undefined
        #@prototype[prop] = fn
        #@bind prop, fn if fn?
      @propget: (prop, getter) -> # string, fn
        @propdef prop, get: getter
      @propset: (prop, setter) -> # string, fn
        @propdef prop, set: setter
      @propalias: (px, py) -> # string, string
        @propdef px,
          get: -> @[py]
          set: (v) -> @[py] = v
      @alias: (x, y) ->  # string, string
        @prototype[x] = @prototype[y]

      constructor: -> super

    @defineClass 'signal', null, class _Signal extends _Prototype
      @propget 'slots', -> @_slots  # [fn]
      @propget 'empty', -> !@_slots # bool
      constructor: ->
        super
        @_slots = [] # [function]
      #slots: => @_slots
      connect: (s) => @_slots.push s unless s in @_slots; @ # return this
      disconnect: (s) => _List.removeFirst @_slots, s; @        # return this
      emit: => # any arguments
        for s in @_slots
          (if s instanceof _Signal then s.emit else s)
            .apply null, arguments

    @defineClass 'object', null, class _Object extends _Prototype
      # Property object creation are delayed
      @signal: (sig) -> # string
        slot = "on#{_s.capitalize sig}"
        _sig = "_#{sig}"
        @prototype[slot] = _nop
        @propget sig, ->
          @[_sig] ?= (new _Signal).connect =>
            @[slot]?.apply null, arguments
      # Define a property with signal and slots. Property object creation are delayed
      @property: (prop, ctor) -> # string, fn
        Prop = _s.capitalize prop
        slot = "on#{Prop}Changed"
        setter = "set#{Prop}"
        getter = "get#{Prop}"
        sig = "#{prop}Changed"
        _sig = "_#{sig}"
        _prop = "_#{prop}"
        eq =
          if ctor is Number then (x, y) -> x is y or (not isNaN(x) and not isNaN(y) and _feq x, y)
          else (x, y) -> x is y
        @prototype[slot] = _nop
        @prototype[getter] = ->
          @[_prop] ?= ctor?.apply @, arguments
        @prototype[setter] = (v) ->
          unless eq v, (w=@[_prop])
            v ?= ctor?.apply @ # i.e., when ctor is given, property will never be undefined
            @[_prop] = v
            @[slot]? v, w
            @[_sig]?.emit v, w
        @propget sig, -> @[_sig] ?= new _Signal
        @propdef prop,
          get: -> @[getter]?.apply @, arguments # allow user to redefine setter or getter later
          set: -> @[setter]?.apply @, arguments # allow user to redefine setter or getter later

      constructor: -> super

      bind: (prop, y, yprop) -> # string, _Object, string, bind y's yprop to this
        yprop ?= prop
        @[prop] = y[yprop]
        y["#{yprop}Changed"].connect @["set{_.capitalize prop}"]

    ###
    Non-object structures
    ###

    @defineClass 'pair', null, class _Pair extends _Prototype
      constructor: (@first, @second) -> super

    @defineClass 'point', null, class _Point extends _Prototype
      constructor: (@x=0, @y=0) -> super

    @defineClass 'size', null, class _Size extends _Prototype
      constructor: (@width=0, @height=0) -> super

    @defineClass 'rect', null, class _Rect extends _Prototype
      constructor: (@x=0, @y=0, @width=0, @height=0) -> super

    ###
    Events
    ###

    @defineClass 'timer', null, class _Timer extends _Object
      @singleShot: (msecs, fn) -> setTimeout fn, msecs
      @property 'interval', Number
      @property 'active', _False
      @property 'singleShot', _True # Different from Qt.QTimer
      @signal 'timeout'
      constructor: (interval, fn, singleShot) ->
        super
        @interval = interval if interval?
        @timeout.connect fn if fn?
        @singleShot = singleShot if singleShot?
      onTimeout: =>
        if @singleShot
          @active = false
        else
          @_timeoutId = setTimeout @timeout.emit, @interval
      start: (interval) =>
        @interval = interval if interval?
        @stop() if @active
        @_timeoutId = setTimeout @timeout.emit, @interval
        @active = true
      stop: =>
        if @active
          clearTimeout @_timeoutId
          @active = false

)(_, _.str)

# EOF
