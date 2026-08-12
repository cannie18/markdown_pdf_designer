'''Interfaz gráfica PySide6 para generar PDF desde Markdown.

La ventana permite abrir o arrastrar un Markdown, editarlo opcionalmente,
configurar estilos básicos, generar el PDF y ver la vista previa real dentro
de la app. La conversión se delega en `app.pdf_builder`.
'''

from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from pathlib import Path

from PySide6.QtCore import QSize, QSettings, Qt, QThread, Signal
from PySide6.QtGui import QColor, QCloseEvent, QDragEnterEvent, QDropEvent, QIcon, QWheelEvent
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import (
  QApplication,
  QColorDialog,
  QComboBox,
  QDoubleSpinBox,
  QFileDialog,
  QFrame,
  QHBoxLayout,
  QInputDialog,
  QLabel,
  QMainWindow,
  QMessageBox,
  QPlainTextEdit,
  QPushButton,
  QScrollArea,
  QSizePolicy,
  QSplitter,
  QStackedWidget,
  QStyle,
  QVBoxLayout,
  QWidget,
)

from .pdf_builder import (
  DEFAULT_TEMPLATE_ID,
  PdfBuildError,
  PdfStyleOptions,
  available_templates,
  build_pdf,
  is_custom_template,
  save_custom_template,
  template_description,
  template_label,
  template_style_preset,
  update_custom_template_style,
)


PREVIEW_PANEL_MIN_WIDTH = 320
WINDOW_MIN_HEIGHT = 480
RECENT_FILES_POPUP_MIN_WIDTH = 560
RECENT_FILES_POPUP_MAX_WIDTH = 960
SELECTED_TEMPLATE_SETTING = 'selected_template_id'
ICON_DIR = Path(__file__).resolve().parents[1] / 'assets' / 'icons'
TEMPLATE_LABELS = {
  'estudio': 'Estudio',
  'profesional': 'Profesional',
  'compacto': 'Compacto',
  'accesibilidad_neurodivergencia': 'Accesibilidad y neurodivergencia',
  'latex_clasico': 'LaTeX clásico',
  'apa_mla': 'Ensayo APA / MLA',
  'informe_ejecutivo': 'Informe ejecutivo',
  'manual_tecnico': 'Manual técnico',
  'manuscrito_novela': 'Manuscrito / novela',
}
DESIGN_LABEL_ICONS = {
  'Plantilla': 'template.svg',
  'Fuente': 'font.svg',
  'Tamaño texto': 'text-size.svg',
  'Color texto': 'text-color.svg',
  'Fondo página': 'page-background.svg',
  'Interlineado': 'line-height.svg',
  'Espacio párrafos': 'paragraph-spacing.svg',
  'Margen lateral': 'margins.svg',
  'Margen vertical': 'margins.svg',
  'Tamaño título 1': 'heading-1.svg',
  'Tamaño título 2': 'heading-2.svg',
  'Tamaño título 3': 'heading-3.svg',
  'Título 1': 'heading-1.svg',
  'Título 2': 'heading-2.svg',
  'Título 3': 'heading-3.svg',
  'Negrita': 'bold.svg',
  'Cursiva': 'italic.svg',
  'Fuente código': 'code.svg',
  'Tamaño código': 'text-size.svg',
  'Fondo código': 'color-fill.svg',
  'Espacio interno': 'quote-block.svg',
  'Borde': 'quote-border.svg',
  'Fondo': 'color-fill.svg',
  'Espacio celdas': 'table-cell-padding.svg',
  'Ancho tabla': 'table-width.svg',
  'Bordes': 'table-border.svg',
  'Fondo cabecera': 'color-fill.svg',
  'Texto cabecera': 'text-color.svg',
}
COLOR_BUTTON_LABELS = {
  'h1': 'Color título 1',
  'h2': 'Color título 2',
  'h3': 'Color título 3',
  'bold': 'Color negrita',
  'italic': 'Color cursiva',
  'body': 'Color texto',
  'page_background': 'Fondo página',
  'code_background': 'Fondo código',
  'table_stroke': 'Bordes',
  'table_text': 'Color texto',
  'table_header_background': 'Fondo cabecera',
  'table_header_text': 'Texto cabecera',
  'quote_border': 'Borde',
  'quote_background': 'Fondo',
  'quote_text': 'Color texto',
}
TEMPLATE_ORDER = [
  'estudio',
  'latex_clasico',
  'apa_mla',
  'informe_ejecutivo',
  'manual_tecnico',
  'accesibilidad_neurodivergencia',
  'manuscrito_novela',
  'profesional',
  'compacto',
]


class BuildWorker(QThread):
  '''Ejecuta la conversión en segundo plano para no bloquear la interfaz.'''

  succeeded = Signal(str)
  failed = Signal(str)

  def __init__(
    self,
    markdown_file: str,
    style: PdfStyleOptions,
    template_id: str,
  ) -> None:
    '''Guarda el archivo y las opciones visuales que se usarán al generar.'''

    super().__init__()
    self.markdown_file = markdown_file
    self.style = style
    self.template_id = template_id

  def run(self) -> None:
    '''Lanza la generación del PDF y emite una señal de éxito o error.'''

    try:
      result = build_pdf(
        self.markdown_file,
        style=self.style,
        template_id=self.template_id,
      )
    except PdfBuildError as exc:
      self.failed.emit(str(exc))
      return
    self.succeeded.emit(str(result.pdf_file))


class DropZone(QFrame):
  '''Zona visual que acepta archivos Markdown arrastrados desde Windows.'''

  file_dropped = Signal(str)

  def __init__(self) -> None:
    '''Construye el area de arrastre con textos centrados.'''

    super().__init__()
    self.setAcceptDrops(True)
    self.setObjectName('dropZone')
    self.setMinimumHeight(110)

    layout = QVBoxLayout(self)
    title = QLabel('Arrastra aquí un Markdown')
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setMinimumWidth(0)
    title.setWordWrap(True)
    title.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    title.setObjectName('dropTitle')

    subtitle = QLabel('También puedes usar Abrir')
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
    subtitle.setMinimumWidth(0)
    subtitle.setWordWrap(True)
    subtitle.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    subtitle.setObjectName('dropSubtitle')

    layout.addStretch()
    layout.addWidget(title)
    layout.addWidget(subtitle)
    layout.addStretch()

  def dragEnterEvent(self, event: QDragEnterEvent) -> None:
    '''Acepta el arrastre si contiene URLs de archivos.'''

    if event.mimeData().hasUrls():
      event.acceptProposedAction()
    else:
      event.ignore()

  def dropEvent(self, event: QDropEvent) -> None:
    '''Emite la ruta local del primer archivo soltado.'''

    urls = event.mimeData().urls()
    if not urls:
      return
    path = urls[0].toLocalFile()
    if path:
      self.file_dropped.emit(path)


class DesignDoubleSpinBox(QDoubleSpinBox):
  '''Spinbox de diseño que no cambia valores con la rueda del ratón.'''

  def wheelEvent(self, event: QWheelEvent) -> None:
    '''Ignora la rueda para que el scroll del panel no cambie parámetros.'''

    event.ignore()


