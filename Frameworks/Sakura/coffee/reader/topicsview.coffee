# topicsview.coffee
# 8/29/2014 jichi
# Required by chat.haml
#
# Beans:
# - cacheBean: cacheman.CacheCoffeeBean
# - i18nBean: coffeebean.I18nBean
# - mainBean: coffeebean.MainBean
# - postInputBean: postinput.PostInputManagerBean
# - postEditBean: postedit.PostEditorManagerBean
# - topicInputBean: topicinput.TopicInputManagerBean
# - topicEditBean: topicedit.TopicEditorManagerBean

dprint = ->
  Array::unshift.call arguments, 'topicsview:'
  console.log.apply console, arguments

# Global variables
@READY = false # needed by postView.py

newPost = (topicId) -> postInputBean.newPost topicId, 'post' # long ->
newTopic = (topicType, subjectId, subjectType) -> topicInputBean.newTopic topicType, subjectId, subjectType # long, string ->
editTopic = (topic) -> topicEditBean.editTopic JSON.stringify topic # long ->

# Export functions

@spin = (t) -> # bool ->
  if t
    @spin.count += 1
  else
    @spin.count -= 1
  $('#spin').spin if @spin.count > 0 then 'large' else false
@spin.count = 0

@addTopic = (topic) ->
  if READY
    if topic.type is 'review'
      @reviewView?.addTopic topic
    else
      @topicView?.addTopic topic
@updateTopic = (topic) ->
  if READY
    if topic.type is 'review'
      @reviewView?.updateTopic topic
    else
      @topicView?.updateTopic topic

@addPost = (post) -> @postView?.addPost post if READY
@updatePost = (post) -> @postView?.updatePost post if READY

# Init

createObjects = ->
  $userReview = $ '.sec.sec-review .forum-topics'
  $userReview = undefined unless $userReview.length

  # Reviews
  $sec = $ '.sec-reviews'
  search =
    type: 'review'
  if SUBJECT_ID
    search.subjectId = SUBJECT_ID
    search.subjectType = 'game'
  @reviewView = new topicsjs.TopicList
    $container: $sec.find '> .sec-content > .forum-topics'
    $more: $sec.find '> .sec-content > .footer > .btn-more'
    $newReview: $sec.find '.new-topic'
    $userReview: $userReview
    search: search
    complete: not TOPIC_ID

  # Topics
  $sec = $ '.sec-topics'
  search =
    notype: 'review'
  if SUBJECT_ID
    search.subjectId = SUBJECT_ID
  @topicView = new topicsjs.TopicList
    $container: $sec.find '> .sec-content > .forum-topics'
    $more: $sec.find '> .sec-content > .footer > .btn-more'
    search: search
    complete: not TOPIC_ID


  reviewView.show()
  topicView.show()

  # Posts
  $sec = $ '.sec-posts'
  if TOPIC_ID
    @postView = new postsjs.PostList
      $container: $sec.find '> .sec-content > .forum-posts'
      $more: $sec.find '> .sec-content > .footer > .btn-more'
      topicId: TOPIC_ID
      search:
        sort: 'updateTime'
        asc: false
    postView.show()

bind = ->
  $('.sec-btn').click ->
    $this = $ @
    $sec = $this.parent '.sec'
    if $sec.length
      $target = $sec.find '.sec-content'
      unless $target.is(':empty') and $this.hasClass('checked')
        $this.toggleClass 'checked'
        #effect = $this.data('effect') or 'blind'
        #effect = $this.data('effect') or 'fade'
        #$target.toggle effect unless $target.is ':empty'
        $target.toggle 'fade' unless $target.is ':empty'
    false

  # Chat
  $sec = $ '.sec.sec-topics'
  $sec.find('.new-topic').click ->
    if SUBJECT_ID
      id = SUBJECT_ID
      type = 'game'
    else
      id = 101 # VNR subject
      type = 'subject'
    newTopic 'chat', id, type
    false

  $sec = $ '.sec.sec-reviews'
  $sec.find('.new-topic').hide().click -> # hide on startup
    if SUBJECT_ID
      topic = reviewView.findUserReview()
      if topic
        editTopic topic
      else
        newTopic 'review', SUBJECT_ID, 'game'
    false

  $sec = $ '.sec.sec-posts'
  $sec.find('.new-post').click ->
    newPost TOPIC_ID
    false

init = ->
  unless @i18nBean? # the last injected bean
    dprint 'init: wait'
    setTimeout init, 100 # Wait until bean is ready
  else
    dprint 'init: enter'

    moment.locale LOCALE

    topicsjs.init()
    postsjs.init()

    createObjects()

    bind()

    @READY = true

    #setTimeout gm.show, 200
    #setTimeout _.partial(quicksearch, styleClass, gf.refreshFilter),  2000
    dprint 'init: leave'

$ -> init()

# EOF
