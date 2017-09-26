# coding: utf8
# caching.py
# 7/25/2013 jichi

__all__ = 'CachingRestApi',
if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from time import time
from hashlib import md5 # pylint: disable-msg=E0611
from amazonproduct.api import API
import restful.offline
#from amazonproduct.contrib.caching import ResponseCachingAPI

class RestCacherBase(restful.offline.CacherBase):
  def __init__(self, *args, **kwargs):
    super(RestCacherBase, self).__init__(*args, **kwargs)

  def _digest(self, expire, url):
    """
    @param  expire  bool
    @param  url  str
    @return  str
    Calculate hash value for request based on URL.
    """
    # Already sorted in amazonproduct.api, no need to sort again
    url = '&'.join((it for it in url.split('&')
          if it and 'Timestamp' not in it and 'Signature' not in it))
    if expire and self.expiretime:
      now = int(time())
      url += '&__expire=' + str(now/self.expiretime)
    return md5(url).hexdigest()

CachingRestApi = restful.offline.FileCacher(API, Base=RestCacherBase, suffix='.xml')

if __name__ == '__main__':

  AWS_ACCESS_KEY = 'AKIAJSUDXZVM3TXLJXPQ'
  SECRET_KEY = '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'
  ASSOCIATE_TAG = 'sakuradite-20'

  cachedir = "s:/tmp/amazon"
  cachedir = 'tmp'

  api = CachingRestApi(
      access_key_id=AWS_ACCESS_KEY,
      secret_access_key=SECRET_KEY,
      locale='jp',
      associate_tag=ASSOCIATE_TAG,
      cachedir=cachedir, expiretime=86400)

  search = 'B00030BDNA'
  search = 'B00AT6K7OE'
  q = api.item_lookup(search,
          ResponseGroup='Large')
  #search = u"レミニセンス"
  #q = api.item_search(
  #        'Music',
  #        Keywords=search,
  #        ResponseGroup='Large',
  #        limit=10) # page size
  for root in q:

    # extract paging information
    #total_results = root.Items.TotalResults.pyval
    #total_pages = root.Items.TotalPages.pyval
    try:
      current_page = root.Items.Request.ItemSearchRequest.ItemPage.pyval
    except AttributeError:
      current_page = 1

    #print 'page %d of %d' % (current_page, total_pages)

    # from lxml import etree
    # print etree.tostring(root, pretty_print=True)

    nspace = root.nsmap.get(None, '')
    books = root.xpath('//aws:Items/aws:Item', namespaces={'aws' : nspace})

    #attrs = 'Binding', 'Brand', 'CatalogNumberList', 'EAN', 'EANList', 'Format', 'Label', 'ListPrice', 'Manufacturer', 'OperatingSystem', 'PackageDimensions', 'PackageQuantity', 'Platform', 'ProductGroup', 'ProductTypeName', 'Publisher', 'ReleaseDate', 'Studio', 'Title'
    attrs = 'Binding', 'Brand', 'EAN', 'Format', 'Label', 'ListPrice', 'ProductGroup', 'ProductTypeName', 'ReleaseDate', 'Title'

    # Label, Publisher, Studio, Manufacturer
    # Brand

    # https://github.com/yoavaviram/python-amazon-simple-product-api/blob/master/amazon/api.py
    for book in books:
      print book.ASIN,
      try:
        print book.LargeImage.URL
        print book.MediumImage.URL
        print book.SmallImage.URL
        #print book.TinyImage.URL # on the fly? or in to the database?
      except: pass
      if book.ItemAttributes.Binding in ('CD', 'CD-ROM'):
        continue
      for a in attrs:
        #try:
        #  if book.ItemAttributes.ProductTypeName != 'ABIS_SOFTWARE':
        #    continue
        #  if book.ItemAttributes.Binding != 'DVD-ROM':
        #    continue
        #except: continue
        try:
          if a == 'ListPrice':
            print "ListPrice =", unicode(book.ItemAttributes.ListPrice.FormattedPrice), ",",
          else:
            print a, "=", unicode(getattr(book.ItemAttributes, a)), ",",
        except Exception: a, "=,",
      print

# EOF
