'''Conversión Markdown -> Typst -> PDF usada por la app PySide6.

Este módulo contiene la lógica no visual de la aplicación. La versión portable
por `crear_pdf.bat` queda separada: aquí solo se usa la plantilla de la app y
una plantilla temporal generada con las opciones escogidas en la interfaz.
'''

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass, fields
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
APP_TEMPLATES_DIR = APP_DIR / 'templates'
DEFAULT_TEMPLATE_ID = 'estudio'
USER_DATA_ENV_VAR = 'PDF_APUNTES_USER_DATA_DIR'


@dataclass(frozen=True)
class PdfStyleOptions:
  '''Opciones visuales que la app inyecta en la plantilla Typst temporal.'''

  font_family: str = 'Arial'
  body_font_size: float = 10.5
  body_color: str = '#131b2e'
  page_background_color: str = '#ffffff'
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
  table_inset: float = 7
  table_stroke_color: str = '#c8d0d8'
  table_text_color: str = '#131b2e'
  table_text_size: float = 10
  table_width_mode: str = 'auto'
  table_header_background_color: str = '#eef2f7'
  table_header_text_color: str = '#1f3552'
  quote_inset: float = 0.85
  quote_border_color: str = '#2e6f73'
  quote_background_color: str = '#eef6f4'
  quote_text_color: str = '#131b2e'
  quote_text_size: float = 10.5


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


HTML_MARK_TOKEN_PREFIX = 'MDPDFMARK'
TOC_TOKEN = 'MDPDFTOC'
PAGEBREAK_TOKEN = 'MDPDFPAGEBREAK'
ADMONITION_STYLES = {
  'NOTE': ('Note', '#2f6feb', 'note.svg'),
  'TIP': ('Tip', '#2da44e', 'tip.svg'),
  'IMPORTANT': ('Important', '#8957e5', 'important.svg'),
  'WARNING': ('Warning', '#bf8700', 'warning.svg'),
  'CAUTION': ('Caution', '#cf222e', 'caution.svg'),
}


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
    table_inset=7,
    table_stroke_color='#b9c3cf',
    table_text_color='#172033',
    table_text_size=10,
    table_header_background_color='#eef2f7',
    table_header_text_color='#233b5d',
    quote_inset=0.85,
    quote_border_color='#c8d0d8',
    quote_background_color='#f7f9fb',
    quote_text_color='#172033',
    quote_text_size=10.5,
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
    table_inset=5,
    table_stroke_color='#c8d0d8',
    table_text_color='#171717',
    table_text_size=8.5,
    table_header_background_color='#edf1f2',
    table_header_text_color='#19324a',
    quote_inset=0.55,
    quote_border_color='#2f665c',
    quote_background_color='#f5f7f8',
    quote_text_color='#171717',
    quote_text_size=9,
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
    table_inset=6,
    table_stroke_color='#000000',
    table_text_color='#000000',
    table_text_size=10.5,
    table_header_background_color='#ffffff',
    table_header_text_color='#000000',
    quote_inset=0.75,
    quote_border_color='#000000',
    quote_background_color='#ffffff',
    quote_text_color='#000000',
    quote_text_size=11,
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
    table_inset=6,
    table_stroke_color='#c8d0d8',
    table_text_color='#111111',
    table_text_size=11,
    table_header_background_color='#f7f7f7',
    table_header_text_color='#111111',
    quote_inset=0.65,
    quote_border_color='#111111',
    quote_background_color='#ffffff',
    quote_text_color='#111111',
    quote_text_size=12,
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
    table_inset=8,
    table_stroke_color='#d3dae2',
    table_text_color='#1c2433',
    table_text_size=10,
    table_header_background_color='#204a66',
    table_header_text_color='#ffffff',
    quote_inset=0.85,
    quote_border_color='#2c7280',
    quote_background_color='#eef4fb',
    quote_text_color='#1c2433',
    quote_text_size=10.5,
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
    table_inset=7,
    table_stroke_color='#c8d0d8',
    table_text_color='#17202c',
    table_text_size=9.5,
    table_header_background_color='#e8f4f8',
    table_header_text_color='#17496b',
    quote_inset=0.85,
    quote_border_color='#286c7d',
    quote_background_color='#eef7ff',
    quote_text_color='#17202c',
    quote_text_size=10,
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
    table_inset=6,
    table_stroke_color='#d6cfc3',
    table_text_color='#151515',
    table_text_size=10.5,
    table_header_background_color='#f1ebe1',
    table_header_text_color='#252525',
    quote_inset=1.2,
    quote_border_color='#d6cfc3',
    quote_background_color='#ffffff',
    quote_text_color='#151515',
    quote_text_size=11,
  ),
  'accesibilidad_neurodivergencia': PdfStyleOptions(
    font_family='Verdana',
    body_font_size=13.5,
    body_color='#333333',
    page_background_color='#fbf6e8',
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
    table_inset=9,
    table_stroke_color='#b8cbc6',
    table_text_color='#333333',
    table_text_size=13,
    table_header_background_color='#e8f4ec',
    table_header_text_color='#24435a',
    quote_inset=0.95,
    quote_border_color='#6aa38f',
    quote_background_color='#e8f4ec',
    quote_text_color='#333333',
    quote_text_size=13.5,
  ),
}


