# forum/posts.coffee
# 12/30/2014 jichi
# Required by chat.haml
#
# Require
# - jquery
# - haml
# - underscore
#
# Beans:
# - mainBean: coffeebean.MainBean
# - postInputBean: postinput.PostInputManagerBean
# - postEditBean: postedit.PostEditorManagerBean

dprint = ->
  Array::unshift.call arguments, 'posts:'
  console.log.apply console, arguments

# Global variables

INIT_POST_COUNT = 10
MORE_POST_COUNT = 20

HIGHLIGHT_INTERVAL = 1500

HAML_POST = null
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
  HAML_POST = Haml """\
.post.post-new(data-id="${id}" data-type="${type}")
  :if userAvatarUrl
    %a(href="${userAvatarUrl}" title="#{tr 'Avatar'}")
      %img.img-circle.avatar(src="${userAvatarUrl}" alt="#{tr 'Avatar'}")
  .right
    .header
      %a.user(href="javascript:" style="${userStyle}") @${userName}
      :if createTime
        .time.text-minor(title="${createTimeString}") = createTime.fromNow()
      .lang = lang
      :if updateTime
        .time.text-success(title="${updateTimeString}") = updateTime.fromNow()
    .content.bbcode = content
    :if USER_NAME
      .footer
        .btn-group.like-group.fade-in
          %a.like.btn.btn-link.btn-sm(role="button" title="#{tr 'Like'}")
            %span.fa.fa-thumbs-up
            %span.value = likeCount
          %a.dislike.btn.btn-link.btn-sm(role="button" title="#{tr 'Dislike'}")
            %span.fa.fa-thumbs-down
            %span.value = dislikeCount
        .btn-group.pull-right.fade-in
          :if userName == USER_NAME
            %a.btn.btn-link.btn-sm.btn-edit(role="button" title="#{tr 'Edit'}") #{tr 'Edit'}
          %a.btn.btn-link.btn-sm.btn-reply(role="button" title="#{tr 'Reply'}") #{tr 'Reply'}
    :if image
      .image
        %a(href="${image.url}" title="${image.title}")
          %img(src="${image.url}" alt="${image.title}")
  .reply
""".replace /\$/g, '#'

# Functions and classes

renderPost = (data) -> # object post -> string
  createTime = updateTime = null
  if data.createTime
    createTime = moment data.createTime * 1000
  if data.updateTime > data.createTime
    updateTime = moment data.updateTime * 1000
  HAML_POST
    id: data.id
    type: data.type
    userName: data.userName
    userStyle: if data.userColor then "color:#{data.userColor}" else ''
    lang: util.getLangName data.lang
    userAvatarUrl: util.getAvatarUrl data.userAvatar
    content: util.renderContent data.content
    createTime: createTime
    updateTime: updateTime
    createTimeString: util.formatDate createTime
    updateTimeString: util.formatDate updateTime
    image: if data.image then {title:data.image.title, url:util.getImageUrl data.image} else null
    likeCount: data.likeCount or 0
    dislikeCount: data.dislikeCount or 0

editPost = (post) -> postEditBean.editPost JSON.stringify post # long ->
replyPost = (topicId, postId) -> postInputBean.replyPost topicId, postId # long, long ->

