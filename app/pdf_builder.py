'''Conversión Markdown -> Typst -> PDF usada por la app PySide6.

Este módulo contiene la lógica no visual de la aplicación. La versión portable
por `crear_pdf.bat` queda separada: aquí solo se usa la plantilla de la app y
una plantilla temporal generada con las opciones escogidas en la interfaz.
'''

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
DEFAULT_TEMPLATE_ID = 'estudio'


@dataclass(frozen=True)
class PdfStyleOptions:
  '''Opciones visuales que la app inyecta en la plantilla Typst temporal.'''

  font_family: str = 'Arial'
  body_font_size: float = 10.5
  body_color: str = '#131b2e'
  paragraph_leading: float = 0.62
  paragraph_spacing: float = 0.82
  page_margin_x: float = 22
  page_margin_y: float = 20
  heading_1_size: float = 24
  heading_2_size: float = 16
  heading_3_size: float = 12.5
  heading_1_color: str = '#1f3552'
  heading_2_color: str = '#2e6f73'
  heading_3_color: str = '#7a3f3f'
  bold_color: str = '#1f3552'
  italic_color: str = '#131b2e'
  code_font_family: str = 'Consolas'
  code_font_size: float = 9
  code_background_color: str = '#f4f1ec'


@dataclass(frozen=True)
class PdfResult:
  '''Rutas importantes resultantes de una generación de PDF.'''

  input_file: Path
  template_file: Path
  pdf_file: Path
  typ_file: Path


class PdfBuildError(RuntimeError):
  '''Error controlado que puede mostrarse de forma legible en la interfaz.'''

  pass


