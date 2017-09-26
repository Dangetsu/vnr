# topicview.coffee
# 1/2/2015 jichi
# Required by chat.haml
#
# Beans:
# - cacheBean: cacheman.CacheCoffeeBean
# - i18nBean: coffeebean.I18nBean
# - mainBean: coffeebean.MainBean
# - postInputBean: postinput.PostInputManagerBean
# - postEditBean: postedit.PostEditorManagerBean
# - topicEditBean: topicedit.TopicEditorManagerBean

dprint = ->
  Array::unshift.call arguments, 'topicsview:'
  console.log.apply console, arguments

# Global variables
@READY = false # needed by postView.py

#newTopic = (topicType, subjectId, subjectType) -> topicInputBean.newTopic topicType, subjectId, subjectType # long, string ->
newPost = (topicId) -> postInputBean.newPost topicId, 'post' # long ->

# Export functions

@spin = (t) -> # bool ->
  if t
    @spin.count += 1
  else
    @spin.count -= 1
  $('#spin').spin if @spin.count > 0 then 'large' else false
@spin.count = 0

@updateTopic = (topic) -> @topicView?.updateTopic topic if READY
@addPost = (post) -> @postView?.addPost post if READY
@updatePost = (post) -> @postView?.updatePost post if READY

# Init

createObjects = ->
  # Topic
  @topicView = new topicjs.Topic TOPIC_ID,
    $container: $ '.forum-topic'

  # Posts
  $topicsec = $ '.sec-topic'
  $postsec = $ '.sec-posts'
  @postView = new postsjs.PostList
    $container: $postsec.children '.forum-posts'
    $topicContainer: $topicsec.children '.forum-posts'
    $more: $postsec.find '> .footer > .btn-more'
    topicId: TOPIC_ID
    search:
      sort: 'createTime'
      asc: true

  topicView.show success: ->
    if topicView.topic.type is 'talk'
      $('ul.filter > li.active').removeClass 'active'
      $('ul.filter > li[data-sort-key="updateTime"]').addClass 'active'
      postView.search.sort = 'updateTime'
      postView.search.asc = false
    postView.show()

refreshPosts = ->
  search = @postView.search

  $li = $ 'ul.filter > li.active'
  search.sort = $li.data 'sort-key'
  search.asc = $li.data 'sort-asc'

  postView.refresh()

bind = ->
  $('.new-post').click ->
    newPost TOPIC_ID
    false

  $('ul.filter > li > a').click ->
    $this = $ @
    $li = $this.parent 'li'
    return false if $li.hasClass 'active'
    $li.parent('ul').children('li.active').removeClass 'active'
    $li.addClass 'active'
    refreshPosts()
    false

init = ->
  unless @i18nBean? # the last injected bean
    dprint 'init: wait'
    setTimeout init, 100 # Wait until bean is ready
  else
    dprint 'init: enter'

    moment.locale LOCALE

    topicjs.init()
    postsjs.init()

    createObjects()

    bind()

    @READY = true

    #setTimeout gm.show, 200
    #setTimeout _.partial(quicksearch, styleClass, gf.refreshFilter),  2000
    dprint 'init: leave'

$ -> init()

# EOF
