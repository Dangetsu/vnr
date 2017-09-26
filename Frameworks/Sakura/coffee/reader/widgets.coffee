# widgets.coffee
# 10/9/2013 jichi

#dprint = -> console.log.apply console,  arguments
#dprint = ->

# See: http://code.google.com/p/dragdealer/source/browse/trunk/dragdealer.js
@ZoomSlider = class
  id: 'zoomSlider'
  inverse: true

  constructor: (@callback) -> # @param  callback  (y) ->

    # See: http://code.ovidiu.ch/dragdealer/
    @dd = new Dragdealer @id,
      horizontal: false
      vertical: true
      y: if @inverse then 1 else 0
      #steps: 6
      animationCallback: (x, y) =>
        @callback if @inverse then (1 - y) else y

  reloadOffset: => @dd.setWrapperOffset()

@Toolbar = class
  id: 'toolbar'

  # @param  options Options
  constructor: (@bean, @options={}) -> # SkWebBean, {}
    @$el = $ "##{@id}"
    @bind()

  bind: =>
    @$el.find('.btn.btn-top').click => @scrollTop(); false
    @$el.find('.btn.btn-bottom').click => @scrollBottom(); false

    # http://stackoverflow.com/questions/2624111/preferred-method-to-reload-page-with-javascript
    #document.location.reload true; false
    @$el.find('.btn.btn-refresh').click => @bean.reload(); false

    $(window).on 'scroll resize', =>
      #x = $window.scrollLeft() + @bean.width() - (@options.width ? 0)
      x = 0 # not used
      #wh = $window.height() # incorrect orz
      y = $(window).scrollTop() + @bean.height() - (@options.height ? 0)
      #$el.animated
      @$el.css
        #left: "#{x}px"
        top: "#{y}px"
        #position: 'absolute' # already set in css
      @options.move? x, y
      false

  scrollTop: => @scrollTo 0
  scrollBottom: => @scrollTo $(document).height()
  scrollTo: (height) -> # int
    $('body').animate scrollTop: height

# EOF
