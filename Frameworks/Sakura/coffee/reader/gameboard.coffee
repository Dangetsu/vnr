# gameboard.coffee
# 7/31/2013 jichi
# Required by gameboard.haml
# Beans:
# - bean: gameboard.GameBoardBean

#dprint = -> console.log.apply console,  arguments
dprint = ->
timer = -> new choco.Timer arguments ...

#SPIN_DURATION = 600 # jquery default is 400

## Game manager ##

DEF_ITEM_WIDTH = 160 # in pixel

@CURRENT_TIME = Math.floor (new Date).getTime()/1000 # int unix timestamp
@RECENT_TIME = @CURRENT_TIME - 86400*30

# See: http://stackoverflow.com/questions/5515869/string-length-in-bytes-in-javascript
# string t, return int  length of utf8 string
#_strsize = (t) -> (unescape encodeURIComponent t).length

GAME_HAML = Haml '''\
.game(data-id="#{g.itemId}" style="width:#{width}px")
  .header
    .label.label-info(data-text="#{g.title}" title="#{g.title} (#{g.romajiTitle})") = shorten(g.title)
    :if g.series
      .label.label-success(title="#{g.series}シリーズ") = g.series
    :if g.brand
      :for it in g.brand.split(',')
        .label.label-inverse(title="ブランド: #{it}") = it
    :if g.visitCount
      :if visitColor === ''
        .badge(title="弾幕数(字幕数)/再生数(使用者)") = g.countString
      :if visitColor === 'o'
        .badge.badge-warning(title="弾幕数(字幕数)/再生数(使用者)") = g.countString
      :if visitColor === 'r'
        .badge.badge-important(title="弾幕数(字幕数)/再生数(使用者)") = g.countString
      :if visitColor === 'g'
        .badge.badge-success(title="弾幕数(字幕数)/再生数(使用者)") = g.countString
      :if visitColor === 'b'
        .badge.badge-inverse(title="弾幕数(字幕数)/再生数(使用者)") = g.countString
    :if g.overallScoreCount
      .badge.badge-important(title="総合得点×点数")
        &#9734;#{sprintf('%.1f', g.overallScore)}
        :if g.overallScoreCount > 1
          x#{g.overallScoreCount}
    :if g.ecchiScoreCount
      .badge.badge-warning(title="えっち得点×点数")
        H  #{sprintf('%.1f', g.ecchiScore)}
        :if g.ecchiScoreCount > 1
          x#{g.ecchiScoreCount}
    :if scoreColor
      :if scoreColor === 'o'
        .badge.badge-warning(title="得点×点数") #{g.scapeMedian}x#{g.scapeCount}
      :if scoreColor === 'r'
        .badge.badge-important(title="得点×点数") #{g.scapeMedian}x#{g.scapeCount}
      :if scoreColor === 'g'
        .badge.badge-success(title="得点×点数") #{g.scapeMedian}x#{g.scapeCount}
      :if scoreColor === 'b'
        .badge.badge-inverse(title="得点×点数") #{g.scapeMedian}x#{g.scapeCount}
    :if g.tags
      :for it in g.tags.split(',')
        .label(title="#{it}") = it
    :if g.date
      .label(data-text="#{g.moment.format('YYYYMM')}" title="発売日") = g.moment.format('M/D/YYYY')
    :if g.date > CURRENT_TIME
      .label.label-important(title="未発売") 未発売
    :if sizeColor
      :if sizeColor === 'o'
        .label.label-warning(title="容量GB" data-text="GB") #{sizeTag}
      :if sizeColor === 'r'
        .label.label-important(title="容量GB" data-text="GB") #{sizeTag}
      :if sizeColor === 'g'
        .label.label-success(title="容量GB" data-text="GB") #{sizeTag}
      :if sizeColor === 'b'
        .label.label-inverse(title="容量MB" data-text="MB") #{sizeTag}
  %img(src="#{g.imageUrl}" title="#{tip}")
  .footer
    :if g.artists
      :for it in g.artists.split(',')
        .label(data-text="#{it}" title="原画: #{it}") = '*' + it
    :if g.sdartists
      :for it in g.sdartists.split(',')
        .label(data-text="#{it}" title="SD原画: #{it}") = '.' + it
    :if g.writers
      :for it in g.writers.split(',')
        .label(data-text="#{it}" title="脚本: #{it}") = '+' + it
    :if g.musicians
      :for it in g.musicians.split(',')
        .label(data-text="#{it}" title="音楽: #{it}") = '♪' + it
'''

