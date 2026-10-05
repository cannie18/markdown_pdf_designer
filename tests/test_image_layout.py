import subprocess
import unittest

from app.pdf_builder import ROOT_DIR, find_executable


class ImageLayoutTests(unittest.TestCase):
  def convert(self, markdown: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
      [
        str(find_executable('pandoc')),
        '-f', 'markdown', '-t', 'typst',
        f'--lua-filter={ROOT_DIR / "app" / "filters" / "image_layout.lua"}',
      ],
      input=markdown,
      capture_output=True,
      text=True,
      encoding='utf-8',
      check=False,
    )

  def test_standalone_images_centered_with_and_without_caption(self):
    for caption in ('', 'Caption'):
      with self.subTest(caption=caption):
        result = self.convert(f'![{caption}](image.svg){{width=50%}}')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('#align(center)[', result.stdout)
        self.assertIn('width: 50%', result.stdout)
        if caption:
          self.assertIn('caption:', result.stdout)
          self.assertIn('Caption', result.stdout)

  def test_alignment_in_nested_blocks_preserves_size(self):
    for alignment in ('left', 'center', 'right'):
      for prefix in ('', '> ', '- '):
        for caption in ('', 'Caption'):
          with self.subTest(alignment=alignment, prefix=prefix, caption=caption):
            result = self.convert(
              prefix + f'![{caption}](image.svg){{width=5cm height=2cm align={alignment}}}'
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.count(f'#align({alignment})['), 1)
            self.assertIn('width: 5cm', result.stdout)
            self.assertIn('height: 2cm', result.stdout)

  def test_inline_images_and_code_are_not_aligned(self):
    result = self.convert(
      'Before ![](image.svg){width=2cm} after.\n\n'
      '```markdown\n![](image.svg){width=50% align=right}\n```'
    )
    self.assertEqual(result.returncode, 0, result.stderr)
    self.assertNotIn('#align(', result.stdout)
    self.assertIn('Before #box(image(', result.stdout)
    self.assertIn('align=right', result.stdout)

  def test_invalid_alignment_reports_allowed_values(self):
    result = self.convert('![](image.svg){align=middle}')
    self.assertNotEqual(result.returncode, 0)
    self.assertIn('align=left, align=center o align=right', result.stderr)


if __name__ == '__main__':
  unittest.main()