TEMPLATE_STYLE_PRESETS = {
  'estudio': PdfStyleOptions(),
  'profesional': PdfStyleOptions(
    font_family='Aptos',
    body_font_size=10.5,
    body_color='#172033',
    paragraph_leading=0.68,
    paragraph_spacing=0.85,
    page_margin_x=22,
    page_margin_y=20,
    heading_1_size=23,
    heading_2_size=15.5,
    heading_3_size=12.5,
    heading_1_color='#233b5d',
    heading_2_color='#2f6470',
    heading_3_color='#705044',
    bold_color='#233b5d',
    italic_color='#172033',
    code_background_color='#f3f5f7',
  ),
  'compacto': PdfStyleOptions(
    font_family='Arial',
    body_font_size=9,
    body_color='#171717',
    paragraph_leading=0.48,
    paragraph_spacing=0.48,
    page_margin_x=16,
    page_margin_y=15,
    heading_1_size=18,
    heading_2_size=13,
    heading_3_size=10.5,
    heading_1_color='#19324a',
    heading_2_color='#2f665c',
    heading_3_color='#6a4f2d',
    bold_color='#19324a',
    italic_color='#171717',
    code_font_size=8,
    code_background_color='#f4f4f4',
  ),
  'latex_clasico': PdfStyleOptions(
    font_family='Latin Modern Roman',
    body_font_size=11,
    body_color='#000000',
    paragraph_leading=0.64,
    paragraph_spacing=0.72,
    page_margin_x=30,
    page_margin_y=30,
    heading_1_size=22,
    heading_2_size=16,
    heading_3_size=13,
    heading_1_color='#000000',
    heading_2_color='#000000',
    heading_3_color='#000000',
    bold_color='#000000',
    italic_color='#000000',
    code_font_size=9,
    code_background_color='#ffffff',
  ),
  'apa_mla': PdfStyleOptions(
    font_family='Times New Roman',
    body_font_size=12,
    body_color='#111111',
    paragraph_leading=1.15,
    paragraph_spacing=1.15,
    page_margin_x=25.4,
    page_margin_y=25.4,
    heading_1_size=20,
    heading_2_size=16,
    heading_3_size=13.5,
    heading_1_color='#111111',
    heading_2_color='#111111',
    heading_3_color='#111111',
    bold_color='#111111',
    italic_color='#111111',
    code_font_size=9,
    code_background_color='#f7f7f7',
  ),
  'informe_ejecutivo': PdfStyleOptions(
    font_family='Aptos',
    body_font_size=10.5,
    body_color='#1c2433',
    paragraph_leading=1.5,
    paragraph_spacing=1.5,
    page_margin_x=27,
    page_margin_y=22,
    heading_1_size=22,
    heading_2_size=15.5,
    heading_3_size=12.5,
    heading_1_color='#204a66',
    heading_2_color='#2c7280',
    heading_3_color='#6b4f3a',
    bold_color='#204a66',
    italic_color='#1c2433',
    code_background_color='#eef2f6',
  ),
  'manual_tecnico': PdfStyleOptions(
    font_family='Segoe UI',
    body_font_size=10,
    body_color='#17202c',
    paragraph_leading=0.65,
    paragraph_spacing=0.72,
    page_margin_x=20,
    page_margin_y=18,
    heading_1_size=21,
    heading_2_size=15,
    heading_3_size=12.5,
    heading_1_color='#17496b',
    heading_2_color='#286c7d',
    heading_3_color='#64533d',
    bold_color='#17496b',
    italic_color='#17202c',
    code_font_size=9,
    code_background_color='#1f2430',
  ),
  'manuscrito_novela': PdfStyleOptions(
    font_family='Times New Roman',
    body_font_size=11,
    body_color='#151515',
    paragraph_leading=0.72,
    paragraph_spacing=0.72,
    page_margin_x=18,
    page_margin_y=20,
    heading_1_size=20,
    heading_2_size=15,
    heading_3_size=12,
    heading_1_color='#252525',
    heading_2_color='#343434',
    heading_3_color='#505050',
    bold_color='#151515',
    italic_color='#151515',
    code_font_size=9,
    code_background_color='#f6f3ee',
  ),
  'accesibilidad_neurodivergencia': PdfStyleOptions(
    font_family='Verdana',
    body_font_size=13.5,
    body_color='#333333',
    paragraph_leading=1.55,
    paragraph_spacing=1.65,
    page_margin_x=32,
    page_margin_y=28,
    heading_1_size=27,
    heading_2_size=20,
    heading_3_size=16,
    heading_1_color='#24435a',
    heading_2_color='#2f6f66',
    heading_3_color='#5a5f7a',
    bold_color='#24435a',
    italic_color='#24435a',
    code_font_family='Cascadia Mono',
    code_font_size=10.5,
    code_background_color='#e7f3f2',
  ),
}


def template_style_preset(template_id: str) -> PdfStyleOptions:
  '''Devuelve los ajustes de diseño iniciales de una plantilla.'''

  normalized_id = template_id.strip().lower() or DEFAULT_TEMPLATE_ID
  return TEMPLATE_STYLE_PRESETS.get(normalized_id, PdfStyleOptions())


def find_executable(name: str) -> Path | str:
  '''Busca un ejecutable priorizando la versión portable del proyecto.

  Orden de búsqueda:
  1. `bin/<name>/<name>.exe`, para mantener portabilidad local.
  2. Ubicacion de usuario de Pandoc, si se busca `pandoc`.
  3. PATH del sistema.
  '''

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
    f'No se encontró {name}. Usa la versión portable en bin\\{name}\\{name}.exe '
    f'o instala {name} en Windows.'
  )


def default_template() -> Path:
  '''Devuelve la plantilla base de la app.

  No usa `templates/apuntes.typ`, porque esa plantilla pertenece al flujo
  portable por `.bat`.
  '''

  return template_path(DEFAULT_TEMPLATE_ID)


def available_templates() -> list[str]:
  '''Lista las plantillas Typst disponibles para la app.'''

  if not APP_TEMPLATES_DIR.exists():
    return []
  return sorted(template.stem for template in APP_TEMPLATES_DIR.glob('*.typ'))