# Make it global so that it can be used to render haml
# string t, int limit, return string
@shorten = (t, limit=11) ->
  if t.length <= limit then t else (t[0..limit-1] + '..')
  #if _strsize(t) <= limit then t else (t[0..limit-1] + '..')

class GameManager
  id: 'games' # containerId
  itemSelector: '.game'

  itemWidth: DEF_ITEM_WIDTH # int in pixel

  constructor: (@bean) -> # GameBoardBean
    @filters =   # {string name, string value}
      tags: []      # [string]
    @options =  # parameters parsed to bean
      sort: 'date'  # string, initial order
      reverse: true # bool

    #@spinner = new Spinner()

    @$search = $ 'input#search'
    @searchText = ''
    @searchTimer = timer 400, @triggerSearch

    @$container = $ '#' + @id # cached
    #@filters = {} # key: jquery selector
    @$container.masonry
      itemSelector: @itemSelector
      #isAnimated: false # disable animation
      #transitionDuration: 0 # set to 0 to disable animation

      #isFitWidth: true # align center
      #transitionDuration: 400
      #columnWidth: 160 # 10/8/2013: does not work?!

    @masonryLayoutTimer = timer 200, => @$container.masonry()
    @masonryAnimateTimer = timer 600, @masonryStartAni # larger than 400

    @scrollTimer = timer 2000 # prevent from scrolling too fast

    #@resetPage()
    @bind()
    @refresh()

  masonryLayoutLater: => @masonryLayoutTimer.start()

  masonryStartAniLater: => @masonryAnimateTimer.start()

  masonryStartAni: =>
    @$container.masonry # enable anime
      isAnimated: true # default = true, enable animation
      transitionDuration: 400 # default = 400, set to 0 to disable animation

  masonryStopAni: =>
    @masonryAnimateTimer.stop()
    @$container.masonry # enable anime
      isAnimated: false # disable animation
      transitionDuration: 0 # set to 0 to disable animation

  ## Zoom ##

  setItemWidth: (v) => # @param  v  int
    v = Math.floor v
    if @itemWidth isnt v
      @itemWidth = v
      $(@itemSelector).width v
      #@$container.masonry()
      @masonryLayoutLater()

  zoom: (v) => # @param  v  float percentage
    @setItemWidth v * DEF_ITEM_WIDTH
    #@$container.masonry()

  ## Queries ##

  queryPageSize: -> # @return  int
    w = $(document).width()
    Math.max 50, w/20

  queryMorePageSize: -> # @return  int
    w = $(document).width()
    Math.max 25, w/30

  #resetPage: =>
  #  @pageStart = 0
  #  w = $(document).width()
  #  @pageLimit = Math.max(50, w/20)
  #increasePageLimit: =>
  #  w = $(document).width()
  #  @pageLimit += Math.max(25, w/30)

  # @param  args  {start:int, count:int}
  # @return  [GameObject]
  queryGames: (args) =>
    l = JSON.parse @bean.games.apply @bean, [
      args?.start or 0
      args?.count or 50
      @options.sort
      @options.reverse
      if @filters then JSON.stringify @filters else ''
    ]
    if l.length
      for g in l
        g.moment = moment(g.date * 1000)
        g.fileSize = Math.floor(g.fileSize / (1024 * 1024)) if g.fileSize > 0 # fileSize is in MB

        s = g.visitCount or 1
        s += "(#{g.playUserCount})" if g.playUserCount > 1
        t = ''
        t = g.commentCount if g.commentCount
        t += "(#{g.subtitleCount})" if g.subtitleCount
        s = t + '/' + s if t
        g.countString = s
    l

  ## Tags ##

  toggleKeyword: (text) => # param  text  unicode
    # http://stackoverflow.com/questions/16994212/remove-item-from-array-of-objects-in-javascript
    # http://stackoverflow.com/questions/237104/array-containsobj-in-javascript
    if text in @filters.tags
      @filters.tags = @filters.tags.filter (it) -> it isnt text
    else
      @filters.tags.push text

  ## Show ##

  bind: =>
    dprint 'bind: enter'

    #@$search.keyup @searchTimer.start  # does not work
    @$search.keyup => @searchTimer.start()

    $('.search .close').click => @search ''; false

    $ window
      .on 'scroll resize', => # http://stackoverflow.com/questions/3898130/how-to-check-if-a-user-has-scrolled-to-the-bottom
        #wh = $(window).height() # incorrect orz
        wh = @bean.height()
        if $(window).scrollTop() + wh > $(document).height() - Math.max(200, wh/2) and @bean.currentCount() < @bean.totalCount() and not @scrollTimer.active
          @scrollTimer.start()
          @more()
          #@increasePageLimit()
          #@refresh()
          #$(window).bind('keydown', function(event) {
      .keydown (e) => # http://stackoverflow.com/questions/93695/best-cross-browser-method-to-capture-ctrls-with-jquery
        if e.ctrlKey or e.metaKey
          switch String.fromCharCode(e.which).toLowerCase()
            when 'f'
              e.preventDefault()
              @$search.focus()
              #alert 'cmd-f'

    self = @

    $('#keyword .close').click ->
      if self.filters.tags.length
        $('#keyword .label').removeClass 'label-info'
        self.filters.tags.length = 0
        self.refresh()
      false
    $('#keyword .label').click ->
      #if @classList.contains cls
      self.toggleKeyword $.trim @innerHTML
      @classList.toggle 'label-info'
      self.refresh()
      false

    $('.options .option-set a').click ->
      $this = $ @
      # don't proceed if already selected
      return false if $this.hasClass 'selected'

      $optionSet = $this.closest '.option-set'
      $optionSet.find('.selected').removeClass 'selected'
      $this.addClass 'selected'

      # make option object dynamically, i.e. { filter: '.my-filter-class' }
      options = {}
      key = $optionSet.data 'option-key'
      value = $this.data 'option-value'

      # parse 'false' as false boolean
      #value = if value is 'false' then false else value
      if key is 'filter'
        group = $optionSet.data 'option-group'
        if value is ''
          delete self.filters[group]
        else
          self.filters[group] = value
      else
        self.options[key] = value

      #self.resetPage()
      self.refresh()
      false

      #if key is 'filter'
      #  self.filters[group] = value
      #  #options.filter = _.values(self.filters).join ''
      #  options.filter = self.getFilter()
      #else
      #  options[key] = value
      #if key is 'layoutMode' and typeof changeLayoutMode is 'function'
      #  changeLayoutMode $this, options # changes in layout modes need extra logic
      #else # otherwise, apply new options
      #  self.isotope options
      #false

    dprint 'bind: leave'

  refresh: =>
    dprint 'refresh: enter'
    #@resetPage()

    # Temporarily disable animation and scheduled refresh task
    @masonryLayoutTimer.stop()
    @masonryStopAni()

    # Clear first as it might take some time
    $items = $ @itemSelector
    if $items.length
      @$container.masonry 'remove', $items
      #@$container.empty() # empty is not needed for the latest version of masonry
    #  setTimeout @repaint, 400 # repaint later
    #else
    #setTimeout @repaint, 300 # surrender current event loop
    @repaint()

    @masonryStartAniLater()

  showBlocker: -> $('.blocker:hidden').fadeIn()
  hideBlocker: -> $('.blocker:visible').fadeOut()

  #showSpinner: =>
  #  #@spinTimer.stop()
  #  $window = $ window
  #  el = document.getElementById 'spinner'
  #  el.style.left = "#{$window.scrollLeft() + @bean.width() / 2}px"
  #  el.style.top = "#{$window.scrollTop() + @bean.height() / 2}px"
  #  $('#spinner').fadeIn()
  #  @spinner.spin el

  #hideSpinner: =>
  #  $('#spinner').hide()
  #  @spinner.stop()

  repaint: =>
    dprint 'repaint: enter'
    gamelist = @queryGames
      count: @queryPageSize()
      #start: 0
    unless gamelist.length
      @games = {}
      @showBlocker()
    else
      @hideBlocker()
      @games = new ->
        @[it.itemId] = it for it in gamelist
        @

      $h = $ @render gamelist
      @$container.append $h
                 .masonry 'appended', $h
                 #.masonry()
      @rebind()
      @masonryLayoutLater()
      $h.find('img').load @masonryLayoutLater

      #@showSpinner()
      #$h = $ @render gamelist
      #  .imagesLoaded =>
      #    @hideSpinner()
      #    @$container.append $h
      #               .masonry 'appended', $h
      #               .masonry()
      #    @rebind()
    dprint 'repaint: leave'

  more: =>
    dprint 'more: enter'
    gamelist = @queryGames
      count: @queryMorePageSize()
      start: @bean.currentCount()
    if gamelist.length
      #@hideBlocker()
      @games[it.itemId] = it for it in gamelist


      $h = $ @render gamelist
      @$container.append $h
                 .masonry 'appended', $h
                 #.masonry()
      @rebind()
      @masonryLayoutLater()
      $h.find('img').load @masonryLayoutLater

      #$h = $ @render gamelist
      #  .imagesLoaded =>
      #    #@hideSpinner()
      #    @$container.append $h
      #               .masonry 'appended', $h
      #               .masonry()
      #    @rebind()
    dprint 'more: leave'

  rebind: =>
    dprint 'rebind: enter'

    #_get = (el) => @games[el.dataset.id]
    #_get$ = ($el) => @games[$el.data 'id']
    #$(@itemSelector).each ->
    #  g = _get @
    #  #@dataset.year = g.dateObject.getFullYear()
    #  #@dataset.month  = g.dateObject.getMonth() + 1
    #  @classList.add 'local' if g.local
    #  @classList.add 'otome' if g.otome
    #  @classList.add 'okazu' if g.okazu

    #$('.label').tooltip title: -> @innerHTML

    self = @

    #$('.game img').tooltip()
    $("#{@itemSelector}.new").each ->
      $this = $ @
        .removeClass 'new'
      $this.find('img').click ->
        bean.showItem @parentNode.dataset.id
        false
      $this.find('.label').click ->
        #cls = 'label-inverse'
        #if @classList.contains cls
        #  text = ''
        #else
        text = @dataset.text or @innerHTML
        self.search text
        #@classList.addClass 'label-inverse'
        false

    dprint 'rebind: leave'

  ## Actions ##

  #show: =>
  #  @$container.show()
  #  $('#init-sort').click()

  #isotope: (v) => @$container.isotope v

  search: (text) =>
    @$search.val(text).trigger 'keyup' # invoke quicksearch

  triggerSearch: =>
    value = $.trim @$search.val()
    if value isnt @searchText
      @searchText = value
      group = 'search'
      if value is ''
        delete @filters[group]
      else
        @filters[group] = value
      #@resetPage()
      @refresh()

  #getFilter: => _.values(@filters).join ','
    #sel = if @filters then _.values(@filters).join '' else '.game'
    #"#{sel}:gt(-#{@limit})" # count backward

  #refreshFilter: =>
  #  @isotope
  #    filter: @getFilter()

  render: (l) => l.map(@_renderGame).join ''

  _renderGame: (g) =>
    tip = g.title #} ##{g.brand or ''} #{date}"
    tip += " (#{g.romajiTitle})" if g.romajiTitle
    tip = tip.replace(/"/g, "'") # escape quotes

    #tip += " #{g.scapeMedian}%" if g.scapeMedian

    if g.date > CURRENT_TIME
      tip += ' 未発売'
    else if g.date > RECENT_TIME
      tip += ' 新作'
    tip += ' 所持ち' if g.local
    tip += ' 女性向け' if g.otome
    tip += if g.okazu then ' 抜きゲー' else ' 純愛系'
    #tip += ' ' + g.tags.replace /,/g, ' ' if g.tags
    #tip += " (#{tags.join ", "})" #if tags.length

    scoreColor = (
      unless g.scapeMedian then '' # gray
      else if g.scapeCount < 5 then 'b' # black
      else if g.scapeMedian >= 90 or g.scapeCount > 500 then 'o' # orange
      else if g.scapeMedian >= 80 or g.scapeCount > 300 then 'r' # red
      else if g.scapeMedian >= 70 or g.scapeCount > 100 then 'g' # green
      else 'b' # black
    )

    visitColor = (
      if g.subtitleCount > 5000 then 'o' # orange

      else if g.visitCount < 6000 and g.commentCount > 5000 then 'o' # orange
      else if g.visitCount < 3000 and g.commentCount > 500 then 'r' # red

      else if g.visitCount < 300 then '' # gray
      else if g.visitCount < 1000 then 'b' # black
      else if g.visitCount < 3000 then 'g' # green
      else if g.visitCount < 6000 then 'r' # red
      else 'o' # orange
    )

    sizeColor = (
      unless g.fileSize then '' # gray
      else if g.fileSize < 1024 then 'b' # black
      else if g.fileSize < 2048 then 'g' # green
      else if g.fileSize < 4048 then 'r' # red
      else 'o' # orange
    )

    sizeTag = (
      unless g.fileSize then ''
      else if g.fileSize < 1024 then g.fileSize + 'M'
      else Math.round(g.fileSize / 1024 * 100)/100 + 'G'
    )

    #labels = if g.brand then g.brand.split ',' else []
    # I don't know why, but zh font looked better than ja
    #date = if g.date then g.moment 'M/D/YYYY' else ''
    h = GAME_HAML
      g: g
      #date: date
      tip: tip
      width: @itemWidth
      scoreColor: scoreColor
      visitColor: visitColor
      sizeColor: sizeColor
      sizeTag: sizeTag

    c = ['game', 'new']
    #c.push 'local' if g.local
    c.push if g.otome then 'otome' else if g.okazu then 'okazu' else 'junai'
    h.replace 'game', c.join ' '    # only replace the first class="game"

## Main ##

init = ->
  unless @bean?
    dprint 'init: wait'
    setTimeout init, 100 # Wait until bean is ready
  else
    dprint 'init: enter'

    moment.locale 'ja'

    #gm = new GameManager @bean
    gm = new GameManager @bean

    slider = new ZoomSlider (y) -> gm.zoom 1 + y * 1.1

    toolbar = new Toolbar @bean,
      width: 60     # height of slider + margin-right
      height: 229   # height of slider + 3 * button + margin-bottom
      move: slider.reloadOffset

    # Export window mamager so that external APIs such as window.search can access it
    # Delay assigning to gameManager until everything else is ready
    @gameManager = gm

    #setTimeout gm.show, 200
    #setTimeout _.partial(quicksearch, styleClass, gf.refreshFilter),  2000
    dprint 'init: leave'

$ -> init()

# External APIs

@search = (text) -> # str ->  set search text
  gameManager.search text if window.gameManager

# EOF
#
#    @isotope
#      itemSelector: '.game'
#      sortBy: 'timestamp'
#      sortAscending: false # this might cause slow startup
#      #filter: @getFilter()
#      getSortData:
#        title: ($el) -> _get$($el).title
#        #brand: ($el) -> _get$($el).brand   # not used
#        timestamp: ($el) -> _get$($el).timestamp
#        date: ($el) ->  _get$($el).date
#        visits: ($el) ->  _get$($el).visitCount
#        comments: ($el) -> _get$($el).commentCount
#        scapeMedian: ($el) -> _get$($el).scapeMedian
#        scapeCount: ($el) -> _get$($el).scapeCount
#
#    $optionSets = $ '.options .option-set'
#    $optionLinks = $optionSets.find 'a'
#    $optionLinks.click ->
#      $this = $ @
#      # don't proceed if already selected
#      return false if $this.hasClass 'selected'
#
#      $optionSet = $this.parents '.option-set'
#      $optionSet.find('.selected').removeClass 'selected'
#      $this.addClass 'selected'
#
#      # make option object dynamically, i.e. { filter: '.my-filter-class' }
#      options = {}
#      group = $optionSet.data 'option-group'
#      key = $optionSet.data 'option-key'
#      value = $this.data 'option-value'
#
#      # parse 'false' as false boolean
#      value = if value is 'false' then false else value
#      if key is 'filter'
#        self.filters[group] = value
#        #options.filter = _.values(self.filters).join ''
#        options.filter = self.getFilter()
#      else
#        options[key] = value
#      if key is 'layoutMode' and typeof changeLayoutMode is 'function'
#        changeLayoutMode $this, options # changes in layout modes need extra logic
#      else # otherwise, apply new options
#        self.isotope options
#      false
#
#    # https://github.com/desandro/isotope/issues/107
#    # https://github.com/riklomas/quicksearch
#    styleClass = 'quicksearch-match'
#    @filters.quicksearch = '.' + styleClass
#    setTimeout (->
#      $('#search').quicksearch '#games .game',
#        delay: 100
#        onAfter: -> setTimeout self.refreshFilter, 100
#
#        show: -> $(@).addClass styleClass
#        hide: -> $(@).removeClass styleClass
#
#        prepareQuery: (val) ->
#          val = _.str.trim val
#          unless val then null
#          else if val[0] is '#' then val
#          else if val.length >= 4 and /^20\d+$/.test val then val
#          else new RegExp val, 'i'
#
#        testQuery: (query, text, el) ->
#          unless query
#            true
#          else
#            g = _get el
#            if typeof query is 'string'
#              if query[0] is '#'
#                query is '#' + g.itemId
#              else
#                _.str.startsWith g.dateString, query
#            else # type of query is RegExp object
#              query.test(g.title) or g.brand and query.test(g.brand) or g.series and query.test(g.series)
#    ), 2000

#fixIsotope = ->
#  # See: https://github.com/desandro/isotope/blob/master/jquery.isotope.js
#  # Version: 1.5.25
#  #
#  #   _init : function( callback ) {
#  #     this.$filteredAtoms = this._filter( this.$allAtoms );
#  #     this._sort();
#  #     this.reLayout( callback );
#  #   },
#  #
#  #isotope_init = $.Isotope::_init
#  $.Isotope::_init = (callback) ->
#    # Original logic in 1.5.25:
#    #@$filteredAtoms = @_filter @$allAtoms
#    #@_sort()
#    #@reLayout callback
#
#    @$filteredAtoms = @_filter @$allAtoms
#    @_sort()
#
#    # See: Isotope::_filter
#    max = 20 - 1
#    $atomsToHide = @$filteredAtoms.filter ":gt(#{max})" # hide > max
#    $atomsToHide.addClass @options.hiddenClass
#    @$filteredAtoms = @$filteredAtoms.not @options.hiddenClass
#
#    @styleQueue.push
#      $el: $atomsToHide
#      style: @options.hiddenStyle
#
#    @reLayout callback
