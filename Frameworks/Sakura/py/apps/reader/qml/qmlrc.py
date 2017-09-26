# coding: utf8
# rc.py
# 10/8/2012 jichi
# Runtime resource locations
#
# All paths are using ascii encoding.
# Assume there are no unicode characters in the relative path.

from PySide.QtCore import Qt, QUrl
from PySide.QtGui import QImage, QPixmap, QIcon
from Qt5.QtQuick1 import QDeclarativeImageProvider
from sakurakit.skdebug import derror
import rc

## Resource image provider ##

# See: http://www.lothlorien.com/kf6gpe/?p=234
class ResourceImageProvider(QDeclarativeImageProvider):

  PROVIDER_ID = 'rc'

  def __init__(self, type=QDeclarativeImageProvider.Pixmap):
    """
    @param  type  int  QDeclarativeImageProvider.ImageType  either Pixmap or Image

    Use QPixmap as default, which renders faster than QImage
    """
    super(ResourceImageProvider, self).__init__(type)

  def requestImage(self, name, rsize, size):
    """@reimp @public
    @param[in]  providerId  unicode  unused
    @param[out]  rsize  QSize
    @param[in]  size  QSize
    @return  QImage not None

    virtual QImage requestImage(const QString &id, QSize *size, const QSize &requestedSize)
    """
    ret = QImage(rc.image_path(name))
    if ret.isNull():
      derror("failed to load image: '%s'" % name)
    elif ret.size() != size:
      ret = (ret.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation) if not size.isEmpty() else
             ret.scaledToWidth(size.width(), Qt.SmoothTransformation) if size.width() > 0 else
             ret.scaledToHeight(size.height(), Qt.SmoothTransformation) if size.height() > 0 else
             ret)
    rsize.setWidth(ret.width())
    rsize.setHeight(ret.height())
    return ret

  def requestPixmap(self, name, rsize, size):
    """@reimp @public
    @param[in]  providerId  unicode  unused
    @param[out]  rsize  QSize
    @param[in]  size  QSize
    @return  QPixmap not None

    virtual QPixmap requestPixmap(const QString &id, QSize *size, const QSize &requestedSize)
    """
    ret = QPixmap(rc.image_path(name))
    if ret.isNull():
      derror("failed to load image: '%s'" % name)
    elif ret.size() != size:
      ret = (ret.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation) if not size.isEmpty() else
             ret.scaledToWidth(size.width(), Qt.SmoothTransformation) if size.width() > 0 else
             ret.scaledToHeight(size.height(), Qt.SmoothTransformation) if size.height() > 0 else
             ret)
    rsize.setWidth(ret.width())
    rsize.setHeight(ret.height())
    return ret

## File image provider ##

# See: http://www.lothlorien.com/kf6gpe/?p=234
class FileImageProvider(QDeclarativeImageProvider):

  PROVIDER_ID = 'file'

  """
  Default icon size on Windows
  See: http://msdn.microsoft.com/en-us/library/ms997636.aspx
  """
  ICON_SIZE = 48, 48

  def __init__(self):
    """
    Use QPixmap as default, which renders faster than QImage
    """
    super(FileImageProvider, self).__init__(QDeclarativeImageProvider.Pixmap)

  def requestPixmap(self, path, rsize, size):
    """@reimp @public
    @param[in]  providerId  unicode  unused
    @param[out]  rsize  QSize
    @param[in]  size  QSize
    @return  QPixmap not None

    virtual QPixmap requestPixmap(const QString &id, QSize *size, const QSize &requestedSize)
    """

    icon = rc.file_icon(path)
    if icon.isNull():
      derror("failed to load image: '%s'" % path)
      ret = QPixmap()
    elif not size.isEmpty():
      ret = icon.pixmap(size)
    else:
      #sizes = icon.availableSizes(QIcon.Selected, QIcon.Off) # crash for executable
      ret = icon.pixmap(*FileImageProvider.ICON_SIZE)

    rsize.setWidth(ret.width())
    rsize.setHeight(ret.height())
    return ret

## URL image provider ##