def template_path(template_id: str) -> Path:
  '''Devuelve la ruta de una plantilla de la app validando su existencia.'''

  normalized_id = template_id.strip().lower() or DEFAULT_TEMPLATE_ID
  template = APP_TEMPLATES_DIR / f'{normalized_id}.typ'
  if not template.exists():
    raise PdfBuildError(f'No existe la plantilla de la app: {template}')
  return template


def normalize_hex_color(color: str) -> str:
  '''Valida y normaliza colores hexadecimales en formato `#rrggbb`.'''

  value = color.strip()
  if not value.startswith('#'):
    value = f'#{value}'
  if len(value) != 7:
    raise PdfBuildError(f'Color no válido: {color}')
  try:
    int(value[1:], 16)
  except ValueError as exc:
    raise PdfBuildError(f'Color no válido: {color}') from exc
  return value.lower()


def render_template(template_file: Path, style: PdfStyleOptions) -> Path:
  '''Crea una plantilla Typst temporal con los valores visuales de la app.

  Pandoc necesita recibir una plantilla física en disco. Por eso no se modifica
  `app/templates/estudio.typ`; se copia su contenido, se sustituyen marcadores
  y se escribe un `.typ` temporal que se borra tras la conversión.
  '''

  template_text = template_file.read_text(encoding='utf-8')
  replacements = {
    '__BODY_FONT__': style.font_family,
    '__BODY_FONT_SIZE__': f'{style.body_font_size:g}',
    '__BODY_COLOR__': normalize_hex_color(style.body_color),
    '__PAR_LEADING__': f'{style.paragraph_leading:g}',
    '__PAR_SPACING__': f'{style.paragraph_spacing:g}',
    '__PAGE_MARGIN_X__': f'{style.page_margin_x:g}',
    '__PAGE_MARGIN_Y__': f'{style.page_margin_y:g}',
    '__H1_SIZE__': f'{style.heading_1_size:g}',
    '__H2_SIZE__': f'{style.heading_2_size:g}',
    '__H3_SIZE__': f'{style.heading_3_size:g}',
    '__H1_COLOR__': normalize_hex_color(style.heading_1_color),
    '__H2_COLOR__': normalize_hex_color(style.heading_2_color),
    '__H3_COLOR__': normalize_hex_color(style.heading_3_color),
    '__BOLD_COLOR__': normalize_hex_color(style.bold_color),
    '__ITALIC_COLOR__': normalize_hex_color(style.italic_color),
    '__CODE_FONT__': style.code_font_family,
    '__CODE_FONT_SIZE__': f'{style.code_font_size:g}',
    '__CODE_BACKGROUND_COLOR__': normalize_hex_color(style.code_background_color),
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
  '''Ejecuta un comando externo y convierte errores en `PdfBuildError`.'''

  creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
  completed = subprocess.run(
    [str(part) for part in command],
    cwd=ROOT_DIR,
    text=True,
    capture_output=True,
    creationflags=creation_flags,
  )
  if completed.returncode == 0:
    return

  details = '\n'.join(
    part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
  )
  raise PdfBuildError(details or 'El comando de conversión falló sin detalles.')


def build_pdf(
  input_file: str | Path,
  style: PdfStyleOptions | None = None,
  template_id: str = DEFAULT_TEMPLATE_ID,
) -> PdfResult:
  '''Genera un PDF desde un archivo Markdown usando Pandoc y Typst.

  El archivo `.typ` intermedio y la plantilla temporal se eliminan al terminar.
  El PDF final se escribe junto al Markdown de entrada.
  '''

  source = Path(input_file).resolve()
  if not source.exists():
    raise PdfBuildError(f'No existe el archivo: {source}')
  if source.suffix.lower() not in {'.md', '.markdown'}:
    raise PdfBuildError('Selecciona un archivo Markdown con extensión .md o .markdown.')

  source_template_file = template_path(template_id)
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
