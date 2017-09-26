# coding: utf8
# rest.py
# 7/25/2013 jichi
# See also: amazonproduct
#
# Apply: https://affiliate.dmm.com/api/guide/
# Source: http://qiita.com/fumix/items/2edf404397543322aaa1
#
# Be careful about the differences between dmm, dmm.R18, version1.0 and version2.0
#
# Example
# http://affiliate-api.dmm.com/?affiliate_id=sakuradite-999&account_id=ezuc1BvgM0f74KV4ZMmS&operation=ItemList&version=1.00&timestamp=2012-01-13%2014%3A08%3A16&site=DMM.com&service=lod&floor=akb48

__all__ = 'RestApi',

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import time, urllib2
from functools import partial
from cStringIO import StringIO
from sakurakit.skdebug import dprint, dwarn

# https://affiliate.dmm.com/api/guide/

class RestApi(object):

  URL = "http://affiliate-api.dmm.com/"

  def __init__(self, api_id, affiliate_id):
    """
    @param api_id  str
    @param  affiliate_id  str
    """
    self.api_id = api_id
    self.affiliate_id = affiliate_id

    self.version = '2.00' #: supported Amazon API version
    self.site = 'DMM.co.jp' # or 'DMM.com' for non-R18
    self.operation = 'ItemList'
    self.encoding = 'euc-jp'
    #self.reader = codecs.getreader(self.encoding)

    # 通販：'mono'
    # 美少女：'pcgame'
    # 同人：'doujin'
    self.service = None
    self.floor = None

    self.debug = 0 # set to 1 to see HTTP headers

    #self.response_processor = processor or LxmlObjectifyProcessor()
    self.parse = self._makeparser()

  def query(self, text, **kwargs):
    """
    @param  text  str
    @param  hits  int
    @return  lxml or None
    """
    try: return self._apply(keyword=text, **kwargs)
    except Exception, e: dwarn(e)

  ## Implementations ##

  @staticmethod
  def _makeparser():
    from lxml import etree, objectify
    #class SelectiveClassLookup(etree.CustomElementClassLookup):
    #  def lookup(self, node_type, document, namespace, name):
    #    if name == 'price':
    #      return objectify.IntElement

    parser = etree.XMLParser()
    #lookup = SelectiveClassLookup()
    #lookup.set_fallback(objectify.ObjectifyElementClassLookup())
    #parser.set_element_class_lookup(lookup)

    # provide a parse method to avoid importing lxml.objectify
    # every time this processor is called
    return partial(
        #lambda p, s: objectify.fromstring(s, p), # parse string
        lambda p, fp: objectify.parse(fp, p), # parse file
        parser)

  def _encodeparam(self, v):
    """
    @param  v  any
    @return  str
    """
    if isinstance(v, str):
      return v
    elif isinstance(v, unicode):
      return v.encode(self.encoding, errors='ignore')
    else:
      return str(v) # May throw

  def _makeurl(self, **params):
    """
    @param  params  request params
    @return  str

    See: https://affiliate.dmm.com/api/reference/com/iroiro/
    """
    if self.service:
      params['service'] = self.service
    if self.floor:
      params['floor'] = self.floor
    params['api_id'] = self.api_id
    params['affiliate_id'] = self.affiliate_id
    params['version'] = self.version
    params['site'] = self.site
    params['operation'] = self.operation
    params['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

    # paramsのハッシュを展開
    request = ["%s=%s" % (k, urllib2.quote(self._encodeparam(v)))
        for k,v in sorted(params.iteritems())] # sorted is needed to make the URL unique for caching

    ret = self.URL + "?" + "&".join(request)
    if self.debug:
      dprint(ret)
    return ret

  def _fetch(self, url):
    """
    @param  url  str
    @return  file object
    @raise
    """
    req = urllib2.Request(url)
    handler = urllib2.HTTPHandler(debuglevel=self.debug)
    opener = urllib2.build_opener(handler)
    return opener.open(req)

  def _recode(self, fp):
    """
    @param  fp  file pointer
    @return  fp
    @raise
    """
    # Have to manually replace encoding in XML
    #return self.reader(fp, errors='ignore')
    t = fp.read()
    t = t.decode(self.encoding, errors='ignore')
    t = t.replace(' encoding="euc-jp"', ' encoding="utf-8"')
    if self.debug:
      dprint(t)
    return StringIO(t)

  def _parse(self, fp):
    """
    @param  fp  file pointer
    @return  unicode
    @raise
    """
    fp = self._recode(fp)
    tree = self.parse(fp)
    root = tree.getroot()

    #~ from lxml import etree
    #~ print etree.tostring(tree, pretty_print=True)

    #try:
    #  nspace = root.nsmap[None]
    #  errors = root.xpath('//aws:Error', namespaces={'aws' : nspace})
    #except KeyError:
    #  errors = root.xpath('//Error')
    return root.xpath('//item')

  def _apply(self, **params):
    """
    @return  iter(etree.lElement)
    @raise
    """
    url = self._makeurl(**params)
    r = self._fetch(url)
    #t = r.read().decode(self.encoding)
    return self._parse(r)

if __name__ == '__main__':
  dmm = RestApi('ezuc1BvgM0f74KV4ZMmS', 'sakuradite-999')
  #dmm.service = 'pcgame'
  #dmm.floor = 'pcgame'
  t = '1653apc10393'
  t = u"幻創のイデア "
  t = u"神咒神威神楽"
  t = u"528lih5035" # product_id
  t = u"000_029pcg" # content_id
  t = '1196wp111' # cid
  t = u'魔王はじめました'
  t = 'hawkeye_0005'
  dmm.debug = 1
  # https://affiliate.dmm.com/api/reference/com/iroiro/
  for item in dmm.query(t, hits=20):
    for it in item:
      print it.tag, it.text

# EOF
