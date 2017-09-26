# coding: utf8
# chart.py
# 3/3/2013 jichi
# http://eli.thegreenplace.net/2009/01/20/matplotlib-with-pyqt-guis/
# http://eli.thegreenplace.net/files/prog_code/qt_mpl_bars.py.txt

import matplotlib as mpl

def _initrc():
  mpl.rcParams['backend'] = 'Qt4Agg'
  mpl.rcParams['backend.qt4'] = 'PySide'
  mpl.rcParams['backend_fallback'] = False

  #import i18n, settings
  #lang = settings.global_().userLanguage()
  #font = i18n.font_family(lang)
  #if font:
  #  # http://matplotlib.org/examples/api/font_family_rc.html
  #  mpl.rcParams['font.family'] = font # default: 'sans-serif'
  mpl.rcParams['font.family'] = 'YouYuan' # default: 'sans-serif'
_initrc()

from collections import Counter, defaultdict
from datetime import datetime
from functools import partial
from operator import itemgetter
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as MplNavigationToolbar
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as MplFigureCanvas
from matplotlib.figure import Figure as MplFigure
from PySide.QtCore import Qt
from Qt5 import QtWidgets
from sakurakit import skcursor, skevents, skqss, skthreads
from sakurakit.skclass import memoizedproperty
from sakurakit.sktr import tr_
from mytr import my, mytr_
import i18n

# FIXME: redraw dows not work

class DataInfo(object):

  def __init__(self, data):
    """
    @param  data  [dataman.Comment|dataman.Term]
    """
    self.data = data

    # Timestamps
    times = {it.timestamp for it in self.data} # set
    self.times = sorted(times) # list
    self.dates = map(datetime.fromtimestamp, self.times)

    # User stats

    stat = defaultdict(int) # [unicode userName:int count]
    for it in self.data:
      stat[it.userName] += 1
    c = Counter(stat).most_common() # [(k, v)], order by v desc
    #c.reverse() # order asc
    self.userNames = map(itemgetter(0), c)
    self.userCounts = map(itemgetter(1), c)

    # Language stats

    stat = defaultdict(int) # [unicode userName:int count]
    for it in self.data:
      stat[it.language] += 1
    c = Counter(stat).most_common() # [(k, v)], order by v desc
    #c.reverse() # order asc
    self.languageCounts = map(itemgetter(1), c)
    self.languages = map(itemgetter(0), c)
    self.languageNames = map(i18n.language_name2, self.languages)

class _ChartDialog(object):

  #FIGURE_SIZE = 1, 1
  SIZE = 800, 600

  def __init__(self, q, data, async):
    """
    @param  data  [dataman.Comment|dataman.Term]
    @param  async  bool
    """
    self._createUi(q)
    #canvas.setContentsMargins(0,0,0,0)
    #q.setContentsMargins(0,0,0,0)
    #skqss.class_(canvas, 'texture')

    if async:
      skthreads.runsync(partial(self._plot, data))
    else:
      self._plot(data)

  def _createUi(self, q):
    canvas = MplFigureCanvas(self.figure)
    toolbar = MplNavigationToolbar(canvas, q)
    q.addToolBar(toolbar)
    q.setCentralWidget(canvas)

  def _plot(self, data):
    """
    @param  data  [dataman.Comment|dataman.Term]
    @param  info  DataInfo
    """
    info = DataInfo(data)
    fig = self.figure
    #fig.clear()
    self._plotLanguageStackFigure(fig.add_subplot(221,
        title=my.tr("Timeline by {0}").format(tr_("language"))),
        info)
    self._plotLanguagePieFigure(fig.add_subplot(222,
        title=my.tr("Percentage by {0}").format(tr_("language"))),
        info)
    self._plotUserStackFigure(fig.add_subplot(223,
        title=my.tr("Timeline by {0}").format(tr_("user"))),
        info)
    self._plotUserPieFigure(fig.add_subplot(224,
        title=my.tr("Percentage by {0}").format(tr_("user"))),
        info)
    fig.autofmt_xdate() # rotate x axis
    #fig.subplots_adjust(hspace=0.4)

  @memoizedproperty
  def figure(self):
    # http://matplotlib.org/api/figure_api.html
    #return MplFigure(figsize=self.FIGURE_SIZE, dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
    return MplFigure(dpi=72, facecolor='#eeeeee', edgecolor=(0,0,0))

  # Pie figures

  @staticmethod
  def _plotUserPieFigure(ax, info):
    """
    @param  ax  matplotlib.axes.Axes
    @param  info  DataInfo
    """
    keys = info.userNames
    values = info.userCounts
    explode = [0.05] * len(values)
    ax.pie(values, labels=keys, explode=explode,
      autopct="%1.1f%%", # draw percentage
      shadow=True,
      #startangle=90,
    )

  @staticmethod
  def _plotLanguagePieFigure(ax, info):
    """
    @param  ax  matplotlib.axes.Axes
    @param  info  DataInfo
    """
    keys = info.languageNames
    values = info.languageCounts
    explode = [0.05] * len(values)
    ax.pie(values, labels=keys, explode=explode,
      autopct="%1.1f%%", # draw percentage
      shadow=True,
      #startangle=90,
    )

  # Stack figures

  @staticmethod
  def _plotStackAxes(ax, info):
    """
    @param  axes  matplotlib.axes.Axes
    @param  info  DataInfo
    """
    # Draw axes
    mint = info.times[0]
    maxt = info.times[-1]

    if maxt - mint > 86400 * 90: # 3 months
      ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%b')) # "Feb 2"
      ax.xaxis.set_major_locator(mpl.dates.MonthLocator())
    else:
      ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%a %b %d')) # "Feb 2, Mon"
      ax.xaxis.set_major_locator(mpl.dates.WeekdayLocator())

    ax.grid(True)
    mindate = info.dates[0]
    maxdate = info.dates[-1]
    ax.set_xlim(mindate, maxdate)
    #ax.set_ylim(ymin=0) # http://stackoverflow.com/questions/5548121/minimum-value-of-y-axis-is-not-being-applied-in-matplotlib-vlines-plot

  @classmethod
  def _plotUserStackFigure(cls, ax, info):
    """
    @param  axes  matplotlib.axes.Axes
    @param  info  DataInfo
    """
    cls._plotStackAxes(ax, info)

    stats = defaultdict(lambda: defaultdict(int))
    for it in info.data:
      stats[it.userName][it.timestamp] += 1

    plots = [] # [[int count]]
    for n in info.userNames:
      c = 1 # at least 1
      l = []
      for t in info.times:
        c += stats[n].get(t) or 0
        l.append(c)
      plots.append(l)

    # Not sure why it is optional to user count
    # Force changing ymin to 0
    # http://stackoverflow.com/questions/5548121/minimum-value-of-y-axis-is-not-being-applied-in-matplotlib-vlines-plot
    #ymax = sum(it[-1] for it in plots)
    #ax.set_ylim(0, ymax)

    ax.stackplot(info.dates, plots)

  @classmethod
  def _plotLanguageStackFigure(cls, ax, info):
    """
    @param  axes  matplotlib.axes.Axes
    @param  info  DataInfo
    """
    cls._plotStackAxes(ax, info)

    stats = defaultdict(lambda: defaultdict(int))
    for it in info.data:
      stats[it.language][it.timestamp] += 1

    plots = [] # [[int count]]
    for n in info.languages:
      c = 1 # at least 1
      l = []
      for t in info.times:
        c += stats[n].get(t) or 0
        l.append(c)
      plots.append(l)

    # Force changing ymin to 0
    # http://stackoverflow.com/questions/5548121/minimum-value-of-y-axis-is-not-being-applied-in-matplotlib-vlines-plot
    ymax = sum(it[-1] for it in plots) + 600 # larger, 600 = 16000 - 15400
    ax.set_ylim(0, ymax)

    ax.stackplot(info.dates, plots)

