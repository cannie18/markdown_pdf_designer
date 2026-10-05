'''Visor PDF con clic sobre enlaces o bloques del documento.'''

from PySide6.QtCore import QPointF, QRectF, QSizeF, Qt, Signal, qVersion
from PySide6.QtGui import QDesktopServices, QGuiApplication
from PySide6.QtPdf import QPdfLinkModel
from PySide6.QtPdfWidgets import QPdfView


class PdfPreview(QPdfView):
  block_clicked = Signal(int, float, float)

  def __init__(self):
    super().__init__()
    self.links = QPdfLinkModel(self)
    self.press_position = None
    # Qt 6.11 removed the screen-DPI multiplier from QPdfView's page layout.
    version = tuple(int(part) for part in qVersion().split('.')[:2])
    self.point_scale = QGuiApplication.primaryScreen().logicalDotsPerInch() / 72 if version < (6, 11) else 1

  def setDocument(self, document):
    self.links.setDocument(document)
    super().setDocument(document)

  def page_rectangles(self):
    document = self.document()
    if document is None:
      return []
    margins = self.documentMargins()
    viewport = self.viewport().size()
    pages = (range(document.pageCount()) if self.pageMode() == self.PageMode.MultiPage
             else [self.pageNavigator().currentPage()])
    sizes = []
    for page in pages:
      points = document.pagePointSize(page)
      size = QSizeF(points * self.point_scale).toSize()
      if self.zoomMode() == self.ZoomMode.FitToWidth:
        scale = (viewport.width() - margins.left() - margins.right()) / size.width()
        size = QSizeF(size.width() * scale, size.height() * scale).toSize()
      elif self.zoomMode() == self.ZoomMode.FitInView:
        size = size.scaled(viewport.width() - margins.left() - margins.right(),
                           viewport.height() - self.pageSpacing(), Qt.AspectRatioMode.KeepAspectRatio)
      else:
        size = QSizeF(points * self.point_scale * self.zoomFactor()).toSize()
      sizes.append((page, size))
    total_width = max((size.width() for _, size in sizes), default=0) + margins.left() + margins.right()
    top = margins.top() - self.verticalScrollBar().value()
    rectangles = []
    for page, size in sizes:
      left = (max(total_width, viewport.width()) - size.width()) // 2 - self.horizontalScrollBar().value()
      rectangles.append((page, QRectF(left, top, size.width(), size.height())))
      top += size.height() + self.pageSpacing()
    return rectangles

  def page_at(self, point):
    for page, rectangle in self.page_rectangles():
      if rectangle.contains(point):
        points = self.document().pagePointSize(page)
        return page, QPointF((point.x() - rectangle.left()) * points.width() / rectangle.width(),
                            (point.y() - rectangle.top()) * points.height() / rectangle.height())
    return None

  def mousePressEvent(self, event):
    self.press_position = event.position() if event.button() == Qt.MouseButton.LeftButton else None
    super().mousePressEvent(event)

  def mouseReleaseEvent(self, event):
    if event.button() != Qt.MouseButton.LeftButton or self.press_position is None:
      return super().mouseReleaseEvent(event)
    distance = event.position() - self.press_position
    self.press_position = None
    if distance.manhattanLength() > 5:
      return
    clicked = self.page_at(event.position())
    if clicked is None:
      return
    page, point = clicked
    self.links.setDocument(self.document())
    self.links.setPage(page)
    link = self.links.linkAt(point)
    if link.isValid() or not link.url().isEmpty():
      if not link.url().isEmpty():
        QDesktopServices.openUrl(link.url())
      else:
        self.pageNavigator().jump(link.page(), link.location(), link.zoom())
        rectangle = dict(self.page_rectangles()).get(link.page())
        if rectangle is not None:
          size = self.document().pagePointSize(link.page())
          self.verticalScrollBar().setValue(round(
            self.verticalScrollBar().value() + rectangle.top() +
            link.location().y() * rectangle.height() / size.height() - 20))
      return
    self.block_clicked.emit(page, point.x(), point.y())
