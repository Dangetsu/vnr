# forum/topic.coffee
# 1/2/2015 jichi
# Required by chat.haml
#
# Require
# - jquery
# - haml
# - underscore
#
# Beans:
# - mainBean: coffeebean.MainBean
# - topicEditBean: topicedit.TopicEditorManagerBean

dprint = ->
  Array::unshift.call arguments, 'topic:'
  console.log.apply console, arguments

# Global variables

HIGHLIGHT_INTERVAL = 1500

HAML_TOPIC = null
createTemplates = ->

  # HAML for topic
  # - id
  # - type
  # - userName
  # - userStyle
  # - lang
  # - userAvatarUrl  url or null
  # - content: string  html
  # - createTime
  # - updateTime
  # - image  url or null
  # - likeCount  int
  # - dislikeCount  int

  HAML_TOPIC = Haml """\
.topic(data-id="${id}" data-type="${type}" data-subject-id="${subjectId}")
  :if userAvatarUrl
    %a(href="${userAvatarUrl}" title="#{tr 'Avatar'}")
      %img.img-circle.avatar(src="${userAvatarUrl}" alt="#{tr 'Avatar'}")
  .right
    .title.text-info(title="#{tr 'Title'}") ${title}
    .header.line
      .type.text-warning = typeName
      %a.user(href="javascript:" style="${userStyle}") @${userName}
      :if createTime
        .time.text-minor(title="${createTimeString}") = createTime.fromNow()
      .lang = lang
      :if updateTime
        .time.text-success(title="${updateTimeString}") = updateTime.fromNow()
      :if scores
        .score
          .item.text-danger
            #{tr 'Score'}: ${'overall' in scores ? scores.overall : '-'}/10
          .item.text-warning
            H: ${'ecchi' in scores ? scores.ecchi : '-'}/10
    :if gameTitle
      .game-title
        %a.pull-right.link-game.btn.btn-link(title="#{tr 'Show'}")
          –– ${gameTitle}
    :if content
      .content.bbcode = content
    .footer
      .btn-group.like-group.fade-in
        %a.like.btn.btn-link.btn-sm(role="button" title="#{tr 'Like'}" data-value="${likeCount}")
          %span.fa.fa-thumbs-up
          %span.value = likeCount
        %a.dislike.btn.btn-link.btn-sm(role="button" title="#{tr 'Dislike'}" data-value="${dislikeCount}")
          %span.fa.fa-thumbs-down
          %span.value = dislikeCount
      .btn-group.fade-in.pull-right
        :if
          %a.btn-reply.btn.btn-link.btn-sm(role="button" title="#{tr 'Reply'}")
            #{tr 'Reply'}
            :if postCount
              = ' (' + postCount + ')'
        :if editable
          %a.btn-edit.btn.btn-link.btn-sm(role="button" title="#{tr 'Edit'}") #{tr 'Edit'}
          %a.btn-add.btn.btn-link.btn-sm(role="button" title="#{tr 'Add'}") #{tr 'Add'}
    :if image
      .image
        %a(href="${image.url}" title="${image.title}")
          %img(src="${image.url}" alt="${image.title}")
""".replace /\$/g, '#'

# Functions and classes

renderTopic = (data) -> # object topic, bool -> string
  createTime = updateTime = null
  if data.createTime
    createTime = moment data.createTime * 1000
  if data.updateTime > data.createTime
    updateTime = moment data.updateTime * 1000
  #su = data.subupload
  #if su
  #  su.ignoreCount = (su.totalCount or 0) - (su.createCount or 0) - (su.updateCount or 0) - (su.errorCount or 0)
  #  su.createTimeString = util.formatDate su.createTime
  #  su.updateTimeString = util.formatDate su.updateTime
  HAML_TOPIC
    id: data.id
    type: data.type
    typeName: util.getTopicTypeName data.type
    editable: data.userName is USER_NAME and data.type in util.TOPIC_TYPES
    lang: util.getLangName data.lang
    subjectId: data.subjectId
    gameTitle: if data.subjectType is 'game' then data.subjectTitle else ''
    #userStyle: if data.userColor then "color:#{data.userColor}" else ''
    #userStyle: ''
    userAvatarUrl: util.getAvatarUrl data.userAvatar
    userStyle: if data.userColor then "color:#{data.userColor}" else ''
    title: data.title
    content: util.renderContent data.content
    createTime: createTime
    updateTime: updateTime
    createTimeString: util.formatDate createTime
    updateTimeString: util.formatDate updateTime
    userName: data.userName
    image: if data.image then {title:data.image.title, url:util.getImageUrl data.image} else null
    postCount: data.postCount
    likeCount: data.likeCount or 0
    dislikeCount: data.dislikeCount or 0
    scores: data.scores # {overall:int score, ecchi:int score}
    #su: su

