import subprocess
import unittest

from app.pdf_builder import ROOT_DIR, find_executable


TABLE = '| ID | Description | State |\n| --- | --- | --- |\n| 1 | Long text | Open |'


class TableLayoutTests(unittest.TestCase):
  def convert(self, markdown: str, mode: str = 'auto') -> subprocess.CompletedProcess[str]:
    return subprocess.run(
      [str(find_executable('pandoc')), '-f', 'markdown', '-t', 'typst',
       f'--lua-filter={ROOT_DIR / "app" / "filters" / "table_layout.lua"}',
       '-M', f'mdpdf-table-width={mode}'],
      input=markdown, capture_output=True, text=True, encoding='utf-8', check=False,
    )

  def test_global_mode_applies_to_unstyled_tables(self):
    for mode, columns in [('auto', 'columns: 3,'), ('full', 'columns: (33.33%, 33.33%, 33.33%),')]:
      with self.subTest(mode=mode):
        result = self.convert(TABLE, mode)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(columns, result.stdout)

  def test_local_styles_override_global_mode_without_affecting_next_table(self):
    result = self.convert(
      '::: {.table-style font-size=8pt cell-padding=0pt table-width=auto}\n\n'
      + TABLE + '\n\n:::\n\n' + TABLE, 'full'
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertIn('columns: 3,', result.stdout)
    self.assertIn('columns: (33.33%, 33.33%, 33.33%),', result.stdout)
    self.assertEqual(result.stdout.count('inset: 0pt,'), 1)
    self.assertIn('#show table.cell: set text(size: 8pt)', result.stdout)
    self.assertLess(result.stdout.index('\n]\n'), result.stdout.rindex('#figure('))

  def test_relative_columns_preserve_alignment_and_caption(self):
    result = self.convert(
      '::: {.table-style columns="1,3,2"}\n\n'
      + TABLE.replace('| --- | --- | --- |', '| ---: | :--- | :---: |')
      + '\n\n: Table caption\n\n:::'
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertIn('columns: (16.67%, 50%, 33.33%),', result.stdout)
    self.assertIn('align: (right,left,center,)', result.stdout)
    self.assertIn('Table caption', result.stdout)

  def test_invalid_options_are_reported(self):
    for options, message in [
      ('columns="1,2"', 'una proporcion por columna'),
      ('columns="1,0,2"', 'proporciones positivas'),
      ('columns="1,,2"', 'proporciones positivas'),
      ('font-size=0pt', 'font-size debe ser'),
      ('font-size=abc', 'font-size debe ser'),
      ('cell-padding=-1pt', 'cell-padding debe ser'),
      ('table-width=other', 'table-width=auto o table-width=full'),
      ('unknown=8', 'opcion desconocida'),
    ]:
      with self.subTest(options=options):
        result = self.convert('::: {.table-style ' + options + '}\n\n' + TABLE + '\n\n:::')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr)

  def test_style_block_requires_one_table(self):
    result = self.convert('::: {.table-style}\n\nNot a table\n\n:::')
    self.assertNotEqual(result.returncode, 0)
    self.assertIn('exactamente una tabla', result.stderr)

  def test_literal_example_is_not_interpreted(self):
    result = self.convert('```markdown\n::: {.table-style font-size=8pt}\n\n' + TABLE + '\n\n:::\n```')
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertNotIn('#show table.cell:', result.stdout)
    self.assertIn('font-size=8pt', result.stdout)


if __name__ == '__main__':
  unittest.main()
