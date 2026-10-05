import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
  from PySide6.QtCore import QEvent, QSettings, Qt
  from PySide6.QtWidgets import QApplication, QFrame, QLabel
  from app.main import MainWindow
except ImportError:
  QApplication = None

from app.pdf_builder import ROOT_DIR


@unittest.skipIf(QApplication is None, 'Las pruebas de ayuda requieren el entorno .venv con PySide6.')
class HelpContentTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.app = QApplication.instance() or QApplication([])
    folder = ROOT_DIR / 'tmp'
    folder.mkdir(exist_ok=True)
    cls.temporary = tempfile.TemporaryDirectory(dir=folder)
    cls.folder = Path(cls.temporary.name)

  @classmethod
  def tearDownClass(cls):
    cls.temporary.cleanup()

  def setUp(self):
    settings = QSettings(str(self.folder / 'settings.ini'), QSettings.Format.IniFormat)
    with patch('app.main.QSettings', return_value=settings):
      self.window = MainWindow()
    self.window.show()
    self.app.processEvents()

  def tearDown(self):
    self.window.editor_dirty = False
    self.window.custom_template_dirty = False
    self.window.close()
    self.window.deleteLater()
    self.app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    self.app.processEvents()

  def help_cards(self):
    return self.window.help_preview_scroll.widget().findChildren(QFrame, 'helpCard')

  @staticmethod
  def card_labels(card):
    return [child for child in card.children() if isinstance(child, QLabel)]

  def test_help_topics_have_a_clear_task_order(self):
    titles = [
      next(label.text() for label in self.card_labels(card)
           if label.objectName() == 'helpCardTitle')
      for card in self.help_cards()
    ]
    self.assertEqual(titles, [
      'Guía rápida',
      'Markdown: archivos y acciones',
      'Markdown: escritura recomendada',
      'Markdown: imágenes',
      'Markdown: tablas',
      'Markdown: funciones especiales',
      'Vista previa PDF',
      'Diseño: secciones',
      'Diseño: plantillas',
      'Diseño: controles y actualización',
    ])

  def test_images_and_tables_have_independent_instructions(self):
    cards = {
      next(label.text() for label in self.card_labels(card)
           if label.objectName() == 'helpCardTitle'): card
      for card in self.help_cards()
    }
    image_text = ' '.join(label.text() for label in self.card_labels(cards['Markdown: imágenes']))
    table_text = ' '.join(label.text() for label in self.card_labels(cards['Markdown: tablas']))
    self.assertIn('align=center', image_text)
    self.assertNotIn('table-style', image_text)
    self.assertIn('table-style', table_text)
    self.assertNotIn('align=center', table_text)

  def test_instructions_use_rich_text_lists(self):
    list_labels = self.window.help_preview_scroll.widget().findChildren(QLabel, 'helpCardText')
    self.assertGreater(len(list_labels), 0)
    for label in list_labels:
      self.assertEqual(label.textFormat(), Qt.TextFormat.RichText)
      self.assertRegex(label.text(), r'^<(?:ol|ul)\b')
      self.assertNotIn('\n- ', label.text())


if __name__ == '__main__':
  unittest.main()
