import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
  from PySide6.QtCore import QEvent, QModelIndex, QPointF, QSettings, QSize, Qt
  from PySide6.QtPdf import QPdfDocument
  from PySide6.QtTest import QTest
  from PySide6.QtWidgets import QApplication
  from app.main import MainWindow
except ImportError:
  QApplication = None

from app.pdf_builder import ROOT_DIR, build_pdf, template_style_preset


@unittest.skipIf(QApplication is None, 'Las pruebas del visor requieren el entorno .venv con PySide6.')
class PdfNavigationTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.app = QApplication.instance() or QApplication([])
    folder = ROOT_DIR / 'tmp'
    folder.mkdir(exist_ok=True)
    cls.temporary = tempfile.TemporaryDirectory(dir=folder)
    cls.folder = Path(cls.temporary.name)
    cls.source = ROOT_DIR / 'ejemplos' / 'prueba_navegacion_pdf.md'
    cls.result = build_pdf(cls.source, style=template_style_preset('estudio'),
                           output_file=cls.folder / 'mapped.pdf', include_navigation=True)
    cls.compact = build_pdf(cls.source, style=template_style_preset('compacto'), template_id='compacto',
                            output_file=cls.folder / 'compact.pdf', include_navigation=True)

  @classmethod
  def tearDownClass(cls):
    cls.temporary.cleanup()

  def setUp(self):
    settings = QSettings(str(self.folder / 'settings.ini'), QSettings.Format.IniFormat)
    with patch('app.main.QSettings', return_value=settings):
      self.window = MainWindow()
    self.window.resize(1200, 800)
    self.window.set_markdown_file(str(self.source))
    self.window.on_success(str(self.result.pdf_file), self.result.navigation)
    self.window.show()
    self.app.processEvents()

  def tearDown(self):
    self.window.editor_dirty = False
    self.window.custom_template_dirty = False
    self.window.close()
    self.window.unload_pdf_preview()
    self.window.deleteLater()
    self.app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    self.app.processEvents()

  def click_pdf(self, page, x, y):
    view = self.window.pdf_view
    view.pageNavigator().jump(page, QPointF(), 0)
    self.app.processEvents()
    rectangle = dict(view.page_rectangles())[page]
    size = self.window.pdf_document.pagePointSize(page)
    point = QPointF(rectangle.left() + x * rectangle.width() / size.width(),
                    rectangle.top() + y * rectangle.height() / size.height())
    if not view.viewport().rect().contains(point.toPoint()):
      view.verticalScrollBar().setValue(view.verticalScrollBar().value() +
                                        round(point.y() - view.viewport().height() / 2))
      self.app.processEvents()
      rectangle = dict(view.page_rectangles())[page]
      point.setY(rectangle.top() + y * rectangle.height() / size.height())
    QTest.mouseClick(view.viewport(), Qt.MouseButton.LeftButton, pos=point.toPoint())
    self.app.processEvents()
    return view.page_at(point)

  def test_click_switches_to_markdown_and_highlights_block_without_editing(self):
    block = next(b for b in self.result.navigation['blocks'] if b['first'] == 19)
    self.window.select_left_section(1)
    self.click_pdf(block['start']['page'] - 1, 100,
                   (block['start']['y'] + block['end']['y']) / 2)
    self.assertEqual(self.window.active_left_section, 0)
    self.assertEqual(self.window.editor.textCursor().blockNumber(), 18)
    self.assertEqual(len(self.window.editor.extraSelections()), 1)
    self.assertFalse(self.window.editor_dirty)
    self.assertFalse(self.window.editor.textCursor().hasSelection())

  def test_changed_markdown_disables_jump_even_if_marked_saved(self):
    self.window.editor.insertPlainText('Changed ')
    self.window.editor_dirty = False
    position = self.window.editor.textCursor().position()
    self.window.jump_to_markdown_block(0, 100, 65)
    self.assertEqual(self.window.editor.textCursor().position(), position)
    self.assertIn('ha cambiado', self.window.status_label.text())

  def test_click_after_scrolling_maps_to_later_page(self):
    block = next(b for b in self.result.navigation['blocks'] if b['first'] == 57)
    self.click_pdf(block['start']['page'] - 1, 100,
                   (block['start']['y'] + block['end']['y']) / 2)
    self.assertEqual(self.window.editor.textCursor().blockNumber(), 56)

  def test_click_in_second_column(self):
    self.window.on_success(str(self.compact.pdf_file), self.compact.navigation)
    self.app.processEvents()
    block = next(b for b in self.compact.navigation['blocks'] if b['first'] == 57)
    self.click_pdf(block['start']['page'] - 1, block['start']['x'] + 30,
                   (block['start']['y'] + block['end']['y']) / 2)
    self.assertEqual(self.window.editor.textCursor().blockNumber(), 56)

  def test_code_image_and_alert_jump_to_original_source(self):
    for line in (30, 37, 41):
      with self.subTest(line=line):
        block = next(b for b in self.result.navigation['blocks'] if b['first'] == line)
        self.window.jump_to_markdown_block(block['start']['page'] - 1, 100,
                                           (block['start']['y'] + block['end']['y']) / 2)
        self.assertEqual(self.window.editor.textCursor().blockNumber(), line - 1)

  def test_preview_can_be_overwritten_after_clicking_a_link(self):
    self.window.pdf_view.links.setDocument(self.window.pdf_document)
    self.window.pdf_view.links.setPage(0)
    self.window.pdf_view.links.rowCount(QModelIndex())
    self.window.unload_pdf_preview()
    result = build_pdf(self.source, style=template_style_preset('estudio'),
                       output_file=self.result.pdf_file, include_navigation=True)
    self.window.on_success(str(result.pdf_file), result.navigation)
    self.assertGreater(self.window.pdf_document.pageCount(), 0)

  def test_external_link_opens_url_without_moving_editor(self):
    view = self.window.pdf_view
    view.links.setDocument(self.window.pdf_document)
    for page in range(self.window.pdf_document.pageCount()):
      view.links.setPage(page)
      for row in range(view.links.rowCount(QModelIndex())):
        link = view.links.data(view.links.index(row, 0), view.links.Role.Link.value)
        if not link.url().isEmpty():
          rect = link.rectangles()[0]
          position = self.window.editor.textCursor().position()
          with patch('app.pdf_preview.QDesktopServices.openUrl', return_value=True) as opened:
            self.click_pdf(page, rect.center().x(), rect.center().y())
          opened.assert_called_once()
          self.assertEqual(self.window.editor.textCursor().position(), position)
          return
    self.fail('El PDF de prueba debe contener un enlace externo.')

  def test_internal_link_navigates_pdf_without_moving_editor(self):
    view = self.window.pdf_view
    view.links.setPage(0)
    for row in range(view.links.rowCount(QModelIndex())):
      link = view.links.data(view.links.index(row, 0), view.links.Role.Link.value)
      if link.isValid() and link.url().isEmpty():
        position = self.window.editor.textCursor().position()
        rect = link.rectangles()[0]
        self.click_pdf(0, rect.center().x(), rect.center().y())
        self.assertEqual(self.window.editor.textCursor().position(), position)
        self.assertEqual(view.pageNavigator().currentPage(), link.page())
        target_rectangle = dict(view.page_rectangles())[link.page()]
        target_y = target_rectangle.top() + link.location().y() * target_rectangle.height() / self.window.pdf_document.pagePointSize(link.page()).height()
        self.assertLess(abs(target_y - 20), 3)
        return
    self.fail('El PDF de prueba debe contener un enlace interno.')

  def test_mapping_does_not_change_rendered_layout(self):
    baseline = build_pdf(self.source, style=template_style_preset('estudio'),
                         output_file=self.folder / 'baseline.pdf')
    document = QPdfDocument()
    document.load(str(baseline.pdf_file))
    try:
      self.assertEqual(document.pageCount(), self.window.pdf_document.pageCount())
      for page in range(document.pageCount()):
        original = document.render(page, QSize(600, 850))
        mapped = self.window.pdf_document.render(page, QSize(600, 850))
        self.assertEqual(original, mapped, f'La navegacion no debe alterar la pagina {page + 1}.')
    finally:
      document.close()


if __name__ == '__main__':
  unittest.main()
