from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
APP_TEMPLATES_DIR = APP_DIR / 'templates'


@dataclass(frozen=True)
class PdfStyleOptions:
  font_family: str = 'Arial'
  body_font_size: float = 10.5
  heading_1_color: str = '#1f3552'
  heading_2_color: str = '#2e6f73'
  heading_3_color: str = '#7a3f3f'


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


def normalize_hex_color(color: str) -> str:
  value = color.strip()
  if not value.startswith('#'):
    value = f'#{value}'
  if len(value) != 7:
    raise PdfBuildError(f'Color no valido: {color}')
  try:
    int(value[1:], 16)
  except ValueError as exc:
    raise PdfBuildError(f'Color no valido: {color}') from exc
  return value.lower()


def render_template(template_file: Path, style: PdfStyleOptions) -> Path:
  template_text = template_file.read_text(encoding='utf-8')
  replacements = {
    '__BODY_FONT__': style.font_family,
    '__BODY_FONT_SIZE__': f'{style.body_font_size:g}',
    '__H1_COLOR__': normalize_hex_color(style.heading_1_color),
    '__H2_COLOR__': normalize_hex_color(style.heading_2_color),
    '__H3_COLOR__': normalize_hex_color(style.heading_3_color),
  }

  for placeholder, value in replacements.items():
    template_text = template_text.replace(placeholder, value)

  temp_dir = ROOT_DIR / 'tmp' / 'app_templates'
  temp_dir.mkdir(parents=True, exist_ok=True)
  temp_file = tempfile.NamedTemporaryFile(
    mode='w',
    encoding='utf-8',
    suffix='.typ',
    prefix='estudio_',
    dir=temp_dir,
    delete=False,
  )
  with temp_file:
    temp_file.write(template_text)
  return Path(temp_file.name)


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


def build_pdf(
  input_file: str | Path,
  style: PdfStyleOptions | None = None,
) -> PdfResult:
  source = Path(input_file).resolve()
  if not source.exists():
    raise PdfBuildError(f'No existe el archivo: {source}')
  if source.suffix.lower() not in {'.md', '.markdown'}:
    raise PdfBuildError('Selecciona un archivo Markdown con extension .md o .markdown.')

  source_template_file = default_template()
  template_file = render_template(source_template_file, style or PdfStyleOptions())
  typ_file = source.with_suffix('.typ')
  pdf_file = source.with_suffix('.pdf')

  pandoc = find_executable('pandoc')
  typst = find_executable('typst')

  try:
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
  finally:
    if template_file.exists():
      template_file.unlink()

  if typ_file.exists():
    typ_file.unlink()

  return PdfResult(
    input_file=source,
    template_file=source_template_file,
    pdf_file=pdf_file,
    typ_file=typ_file,
  )