# Classes
class PostList

  constructor: ({
      $container: @$postContainer       # $  container of posts
      $topicContainer: @$topicContainer # $  container of topics
      $more: @$more         # $ more button
      topicId: @topicId     # long  topicId
      search: @search       # dict
    }) ->
    @$sel = @$postContainer
    @$sel = @$sel.add @$topicContainer if @$topicContainer?

    @posts = [] # [object post]

    @bind()

  # Helper functions

  $getPost: (postId) =>  @$sel.find ".post[data-id=#{postId}]" # long -> $el
  getPost: (postId) => _.findWhere @posts, id:postId # long -> object

  _bindNewPosts: =>
    self = @
    @$sel.find('.post.post-new').each ->
      $post = $ @
        .removeClass 'post-new'

      postId = $post.data 'id'
      post = self.getPost postId

      $post.addClass 'highlight' if post.highlight

      $header = $post.find '> .right > .header'
      $footer = $post.find '> .right > .footer'

      $header.find('a.user').click ->
        mainBean.showUser post.userName if post?.userName
        false

      $footer.find('.btn-edit').click ->
        editPost post if post
        false

      $footer.find('.btn-reply').click ->
        replyPost self.topicId, postId if self.topicId and postId
        false

      $footer.find('.like-group').removeClass 'fade-in' if post?.likeCount or post?.dislikeCount

      $footer.find('.btn.like').click ->
        if post and USER_NAME and USER_NAME isnt post.userName
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
              targetType: 'post'
              targetId: postId
              type: 'like'
              value: value
            success: =>
              $this.toggleClass 'selected'
              $value = $this.find '.value'
              $value.text (if selected then -1 else 1) + Number $value.text()
        false

      $footer.find('.btn.dislike').click ->
        if post and USER_NAME and USER_NAME isnt post.userName
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
              targetType: 'post'
              targetId: postId
              type: 'like'
              value: value
            success: =>
              $this.toggleClass 'selected'
              $value = $this.find '.value'
              $value.text (if selected then -1 else 1) + Number $value.text()
        false

  addPosts: (posts) => # [object post] ->
    @posts.push.apply @posts, posts

    #document.title = "#{PAGE_TITLE} (#{@posts.length})"
    h = (renderPost it for it in posts when it.type is 'post').join ''
    @$postContainer.append h if h

    if @$topicContainer?
      h = (renderPost it for it in posts when it.type is 'topic').join ''
      @$topicContainer.append h if h

    replies = (it for it in posts when it.type is 'reply')
    if replies.length
      replies = _.sortBy replies, (it) -> it.createTime
      for it in replies
        $ref = @$getPost it.replyId
        if $ref.length
          h = renderPost it
          $ref.children('.reply').append h
        else
          dprint 'addPosts: error: post lost'

    @_bindNewPosts()

  _highlightNewPosts: =>
    @$sel.find '.post.post-new'
      .effect 'highlight', HIGHLIGHT_INTERVAL

  addPost: (post) => # object post ->
    @posts.push post
    #document.title = "#{PAGE_TITLE} (#{@posts.length})"
    if post.type is 'post'
      h = renderPost post
      @$postContainer.prepend h
      @_highlightNewPosts()
      @_bindNewPosts()
    else if post.type is 'topic'
      if @$topicContainer?
        h = renderPost post
        @$topicContainer.append h
        @_highlightNewPosts()
        @_bindNewPosts()
    else if post.type is 'reply'
      $ref = @$getPost post.replyId
      if $ref.length
        h = renderPost post
        $ref.children('.reply').append h
        @_highlightNewPosts()
        @_bindNewPosts()
      else
        dprint 'addPost: error: post lost'
    else
      dprint 'addPost: error: unknown post type'

  updatePost: (post) => # object post ->
    oldpost = @getPost post.id
    if oldpost
      util.fillObject oldpost, post
      $post = @$getPost post.id
      if $post.length
        $h = $ renderPost post
        $h.children('.reply').replaceWith $post.children '.reply'

        $post.replaceWith $h

        #$post = @$getPost post.id
        #$post.children('reply').replaceWith $reply

        #$h.effect 'highlight', HIGHLIGHT_INTERVAL
        @_highlightNewPosts()
        @_bindNewPosts()
        return

    dprint 'updatePost: error: post lost'

  # AJAX actions

  bind: =>
    self = @
    @$more.hide().click ->
      $this = $ @
      unless $this.data 'locked'
        $this.data 'lock', true
        self.more()
        $this.data 'lock', false
      false

  refresh: =>
    @$topicContainer.empty()
    @$postContainer?.empty()
    @show()

  show: =>
    self = @
    spin true
    search =
      topic: @topicId
      limit: INIT_POST_COUNT
    _.extend search, @search
    rest.forum.list 'post',
      data: search
      error: ->
        spin false
        growl.warn tr 'Internet error'
      success: (data) ->
        spin false
        if data.length
          self.addPosts data
          self.$more.show()

  more: =>
    self = @
    spin true
    search =
      topic: @topicId
      first: @posts.length
      limit: MORE_POST_COUNT
    _.extend search, @search
    rest.forum.list 'post',
      data: search
      error: ->
        spin false
        growl.warn tr 'Internet error'
      success: (data) ->
        spin false
        if data.length
          self.addPosts data
        else
          growl tr "No more"

## Export ##

init = ->
  createTemplates()

@postsjs =
  init: init
  PostList: PostList

# EOF
