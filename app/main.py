from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
  QApplication,
  QFileDialog,
  QFrame,
  QHBoxLayout,
  QLabel,
  QLineEdit,
  QMainWindow,
  QMessageBox,
  QPushButton,
  QVBoxLayout,
  QWidget,
)

from .pdf_builder import PdfBuildError, build_pdf


class BuildWorker(QThread):
  succeeded = Signal(str)
  failed = Signal(str)

  def __init__(self, markdown_file: str) -> None:
    super().__init__()
    self.markdown_file = markdown_file

  def run(self) -> None:
    try:
      result = build_pdf(self.markdown_file)
    except PdfBuildError as exc:
      self.failed.emit(str(exc))
      return
    self.succeeded.emit(str(result.pdf_file))


class DropZone(QFrame):
  file_dropped = Signal(str)

  def __init__(self) -> None:
    super().__init__()
    self.setAcceptDrops(True)
    self.setObjectName('dropZone')
    self.setMinimumHeight(110)

    layout = QVBoxLayout(self)
    title = QLabel('Arrastra aqui un archivo Markdown')
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setObjectName('dropTitle')

    subtitle = QLabel('Tambien puedes usar el boton Abrir')
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
    subtitle.setObjectName('dropSubtitle')

    layout.addStretch()
    layout.addWidget(title)
    layout.addWidget(subtitle)
    layout.addStretch()

  def dragEnterEvent(self, event: QDragEnterEvent) -> None:
    if event.mimeData().hasUrls():
      event.acceptProposedAction()
    else:
      event.ignore()

  def dropEvent(self, event: QDropEvent) -> None:
    urls = event.mimeData().urls()
    if not urls:
      return
    path = urls[0].toLocalFile()
    if path:
      self.file_dropped.emit(path)


class MainWindow(QMainWindow):
  def __init__(self, initial_file: str | None = None) -> None:
    super().__init__()
    self.worker: BuildWorker | None = None
    self.setWindowTitle('PDF Apuntes')
    self.resize(720, 360)
    self.setMinimumSize(640, 320)

    self.file_input = QLineEdit()
    self.file_input.setPlaceholderText('Selecciona o arrastra un archivo .md')
    if initial_file:
      self.file_input.setText(initial_file)

    open_button = QPushButton('Abrir')
    open_button.clicked.connect(self.choose_file)

    self.build_button = QPushButton('Generar PDF')
    self.build_button.clicked.connect(self.generate_pdf)

    self.status_label = QLabel('Listo.')
    self.status_label.setWordWrap(True)

    drop_zone = DropZone()
    drop_zone.file_dropped.connect(self.set_markdown_file)

    file_row = QHBoxLayout()
    file_row.addWidget(self.file_input, 1)
    file_row.addWidget(open_button)

    actions_row = QHBoxLayout()
    actions_row.addStretch()
    actions_row.addWidget(self.build_button)

    layout = QVBoxLayout()
    layout.addWidget(drop_zone)
    layout.addLayout(file_row)
    layout.addLayout(actions_row)
    layout.addWidget(self.status_label)

    container = QWidget()
    container.setLayout(layout)
    self.setCentralWidget(container)
    self.apply_styles()

  def apply_styles(self) -> None:
    self.setStyleSheet(
      '''
      QWidget {
        font-family: Segoe UI;
        font-size: 10.5pt;
      }
      QLineEdit {
        padding: 8px;
      }
      QPushButton {
        padding: 8px 14px;
      }
      #dropZone {
        border: 1px dashed #7a8a99;
        border-radius: 6px;
        background: #f7f9fb;
      }
      #dropTitle {
        font-size: 13pt;
        font-weight: 600;
        color: #26364a;
      }
      #dropSubtitle {
        color: #66717d;
      }
      '''
    )

  def choose_file(self) -> None:
    filename, _ = QFileDialog.getOpenFileName(
      self,
      'Abrir Markdown',
      str(Path.home()),
      'Markdown (*.md *.markdown);;Todos los archivos (*.*)',
    )
    if filename:
      self.set_markdown_file(filename)

  def set_markdown_file(self, filename: str) -> None:
    self.file_input.setText(filename)
    self.status_label.setText('Archivo seleccionado. Pulsa Generar PDF.')

  def generate_pdf(self) -> None:
    markdown_file = self.file_input.text().strip()
    if not markdown_file:
      QMessageBox.warning(self, 'Falta archivo', 'Selecciona un archivo Markdown.')
      return

    self.build_button.setEnabled(False)
    self.status_label.setText('Generando PDF...')
    self.worker = BuildWorker(markdown_file)
    self.worker.succeeded.connect(self.on_success)
    self.worker.failed.connect(self.on_error)
    self.worker.finished.connect(lambda: self.build_button.setEnabled(True))
    self.worker.start()

  def on_success(self, pdf_file: str) -> None:
    self.status_label.setText(f'PDF generado: {pdf_file}')
    answer = QMessageBox.question(
      self,
      'PDF generado',
      'El PDF se genero correctamente. ¿Quieres abrirlo?',
    )
    if answer == QMessageBox.StandardButton.Yes:
      subprocess.Popen(['cmd', '/c', 'start', '', pdf_file], shell=False)

  def on_error(self, message: str) -> None:
    self.status_label.setText('Error al generar el PDF.')
    QMessageBox.critical(self, 'Error', message)


def main() -> int:
  app = QApplication(sys.argv)
  initial_file = sys.argv[1] if len(sys.argv) > 1 else None
  window = MainWindow(initial_file)
  window.show()
  return app.exec()


if __name__ == '__main__':
  raise SystemExit(main())
