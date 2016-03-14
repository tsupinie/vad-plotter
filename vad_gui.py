
import numpy as np

from PySide import QtCore
from PySide import QtGui

import sys

class VADWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(VADWidget, self).__init__(parent=parent)
        self._min_u, self._max_u = -40., 80.
        self._min_v, self._max_v = -40., 80.
        self._drng = 10

        self._pix_wid, self._pix_hgt = 500, 500
        self._mrg_wid, self._mrg_hgt = 10, 10
        self._hodo_rect = QtCore.QRect(self._mrg_wid, self._mrg_hgt, self._pix_wid - 2 * self._mrg_wid, self._pix_hgt - 2 * self._mrg_hgt)

        self._initWidget()

    def _pix2uv(self, pix_x, pix_y):
        u_pt = self._min_u + (self._max_u - self._min_u) * float(pix_x - self._mrg_wid) / (self._pix_wid - 2 * self._mrg_wid)
        v_pt = self._max_v - (self._max_v - self._min_v) * float(pix_y - self._mrg_hgt) / (self._pix_hgt - 2 * self._mrg_hgt)
        return u_pt, v_pt

    def _uv2Pix(self, u_pt, v_pt):
        pix_x = (u_pt - self._min_u) / (self._max_u - self._min_u) * (self._pix_wid - 2 * self._mrg_wid) + self._mrg_wid
        pix_y = (self._max_v - v_pt) / (self._max_v - self._min_v) * (self._pix_hgt - 2 * self._mrg_hgt) + self._mrg_hgt
        return int(round(pix_x)), int(round(pix_y))

    def _initWidget(self):
        self._background = QtGui.QPixmap(self._pix_wid, self._pix_hgt)
        self._background.fill(QtCore.Qt.white)
        self._drawBackground()
        self._foreground = self._background.copy()

        self.setMinimumSize(self._pix_wid, self._pix_hgt)

    def _drawBackground(self):
        max_u = max(abs(self._min_u), abs(self._max_u))
        max_v = max(abs(self._min_v), abs(self._max_v))
        max_rng = int(round(np.hypot(max_u, max_v)))

        pen = QtGui.QPen()
        pen.setStyle(QtCore.Qt.DashLine)
        pen.setWidth(1.5)
        pen.setColor(QtGui.QColor('#888888'))

        qp = QtGui.QPainter()
        qp.begin(self._background)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, on=True)
        qp.setClipRect(self._hodo_rect)
        qp.setClipping(True)
        qp.setPen(pen)

        for irng in xrange(self._drng, max_rng, self._drng):
            x1, y1 = self._uv2Pix(-irng, -irng)
            x2, y2 = self._uv2Pix(irng, irng)
            qp.drawEllipse(x1, y1, x2 - x1, y2 - y1)

            rng_str = "%d" % irng if irng != self._max_u - self._drng else "%d kts" % irng
            x1, y1 = self._uv2Pix(irng, 0)
            qp.drawText(QtCore.QPoint(x1 + 2, y1 + 12), rng_str)

        pen.setStyle(QtCore.Qt.SolidLine)
        qp.setPen(pen)

        x1, y1 = self._uv2Pix(self._min_u, 0)
        x2, y2 = self._uv2Pix(self._max_u, 0)
        qp.drawLine(x1, y1, x2, y2)

        x1, y1 = self._uv2Pix(0, self._min_v)
        x2, y2 = self._uv2Pix(0, self._max_v)
        qp.drawLine(x1, y1, x2, y2)
        qp.setClipping(False)

        pen.setColor(QtCore.Qt.black)
        pen.setWidth(2)
        qp.setPen(pen)
        qp.drawRect(self._hodo_rect)

        qp.end()

    def paintEvent(self, e):
        super(VADWidget, self).paintEvent(e)
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawPixmap(0, 0, self._foreground)
        qp.end()

class VADGui(QtGui.QMainWindow):
    def __init__(self):
        super(VADGui, self).__init__(parent=None)
        self._initUI()

    def _initUI(self):
        self.setCentralWidget(VADWidget(parent=self))
        self.setWindowTitle("VAD Gui")

        self.show()
        self.raise_()

if __name__ == "__main__":
    app = QtGui.QApplication([])
    gui = VADGui()
    sys.exit(app.exec_())
