# coding: utf8
# forumapi.py
# 1/1/2015 jichi

import json
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint, dwarn
from mytr import my
import dataman, netman, growl

@memoized
def manager(): return ForumApi()

class ForumApi:
  def __init__(self):
    self.__d = _ForumApi()

  def submitPost(self, *args, **kwargs): self.__d.submitPost(*args, **kwargs)
  def updatePost(self, *args, **kwargs): self.__d.updatePost(*args, **kwargs)
  def submitTopic(self, *args, **kwargs): self.__d.submitTopic(*args, **kwargs)
  def updateTopic(self, *args, **kwargs): self.__d.updateTopic(*args, **kwargs)

class _ForumApi:

  def submitPost(self, postData, imageData, topicId):
    """
    @param  postData  unicode json
    @param  imageData  unicode
    @param  topicId  long
    """
    if topicId:
      user = dataman.manager().user()
      if user.name and user.password:
        post = json.loads(postData)
        if not post.get('topic'):
          post['topic'] = topicId
        post['login'] = user.name
        post['password'] = user.password
        if imageData:
          image = json.loads(imageData)
          image['login'] = user.name
          image['password'] = user.password
        else:
          image = None
        self._submitPost(post, image)

  @staticmethod
  def _submitPost(post, image):
    """
    @param  post  kw
    @param  image  kw or None
    """
    dprint("enter")
    if image:
      data = skfileio.readdata(image['filename'])
      if data:
        post['image'] = netman.manager().submitImage(data, image)

    if image and not post.get('image') or not netman.manager().submitPost(post):
      growl.warn("<br/>".join((
        my.tr("Failed to submit post"),
        my.tr("Please try again"),
      )))
    dprint("leave")

  def updatePost(self, postData, imageData):
    """
    @param  postData  unicode json
    @param  imageData  unicode json
    """
    user = dataman.manager().user()
    if user.name and user.password:
      post = json.loads(postData)
      #post['topic'] = self.topicId
      post['login'] = user.name
      post['password'] = user.password

      if imageData:
        image = json.loads(imageData)
        image['login'] = user.name
        image['password'] = user.password
      else:
        image = None
      self._updatePost(post, image)

  def _updatePost(self, post, image):
    """
    @param  post  kw
    @param  image  kw or None
    """
    dprint("enter")
    nm = netman.manager()
    if image:
      data = skfileio.readdata(image['filename'])
      if data:
        post['image'] = nm.submitImage(data, image)

    if image and not post.get('image') or not nm.updatePost(post):
      growl.warn("<br/>".join((
        my.tr("Failed to update post"),
        my.tr("Please try again"),
      )))
    dprint("leave")

  def submitTopic(self, topicData, imageData, ticketData):
    """
    @param  topicData  unicode json
    @param  imageData  unicode json
    @param  ticketData  unicode json
    """
    user = dataman.manager().user()
    if user.name and user.password:
      topic = json.loads(topicData)
      subjectId = topic.get('subjectId')
      subjectType = topic.get('subjectType')
      if not subjectId or not subjectType:
        return
      topic['login'] = user.name
      topic['password'] = user.password
      if imageData:
        image = json.loads(imageData)
        image['login'] = user.name
        image['password'] = user.password
      else:
        image = None
      tickets = None
      if ticketData and subjectType == 'game':
        tickets = self._parseGameTicketData(ticketData, subjectId)
      self._submitTopic(topic, image, tickets)

  def _parseGameTicketData(self, data, gameId): # string -> [{kw}]
    ret = []
    user = dataman.manager().user()
    a = json.loads(data)
    for k,v in a.iteritems():
      ret.append({
        'type': k,
        'value': v,
        'targetId': gameId,
        'targetType': 'game',
        'login': user.name,
        'password': user.password,
      })
    return ret

  def _submitTickets(self, tickets): # [{kw}] ->
    nm = netman.manager()
    for data in tickets:
      nm.updateTicket(data) # error not checked

  def _submitTopic(self, topic, image, tickets):
    """
    @param  topic  kw
    @param  image  kw or None
    @param  tickets [kw]
    """
    dprint("enter")
    nm = netman.manager()
    if tickets:
      self._submitTickets(tickets)
    if image:
      data = skfileio.readdata(image['filename'])
      if data:
        topic['image'] = nm.submitImage(data, image)

    if image and not topic.get('image'):
      growl.warn("<br/>".join((
        my.tr("Failed to submit topic"),
        my.tr("Please try again"),
      )))
      return
    if nm.submitTopic(topic):
      self._onTopicSubmitted(topic, tickets)
    else:
      growl.warn("<br/>".join((
        my.tr("Failed to submit topic"),
        my.tr("Please try again"),
      )))
    dprint("leave")

  def _onTopicSubmitted(self, topic, tickets):
    """
    @param  topic  kw
    @param  tickets  [kw]
    """
    if topic.get('subjectType') == 'game':
      itemId = topic.get('subjectId')
      dm = dataman.manager()
      dm.increaseGameTopicCount(itemId)
      if topic.get('type') == 'review' and tickets:
        scores = {}
        for ticket in tickets:
          if ticket.get('type') == 'ecchi':
            scores['ecchiScore'] = ticket.get('value')
          elif ticket.get('type') == 'overall':
            scores['overallScore'] = ticket.get('value')
        if scores:
          dm.addGameScore(itemId, **scores)

  def updateTopic(self, topicData, imageData, ticketData):
    """
    @param  topicData  unicode  json
    @param  imageData  unicode  json
    @param  ticketData  unicode  json
    """
    user = dataman.manager().user()
    if user.name and user.password:
      topic = json.loads(topicData)
      #topic['subjectId'] = self.gameId
      topic['login'] = user.name
      topic['password'] = user.password

      if imageData:
        image = json.loads(imageData)
        image['login'] = user.name
        image['password'] = user.password
      else:
        image = None

      subjectId = topic.get('subjectId')
      subjectType = topic.get('subjectType')
      tickets = None
      if ticketData and subjectId and subjectType == 'game':
        tickets = self._parseGameTicketData(ticketData, subjectId)
      if subjectId:
        del topic['subjectId']
      if subjectType:
        del topic['subjectType']
      self._updateTopic(topic, image, tickets)

  def _updateTopic(self, topic, image, tickets):
    """
    @param  topic  kw
    @param  image  kw or None
    @param  tickets  [kw] or None
    """
    dprint("enter")
    if tickets:
      self._submitTickets(tickets)
    if image:
      data = skfileio.readdata(image['filename'])
      if data:
        topic['image'] = netman.manager().submitImage(data, image)

    if image and not topic.get('image') or not netman.manager().updateTopic(topic):
      growl.warn("<br/>".join((
        my.tr("Failed to update topic"),
        my.tr("Please try again"),
      )))
    dprint("leave")

# EOF