def template_style_preset(template_id: str) -> PdfStyleOptions:
  '''Devuelve los ajustes de diseño iniciales de una plantilla.'''

  normalized_id = template_id.strip().lower() or DEFAULT_TEMPLATE_ID
  if normalized_id in TEMPLATE_STYLE_PRESETS:
    return TEMPLATE_STYLE_PRESETS[normalized_id]

  metadata = template_metadata(normalized_id)
  style_data = metadata.get('style')
  if isinstance(style_data, dict):
    return style_options_from_data(style_data)

  return PdfStyleOptions()


def user_data_dir() -> Path:
  '''Devuelve la carpeta de datos de usuario de la app.'''

  override = os.environ.get(USER_DATA_ENV_VAR)
  if override:
    return Path(override).expanduser()

  appdata = os.environ.get('APPDATA')
  if appdata:
    return Path(appdata) / 'pdf_apuntes'

  return Path.home() / '.pdf_apuntes'


def user_templates_dir() -> Path:
  '''Devuelve la carpeta de plantillas creadas por el usuario.'''

  return user_data_dir() / 'templates'


def template_metadata_path(template_id: str) -> Path | None:
  '''Busca los metadatos de una plantilla personalizada.'''

  normalized_id = template_id.strip().lower() or DEFAULT_TEMPLATE_ID
  user_metadata = user_templates_dir() / f'{normalized_id}.json'
  if user_metadata.exists():
    return user_metadata

  legacy_metadata = APP_TEMPLATES_DIR / f'{normalized_id}.json'
  if legacy_metadata.exists():
    return legacy_metadata

  return None


def style_options_from_data(data: dict[str, object]) -> PdfStyleOptions:
  '''Construye opciones visuales ignorando claves desconocidas.'''

  field_names = {field.name for field in fields(PdfStyleOptions)}
  values = {
    key: value
    for key, value in data.items()
    if key in field_names
  }
  return PdfStyleOptions(**values)


def template_metadata(template_id: str) -> dict[str, object]:
  '''Lee los metadatos opcionales de una plantilla de la app.'''

  metadata_file = template_metadata_path(template_id)
  if metadata_file is None:
    return {}

  try:
    data = json.loads(metadata_file.read_text(encoding='utf-8'))
  except (OSError, json.JSONDecodeError):
    return {}

  if isinstance(data, dict):
    return data
  return {}


def template_label(template_id: str) -> str | None:
  '''Devuelve el nombre visible de una plantilla personalizada si existe.'''

  label = template_metadata(template_id).get('label')
  if isinstance(label, str) and label.strip():
    return label.strip()
  return None


def template_description(template_id: str) -> str | None:
  '''Devuelve la descripción de una plantilla personalizada si existe.'''

  description = template_metadata(template_id).get('description')
  if isinstance(description, str) and description.strip():
    return description.strip()
  return None


def is_custom_template(template_id: str) -> bool:
  '''Indica si una plantilla tiene metadatos editables de usuario.'''

  normalized_id = template_id.strip().lower() or DEFAULT_TEMPLATE_ID
  return (
    normalized_id not in TEMPLATE_STYLE_PRESETS
    and template_metadata_path(normalized_id) is not None
  )


