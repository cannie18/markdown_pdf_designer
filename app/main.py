'''Interfaz grafica PySide6 para generar PDF desde Markdown.

La ventana permite abrir o arrastrar un Markdown, editarlo opcionalmente,
configurar estilos basicos, generar el PDF y ver la vista previa real dentro
de la app. La conversion se delega en `app.pdf_builder`.
'''

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QThread, Signal
from PySide6.QtGui import QColor, QCloseEvent, QDragEnterEvent, QDropEvent
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import (
  QApplication,
  QColorDialog,
  QComboBox,
  QDoubleSpinBox,
  QFileDialog,
  QFormLayout,
  QFrame,
  QHBoxLayout,
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

from .pdf_builder import PdfBuildError, PdfStyleOptions, build_pdf


PREVIEW_PANEL_MIN_WIDTH = 320
WINDOW_MIN_HEIGHT = 480


class BuildWorker(QThread):
  '''Ejecuta la conversion en segundo plano para no bloquear la interfaz.'''

  succeeded = Signal(str)
  failed = Signal(str)

  def __init__(self, markdown_file: str, style: PdfStyleOptions) -> None:
    '''Guarda el archivo y las opciones visuales que se usaran al generar.'''

    super().__init__()
    self.markdown_file = markdown_file
    self.style = style

  def run(self) -> None:
    '''Lanza la generacion del PDF y emite una senal de exito o error.'''

    try:
      result = build_pdf(self.markdown_file, style=self.style)
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

    subtitle = QLabel('Tambien puedes usar Abrir')
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


class MainWindow(QMainWindow):
  '''Ventana principal de la app de escritorio.'''

  def __init__(self, initial_file: str | None = None) -> None:
    '''Crea la interfaz y carga un Markdown inicial si se arrastro al `.bat`.'''

    super().__init__()
    self.worker: BuildWorker | None = None
    self.current_file: Path | None = None
    self.current_pdf: Path | None = None
    self.editor_dirty = False
    self.settings = QSettings('pdf_apuntes', 'Markdown PDF Designer')
    self.heading_colors = {
      'h1': '#1f3552',
      'h2': '#2e6f73',
      'h3': '#7a3f3f',
      'bold': '#1f3552',
      'italic': '#131b2e',
      'body': '#131b2e',
      'code_background': '#f4f1ec',
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
    self.file_input.lineEdit().setPlaceholderText('Selecciona o arrastra un archivo .md')
    self.file_input.activated.connect(self.open_recent_markdown)
    self.load_recent_markdowns()

    open_button = QPushButton('Abrir')
    open_button.clicked.connect(self.choose_file)

    new_button = QPushButton('Nuevo')
    new_button.clicked.connect(self.create_markdown_file)

    self.edit_button = QPushButton('Cerrar')
    self.edit_button.clicked.connect(self.close_markdown_file)
    self.edit_button.setEnabled(False)
    self.edit_button.setVisible(False)

    self.save_button = QPushButton('Guardar')
    self.save_button.clicked.connect(self.save_editor)
    self.save_button.setEnabled(False)
    self.save_button.setVisible(False)

    self.save_as_button = QPushButton('Guardar como')
    self.save_as_button.clicked.connect(self.save_editor_as)
    self.save_as_button.setEnabled(False)
    self.save_as_button.setVisible(False)

    self.build_button = QPushButton('Generar PDF')
    self.build_button.clicked.connect(self.generate_pdf)
    self.build_button.setEnabled(False)
    self.build_button.setVisible(False)

    self.open_pdf_button = QPushButton('Abrir en Windows')
    self.open_pdf_button.clicked.connect(self.open_current_pdf)
    self.open_pdf_button.setEnabled(False)
    self.open_pdf_button.setVisible(False)

    self.status_label = QLabel('Listo.')
    self.status_label.setMinimumWidth(0)
    self.status_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
    self.status_label.setWordWrap(True)

    self.editor = QPlainTextEdit()
    self.editor.setPlaceholderText('El contenido del Markdown aparecera aqui.')
    self.editor.setMinimumWidth(0)
    self.editor.setVisible(False)
    self.editor.textChanged.connect(self.mark_editor_dirty)

    self.font_combo = QComboBox()
    self.font_combo.addItems(['Arial', 'Aptos', 'Calibri', 'Segoe UI', 'Times New Roman'])
    self.font_combo.setCurrentText('Arial')

    self.body_size_input = QDoubleSpinBox()
    self.body_size_input.setRange(6, 48)
    self.body_size_input.setSingleStep(0.5)
    self.body_size_input.setDecimals(1)
    self.body_size_input.setSuffix(' pt')
    self.body_size_input.setValue(10.5)

    self.paragraph_leading_input = QDoubleSpinBox()
    self.paragraph_leading_input.setRange(0.35, 2.5)
    self.paragraph_leading_input.setSingleStep(0.05)
    self.paragraph_leading_input.setDecimals(2)
    self.paragraph_leading_input.setValue(0.62)

    self.paragraph_spacing_input = QDoubleSpinBox()
    self.paragraph_spacing_input.setRange(0.2, 3.0)
    self.paragraph_spacing_input.setSingleStep(0.05)
    self.paragraph_spacing_input.setDecimals(2)
    self.paragraph_spacing_input.setValue(0.82)

    self.margin_x_input = QDoubleSpinBox()
    self.margin_x_input.setRange(0.3, 7)
    self.margin_x_input.setSingleStep(0.1)
    self.margin_x_input.setDecimals(1)
    self.margin_x_input.setSuffix(' cm')
    self.margin_x_input.setValue(2.2)

    self.margin_y_input = QDoubleSpinBox()
    self.margin_y_input.setRange(0.3, 7)
    self.margin_y_input.setSingleStep(0.1)
    self.margin_y_input.setDecimals(1)
    self.margin_y_input.setSuffix(' cm')
    self.margin_y_input.setValue(2.0)

    self.h1_size_input = QDoubleSpinBox()
    self.h1_size_input.setRange(6, 48)
    self.h1_size_input.setSingleStep(0.5)
    self.h1_size_input.setDecimals(1)
    self.h1_size_input.setSuffix(' pt')
    self.h1_size_input.setValue(24)

    self.h2_size_input = QDoubleSpinBox()
    self.h2_size_input.setRange(6, 48)
    self.h2_size_input.setSingleStep(0.5)
    self.h2_size_input.setDecimals(1)
    self.h2_size_input.setSuffix(' pt')
    self.h2_size_input.setValue(16)

    self.h3_size_input = QDoubleSpinBox()
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
    self.code_background_color_button = self.create_color_button('code_background')

    self.code_font_combo = QComboBox()
    self.code_font_combo.addItems(['Consolas', 'Cascadia Mono', 'Courier New', 'JetBrains Mono'])
    self.code_font_combo.setCurrentText('Consolas')

    self.code_size_input = QDoubleSpinBox()
    self.code_size_input.setRange(6, 48)
    self.code_size_input.setSingleStep(0.5)
    self.code_size_input.setDecimals(1)
    self.code_size_input.setSuffix(' pt')
    self.code_size_input.setValue(9)

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
      'La vista previa aparecera aqui cuando generes el primer PDF.'
    )
    self.empty_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.empty_preview_label.setWordWrap(True)
    self.empty_preview_label.setObjectName('emptyPreview')
    pdf_panel_layout.addWidget(preview_label)
    pdf_panel_layout.addWidget(self.empty_preview_label, 1)
    pdf_panel_layout.addWidget(self.pdf_view, 1)
    self.pdf_view.setVisible(False)

    self.drop_zone = DropZone()
    self.drop_zone.setMinimumWidth(0)
    self.drop_zone.file_dropped.connect(self.set_markdown_file)

    self.file_tab_button = self.create_nav_button('Archivo', 0)
    self.design_tab_button = self.create_nav_button('Diseno', 1)
    self.templates_tab_button = self.create_nav_button('Plantillas', 2)

    nav_row = QHBoxLayout()
    nav_row.addWidget(self.file_tab_button)
    nav_row.addWidget(self.design_tab_button)
    nav_row.addWidget(self.templates_tab_button)
    nav_row.addStretch()

    file_row = QHBoxLayout()
    file_row.addWidget(self.file_input, 1)
    file_row.addWidget(new_button)
    file_row.addWidget(open_button)

    file_page = QWidget()
    file_layout = QVBoxLayout(file_page)
    file_layout.setContentsMargins(0, 0, 0, 0)
    file_layout.addWidget(self.drop_zone)
    file_layout.addLayout(file_row)
    file_layout.addWidget(self.editor, 1)

    design_page = QWidget()
    design_layout = QVBoxLayout(design_page)
    design_layout.setContentsMargins(0, 0, 0, 0)
    design_title = QLabel('Ajustes de diseno')
    design_title.setObjectName('sectionTitle')
    design_help = QLabel(
      'Modifica la fuente, el tamano base y los colores. Luego vuelve a generar el PDF.'
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
    style_panel_layout.addLayout(
      self.create_design_group(
        'Base',
        [
          ('Fuente', self.font_combo),
          ('Tamano texto', self.body_size_input),
          ('Color texto', self.body_color_button),
          ('Interlineado', self.paragraph_leading_input),
          ('Espacio parrafos', self.paragraph_spacing_input),
        ],
      )
    )
    style_panel_layout.addLayout(
      self.create_design_group(
        'Pagina',
        [
          ('Margen lateral', self.margin_x_input),
          ('Margen vertical', self.margin_y_input),
        ],
      )
    )
    style_panel_layout.addLayout(
      self.create_design_group(
        'Titulos',
        [
          ('Tamano titulo 1', self.h1_size_input),
          ('Tamano titulo 2', self.h2_size_input),
          ('Tamano titulo 3', self.h3_size_input),
          ('Titulo 1', self.h1_color_button),
          ('Titulo 2', self.h2_color_button),
          ('Titulo 3', self.h3_color_button),
        ],
      )
    )
    style_panel_layout.addLayout(
      self.create_design_group(
        'Enfasis',
        [
          ('Negrita', self.bold_color_button),
          ('Cursiva', self.italic_color_button),
        ],
      )
    )
    style_panel_layout.addLayout(
      self.create_design_group(
        'Codigo',
        [
          ('Fuente codigo', self.code_font_combo),
          ('Tamano codigo', self.code_size_input),
          ('Fondo codigo', self.code_background_color_button),
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

    templates_page = QWidget()
    templates_layout = QVBoxLayout(templates_page)
    templates_layout.setContentsMargins(0, 0, 0, 0)
    templates_title = QLabel('Plantillas')
    templates_title.setObjectName('sectionTitle')
    templates_help = QLabel(
      'Aqui prepararemos plantillas base como estudio, compacto o tesis. '
      'De momento la app usa la plantilla estudio.'
    )
    templates_help.setObjectName('sectionHelp')
    templates_help.setWordWrap(True)
    templates_card = QFrame()
    templates_card.setObjectName('placeholderCard')
    templates_card_layout = QVBoxLayout(templates_card)
    templates_card_layout.addWidget(QLabel('Activa: estudio'))
    templates_card_layout.addWidget(QLabel('Nuevas plantillas: pendiente'))
    templates_layout.addWidget(templates_title)
    templates_layout.addWidget(templates_help)
    templates_layout.addWidget(templates_card)
    templates_layout.addStretch()

    self.templates_scroll = QScrollArea()
    self.templates_scroll.setWidget(templates_page)
    self.templates_scroll.setWidgetResizable(True)
    self.templates_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    self.templates_scroll.setFrameShape(QFrame.Shape.NoFrame)

    self.left_stack = QStackedWidget()
    self.left_stack.addWidget(file_page)
    self.left_stack.addWidget(self.design_scroll)
    self.left_stack.addWidget(self.templates_scroll)

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

  def select_left_section(self, index: int) -> None:
    '''Muestra una de las secciones principales del panel izquierdo.'''

    self.left_stack.setCurrentIndex(index)
    buttons = [
      self.file_tab_button,
      self.design_tab_button,
      self.templates_tab_button,
    ]
    for button_index, button in enumerate(buttons):
      button.setProperty('active', button_index == index)
      button.style().unpolish(button)
      button.style().polish(button)

  def create_design_group(self, title: str, rows: list[tuple[str, QWidget]]) -> QVBoxLayout:
    '''Crea una seccion compacta para opciones de diseno relacionadas.'''

    group_layout = QVBoxLayout()
    group_layout.setContentsMargins(0, 0, 0, 0)
    group_layout.setSpacing(4)

    group_title = QLabel(title)
    group_title.setObjectName('designGroupTitle')
    group_layout.addWidget(group_title)

    form_layout = QFormLayout()
    form_layout.setContentsMargins(0, 0, 0, 0)
    form_layout.setHorizontalSpacing(8)
    form_layout.setVerticalSpacing(5)
    form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
    form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    for label, widget in rows:
      form_layout.addRow(label, widget)

    group_layout.addLayout(form_layout)
    return group_layout

  def create_color_button(self, color_key: str) -> QPushButton:
    '''Crea un boton que abre el selector para un color del PDF.'''

    button = QPushButton()
    button.clicked.connect(lambda: self.choose_heading_color(color_key))
    return button

  def choose_heading_color(self, color_key: str) -> None:
    '''Permite escoger un color del PDF con el dialogo nativo de Qt.'''

    current = QColor(self.heading_colors[color_key])
    color = QColorDialog.getColor(current, self, 'Elegir color')
    if not color.isValid():
      return

    self.heading_colors[color_key] = color.name()
    self.refresh_color_buttons()

  def refresh_color_buttons(self) -> None:
    '''Actualiza texto y fondo de los botones de color.'''

    buttons = {
      'h1': self.h1_color_button,
      'h2': self.h2_color_button,
      'h3': self.h3_color_button,
      'bold': self.bold_color_button,
      'italic': self.italic_color_button,
      'body': self.body_color_button,
      'code_background': self.code_background_color_button,
    }
    for color_key, button in buttons.items():
      color = self.heading_colors[color_key]
      button.setText(color)
      button.setStyleSheet(
        f'background: {color}; color: {self.text_color_for_background(color)};'
      )

  def text_color_for_background(self, color: str) -> str:
    '''Elige texto blanco o negro segun la luminosidad del color de fondo.'''

    value = color.lstrip('#')
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    brightness = (red * 299 + green * 587 + blue * 114) / 1000
    return '#000000' if brightness > 150 else '#ffffff'

  def current_style_options(self) -> PdfStyleOptions:
    '''Construye las opciones visuales actuales para el generador de PDF.'''

    return PdfStyleOptions(
      font_family=self.font_combo.currentText(),
      body_font_size=self.body_size_input.value(),
      body_color=self.heading_colors['body'],
      paragraph_leading=self.paragraph_leading_input.value(),
      paragraph_spacing=self.paragraph_spacing_input.value(),
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
    )

  def load_recent_markdowns(self) -> None:
    '''Carga en el desplegable las ultimas rutas Markdown usadas.'''

    recent = self.settings.value('recent_markdowns', [], list)
    self.file_input.blockSignals(True)
    self.file_input.clear()
    self.file_input.addItems([str(path) for path in recent[:10]])
    self.file_input.setCurrentText('')
    self.file_input.blockSignals(False)

  def set_initial_splitter_sizes(self) -> None:
    '''Asigna un ancho inicial estable al panel izquierdo.'''

    left_width = self.left_panel.minimumWidth()
    self.splitter.setSizes([left_width, self.width() - left_width])

  def update_left_panel_min_width(self) -> None:
    '''Calcula el minimo del panel izquierdo desde la fila de botones Markdown.'''

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
    '''Guarda una ruta Markdown en el historial de las 10 ultimas opciones.'''

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
    '''Restaura posicion, monitor y tamano de la ventana si existen.'''

    geometry = self.settings.value('window_geometry')
    if geometry:
      self.restoreGeometry(geometry)

  def closeEvent(self, event: QCloseEvent) -> None:
    '''Guarda geometria de ventana antes de cerrar la app.'''

    if self.editor_dirty and not self.confirm_save_before_close_editor():
      event.ignore()
      return

    self.settings.setValue('window_geometry', self.saveGeometry())
    event.accept()

  def choose_file(self) -> None:
    '''Abre un dialogo para seleccionar un archivo Markdown.'''

    filename, _ = QFileDialog.getOpenFileName(
      self,
      'Abrir Markdown',
      str(Path.home()),
      'Markdown (*.md *.markdown);;Todos los archivos (*.*)',
    )
    if filename:
      self.set_markdown_file(filename)

  def create_markdown_file(self) -> None:
    '''Crea un archivo Markdown vacio y lo abre en el editor.'''

    if not self.confirm_discard_unsaved_changes():
      return

    filename, _ = QFileDialog.getSaveFileName(
      self,
      'Crear Markdown',
      str(Path.home() / 'nuevo_apunte.md'),
      'Markdown (*.md);;Todos los archivos (*.*)',
    )
    if not filename:
      return

    path = Path(filename)
    if path.suffix.lower() != '.md':
      path = path.with_suffix('.md')

    try:
      path.write_text('', encoding='utf-8')
    except OSError as exc:
      QMessageBox.critical(self, 'Error', f'No se pudo crear el archivo:\n{exc}')
      return

    self.set_markdown_file(str(path))

  def set_markdown_file(self, filename: str) -> None:
    '''Registra un Markdown seleccionado o arrastrado y reinicia la vista.'''

    path = Path(filename).resolve()
    if not path.exists():
      QMessageBox.warning(self, 'Archivo no encontrado', f'No existe el archivo:\n{path}')
      return
    if path.suffix.lower() not in {'.md', '.markdown'}:
      QMessageBox.warning(self, 'Formato no valido', 'Selecciona un archivo Markdown.')
      return

    if not self.confirm_discard_unsaved_changes():
      return

    self.current_file = path
    self.current_pdf = None
    self.remember_markdown(path)
    self.editor.clear()
    if not self.load_markdown_into_editor():
      return
    self.drop_zone.setVisible(False)
    self.editor.setVisible(True)
    self.pdf_document.close()
    self.pdf_view.setVisible(False)
    self.empty_preview_label.setVisible(True)
    self.editor_dirty = False
    self.edit_button.setText('Cerrar')
    self.edit_button.setEnabled(True)
    self.edit_button.setVisible(True)
    self.save_button.setEnabled(False)
    self.save_button.setVisible(True)
    self.save_as_button.setEnabled(True)
    self.save_as_button.setVisible(True)
    self.open_pdf_button.setEnabled(False)
    self.open_pdf_button.setVisible(False)
    self.build_button.setEnabled(True)
    self.build_button.setVisible(True)
    self.status_label.setText('Archivo seleccionado. Pulsa Generar PDF.')

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

    if self.current_file is None:
      return

    if not self.confirm_save_before_close_editor():
      return

    self.current_file = None
    self.current_pdf = None
    self.file_input.setCurrentText('')
    self.drop_zone.setVisible(True)
    self.editor.clear()
    self.editor.setVisible(False)
    self.pdf_document.close()
    self.pdf_view.setVisible(False)
    self.empty_preview_label.setVisible(True)
    self.editor_dirty = False
    self.edit_button.setText('Cerrar')
    self.edit_button.setEnabled(False)
    self.edit_button.setVisible(False)
    self.save_button.setEnabled(False)
    self.save_button.setVisible(False)
    self.save_as_button.setEnabled(False)
    self.save_as_button.setVisible(False)
    self.open_pdf_button.setEnabled(False)
    self.open_pdf_button.setVisible(False)
    self.build_button.setEnabled(False)
    self.build_button.setVisible(False)
    self.status_label.setText('Listo.')

  def mark_editor_dirty(self) -> None:
    '''Marca el editor como modificado para proteger cambios sin guardar.'''

    if self.current_file is None:
      return
    self.editor_dirty = True
    self.save_button.setEnabled(True)
    self.status_label.setText('Hay cambios sin guardar.')

  def save_editor(self) -> bool:
    '''Guarda el contenido del editor en el Markdown actual.'''

    if self.current_file is None:
      return True

    try:
      self.current_file.write_text(self.editor.toPlainText(), encoding='utf-8')
    except OSError as exc:
      QMessageBox.critical(self, 'Error', f'No se pudo guardar el archivo:\n{exc}')
      return False

    self.editor_dirty = False
    self.save_button.setEnabled(False)
    self.status_label.setText('Cambios guardados.')
    return True

  def save_editor_as(self) -> bool:
    '''Guarda el Markdown actual en una ruta nueva y cambia a ese archivo.'''

    if self.current_file is None:
      return False

    filename, _ = QFileDialog.getSaveFileName(
      self,
      'Guardar Markdown como',
      str(self.current_file),
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
    self.pdf_view.setVisible(False)
    self.empty_preview_label.setVisible(True)
    self.open_pdf_button.setEnabled(False)
    self.open_pdf_button.setVisible(False)
    self.editor_dirty = False
    self.save_button.setEnabled(False)
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
    '''Pregunta que hacer con cambios pendientes antes de generar el PDF.'''

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
    '''Pregunta que hacer con cambios pendientes antes de cerrar el editor.'''

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
    '''Inicia la generacion del PDF con los valores actuales de la interfaz.'''

    markdown_file = self.file_input.currentText().strip()
    if not markdown_file:
      QMessageBox.warning(self, 'Falta archivo', 'Selecciona un archivo Markdown.')
      return
    if not self.confirm_save_before_build():
      return

    self.build_button.setEnabled(False)
    self.status_label.setText('Generando PDF...')
    self.worker = BuildWorker(markdown_file, self.current_style_options())
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
      self.pdf_view.setVisible(False)
      self.empty_preview_label.setVisible(True)
      self.open_pdf_button.setEnabled(True)
      self.open_pdf_button.setVisible(True)
      QMessageBox.warning(
        self,
        'Vista previa',
        'El PDF se genero, pero no se pudo cargar la vista previa.',
      )
      return

    self.empty_preview_label.setVisible(False)
    self.pdf_view.setVisible(True)
    self.open_pdf_button.setEnabled(True)
    self.open_pdf_button.setVisible(True)
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
    '''Muestra en la interfaz un error de conversion controlado.'''

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