class ChartDialog(QtWidgets.QMainWindow):

  def __init__(self, data, parent=None):
    """
    @param  data  [dataman.Comment|dataman.Term]
    """
    self.ready = False
    async = len(data) > 15000
    async = True
    cursor = skcursor.SkAutoBusyCursor() if async else skcursor.SkAutoWaitCursor()

    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(ChartDialog, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.resize(*_ChartDialog.SIZE)
    self.__d = _ChartDialog(self, data, async=async)

    skevents.runlater(partial(self.setReady, True))

  def isReady(self): return self.ready
  def setReady(self, val): self.ready = val

  #def setVisible(self, visible):
  #  """@reimp @public"""
  #  if visible and not self.isVisible():
  #    self.__d.refresh()
  #  super(ChartDialog, self).setVisible(visible)

## Dialogs ##

class CommentChartDialog(ChartDialog):

  def __init__(self): pass

  def init(self, data, parent=None):
    """
    @param  data  [dataman.Comment]
    """
    super(CommentChartDialog, self).__init__(data, parent=parent)
    self.setWindowTitle("%s - %s" % (tr_("Statistics"), tr_("Subtitles")))

class TermChartDialog(ChartDialog):

  def __init__(self, data, parent=None):
    """
    @param  data  [dataman.Term]
    """
    super(TermChartDialog, self).__init__(data, parent=parent)
    self.setWindowTitle("%s - %s" % (tr_("Statistics"), mytr_("Shared Dictionary")))

if __name__ == '__main__':
  import matplotlib as mpl
  mpl.rcParams['backend'] = 'Qt4Agg'
  mpl.rcParams['backend.qt4'] = 'PySide'
  mpl.rcParams['backend_fallback'] = False

  import sys
  from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
  from matplotlib.figure import Figure

  from PySide import QtCore, QtGui

  app = QtGui.QApplication(sys.argv)

  # generate the plot
  fig = Figure(figsize=(600,600), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
  ax = fig.add_subplot(121)
  ax.plot([0,1])
  ax = fig.add_subplot(122)
  #ax.plot([0,1])
  labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
  data = [15, 30, 45, 10]
  ax.pie(data, labels=labels,
         autopct='%1.1f%%', shadow=True, startangle=90)

  # generate the canvas to display the plot
  canvas = FigureCanvas(fig)

  win = QtGui.QMainWindow()
  # add the plot canvas to a window
  win.setCentralWidget(canvas)

  win.show()

  sys.exit(app.exec_())

# EOF

#http://matplotlib.org/users/screenshots.html
#
#if __name__ == '__main__':
#  from matplotlib import pyplot
#
#  # make a square figure and axes
#  pyplot.figure(1, figsize=(6,6))
#  ax = pyplot.axes([0.1, 0.1, 0.8, 0.8])
#
#  # The slices will be ordered and plotted counter-clockwise.
#  labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
#  fracs = [15, 30, 45, 10]
#  explode=(0, 0.05, 0, 0)
#
#  pyplot.pie(fracs, explode=explode, labels=labels,
#                  autopct='%1.1f%%', shadow=True, startangle=90)
#                  # The default startangle is 0, which would start
#                  # the Frogs slice on the x-axis.  With startangle=90,
#                  # everything is rotated counter-clockwise by 90 degrees,
#                  # so the plotting starts on the positive y-axis.
#
#  pyplot.title('Raining Hogs and Dogs', bbox={'facecolor':'0.8', 'pad':5})
#
#  pyplot.show()

