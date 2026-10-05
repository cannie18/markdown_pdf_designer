'''Correspondencia entre bloques Markdown y posiciones de la vista previa.'''

import hashlib
from difflib import SequenceMatcher


def text_digest(text: str) -> str:
  return hashlib.sha256(text.replace('\r\n', '\n').encode('utf-8')).hexdigest()


def source_line_map(original: str, processed: str) -> list[int]:
  original_lines, processed_lines = original.splitlines(), processed.splitlines()
  result = [1] * len(processed_lines)
  for _, a, b, c, d in SequenceMatcher(None, original_lines, processed_lines, autojunk=False).get_opcodes():
    for index in range(c, d):
      result[index] = min(max(1, len(original_lines)), a + min(index - c, max(0, b - a - 1)) + 1)
  return result


def navigation_map(markers: list[dict], original: str, processed: str, columns: int,
                   margin_x: float, margin_y: float) -> dict:
  lines = source_line_map(original, processed)
  blocks = {}
  for marker in markers:
    block = blocks.setdefault(marker['block'], {})
    block[marker['edge']] = {key: marker[key] for key in ('page', 'x', 'y')}
    block['first'] = lines[min(len(lines) - 1, marker['first'] - 1)] if lines else 1
    block['last'] = lines[min(len(lines) - 1, marker['last'] - 1)] if lines else 1
  return {'digest': text_digest(original), 'columns': columns, 'margin_x': margin_x,
          'margin_y': margin_y, 'blocks': [block for block in blocks.values()
                                        if 'start' in block and 'end' in block]}


def block_at(data: dict, page: int, x: float, y: float, page_sizes: list[tuple[float, float]]) -> dict | None:
  '''Localiza un bloque en orden de lectura, incluyendo columnas y varias paginas.'''

  width, height = page_sizes[page]
  margin_x, margin_y = data['margin_x'], data['margin_y']
  if not (margin_x <= x <= width - margin_x and margin_y <= y <= height - margin_y):
    return None
  columns = data['columns']

  def key(position):
    page_index = position['page'] - 1
    page_width = page_sizes[page_index][0]
    column = min(columns - 1, max(0, int((position['x'] - margin_x) /
                                       ((page_width - 2 * margin_x) / columns))))
    return page_index, column, position['y']

  clicked = key({'page': page + 1, 'x': x, 'y': y})
  for block in data['blocks']:
    if key(block['start']) <= clicked < key(block['end']):
      return block
  return None