def save_custom_template(
  template_id: str,
  label: str,
  style: PdfStyleOptions,
  source_template_id: str,
) -> None:
  '''Guarda una plantilla personalizada basada en la plantilla actual.'''

  normalized_id = template_id.strip().lower()
  if not normalized_id:
    raise PdfBuildError('El identificador de la plantilla no puede estar vacío.')

  user_template_dir = user_templates_dir()
  user_template_dir.mkdir(parents=True, exist_ok=True)
  source_template = template_path(source_template_id)
  target_template = user_template_dir / f'{normalized_id}.typ'
  target_metadata = user_template_dir / f'{normalized_id}.json'
  legacy_template = APP_TEMPLATES_DIR / f'{normalized_id}.typ'
  legacy_metadata = APP_TEMPLATES_DIR / f'{normalized_id}.json'
  if (
    target_template.exists()
    or target_metadata.exists()
    or legacy_template.exists()
    or legacy_metadata.exists()
  ):
    raise PdfBuildError(f'Ya existe una plantilla con ese identificador: {normalized_id}')

  target_template.write_text(source_template.read_text(encoding='utf-8'), encoding='utf-8')
  metadata = {
    'label': label.strip(),
    'description': 'Plantilla personalizada.',
    'source_template': source_template_id,
    'style': asdict(style),
  }
  target_metadata.write_text(
    json.dumps(metadata, ensure_ascii=False, indent=2),
    encoding='utf-8',
  )


def update_custom_template_style(template_id: str, style: PdfStyleOptions) -> None:
  '''Actualiza los ajustes visuales de una plantilla personalizada existente.'''

  normalized_id = template_id.strip().lower()
  if not is_custom_template(normalized_id):
    raise PdfBuildError('Solo se pueden actualizar plantillas personalizadas.')

  metadata_file = template_metadata_path(normalized_id)
  if metadata_file is None:
    raise PdfBuildError('No se encontraron los metadatos de la plantilla.')

  metadata = template_metadata(normalized_id)
  metadata['style'] = asdict(style)
  metadata_file.write_text(
    json.dumps(metadata, ensure_ascii=False, indent=2),
    encoding='utf-8',
  )


def migrate_legacy_custom_templates() -> None:
  '''Copia plantillas personalizadas antiguas a la carpeta de usuario.'''

  if not APP_TEMPLATES_DIR.exists():
    return

  target_dir = user_templates_dir()
  for metadata_file in APP_TEMPLATES_DIR.glob('*.json'):
    template_id = metadata_file.stem
    if template_id in TEMPLATE_STYLE_PRESETS:
      continue

    source_template = APP_TEMPLATES_DIR / f'{template_id}.typ'
    if not source_template.exists():
      continue

    target_template = target_dir / source_template.name
    target_metadata = target_dir / metadata_file.name
    if target_template.exists() or target_metadata.exists():
      continue

    target_dir.mkdir(parents=True, exist_ok=True)
    target_template.write_text(
      source_template.read_text(encoding='utf-8'),
      encoding='utf-8',
    )
    target_metadata.write_text(metadata_file.read_text(encoding='utf-8'), encoding='utf-8')


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

  migrate_legacy_custom_templates()

  templates = set()
  if APP_TEMPLATES_DIR.exists():
    templates.update(template.stem for template in APP_TEMPLATES_DIR.glob('*.typ'))
  current_user_templates_dir = user_templates_dir()
  if current_user_templates_dir.exists():
    templates.update(template.stem for template in current_user_templates_dir.glob('*.typ'))
  return sorted(templates)