class MainWindow(QMainWindow):
  '''Ventana principal de la app de escritorio.'''

  def __init__(self, initial_file: str | None = None) -> None:
    '''Crea la interfaz y carga un Markdown inicial si se arrastro al `.bat`.'''

    super().__init__()
    self.worker: BuildWorker | None = None
    self.current_file: Path | None = None
    self.current_pdf: Path | None = None
    self.markdown_open = False
    self.editor_dirty = False
    self.active_left_section = 0
    self.loading_style_options = False
    self.selected_template_id = DEFAULT_TEMPLATE_ID
    self.custom_template_dirty = False
    self.settings = QSettings('pdf_apuntes', 'Markdown PDF Designer')
    self.template_ids = self.sorted_template_ids(available_templates())
    if DEFAULT_TEMPLATE_ID not in self.template_ids:
      self.template_ids.insert(0, DEFAULT_TEMPLATE_ID)
    self.heading_colors = {
      'h1': '#1f3552',
      'h2': '#2e6f73',
      'h3': '#7a3f3f',
      'bold': '#1f3552',
      'italic': '#131b2e',
      'body': '#131b2e',
      'page_background': '#ffffff',
      'code_background': '#f4f1ec',
      'table_stroke': '#c8d0d8',
      'table_text': '#131b2e',
      'table_header_background': '#eef2f7',
      'table_header_text': '#1f3552',
      'quote_border': '#2e6f73',
      'quote_background': '#eef6f4',
      'quote_text': '#131b2e',
    }
    self.setWindowTitle('Markdown PDF Designer')
    self.resize(1180, 720)
    self.setMinimumSize(PREVIEW_PANEL_MIN_WIDTH, WINDOW_MIN_HEIGHT)

    self.file_input = QComboBox()
    self.file_input.setEditable(True)
    self.file_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
    self.file_input.setMinimumContentsLength(8)
    self.file_input.setMinimumWidth(0)
    self.file_input.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
    self.file_input.setSizeAdjustPolicy(
      QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
    )
    self.file_input.view().setMinimumWidth(RECENT_FILES_POPUP_MIN_WIDTH)
    self.file_input.lineEdit().setPlaceholderText('Selecciona o arrastra un archivo .md')
    self.file_input.activated.connect(self.open_recent_markdown)
    self.load_recent_markdowns()

    open_button = QPushButton('Abrir')
    open_button.clicked.connect(self.choose_file)
    self.set_button_icon(open_button, 'open.svg')

    new_button = QPushButton('Nuevo')
    new_button.clicked.connect(self.create_markdown_file)
    self.set_button_icon(new_button, 'new-file.svg')

    self.edit_button = QPushButton('Cerrar')
    self.edit_button.clicked.connect(self.close_markdown_file)
    self.set_button_icon(self.edit_button, 'close-file.svg')
    self.edit_button.setEnabled(False)
    self.edit_button.setVisible(False)

    self.save_button = QPushButton('Guardar')
    self.save_button.clicked.connect(self.save_editor)
    self.set_button_icon(self.save_button, 'save.svg')
    self.save_button.setEnabled(False)
    self.save_button.setVisible(False)

    self.save_as_button = QPushButton('Guardar como')
    self.save_as_button.clicked.connect(self.save_editor_as)
    self.set_button_icon(self.save_as_button, 'save-as.svg')
    self.save_as_button.setEnabled(False)
    self.save_as_button.setVisible(False)

    self.build_button = QPushButton('Generar PDF')
    self.build_button.clicked.connect(self.generate_pdf)
    self.set_button_icon(self.build_button, 'generate-pdf.svg')
    self.build_button.setEnabled(False)
    self.build_button.setVisible(False)

    self.open_pdf_button = QPushButton('Abrir PDF en Windows')
    self.open_pdf_button.clicked.connect(self.open_current_pdf)
    self.set_button_icon(self.open_pdf_button, 'preview.svg')
    self.open_pdf_button.setEnabled(False)
    self.open_pdf_button.setVisible(False)

    self.status_label = QLabel('Listo.')
    self.status_label.setMinimumWidth(0)
    self.status_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    self.status_label.setWordWrap(True)

    self.editor = QPlainTextEdit()
    self.editor.setPlaceholderText('El contenido del Markdown aparecerá aquí.')
    self.editor.setMinimumWidth(0)
    self.editor.setVisible(False)
    self.editor.textChanged.connect(self.mark_editor_dirty)

    self.font_combo = QComboBox()
    self.font_combo.addItems([
      'Arial',
      'Aptos',
      'Calibri',
      'Comic Sans MS',
      'Inter',
      'Latin Modern Roman',
      'Lexend',
      'OpenDyslexic',
      'Segoe UI',
      'Tahoma',
      'Times New Roman',
      'Verdana',
    ])
    self.font_combo.setCurrentText('Arial')

    self.body_size_input = DesignDoubleSpinBox()
    self.body_size_input.setRange(6, 48)
    self.body_size_input.setSingleStep(0.5)
    self.body_size_input.setDecimals(1)
    self.body_size_input.setSuffix(' pt')
    self.body_size_input.setValue(10.5)

    self.paragraph_leading_input = DesignDoubleSpinBox()
    self.paragraph_leading_input.setRange(0.35, 2.5)
    self.paragraph_leading_input.setSingleStep(0.05)
    self.paragraph_leading_input.setDecimals(2)
    self.paragraph_leading_input.setValue(0.62)

    self.paragraph_spacing_input = DesignDoubleSpinBox()
    self.paragraph_spacing_input.setRange(0, 3.0)
    self.paragraph_spacing_input.setSingleStep(0.05)
    self.paragraph_spacing_input.setDecimals(2)
    self.paragraph_spacing_input.setValue(0.82)
    self.paragraph_leading_input.valueChanged.connect(self.ensure_paragraph_spacing_minimum)
    self.paragraph_spacing_input.valueChanged.connect(self.ensure_paragraph_spacing_minimum)

    self.margin_x_input = DesignDoubleSpinBox()
    self.margin_x_input.setRange(0.3, 7)
    self.margin_x_input.setSingleStep(0.1)
    self.margin_x_input.setDecimals(1)
    self.margin_x_input.setSuffix(' cm')
    self.margin_x_input.setValue(2.2)

    self.margin_y_input = DesignDoubleSpinBox()
    self.margin_y_input.setRange(0.3, 7)
    self.margin_y_input.setSingleStep(0.1)
    self.margin_y_input.setDecimals(1)
    self.margin_y_input.setSuffix(' cm')
    self.margin_y_input.setValue(2.0)

    self.h1_size_input = DesignDoubleSpinBox()
    self.h1_size_input.setRange(6, 48)
    self.h1_size_input.setSingleStep(0.5)
    self.h1_size_input.setDecimals(1)
    self.h1_size_input.setSuffix(' pt')
    self.h1_size_input.setValue(24)

    self.h2_size_input = DesignDoubleSpinBox()
    self.h2_size_input.setRange(6, 48)
    self.h2_size_input.setSingleStep(0.5)
    self.h2_size_input.setDecimals(1)
    self.h2_size_input.setSuffix(' pt')
    self.h2_size_input.setValue(16)

    self.h3_size_input = DesignDoubleSpinBox()
    self.h3_size_input.setRange(6, 48)
    self.h3_size_input.setSingleStep(0.5)
    self.h3_size_input.setDecimals(1)
    self.h3_size_input.setSuffix(' pt')
    self.h3_size_input.setValue(12.5)

    self.h1_color_button = self.create_color_button('h1')
    self.h2_color_button = self.create_color_button('h2')
    self.h3_color_button = self.create_color_button('h3')
    self.bold_color_button = self.create_color_button('bold')
    self.italic_color_button = self.create_color_button('italic')
    self.body_color_button = self.create_color_button('body')
    self.page_background_color_button = self.create_color_button('page_background')
    self.code_background_color_button = self.create_color_button('code_background')
    self.table_stroke_color_button = self.create_color_button('table_stroke')
    self.table_text_color_button = self.create_color_button('table_text')
    self.table_header_background_color_button = self.create_color_button(
      'table_header_background'
    )
    self.table_header_text_color_button = self.create_color_button('table_header_text')
    self.quote_border_color_button = self.create_color_button('quote_border')
    self.quote_background_color_button = self.create_color_button('quote_background')
    self.quote_text_color_button = self.create_color_button('quote_text')

    self.code_font_combo = QComboBox()
    self.code_font_combo.addItems(['Consolas', 'Cascadia Mono', 'Courier New', 'JetBrains Mono'])
    self.code_font_combo.setCurrentText('Consolas')

    self.code_size_input = DesignDoubleSpinBox()
    self.code_size_input.setRange(6, 48)
    self.code_size_input.setSingleStep(0.5)
    self.code_size_input.setDecimals(1)
    self.code_size_input.setSuffix(' pt')
    self.code_size_input.setValue(9)

    self.table_inset_input = DesignDoubleSpinBox()
    self.table_inset_input.setRange(2, 18)
    self.table_inset_input.setSingleStep(0.5)
    self.table_inset_input.setDecimals(1)
    self.table_inset_input.setSuffix(' pt')
    self.table_inset_input.setValue(7)

    self.table_text_size_input = DesignDoubleSpinBox()
    self.table_text_size_input.setRange(6, 48)
    self.table_text_size_input.setSingleStep(0.5)
    self.table_text_size_input.setDecimals(1)
    self.table_text_size_input.setSuffix(' pt')
    self.table_text_size_input.setValue(10)

    self.table_width_mode_combo = QComboBox()
    self.table_width_mode_combo.addItem('Ajustar al contenido', 'auto')
    self.table_width_mode_combo.addItem('Usar ancho disponible', 'full')

    self.quote_inset_input = DesignDoubleSpinBox()
    self.quote_inset_input.setRange(0.2, 2.5)
    self.quote_inset_input.setSingleStep(0.05)
    self.quote_inset_input.setDecimals(2)
    self.quote_inset_input.setSuffix(' em')
    self.quote_inset_input.setValue(0.85)

    self.quote_text_size_input = DesignDoubleSpinBox()
    self.quote_text_size_input.setRange(6, 48)
    self.quote_text_size_input.setSingleStep(0.5)
    self.quote_text_size_input.setDecimals(1)
    self.quote_text_size_input.setSuffix(' pt')
    self.quote_text_size_input.setValue(10.5)

    self.create_template_button = QPushButton('Crear nueva plantilla')
    self.create_template_button.clicked.connect(self.create_custom_template)
    self.set_button_icon(self.create_template_button, 'template-new.svg')
    self.create_template_button.setSizePolicy(
      QSizePolicy.Policy.Expanding,
      QSizePolicy.Policy.Fixed,
    )
    self.update_template_button = QPushButton('Guardar cambios')
    self.update_template_button.clicked.connect(self.update_custom_template)
    self.set_button_icon(self.update_template_button, 'template-save.svg')
    self.update_template_button.setSizePolicy(
      QSizePolicy.Policy.Expanding,
      QSizePolicy.Policy.Fixed,
    )
    self.template_actions = QWidget()
    template_actions_layout = QHBoxLayout(self.template_actions)
    template_actions_layout.setContentsMargins(0, 0, 0, 0)
    template_actions_layout.addWidget(self.create_template_button)
    template_actions_layout.addWidget(self.update_template_button)

    self.template_combo = QComboBox()
    for template_id in self.template_ids:
      self.template_combo.addItem(
        self.display_template_label(template_id),
        template_id,
      )
    self.template_combo.setCurrentIndex(
      max(0, self.template_combo.findData(DEFAULT_TEMPLATE_ID))
    )
    self.template_combo.currentIndexChanged.connect(self.handle_template_changed)
    self.connect_design_change_signals()

    self.pdf_document = QPdfDocument(self)
    self.pdf_view = QPdfView()
    self.pdf_view.setDocument(self.pdf_document)
    self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
    self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

    self.pdf_panel = QWidget()
    pdf_panel_layout = QVBoxLayout(self.pdf_panel)
    pdf_panel_layout.setContentsMargins(0, 0, 0, 0)
    preview_label = QLabel('Vista previa del PDF')
    preview_label.setObjectName('previewTitle')
    self.empty_preview_label = QLabel(
      'Empieza abriendo o arrastrando un Markdown.\n\n'
      '1. Revisa o edita el contenido en Markdown.\n'
      '2. Elige una plantilla y ajusta el estilo en Diseño.\n'
      '3. Pulsa Generar PDF para ver aquí el resultado real.'
    )
    self.empty_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.empty_preview_label.setWordWrap(True)
    self.empty_preview_label.setObjectName('emptyPreview')
    pdf_panel_layout.addWidget(preview_label)
    pdf_panel_layout.addWidget(self.empty_preview_label, 1)
    pdf_panel_layout.addWidget(self.pdf_view, 1)
    self.pdf_view.setVisible(False)
    self.help_preview_scroll = QScrollArea()
    self.help_preview_scroll.setWidget(self.create_help_content())
    self.help_preview_scroll.setWidgetResizable(True)
    self.help_preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.help_preview_scroll.setFrameShape(QFrame.Shape.NoFrame)
    pdf_panel_layout.addWidget(self.help_preview_scroll, 1)
    self.help_preview_scroll.setVisible(False)

    self.drop_zone = DropZone()
    self.drop_zone.setMinimumWidth(0)
    self.drop_zone.file_dropped.connect(self.set_markdown_file)

    self.file_tab_button = self.create_nav_button('Markdown', 0)
    self.design_tab_button = self.create_nav_button('Diseño', 1)
    self.set_button_icon(self.file_tab_button, 'code.svg')
    self.set_button_icon(self.design_tab_button, 'settings.svg')
    self.help_tab_button = QPushButton('Ayuda')
    self.help_tab_button.setObjectName('navButton')
    self.set_button_icon(self.help_tab_button, 'help.svg')
    self.help_tab_button.clicked.connect(self.toggle_help_preview)

    nav_row = QHBoxLayout()
    nav_row.addWidget(self.file_tab_button)
    nav_row.addWidget(self.design_tab_button)
    nav_row.addWidget(self.help_tab_button)
    nav_row.addStretch()

    file_row = QHBoxLayout()
    file_row.addWidget(self.file_input, 1)
    file_row.addWidget(open_button)
    file_row.addWidget(new_button)

    file_page = QWidget()
    file_layout = QVBoxLayout(file_page)
    file_layout.setContentsMargins(0, 0, 0, 0)
    file_layout.addLayout(file_row)
    file_layout.addWidget(self.drop_zone)
    file_layout.addWidget(self.editor, 1)

    design_page = QWidget()
    design_layout = QVBoxLayout(design_page)
    design_layout.setContentsMargins(0, 0, 0, 0)
    design_title = QLabel('Ajustes de diseño')
    design_title.setObjectName('sectionTitle')
    design_help = QLabel(
      'Modifica la fuente, el tamaño base y los colores. Luego vuelve a generar el PDF.'
    )
    design_help.setObjectName('sectionHelp')
    design_help.setWordWrap(True)
    style_panel = QFrame()
    style_panel.setObjectName('stylePanel')
    style_panel.setMinimumWidth(0)
    style_panel.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    style_panel_layout = QVBoxLayout(style_panel)
    style_panel_layout.setContentsMargins(10, 10, 10, 10)
    style_panel_layout.setSpacing(8)
    self.template_status_label = QLabel()
    self.template_status_label.setObjectName('sectionHelp')
    self.template_status_label.setWordWrap(True)
    style_panel_layout.addLayout(self.create_template_group())
    style_panel_layout.addLayout(
      self.create_design_group(
        'Página',
        [
          [
            ('Margen lateral', self.margin_x_input),
            ('Margen vertical', self.margin_y_input),
          ],
          [('Fondo página', self.page_background_color_button)],
        ],
      )
    )
    style_panel_layout.addLayout(
      self.create_design_group(
        'Texto',
        [
          [('Fuente', self.font_combo)],
          [
            ('Tamaño texto', self.body_size_input),
            ('Color texto', self.body_color_button),
          ],
          [
            ('Interlineado', self.paragraph_leading_input),
            ('Espacio párrafos', self.paragraph_spacing_input),
          ],
          [
            ('Tamaño título 1', self.h1_size_input),
            ('Título 1', self.h1_color_button),
          ],
          [
            ('Tamaño título 2', self.h2_size_input),
            ('Título 2', self.h2_color_button),
          ],
          [
            ('Tamaño título 3', self.h3_size_input),
            ('Título 3', self.h3_color_button),
          ],
          [
            ('Negrita', self.bold_color_button),
            ('Cursiva', self.italic_color_button),
          ],
        ],
      )
    )
    style_panel_layout.addLayout(
      self.create_design_group(
        'Código',
        [
          [('Fuente código', self.code_font_combo)],
          [
            ('Tamaño código', self.code_size_input),
            ('Fondo código', self.code_background_color_button),
          ],
        ],
      )
    )
    style_panel_layout.addLayout(
      self.create_design_group(
        'Bloques',
        [
          [
            ('Espacio interno', self.quote_inset_input),
            ('Tamaño texto', self.quote_text_size_input),
          ],
          [
            ('Color texto', self.quote_text_color_button),
            ('Borde', self.quote_border_color_button),
          ],
          [('Fondo', self.quote_background_color_button)],
        ],
      )
    )
    style_panel_layout.addLayout(
      self.create_design_group(
        'Tablas',
        [
          [
            ('Espacio celdas', self.table_inset_input),
            ('Ancho tabla', self.table_width_mode_combo),
          ],
          [
            ('Tamaño texto', self.table_text_size_input),
            ('Color texto', self.table_text_color_button),
          ],
          [
            ('Bordes', self.table_stroke_color_button),
            ('Fondo cabecera', self.table_header_background_color_button),
          ],
          [('Texto cabecera', self.table_header_text_color_button)],
        ],
      )
    )
    design_layout.addWidget(design_title)
    design_layout.addWidget(design_help)
    design_layout.addWidget(style_panel)
    design_layout.addStretch()

    self.design_scroll = QScrollArea()
    self.design_scroll.setWidget(design_page)
    self.design_scroll.setWidgetResizable(True)
    self.design_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.design_scroll.setFrameShape(QFrame.Shape.NoFrame)

    self.left_stack = QStackedWidget()
    self.left_stack.addWidget(file_page)
    self.left_stack.addWidget(self.design_scroll)

    editor_actions_row = QHBoxLayout()
    self.editor_actions_row = editor_actions_row
    editor_actions_row.addWidget(self.edit_button)
    editor_actions_row.addWidget(self.save_button)
    editor_actions_row.addWidget(self.save_as_button)
    editor_actions_row.addStretch()

    pdf_actions_row = QHBoxLayout()
    pdf_actions_row.addWidget(self.open_pdf_button)
    pdf_actions_row.addWidget(self.build_button)
    pdf_actions_row.addStretch()

    self.left_panel = QWidget()
    left_layout = QVBoxLayout(self.left_panel)
    left_layout.setContentsMargins(16, 16, 16, 16)
    left_layout.addLayout(nav_row)
    left_layout.addWidget(self.left_stack, 1)
    left_layout.addLayout(editor_actions_row)
    left_layout.addLayout(pdf_actions_row)
    left_layout.addWidget(self.status_label)

    self.splitter = QSplitter(Qt.Orientation.Horizontal)
    self.splitter.addWidget(self.left_panel)
    self.splitter.addWidget(self.pdf_panel)
    self.pdf_panel.setMinimumWidth(PREVIEW_PANEL_MIN_WIDTH)
    self.splitter.setStretchFactor(0, 0)
    self.splitter.setStretchFactor(1, 1)
    self.splitter.setCollapsible(0, False)
    self.splitter.setCollapsible(1, False)
    self.set_initial_splitter_sizes()

    container = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(self.splitter, 1)
    container.setLayout(layout)
    self.setCentralWidget(container)
    self.apply_styles()
    self.update_left_panel_min_width()

    self.restore_window_settings()
    if initial_file:
      self.set_markdown_file(initial_file)
    self.select_left_section(0)
    self.restore_design_settings()

  def apply_styles(self) -> None:
    '''Aplica estilos visuales de la interfaz, no del PDF generado.'''

    self.setStyleSheet(
      '''
      QWidget {
        font-family: Segoe UI;
        font-size: 10.5pt;
        color: #131b2e;
        background: #faf8ff;
      }
      QLineEdit {
        padding: 8px;
        border: 1px solid #c3c6d7;
        border-radius: 4px;
        background: #ffffff;
      }
      QComboBox {
        padding: 6px;
        border: 1px solid #c3c6d7;
        border-radius: 4px;
        background: #ffffff;
      }
      QComboBox QAbstractItemView {
        border: 1px solid #b4c5ff;
        selection-background-color: #dbe1ff;
        selection-color: #00174b;
        outline: 0;
      }
      QComboBox QAbstractItemView::item {
        min-height: 26px;
        padding: 5px 8px;
      }
      QComboBox QAbstractItemView::item:hover {
        color: #00174b;
        background: #edf1ff;
      }
      QComboBox QAbstractItemView::item:selected {
        color: #00174b;
        background: #dbe1ff;
      }
      QPlainTextEdit {
        font-family: Consolas;
        font-size: 10pt;
        padding: 8px;
        border: 1px solid #c3c6d7;
        border-radius: 6px;
        background: #ffffff;
      }
      QPushButton {
        padding: 8px 14px;
        border: 1px solid #c3c6d7;
        border-radius: 4px;
        background: #ffffff;
      }
      QPushButton:hover {
        background: #f2f3ff;
      }
      QPushButton#primaryButton {
        color: #ffffff;
        background: #004ac6;
        border-color: #004ac6;
      }
      QPushButton#primaryButton:hover {
        background: #003ea8;
      }
      QPushButton#navButton {
        text-align: left;
        font-weight: 600;
        border: 1px solid transparent;
        background: transparent;
      }
      QPushButton#navButton[active='true'] {
        color: #00174b;
        background: #dbe1ff;
        border-color: #b4c5ff;
      }
      #stylePanel {
        border: 1px solid #d7dde3;
        border-radius: 6px;
        background: #ffffff;
        padding: 8px;
      }
      #stylePanel QLabel {
        font-size: 9.5pt;
      }
      #stylePanel QComboBox,
      #stylePanel QPushButton {
        font-size: 9.5pt;
        padding: 5px 8px;
      }
      #stylePanel QDoubleSpinBox {
        font-size: 9.5pt;
        min-height: 26px;
      }
      #designGroupTitle {
        font-size: 10pt;
        font-weight: 700;
        color: #26364a;
        padding-top: 4px;
      }
      #dropZone {
        border: 1px dashed #7a8a99;
        border-radius: 6px;
        background: #ffffff;
      }
      #dropTitle {
        font-size: 13pt;
        font-weight: 600;
        color: #26364a;
      }
      #dropSubtitle {
        color: #66717d;
      }
      #previewTitle {
        font-size: 11pt;
        font-weight: 600;
        color: #26364a;
      }
      #emptyPreview {
        color: #737686;
        border: 1px dashed #c3c6d7;
        border-radius: 6px;
        background: #ffffff;
        padding: 24px;
      }
      #appTitle {
        font-size: 18pt;
        font-weight: 700;
        color: #004ac6;
      }
      #appSubtitle {
        color: #434655;
      }
      #sectionTitle {
        font-size: 16pt;
        font-weight: 700;
      }
      #sectionHelp {
        color: #434655;
      }
      #helpCard {
        border: 1px solid #d7dde3;
        border-radius: 6px;
        background: #ffffff;
        padding: 10px;
      }
      #helpCardTitle {
        font-size: 10.5pt;
        font-weight: 700;
        color: #26364a;
      }
      #helpCardText {
        color: #434655;
      }
      #placeholderCard {
        border: 1px solid #d7dde3;
        border-radius: 6px;
        background: #ffffff;
        padding: 12px;
      }
      '''
    )
    self.build_button.setObjectName('primaryButton')
    self.refresh_color_buttons()

  def create_nav_button(self, text: str, index: int) -> QPushButton:
    '''Crea un boton de navegacion para cambiar el panel izquierdo.'''

    button = QPushButton(text)
    button.setObjectName('navButton')
    button.clicked.connect(lambda: self.select_left_section(index))
    return button

  def set_button_icon(self, button: QPushButton, icon_name: str) -> None:
    '''Asigna un icono SVG si existe en assets/icons.'''

    icon_file = ICON_DIR / icon_name
    if not icon_file.exists():
      return

    button.setIcon(QIcon(str(icon_file)))
    button.setIconSize(QSize(18, 18))

  def create_design_label(self, text: str) -> QWidget:
    '''Crea una etiqueta compacta con icono para el panel de diseño.'''

    label_container = QWidget()
    label_layout = QHBoxLayout(label_container)
    label_layout.setContentsMargins(0, 0, 0, 0)
    label_layout.setSpacing(5)
    label_layout.addStretch(1)

    icon_name = DESIGN_LABEL_ICONS.get(text)
    if icon_name:
      icon_file = ICON_DIR / icon_name
      if icon_file.exists():
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(str(icon_file)).pixmap(QSize(16, 16)))
        icon_label.setFixedSize(16, 16)
        label_layout.addWidget(icon_label)

    text_label = QLabel(text)
    text_label.setObjectName('designOptionLabel')
    text_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    label_layout.addWidget(text_label)
    return label_container

  def select_left_section(self, index: int) -> None:
    '''Muestra una de las secciones principales del panel izquierdo.'''

    self.active_left_section = index
    self.left_stack.setCurrentIndex(index)
    buttons = [
      self.file_tab_button,
      self.design_tab_button,
    ]
    for button_index, button in enumerate(buttons):
      button.setProperty('active', button_index == index)
      button.style().unpolish(button)
      button.style().polish(button)
    self.update_action_visibility()

  def markdown_is_open(self) -> bool:
    '''Indica si hay un Markdown abierto o nuevo en edición.'''

    return self.markdown_open

  def update_action_visibility(self) -> None:
    '''Actualiza botones inferiores segun la seccion activa.'''

    has_markdown = self.markdown_is_open()
    in_markdown = self.active_left_section == 0
    in_design = self.active_left_section == 1

    self.edit_button.setVisible(in_markdown and has_markdown)
    self.edit_button.setEnabled(in_markdown and has_markdown)
    self.save_button.setVisible(in_markdown and has_markdown)
    self.save_button.setEnabled(in_markdown and has_markdown and self.editor_dirty)
    self.save_as_button.setVisible(in_markdown and has_markdown)
    self.save_as_button.setEnabled(in_markdown and has_markdown)

    self.open_pdf_button.setVisible(in_markdown and self.current_pdf is not None)
    self.open_pdf_button.setEnabled(in_markdown and self.current_pdf is not None)
    self.build_button.setVisible((in_markdown and has_markdown) or in_design)
    self.build_button.setEnabled((in_markdown and has_markdown) or in_design)

  def show_document_preview(self) -> None:
    '''Restaura el visor de PDF o la guia inicial.'''

    self.help_preview_scroll.setVisible(False)
    self.help_tab_button.setProperty('active', False)
    self.help_tab_button.style().unpolish(self.help_tab_button)
    self.help_tab_button.style().polish(self.help_tab_button)
    has_preview = self.current_pdf is not None and self.pdf_document.pageCount() > 0
    self.pdf_view.setVisible(has_preview)
    self.empty_preview_label.setVisible(not has_preview)

  def refresh_document_preview_if_visible(self) -> None:
    '''Actualiza el visor documental sin cerrar la ayuda activa.'''

    if not self.help_preview_scroll.isVisible():
      self.show_document_preview()

  def toggle_help_preview(self) -> None:
    '''Alterna entre la ayuda y el visor documental disponible.'''

    if self.help_preview_scroll.isVisible():
      self.show_document_preview()
      return
    self.show_help_preview()

  def show_help_preview(self) -> None:
    '''Muestra la ayuda en el area amplia de vista previa.'''

    self.pdf_view.setVisible(False)
    self.empty_preview_label.setVisible(False)
    self.help_preview_scroll.setVisible(True)
    self.help_tab_button.setProperty('active', True)
    self.help_tab_button.style().unpolish(self.help_tab_button)
    self.help_tab_button.style().polish(self.help_tab_button)

  def create_help_content(self) -> QWidget:
    '''Crea el contenido de ayuda que se muestra en el visor.'''

    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(12)

    title = QLabel('Cómo usar Markdown PDF Designer')
    title.setObjectName('sectionTitle')
    title.setWordWrap(True)
    intro = QLabel(
      'La app convierte Markdown en PDF separando contenido y presentación. '
      'El Markdown describe la estructura; las plantillas y los controles de '
      'Diseño deciden cómo se verá el documento final. Pulsa Ayuda otra vez '
      'para volver a la vista previa del PDF o a la guía inicial.'
    )
    intro.setObjectName('sectionHelp')
    intro.setWordWrap(True)

    layout.addWidget(title)
    layout.addWidget(intro)
    layout.addWidget(
      self.create_help_card(
        'Guía rápida',
        [
          'Abre, crea o arrastra un archivo Markdown.',
          'Revisa el texto en Markdown y guarda los cambios si los haces.',
          'Elige una plantilla en Diseño y ajusta solo lo que necesites.',
          'Pulsa Generar PDF para ver el resultado real en el visor.',
          'Pulsa Ayuda de nuevo para volver al PDF sin regenerarlo.',
        ],
      )
    )
    layout.addWidget(
      self.create_help_card(
        'Markdown: botones y flujo',
        [
          'Nuevo abre un Markdown vacío sin elegir ubicación todavía.',
          'Abrir permite seleccionar un archivo .md o .markdown desde Windows.',
          'La caja de ruta permite escribir una ruta o elegir documentos recientes.',
          'Cerrar cierra el Markdown actual y vuelve al estado inicial de la app.',
          'Guardar escribe los cambios del editor en el archivo abierto.',
          'Guardar como crea una copia en otra ruta y cambia a ese nuevo archivo.',
          'Generar PDF convierte el Markdown actual usando la plantilla elegida.',
          'Abrir PDF en Windows abre el último PDF generado con el visor del sistema.',
          'La zona de arrastre acepta archivos Markdown soltados desde el explorador.',
        ],
      )
    )
    layout.addWidget(
      self.create_help_card(
        'Markdown: escritura recomendada',
        [
          'Usa # para el título principal, ## para secciones y ### para subsecciones.',
          'Usa listas, tablas, citas y bloques de código estándar de Markdown.',
          'Usa negrita y cursiva para énfasis semántico, no para maquetar a mano.',
          'Evita simular diseño con espacios, saltos vacíos o símbolos decorativos.',
          'Mantén el contenido limpio: el aspecto final se controla desde Diseño.',
        ],
      )
    )
    layout.addWidget(
      self.create_help_card(
        'Diseño: flujo para crear una plantilla',
        [
          'Selecciona una plantilla base parecida al resultado que quieres.',
          'Ajusta fuente, tamaños, colores, márgenes, bloques, tablas y código.',
          'Genera un PDF de prueba para revisar el resultado real.',
          'Cuando el diseño te guste, pulsa Crear nueva plantilla.',
          'Escribe un nombre claro para reconocerla después.',
          'Las plantillas personalizadas se guardan en tus datos de usuario.',
          'Si estás usando una plantilla personalizada, Guardar cambios actualiza esa plantilla.',
          'Las plantillas predefinidas no se sobrescriben desde la app.',
        ],
      )
    )
    layout.addWidget(
      self.create_help_card(
        'Diseño: secciones modificables',
        [
          'Plantilla visual define el punto de partida del documento.',
          'Página controla los márgenes laterales, márgenes verticales y color de fondo del PDF.',
          'Texto controla fuente principal, tamaño, color, interlineado, espacio entre párrafos, títulos y énfasis.',
          'Código controla fuente, tamaño y fondo de los bloques de código.',
          'Bloques controla citas o bloques destacados: espacio interno, texto, borde y fondo.',
          'Tablas controla ancho, espacio de celdas, texto, bordes y colores de cabecera.',
        ],
      )
    )
    layout.addWidget(
      self.create_help_card(
        'Diseño: botones',
        [
          'Crear nueva plantilla guarda los ajustes actuales como una plantilla personalizada.',
          'Guardar cambios aparece con plantillas personalizadas y sobrescribe sus ajustes.',
          'Los botones de color abren el selector para cambiar el color asociado.',
          'Los controles numéricos se modifican con teclado o flechas, no con la rueda del ratón.',
          'Después de cualquier cambio de diseño, vuelve a pulsar Generar PDF para ver el resultado.',
        ],
      )
    )
    layout.addStretch()
    return content

  def create_help_card(self, title: str, items: list[str]) -> QFrame:
    '''Crea un bloque compacto de instrucciones para la seccion de ayuda.'''

    card = QFrame()
    card.setObjectName('helpCard')
    card.setMinimumWidth(0)
    card.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(6)

    title_label = QLabel(title)
    title_label.setObjectName('helpCardTitle')
    title_label.setWordWrap(True)

    text_label = QLabel('\n'.join(f'- {item}' for item in items))
    text_label.setObjectName('helpCardText')
    text_label.setWordWrap(True)
    text_label.setMinimumWidth(0)
    text_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    layout.addWidget(title_label)
    layout.addWidget(text_label)
    return card

  def create_template_group(self) -> QVBoxLayout:
    '''Crea la sección de selección y acciones de plantilla.'''

    group_layout = QVBoxLayout()
    group_layout.setContentsMargins(0, 0, 0, 0)
    group_layout.setSpacing(5)

    group_title = QLabel('Plantilla visual')
    group_title.setObjectName('designGroupTitle')
    group_layout.addWidget(group_title)

    template_row = QHBoxLayout()
    template_row.setContentsMargins(0, 0, 0, 0)
    template_row.setSpacing(8)
    template_label_widget = self.create_design_label('Plantilla')
    template_row.addWidget(template_label_widget)
    template_row.addWidget(self.template_combo, 1)

    group_layout.addLayout(template_row)
    group_layout.addWidget(self.template_status_label)
    group_layout.addWidget(self.template_actions)
    return group_layout

  def create_design_group(
    self,
    title: str,
    rows: list[list[tuple[str, QWidget]]],
  ) -> QVBoxLayout:
    '''Crea una sección compacta para opciones de diseño relacionadas.'''

    group_layout = QVBoxLayout()
    group_layout.setContentsMargins(0, 0, 0, 0)
    group_layout.setSpacing(4)

    group_title = QLabel(title)
    group_title.setObjectName('designGroupTitle')
    group_layout.addWidget(group_title)

    for row in rows:
      row_layout = QHBoxLayout()
      row_layout.setContentsMargins(0, 0, 0, 0)
      row_layout.setSpacing(8)
      for label, widget in row:
        row_layout.addWidget(self.create_design_parameter(label, widget), 1)
      group_layout.addLayout(row_layout)

    return group_layout

  def create_design_parameter(self, label: str, widget: QWidget) -> QWidget:
    '''Crea un parametro de diseño con icono y tooltip, sin texto visible.'''

    parameter = QWidget()
    parameter_layout = QHBoxLayout(parameter)
    parameter_layout.setContentsMargins(0, 0, 0, 0)
    parameter_layout.setSpacing(5)

    icon_label = QLabel()
    icon_label.setFixedSize(18, 18)
    icon_label.setToolTip(label)
    icon_name = DESIGN_LABEL_ICONS.get(label)
    if icon_name:
      icon_file = ICON_DIR / icon_name
      if icon_file.exists():
        icon_label.setPixmap(QIcon(str(icon_file)).pixmap(QSize(18, 18)))

    widget.setToolTip(label)
    parameter_layout.addWidget(icon_label)
    parameter_layout.addWidget(widget, 1)
    return parameter

  def create_color_button(self, color_key: str) -> QPushButton:
    '''Crea un boton que abre el selector para un color del PDF.'''

    button = QPushButton()
    button.setMinimumWidth(42)
    button.clicked.connect(lambda: self.choose_heading_color(color_key))
    return button

  def choose_heading_color(self, color_key: str) -> None:
    '''Permite escoger un color del PDF con el diálogo nativo de Qt.'''

    current = QColor(self.heading_colors[color_key])
    color = QColorDialog.getColor(current, self, 'Elegir color')
    if not color.isValid():
      return

    self.heading_colors[color_key] = color.name()
    self.refresh_color_buttons()
    self.mark_template_dirty()

  def refresh_color_buttons(self) -> None:
    '''Actualiza las muestras de color de los botones.'''

    buttons = {
      'h1': self.h1_color_button,
      'h2': self.h2_color_button,
      'h3': self.h3_color_button,
      'bold': self.bold_color_button,
      'italic': self.italic_color_button,
      'body': self.body_color_button,
      'page_background': self.page_background_color_button,
      'code_background': self.code_background_color_button,
      'table_stroke': self.table_stroke_color_button,
      'table_text': self.table_text_color_button,
      'table_header_background': self.table_header_background_color_button,
      'table_header_text': self.table_header_text_color_button,
      'quote_border': self.quote_border_color_button,
      'quote_background': self.quote_background_color_button,
      'quote_text': self.quote_text_color_button,
    }
    for color_key, button in buttons.items():
      color = self.heading_colors[color_key]
      label = COLOR_BUTTON_LABELS.get(color_key, 'Color')
      button.setText('')
      button.setToolTip(f'{label}: {color}')
      button.setStyleSheet(
        f'background: {color}; border: 1px solid #7f8794;'
      )

  def apply_style_options(self, style: PdfStyleOptions) -> None:
    '''Carga un conjunto de opciones visuales en los controles de Diseño.'''

    self.loading_style_options = True
    controlled_widgets = [
      self.font_combo,
      self.body_size_input,
      self.paragraph_leading_input,
      self.paragraph_spacing_input,
      self.margin_x_input,
      self.margin_y_input,
      self.h1_size_input,
      self.h2_size_input,
      self.h3_size_input,
      self.code_font_combo,
      self.code_size_input,
      self.table_inset_input,
      self.table_text_size_input,
      self.table_width_mode_combo,
      self.quote_inset_input,
      self.quote_text_size_input,
    ]
    for widget in controlled_widgets:
      widget.blockSignals(True)

    self.font_combo.setCurrentText(style.font_family)
    self.body_size_input.setValue(style.body_font_size)
    self.paragraph_leading_input.setValue(style.paragraph_leading)
    self.paragraph_spacing_input.setValue(style.paragraph_spacing)
    self.margin_x_input.setValue(style.page_margin_x / 10)
    self.margin_y_input.setValue(style.page_margin_y / 10)
    self.h1_size_input.setValue(style.heading_1_size)
    self.h2_size_input.setValue(style.heading_2_size)
    self.h3_size_input.setValue(style.heading_3_size)
    self.code_font_combo.setCurrentText(style.code_font_family)
    self.code_size_input.setValue(style.code_font_size)
    self.table_inset_input.setValue(style.table_inset)
    self.table_text_size_input.setValue(style.table_text_size)
    width_mode_index = self.table_width_mode_combo.findData(style.table_width_mode)
    self.table_width_mode_combo.setCurrentIndex(max(0, width_mode_index))
    self.quote_inset_input.setValue(style.quote_inset)
    self.quote_text_size_input.setValue(style.quote_text_size)

    for widget in controlled_widgets:
      widget.blockSignals(False)

    self.ensure_paragraph_spacing_minimum()
    self.heading_colors.update(
      {
        'body': style.body_color,
        'page_background': style.page_background_color,
        'h1': style.heading_1_color,
        'h2': style.heading_2_color,
        'h3': style.heading_3_color,
        'bold': style.bold_color,
        'italic': style.italic_color,
        'code_background': style.code_background_color,
        'table_stroke': style.table_stroke_color,
        'table_text': style.table_text_color,
        'table_header_background': style.table_header_background_color,
        'table_header_text': style.table_header_text_color,
        'quote_border': style.quote_border_color,
        'quote_background': style.quote_background_color,
        'quote_text': style.quote_text_color,
      }
    )
    self.refresh_color_buttons()
    self.loading_style_options = False

  def connect_design_change_signals(self) -> None:
    '''Conecta controles de Diseño al estado de plantilla modificada.'''

    for combo in (self.font_combo, self.code_font_combo, self.table_width_mode_combo):
      combo.currentTextChanged.connect(self.mark_template_dirty)

    for spin_box in (
      self.body_size_input,
      self.paragraph_leading_input,
      self.paragraph_spacing_input,
      self.margin_x_input,
      self.margin_y_input,
      self.h1_size_input,
      self.h2_size_input,
      self.h3_size_input,
      self.code_size_input,
      self.table_inset_input,
      self.table_text_size_input,
      self.quote_inset_input,
      self.quote_text_size_input,
    ):
      spin_box.valueChanged.connect(self.mark_template_dirty)

  def mark_template_dirty(self, *_args: object) -> None:
    '''Marca cambios pendientes solo en plantillas personalizadas.'''

    if self.loading_style_options:
      return
    if not is_custom_template(self.current_template_id()):
      return

    self.custom_template_dirty = True
    self.update_template_status()
    self.update_template_button.setEnabled(True)

  def current_style_options(self) -> PdfStyleOptions:
    '''Construye las opciones visuales actuales para el generador de PDF.'''

    paragraph_leading = self.paragraph_leading_input.value()
    paragraph_spacing = max(self.paragraph_spacing_input.value(), paragraph_leading)
    return PdfStyleOptions(
      font_family=self.font_combo.currentText(),
      body_font_size=self.body_size_input.value(),
      body_color=self.heading_colors['body'],
      page_background_color=self.heading_colors['page_background'],
      paragraph_leading=paragraph_leading,
      paragraph_spacing=paragraph_spacing,
      page_margin_x=self.margin_x_input.value() * 10,
      page_margin_y=self.margin_y_input.value() * 10,
      heading_1_size=self.h1_size_input.value(),
      heading_2_size=self.h2_size_input.value(),
      heading_3_size=self.h3_size_input.value(),
      heading_1_color=self.heading_colors['h1'],
      heading_2_color=self.heading_colors['h2'],
      heading_3_color=self.heading_colors['h3'],
      bold_color=self.heading_colors['bold'],
      italic_color=self.heading_colors['italic'],
      code_font_family=self.code_font_combo.currentText(),
      code_font_size=self.code_size_input.value(),
      code_background_color=self.heading_colors['code_background'],
      table_inset=self.table_inset_input.value(),
      table_stroke_color=self.heading_colors['table_stroke'],
      table_text_color=self.heading_colors['table_text'],
      table_text_size=self.table_text_size_input.value(),
      table_width_mode=str(self.table_width_mode_combo.currentData() or 'auto'),
      table_header_background_color=self.heading_colors['table_header_background'],
      table_header_text_color=self.heading_colors['table_header_text'],
      quote_inset=self.quote_inset_input.value(),
      quote_border_color=self.heading_colors['quote_border'],
      quote_background_color=self.heading_colors['quote_background'],
      quote_text_color=self.heading_colors['quote_text'],
      quote_text_size=self.quote_text_size_input.value(),
    )

  def ensure_paragraph_spacing_minimum(self) -> None:
    '''Evita que el espacio entre párrafos quede por debajo del interlineado.'''

    paragraph_leading = self.paragraph_leading_input.value()
    if self.paragraph_spacing_input.value() >= paragraph_leading:
      return

    self.paragraph_spacing_input.blockSignals(True)
    self.paragraph_spacing_input.setValue(paragraph_leading)
    self.paragraph_spacing_input.blockSignals(False)

  def current_template_id(self) -> str:
    '''Devuelve la plantilla seleccionada para generar el PDF.'''

    template_id = self.template_combo.currentData()
    if isinstance(template_id, str) and template_id.strip():
      return template_id.strip()
    return DEFAULT_TEMPLATE_ID

  def sorted_template_ids(self, template_ids: list[str]) -> list[str]:
    '''Ordena las plantillas conocidas y deja al final las personalizadas.'''

    known_templates = [
      template_id for template_id in TEMPLATE_ORDER if template_id in template_ids
    ]
    custom_templates = sorted(
      template_id for template_id in template_ids if template_id not in TEMPLATE_ORDER
    )
    return known_templates + custom_templates

  def update_template_status(self) -> None:
    '''Actualiza el texto informativo de la plantilla seleccionada.'''

    template_id = self.current_template_id()
    descriptions = {
      'apa_mla': 'Ensayo universitario con márgenes de 1 pulgada e interlineado doble.',
      'accesibilidad_neurodivergencia': 'Lectura accesible con sans-serif, aire amplio, fondo crema y cursivas convertidas a negrita.',
      'compacto': 'Usa dos columnas y reduce espacios para ahorrar páginas.',
      'estudio': 'Equilibrada para apuntes claros y lectura cómoda.',
      'informe_ejecutivo': 'Corporativa, con títulos destacados y bloques de decisión.',
      'latex_clasico': 'Académica, monocromática, con márgenes amplios y títulos numerados.',
      'manual_tecnico': 'Documentación técnica con código oscuro y bloques destacados.',
      'manuscrito_novela': 'Formato A5 para capítulos, relatos y lectura prolongada.',
      'profesional': 'Más formal, con bloques de título y acentos de informe.',
    }
    description = descriptions.get(template_id)
    if description is None:
      description = template_description(template_id) or 'Plantilla personalizada.'
    if self.custom_template_dirty and is_custom_template(template_id):
      description = f'{description} Cambios sin guardar.'
    self.template_status_label.setText(description)

  def handle_template_changed(self) -> None:
    '''Sincroniza la plantilla seleccionada con su preset visual.'''

    template_id = self.current_template_id()
    previous_template_id = self.selected_template_id
    if (
      template_id != previous_template_id
      and not self.confirm_custom_template_changes(previous_template_id)
    ):
      previous_index = self.template_combo.findData(previous_template_id)
      self.template_combo.blockSignals(True)
      self.template_combo.setCurrentIndex(max(0, previous_index))
      self.template_combo.blockSignals(False)
      self.update_template_status()
      return

    self.selected_template_id = template_id
    self.custom_template_dirty = False
    self.apply_style_options(template_style_preset(template_id))
    self.update_template_status()
    self.update_template_button.setVisible(is_custom_template(template_id))
    self.update_template_button.setEnabled(False)

  def confirm_custom_template_changes(self, template_id: str) -> bool:
    '''Pregunta qué hacer con cambios pendientes de una plantilla personalizada.'''

    if not self.custom_template_dirty or not is_custom_template(template_id):
      return True

    answer = QMessageBox.question(
      self,
      'Cambios en plantilla',
      (
        'La plantilla personalizada tiene cambios sin guardar. '
        '¿Quieres guardarlos antes de continuar?'
      ),
      QMessageBox.StandardButton.Yes
      | QMessageBox.StandardButton.No
      | QMessageBox.StandardButton.Cancel,
      QMessageBox.StandardButton.Yes,
    )
    if answer == QMessageBox.StandardButton.Cancel:
      return False
    if answer == QMessageBox.StandardButton.Yes:
      return self.save_custom_template_changes(template_id)

    self.custom_template_dirty = False
    return True

  def save_custom_template_changes(self, template_id: str) -> bool:
    '''Guarda los ajustes actuales sobre una plantilla personalizada.'''

    if not is_custom_template(template_id):
      return True

    try:
      update_custom_template_style(template_id, self.current_style_options())
    except PdfBuildError as exc:
      QMessageBox.critical(self, 'Error', str(exc))
      return False
    except OSError as exc:
      QMessageBox.critical(self, 'Error', f'No se pudo actualizar la plantilla:\n{exc}')
      return False

    self.custom_template_dirty = False
    self.update_template_status()
    self.update_template_button.setEnabled(False)
    self.status_label.setText(
      f'Cambios guardados en la plantilla: {self.display_template_label(template_id)}'
    )
    return True

  def restore_design_settings(self) -> None:
    '''Restaura la última plantilla usada con sus valores base.'''

    template_id = self.settings.value(
      SELECTED_TEMPLATE_SETTING,
      DEFAULT_TEMPLATE_ID,
      str,
    )
    if not isinstance(template_id, str) or not template_id.strip():
      template_id = DEFAULT_TEMPLATE_ID

    template_index = self.template_combo.findData(template_id)
    self.template_combo.blockSignals(True)
    self.template_combo.setCurrentIndex(max(0, template_index))
    self.template_combo.blockSignals(False)
    self.handle_template_changed()

  def save_design_settings(self) -> None:
    '''Guarda la última plantilla seleccionada.'''

    self.settings.setValue(SELECTED_TEMPLATE_SETTING, self.current_template_id())

  def display_template_label(self, template_id: str) -> str:
    '''Devuelve el texto visible para el selector de plantillas.'''

    return (
      TEMPLATE_LABELS.get(template_id)
      or template_label(template_id)
      or template_id.replace('_', ' ').title()
    )

  def create_custom_template(self) -> None:
    '''Crea una plantilla personalizada desde los ajustes actuales.'''

    label, accepted = QInputDialog.getText(
      self,
      'Crear nueva plantilla',
      'Nombre de la nueva plantilla:',
    )
    label = label.strip()
    if not accepted or not label:
      return

    template_id = self.unique_template_id(label)
    try:
      save_custom_template(
        template_id,
        label,
        self.current_style_options(),
        self.current_template_id(),
      )
    except PdfBuildError as exc:
      QMessageBox.critical(self, 'Error', str(exc))
      return
    except OSError as exc:
      QMessageBox.critical(self, 'Error', f'No se pudo crear la plantilla:\n{exc}')
      return

    self.template_ids = self.sorted_template_ids(available_templates())
    self.template_combo.blockSignals(True)
    self.template_combo.clear()
    for current_template_id in self.template_ids:
      self.template_combo.addItem(
        self.display_template_label(current_template_id),
        current_template_id,
      )
    self.template_combo.setCurrentIndex(self.template_combo.findData(template_id))
    self.template_combo.blockSignals(False)
    self.handle_template_changed()
    self.status_label.setText(f'Plantilla creada: {label}')

  def update_custom_template(self) -> None:
    '''Guarda los cambios actuales en la plantilla personalizada activa.'''

    template_id = self.current_template_id()
    if not is_custom_template(template_id):
      return

    self.save_custom_template_changes(template_id)

  def unique_template_id(self, label: str) -> str:
    '''Genera un identificador de plantilla disponible desde un nombre visible.'''

    normalized = unicodedata.normalize('NFKD', label)
    ascii_label = normalized.encode('ascii', 'ignore').decode('ascii')
    base_id = re.sub(r'[^a-z0-9]+', '_', ascii_label.lower()).strip('_')
    if not base_id:
      base_id = 'plantilla'

    existing_ids = set(available_templates())
    candidate = base_id
    counter = 2
    while candidate in existing_ids:
      candidate = f'{base_id}_{counter}'
      counter += 1
    return candidate

  def load_recent_markdowns(self) -> None:
    '''Carga en el desplegable las últimas rutas Markdown usadas.'''

    recent = self.settings.value('recent_markdowns', [], list)
    recent_paths = [str(path) for path in recent[:10]]
    self.file_input.blockSignals(True)
    self.file_input.clear()
    self.file_input.addItems(recent_paths)
    self.file_input.setCurrentText('')
    self.file_input.blockSignals(False)
    self.update_recent_files_popup_width(recent_paths)

  def update_recent_files_popup_width(self, recent_paths: list[str]) -> None:
    '''Ajusta el ancho del desplegable para leer rutas recientes largas.'''

    if not recent_paths:
      self.file_input.view().setMinimumWidth(RECENT_FILES_POPUP_MIN_WIDTH)
      return

    longest_path = max(recent_paths, key=len)
    measured_width = self.file_input.fontMetrics().horizontalAdvance(longest_path) + 48
    popup_width = min(
      max(measured_width, RECENT_FILES_POPUP_MIN_WIDTH),
      RECENT_FILES_POPUP_MAX_WIDTH,
    )
    self.file_input.view().setMinimumWidth(popup_width)

  def set_initial_splitter_sizes(self) -> None:
    '''Asigna un ancho inicial estable al panel izquierdo.'''

    left_width = self.left_panel.minimumWidth()
    self.splitter.setSizes([left_width, self.width() - left_width])

  def update_left_panel_min_width(self) -> None:
    '''Calcula el mínimo del panel izquierdo desde la fila de botones Markdown.'''

    margins = self.left_panel.layout().contentsMargins()
    spacing = self.editor_actions_row.spacing()
    if spacing < 0:
      spacing = self.style().pixelMetric(QStyle.PixelMetric.PM_LayoutHorizontalSpacing)

    buttons_width = sum(
      button.sizeHint().width()
      for button in (self.edit_button, self.save_button, self.save_as_button)
    )
    scroll_width = self.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent)
    left_width = buttons_width + (spacing * 2) + margins.left() + margins.right() + scroll_width

    self.left_panel.setMinimumWidth(left_width)
    self.setMinimumWidth(left_width + PREVIEW_PANEL_MIN_WIDTH)
    self.set_initial_splitter_sizes()

  def remember_markdown(self, path: Path) -> None:
    '''Guarda una ruta Markdown en el historial de las 10 últimas opciones.'''

    path_text = str(path)
    recent = [str(item) for item in self.settings.value('recent_markdowns', [], list)]
    recent = [item for item in recent if item != path_text]
    recent.insert(0, path_text)
    recent = recent[:10]
    self.settings.setValue('recent_markdowns', recent)
    self.load_recent_markdowns()
    self.file_input.setCurrentText(path_text)

  def open_recent_markdown(self, _index: int | None = None) -> None:
    '''Abre la ruta seleccionada desde el historial del desplegable.'''

    filename = self.file_input.currentText().strip()
    if filename:
      self.set_markdown_file(filename)

  def restore_window_settings(self) -> None:
    '''Restaura posición, monitor y tamaño de la ventana si existen.'''

    geometry = self.settings.value('window_geometry')
    if geometry:
      self.restoreGeometry(geometry)

  def closeEvent(self, event: QCloseEvent) -> None:
    '''Guarda geometría de ventana antes de cerrar la app.'''

    if self.editor_dirty and not self.confirm_save_before_close_editor():
      event.ignore()
      return
    if not self.confirm_custom_template_changes(self.selected_template_id):
      event.ignore()
      return

    self.settings.setValue('window_geometry', self.saveGeometry())
    self.save_design_settings()
    event.accept()

  def choose_file(self) -> None:
    '''Abre un diálogo para seleccionar un archivo Markdown.'''

    filename, _ = QFileDialog.getOpenFileName(
      self,
      'Abrir Markdown',
      str(Path.home()),
      'Markdown (*.md *.markdown);;Todos los archivos (*.*)',
    )
    if filename:
      self.set_markdown_file(filename)

  def create_markdown_file(self) -> None:
    '''Crea un Markdown nuevo sin pedir ruta hasta guardar.'''

    if self.markdown_is_open() and not self.confirm_save_before_close_editor():
      return

    self.current_file = None
    self.current_pdf = None
    self.markdown_open = True
    self.file_input.setCurrentText('')
    self.drop_zone.setVisible(False)
    self.editor.blockSignals(True)
    self.editor.clear()
    self.editor.blockSignals(False)
    self.editor.setVisible(True)
    self.pdf_document.close()
    self.refresh_document_preview_if_visible()
    self.editor_dirty = False
    self.update_action_visibility()
    self.status_label.setText('Markdown nuevo sin guardar. Usa Guardar como para elegir ubicación.')

  def set_markdown_file(self, filename: str) -> None:
    '''Registra un Markdown seleccionado o arrastrado y reinicia la vista.'''

    path = Path(filename).resolve()
    if not path.exists():
      QMessageBox.warning(self, 'Archivo no encontrado', f'No existe el archivo:\n{path}')
      return
    if path.suffix.lower() not in {'.md', '.markdown'}:
      QMessageBox.warning(self, 'Formato no válido', 'Selecciona un archivo Markdown.')
      return

    if not self.confirm_discard_unsaved_changes():
      return

    self.current_file = path
    self.current_pdf = None
    self.remember_markdown(path)
    self.editor.clear()
    if not self.load_markdown_into_editor():
      self.current_file = None
      self.current_pdf = None
      self.markdown_open = False
      return
    self.markdown_open = True
    self.drop_zone.setVisible(False)
    self.editor.setVisible(True)
    self.pdf_document.close()
    self.refresh_document_preview_if_visible()
    self.editor_dirty = False
    self.edit_button.setText('Cerrar')
    self.update_action_visibility()
    self.status_label.setText('Markdown seleccionado. Pulsa Generar PDF.')

  def load_markdown_into_editor(self) -> bool:
    '''Carga el Markdown actual en el editor sin marcarlo como modificado.'''

    if self.current_file is None:
      return False

    try:
      content = self.current_file.read_text(encoding='utf-8')
    except OSError as exc:
      QMessageBox.critical(self, 'Error', f'No se pudo leer el archivo:\n{exc}')
      return False

    self.editor.blockSignals(True)
    self.editor.setPlainText(content)
    self.editor.blockSignals(False)
    self.editor_dirty = False
    return True

  def close_markdown_file(self) -> None:
    '''Cierra el Markdown actual y vuelve al estado inicial de la app.'''

    if not self.markdown_is_open():
      return

    if not self.confirm_save_before_close_editor():
      return

    self.current_file = None
    self.current_pdf = None
    self.markdown_open = False
    self.file_input.setCurrentText('')
    self.drop_zone.setVisible(True)
    self.editor.clear()
    self.editor.setVisible(False)
    self.pdf_document.close()
    self.refresh_document_preview_if_visible()
    self.editor_dirty = False
    self.edit_button.setText('Cerrar')
    self.update_action_visibility()
    self.status_label.setText('Listo.')

  def mark_editor_dirty(self) -> None:
    '''Marca el editor como modificado para proteger cambios sin guardar.'''

    if not self.markdown_is_open():
      return
    self.editor_dirty = True
    self.update_action_visibility()
    self.status_label.setText('Hay cambios sin guardar.')

  def save_editor(self) -> bool:
    '''Guarda el contenido del editor en el Markdown actual.'''

    if self.current_file is None:
      return self.save_editor_as()

    try:
      self.current_file.write_text(self.editor.toPlainText(), encoding='utf-8')
    except OSError as exc:
      QMessageBox.critical(self, 'Error', f'No se pudo guardar el archivo:\n{exc}')
      return False

    self.editor_dirty = False
    self.update_action_visibility()
    self.status_label.setText('Cambios guardados.')
    return True

  def save_editor_as(self) -> bool:
    '''Guarda el Markdown actual en una ruta nueva y cambia a ese archivo.'''

    if not self.markdown_is_open():
      return False

    default_path = self.current_file or Path.home() / 'nuevo_apunte.md'
    filename, _ = QFileDialog.getSaveFileName(
      self,
      'Guardar Markdown como',
      str(default_path),
      'Markdown (*.md);;Todos los archivos (*.*)',
    )
    if not filename:
      return False

    path = Path(filename)
    if path.suffix.lower() != '.md':
      path = path.with_suffix('.md')

    try:
      path.write_text(self.editor.toPlainText(), encoding='utf-8')
    except OSError as exc:
      QMessageBox.critical(self, 'Error', f'No se pudo guardar el archivo:\n{exc}')
      return False

    self.current_file = path.resolve()
    self.current_pdf = None
    self.remember_markdown(self.current_file)
    self.pdf_document.close()
    self.refresh_document_preview_if_visible()
    self.editor_dirty = False
    self.update_action_visibility()
    self.status_label.setText('Markdown guardado como archivo nuevo.')
    return True

  def confirm_discard_unsaved_changes(self) -> bool:
    '''Pregunta antes de cambiar de archivo si hay cambios sin guardar.'''

    if not self.editor_dirty:
      return True

    answer = QMessageBox.question(
      self,
      'Cambios sin guardar',
      'Hay cambios sin guardar. ¿Quieres descartarlos?',
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
      QMessageBox.StandardButton.No,
    )
    return answer == QMessageBox.StandardButton.Yes

  def confirm_save_before_build(self) -> bool:
    '''Pregunta qué hacer con cambios pendientes antes de generar el PDF.'''

    if self.current_file is None:
      return self.save_editor_as()

    if not self.editor_dirty:
      return True

    answer = QMessageBox.question(
      self,
      'Cambios sin guardar',
      'Hay cambios sin guardar. ¿Quieres guardarlos antes de generar el PDF?',
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
      QMessageBox.StandardButton.Yes,
    )
    if answer == QMessageBox.StandardButton.Cancel:
      return False
    if answer == QMessageBox.StandardButton.Yes:
      return self.save_editor()
    return True

  def confirm_save_before_close_editor(self) -> bool:
    '''Pregunta qué hacer con cambios pendientes antes de cerrar el editor.'''

    if not self.editor_dirty:
      return True

    answer = QMessageBox.question(
      self,
      'Cambios sin guardar',
      'Hay cambios sin guardar. ¿Quieres guardarlos antes de cerrar el editor?',
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
      QMessageBox.StandardButton.Yes,
    )
    if answer == QMessageBox.StandardButton.Cancel:
      return False
    if answer == QMessageBox.StandardButton.Yes:
      return self.save_editor()
    return True

  def generate_pdf(self) -> None:
    '''Inicia la generación del PDF con los valores actuales de la interfaz.'''

    if not self.markdown_is_open():
      QMessageBox.warning(self, 'Falta Markdown', 'Abre o crea un Markdown antes de generar.')
      return
    if not self.confirm_save_before_build():
      return
    if self.current_file is None:
      QMessageBox.warning(self, 'Falta archivo', 'Guarda el Markdown antes de generar.')
      return

    self.build_button.setEnabled(False)
    self.status_label.setText('Generando PDF...')
    self.worker = BuildWorker(
      str(self.current_file),
      self.current_style_options(),
      self.current_template_id(),
    )
    self.worker.succeeded.connect(self.on_success)
    self.worker.failed.connect(self.on_error)
    self.worker.finished.connect(lambda: self.build_button.setEnabled(True))
    self.worker.start()

  def on_success(self, pdf_file: str) -> None:
    '''Actualiza la interfaz cuando el PDF se ha generado correctamente.'''

    self.current_pdf = Path(pdf_file)
    self.status_label.setText(f'PDF generado: {pdf_file}')
    self.load_pdf_preview(self.current_pdf)

  def load_pdf_preview(self, pdf_file: Path) -> None:
    '''Carga el PDF generado en el visor embebido de Qt.'''

    self.pdf_document.close()
    error = self.pdf_document.load(str(pdf_file))
    if error != QPdfDocument.Error.None_:
      self.show_document_preview()
      self.update_action_visibility()
      QMessageBox.warning(
        self,
        'Vista previa',
        'El PDF se generó, pero no se pudo cargar la vista previa.',
      )
      return

    self.show_document_preview()
    self.update_action_visibility()
    self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

  def open_current_pdf(self) -> None:
    '''Abre el PDF generado en el visor externo predeterminado de Windows.'''

    if self.current_pdf is None:
      return

    self.status_label.setText('Abriendo PDF en el visor predeterminado de Windows...')
    try:
      subprocess.Popen(['cmd', '/c', 'start', '', str(self.current_pdf)], shell=False)
    except OSError as exc:
      self.status_label.setText('No se pudo abrir el PDF en Windows.')
      QMessageBox.critical(self, 'Error', f'No se pudo abrir el PDF:\n{exc}')
      return

    self.status_label.setText(f'PDF abierto en Windows: {self.current_pdf}')

  def on_error(self, message: str) -> None:
    '''Muestra en la interfaz un error de conversión controlado.'''

    self.status_label.setText('Error al generar el PDF.')
    QMessageBox.critical(self, 'Error', message)


def main() -> int:
  '''Punto de entrada de la app cuando se ejecuta `python -m app.main`.'''

  app = QApplication(sys.argv)
  initial_file = sys.argv[1] if len(sys.argv) > 1 else None
  window = MainWindow(initial_file)
  window.show()
  return app.exec()


if __name__ == '__main__':
  raise SystemExit(main())