newPost = (topicId, postType) -> postInputBean.newPost topicId, postType # long, string ->
editTopic = (topic) -> topicEditBean.editTopic JSON.stringify topic # long ->

# Classes
class Topic

  constructor: (@id, {$container:@$sel}) ->
    @topic = {}

  # Helper functions

  _bindTopic: =>
    $topic = @$sel.children '.topic'
    topic = @topic

    topicId = $topic.data 'id'
    subjectId = $topic.data 'subject-id'

    $header = $topic.find '> .right > .header'
    $footer = $topic.find '> .right > .footer'

    $topic.addClass 'finished' if topic.finished

    $topic.find('a.link-game').click ->
      mainBean.showGame subjectId if subjectId
      false

    $header.find('a.user').click ->
      mainBean.showUser topic.userName if topic?.userName
      false

    $footer.find('.btn-edit').click ->
      editTopic topic
      false

    $footer.find('.btn-add').click ->
      newPost topicId, 'topic'
      false

    $footer.find('.btn-reply').click ->
      newPost topicId, 'post'
      false

    $footer.find('.like-group').removeClass 'fade-in' if topic?.likeCount or topic?.dislikeCount

    $footer.find('.btn.like').click ->
      if topic and USER_NAME and USER_NAME isnt topic.userName
        $that = $footer.find '.btn.dislike.selected'
        if $that.length
          $that.removeClass 'selected'
          $value = $that.find '.value'
          $value.text -1 + Number $value.text()
        $this = $ @
        $this.parent('.like-group').removeClass 'fade-in'
        selected = $this.hasClass 'selected'
        value = if selected then 0 else 1
        ticket.update
          data:
            login: USER_NAME
            password: USER_PASSWORD
            targetType: 'topic'
            targetId: topicId
            type: 'like'
            value: value
          success: =>
            $this.toggleClass 'selected'
            $value = $this.find '.value'
            $value.text (if selected then -1 else 1) + Number $value.text()
      false

    $footer.find('.btn.dislike').click ->
      if topic and USER_NAME and USER_NAME isnt topic.userName
        $that = $footer.find '.btn.like.selected'
        if $that.length
          $that.removeClass 'selected'
          $value = $that.find '.value'
          $value.text -1 + Number $value.text()
        $this = $ @
        $this.parent('.like-group').removeClass 'fade-in'
        selected = $this.hasClass 'selected'
        value = if selected then 0 else -1
        ticket.update
          data:
            login: USER_NAME
            password: USER_PASSWORD
            targetType: 'topic'
            targetId: topicId
            type: 'like'
            value: value
          success: =>
            $this.toggleClass 'selected'
            $value = $this.find '.value'
            $value.text (if selected then -1 else 1) + Number $value.text()
      false

  _highlightTopic: => @$sel.effect 'highlight', HIGHLIGHT_INTERVAL

  showTopic: (@topic) =>
    @updateTopic @topic, false

  updateTopic: (topic, highlight=true) => # object topic ->
    if topic.id isnt @topic.id
      dprint 'different topic id'
      return
    @topic = topic
    h = renderTopic @topic
    @$sel.html h

    @_highlightTopic() if highlight
    @_bindTopic()

  show: ({success:success}) =>
    self = @
    spin true
    rest.forum.query 'topic',
      data:
        id: @id
      error: ->
        spin false
        growl.warn tr 'Internet error'
      success: (data) ->
        spin false
        if data.id
          self.showTopic data
          success?()

## Export ##

init = ->
  createTemplates()

@topicjs =
  init: init
  Topic: Topic

# EOF