def template_path(template_id: str) -> Path:
  '''Devuelve la ruta de una plantilla de la app validando su existencia.'''

  normalized_id = template_id.strip().lower() or DEFAULT_TEMPLATE_ID
  app_template = APP_TEMPLATES_DIR / f'{normalized_id}.typ'
  if app_template.exists():
    return app_template

  user_template = user_templates_dir() / f'{normalized_id}.typ'
  if user_template.exists():
    return user_template

  raise PdfBuildError(f'No existe la plantilla de la app: {app_template}')


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
  page_background = normalize_hex_color(style.page_background_color)
  if '__PAGE_BACKGROUND_COLOR__' not in template_text:
    template_text = template_text.replace(
      'margin: (x: __PAGE_MARGIN_X__mm, y: __PAGE_MARGIN_Y__mm),',
      (
        'margin: (x: __PAGE_MARGIN_X__mm, y: __PAGE_MARGIN_Y__mm),\n'
        f'  fill: rgb("{page_background}"),'
      ),
      1,
    )
  replacements = {
    '__BODY_FONT__': style.font_family,
    '__BODY_FONT_SIZE__': f'{style.body_font_size:g}',
    '__BODY_COLOR__': normalize_hex_color(style.body_color),
    '__PAGE_BACKGROUND_COLOR__': page_background,
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
    '__TABLE_INSET__': f'{style.table_inset:g}',
    '__TABLE_STROKE_COLOR__': normalize_hex_color(style.table_stroke_color),
    '__TABLE_TEXT_COLOR__': normalize_hex_color(style.table_text_color),
    '__TABLE_TEXT_SIZE__': f'{style.table_text_size:g}',
    '__TABLE_HEADER_BACKGROUND_COLOR__': normalize_hex_color(
      style.table_header_background_color
    ),
    '__TABLE_HEADER_TEXT_COLOR__': normalize_hex_color(style.table_header_text_color),
    '__QUOTE_INSET__': f'{style.quote_inset:g}',
    '__QUOTE_BORDER_COLOR__': normalize_hex_color(style.quote_border_color),
    '__QUOTE_BACKGROUND_COLOR__': normalize_hex_color(style.quote_background_color),
    '__QUOTE_TEXT_COLOR__': normalize_hex_color(style.quote_text_color),
    '__QUOTE_TEXT_SIZE__': f'{style.quote_text_size:g}',
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


def prepare_markdown_source(source: Path) -> tuple[Path, dict[str, str]]:
  '''Normaliza casos Markdown/HTML que Pandoc no conserva al convertir a Typst.'''

  markdown_text = source.read_text(encoding='utf-8')
  markdown_text, mark_replacements = extract_mark_tags(markdown_text)
  markdown_text = normalize_basic_html(markdown_text)
  markdown_text = normalize_github_admonitions(markdown_text)
  markdown_text = normalize_toc_and_pagebreaks(markdown_text)

  temp_file = tempfile.NamedTemporaryFile(
    mode='w',
    encoding='utf-8',
    delete=False,
    dir=source.parent,
    prefix=f'{source.stem}_processed_',
    suffix=source.suffix,
  )
  with temp_file:
    temp_file.write(markdown_text)
  return Path(temp_file.name), mark_replacements


def extract_mark_tags(markdown_text: str) -> tuple[str, dict[str, str]]:
  '''Extrae `<mark>` para convertirlo después en resaltado Typst.'''

  replacements: dict[str, str] = {}

  def replace_mark(match: re.Match[str]) -> str:
    token = f'{HTML_MARK_TOKEN_PREFIX}{len(replacements)}'
    replacements[token] = match.group(1).strip()
    return token

  markdown_text = re.sub(
    r'<mark\b[^>]*>(.*?)</mark>',
    replace_mark,
    markdown_text,
    flags=re.IGNORECASE | re.DOTALL,
  )
  return markdown_text, replacements


def normalize_basic_html(markdown_text: str) -> str:
  '''Convierte HTML inline básico a Markdown equivalente.'''

  replacements = [
    (r'<(?:strong|b)\b[^>]*>(.*?)</(?:strong|b)>', r'**\1**'),
    (r'<(?:em|i)\b[^>]*>(.*?)</(?:em|i)>', r'*\1*'),
  ]
  for pattern, replacement in replacements:
    markdown_text = re.sub(
      pattern,
      replacement,
      markdown_text,
      flags=re.IGNORECASE | re.DOTALL,
    )

  return re.sub(r'<br\s*/?>', '  \n', markdown_text, flags=re.IGNORECASE)


def normalize_github_admonitions(markdown_text: str) -> str:
  '''Convierte alertas tipo GitHub en citas Markdown legibles.'''

  output_lines: list[str] = []
  for line in markdown_text.splitlines():
    match = re.match(r'^(>\s*)\[!(\w+)\]\s*$', line, flags=re.IGNORECASE)
    if not match:
      output_lines.append(line)
      continue

    quote_prefix = match.group(1)
    admonition_type = match.group(2).upper()
    label = ADMONITION_STYLES.get(
      admonition_type,
      (admonition_type.title(), '#57606a', 'note.svg'),
    )[0]
    output_lines.append(f'{quote_prefix}**MDPDFALERT-{admonition_type} {label}**')
    output_lines.append(quote_prefix.rstrip())

  return '\n'.join(output_lines) + ('\n' if markdown_text.endswith('\n') else '')


def normalize_toc_and_pagebreaks(markdown_text: str) -> str:
  '''Marca `[TOC]` y `<!-- pagebreak -->` para convertirlos a Typst real.'''

  markdown_text = re.sub(
    r'(?im)^\s*\[TOC\]\s*$',
    TOC_TOKEN,
    markdown_text,
  )
  return re.sub(
    r'(?i)<!--\s*pagebreak\s*-->',
    PAGEBREAK_TOKEN,
    markdown_text,
  )


def apply_mark_replacements(typ_file: Path, replacements: dict[str, str]) -> None:
  '''Inserta resaltados Typst en los tokens generados para `<mark>`.'''

  if not replacements:
    return

  typ_text = typ_file.read_text(encoding='utf-8')
  for token, content in replacements.items():
    typ_text = typ_text.replace(token, f'#highlight[{escape_typst_content(content)}]')
  typ_file.write_text(typ_text, encoding='utf-8')


def apply_special_markdown_tokens(typ_file: Path) -> None:
  '''Convierte tokens de Markdown extendido en instrucciones Typst.'''

  typ_text = typ_file.read_text(encoding='utf-8')
  typ_text = typ_text.replace(
    TOC_TOKEN,
    '\n\n#block(above: 1em, below: 1em)[\n  #outline(title: [Índice])\n]\n\n',
  )
  break_command = '#colbreak()' if '#columns(' in typ_text else '#pagebreak()'
  typ_text = typ_text.replace(PAGEBREAK_TOKEN, f'\n{break_command}\n')
  typ_file.write_text(typ_text, encoding='utf-8')


def apply_github_admonition_styles(typ_file: Path) -> None:
  '''Maqueta alertas tipo GitHub como bloques coloreados.'''

  typ_text = typ_file.read_text(encoding='utf-8')

  def replace_admonition(match: re.Match[str]) -> str:
    admonition_type = match.group(1).upper()
    label = match.group(2).strip()
    body = match.group(3).strip()
    _default_label, color, icon_file = ADMONITION_STYLES.get(
      admonition_type,
      (label, '#57606a', 'note.svg'),
    )
    icon_path = f'/assets/icons/{icon_file}'
    return (
      '#block(\n'
      '  above: 0.9em,\n'
      '  below: 0.9em,\n'
      '  inset: (left: 0.9em, right: 0em, top: 0.25em, bottom: 0.25em),\n'
      '  stroke: (left: 3pt + rgb("' + color + '")),\n'
      ')[\n'
      '  #box(width: 9pt, height: 9pt, image("' + icon_path + '", width: 9pt))\n'
      '  #h(0.22em)\n'
      '  #text(weight: "bold", fill: rgb("' + color + '"))[' + label + ']\n'
      '  #v(0.55em)\n'
      f'  {body}\n'
      ']'
    )

  typ_text = re.sub(
    r'#quote\(block: true\)\[\s*#strong\[MDPDFALERT-([A-Z]+) ([^\]]+)\]\s*(.*?)\n\]',
    replace_admonition,
    typ_text,
    flags=re.DOTALL,
  )
  typ_file.write_text(typ_text, encoding='utf-8')


def escape_typst_content(content: str) -> str:
  '''Escapa texto simple para introducirlo dentro de contenido Typst.'''

  return (
    content
    .replace('\\', '\\\\')
    .replace('#', '\\#')
    .replace('[', '\\[')
    .replace(']', '\\]')
  )


def apply_table_width_mode(typ_file: Path, style: PdfStyleOptions) -> None:
  '''Ajusta columnas de tablas generadas por Pandoc.'''

  if style.table_width_mode != 'full':
    return

  typ_text = typ_file.read_text(encoding='utf-8')
  typ_text = re.sub(
    r'(#table\(\n\s*columns:\s*)(\d+)(\s*,)',
    r'\1(1fr,) * \2\3',
    typ_text,
  )
  typ_file.write_text(typ_text, encoding='utf-8')


def run_command(command: list[str | Path]) -> None:
  '''Ejecuta un comando externo y convierte errores en `PdfBuildError`.'''

  creation_flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
  completed = subprocess.run(
    [str(part) for part in command],
    cwd=ROOT_DIR,
    text=True,
    encoding='utf-8',
    errors='replace',
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
  processed_source, mark_replacements = prepare_markdown_source(source)
  typ_file = source.with_suffix('.typ')
  pdf_file = source.with_suffix('.pdf')

  pandoc = find_executable('pandoc')
  typst = find_executable('typst')

  try:
    run_command(
      [
        pandoc,
        processed_source,
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
    apply_mark_replacements(typ_file, mark_replacements)
    apply_special_markdown_tokens(typ_file)
    apply_github_admonition_styles(typ_file)
    apply_table_width_mode(typ_file, style or PdfStyleOptions())
    run_command([typst, 'compile', '--root', ROOT_DIR, typ_file, pdf_file])
  finally:
    if template_file.exists():
      template_file.unlink()
    if processed_source.exists():
      processed_source.unlink()

  if typ_file.exists():
    typ_file.unlink()

  return PdfResult(
    input_file=source,
    template_file=source_template_file,
    pdf_file=pdf_file,
    typ_file=typ_file,
  )
