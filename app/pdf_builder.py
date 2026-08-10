from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
APP_TEMPLATES_DIR = APP_DIR / 'templates'


@dataclass(frozen=True)
class PdfResult:
  input_file: Path
  template_file: Path
  pdf_file: Path
  typ_file: Path


class PdfBuildError(RuntimeError):
  pass


def find_executable(name: str) -> Path | str:
  local_exe = ROOT_DIR / 'bin' / name / f'{name}.exe'
  if local_exe.exists():
    return local_exe

  if name == 'pandoc':
    local_appdata = os.environ.get('LOCALAPPDATA')
    if local_appdata:
      user_pandoc = Path(local_appdata) / 'Pandoc' / 'pandoc.exe'
      if user_pandoc.exists():
        return user_pandoc

  found = shutil.which(name)
  if found:
    return found

  raise PdfBuildError(
    f'No se encontro {name}. Usa la version portable en bin\\{name}\\{name}.exe '
    f'o instala {name} en Windows.'
  )


def default_template() -> Path:
  template = APP_TEMPLATES_DIR / 'estudio.typ'
  if not template.exists():
    raise PdfBuildError(f'No existe la plantilla de la app: {template}')
  return template


def run_command(command: list[str | Path]) -> None:
  completed = subprocess.run(
    [str(part) for part in command],
    cwd=ROOT_DIR,
    text=True,
    capture_output=True,
  )
  if completed.returncode == 0:
    return

  details = '\n'.join(
    part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
  )
  raise PdfBuildError(details or 'El comando de conversion fallo sin detalles.')


def build_pdf(input_file: str | Path) -> PdfResult:
  source = Path(input_file).resolve()
  if not source.exists():
    raise PdfBuildError(f'No existe el archivo: {source}')
  if source.suffix.lower() not in {'.md', '.markdown'}:
    raise PdfBuildError('Selecciona un archivo Markdown con extension .md o .markdown.')

  template_file = default_template()
  typ_file = source.with_suffix('.typ')
  pdf_file = source.with_suffix('.pdf')

  pandoc = find_executable('pandoc')
  typst = find_executable('typst')

  run_command(
    [
      pandoc,
      source,
      '-f',
      'markdown',
      '-t',
      'typst',
      '-s',
      f'--template={template_file}',
      '-o',
      typ_file,
    ]
  )
  run_command([typst, 'compile', typ_file, pdf_file])

  if typ_file.exists():
    typ_file.unlink()

  return PdfResult(
    input_file=source,
    template_file=template_file,
    pdf_file=pdf_file,
    typ_file=typ_file,
  )