class SpringImageProvider(QDeclarativeImageProvider):

  PROVIDER_ID = 'spring'

  def __init__(self):
    """
    Use QPixmap as default, which renders faster than QImage
    """
    super(SpringImageProvider, self).__init__(QDeclarativeImageProvider.Pixmap)

  def requestPixmap(self, path, rsize, size):
    """@reimp @public
    @param[in]  providerId  unicode  unused
    @param[out]  rsize  QSize
    @param[in]  size  QSize
    @return  QPixmap not None

    virtual QPixmap requestPixmap(const QString &id, QSize *size, const QSize &requestedSize)
    """

    ret = QPixmap(QUrl(path).toLocalFile())
    if ret.isNull():
      derror("failed to load image: '%s'" % path)
    elif size != ret.size() and not size.isEmpty() and not ret.size().isEmpty():
      if ret.width() * size.height() > ret.height() * size.width():
        ret = ret.scaledToHeight(min(800, size.height()), Qt.SmoothTransformation)
      else:
        w = 1000 if ret.width() > ret.height() else 600
        ret = ret.scaledToWidth(min(w, size.width()), Qt.SmoothTransformation)
    #elif size != ret.size():
    #  ret = (ret.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation) if not size.isEmpty() else
    #         ret.scaledToWidth(size.width(), Qt.SmoothTransformation) if size.width() > 0 else
    #         ret.scaledToHeight(size.height(), Qt.SmoothTransformation) if size.height() > 0 else
    #         ret)
    rsize.setWidth(ret.width())
    rsize.setHeight(ret.height())
    return ret

# EOF

## URL image provider ##

#class UrlImageProvider(QDeclarativeImageProvider):
#
#  PROVIDER_ID = 'url'
#
#  def __init__(self):
#    """
#    Use QPixmap as default, which renders faster than QImage
#    """
#    super(UrlImageProvider, self).__init__(QDeclarativeImageProvider.Pixmap)
#
#  def requestPixmap(self, path, rsize, size):
#    """@reimp @public
#    @param[in]  providerId  unicode  unused
#    @param[out]  rsize  QSize
#    @param[in]  size  QSize
#    @return  QPixmap not None
#
#    virtual QPixmap requestPixmap(const QString &id, QSize *size, const QSize &requestedSize)
#    """
#
#    ret = QPixmap(QUrl(path).toLocalFile())
#    if ret.isNull():
#      derror("failed to load image: '%s'" % path)
#    elif size != ret.size():
#      ret = (ret.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation) if not size.isEmpty() else
#             ret.scaledToWidth(size.width(), Qt.SmoothTransformation) if size.width() > 0 else
#             ret.scaledToHeight(size.height(), Qt.SmoothTransformation) if size.height() > 0 else
#             ret)
#    rsize.setWidth(ret.width())
#    rsize.setHeight(ret.height())
#    return ret

## Filter image provider ##

#from qimp import qimp
#class FilterImageProvider(QDeclarativeImageProvider):
#
#  PROVIDER_ID = 'filter'
#
#  def __init__(self):
#    """
#    Use QPixmap as default, which renders faster than QImage
#    """
#    super(FilterImageProvider, self).__init__(QDeclarativeImageProvider.Pixmap)
#
#  def requestPixmap(self, path, rsize, size):
#    """@reimp @public
#    @param[in]  providerId  unicode  unused
#    @param[out]  rsize  QSize
#    @param[in]  size  QSize
#    @return  QPixmap not None
#
#    virtual QPixmap requestPixmap(const QString &id, QSize *size, const QSize &requestedSize)
#    """
#    ret = QPixmap(QUrl(path).toLocalFile())
#    if ret.isNull():
#      derror("failed to load image: '%s'" % path)
#    #elif size != ret.size():
#    elif size.width() < ret.width() or size.height() < ret.height(): # do increase size
#      ret = (ret.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation) if not size.isEmpty() else
#             ret.scaledToWidth(size.width(), Qt.SmoothTransformation) if size.width() > 0 and size.width() < ret.width() else
#             ret.scaledToHeight(size.height(), Qt.SmoothTransformation) if size.height() > 0 and size.height() < ret.height() else
#             ret)
#    rsize.setWidth(ret.width())
#    rsize.setHeight(ret.height())
#    if ret and not ret.isNull():
#      qimp.gradientpixmap(ret)
#    return ret
