import unittest

from app.source_navigation import block_at, source_line_map, text_digest


class SourceNavigationTests(unittest.TestCase):
  def test_line_mapping_after_alert_expansion(self):
    original = '# Title\n\n> [!NOTE]\n> Body\n\n## Next\n'
    processed = '# Title\n\n> **Note**\n>\n> Body\n\n## Next\n'
    mapping = source_line_map(original, processed)
    self.assertEqual(mapping[2], 3)
    self.assertEqual(mapping[4], 4)
    self.assertEqual(mapping[6], 6)

  def test_digest_tracks_content_not_line_endings(self):
    self.assertEqual(text_digest('a\r\nb'), text_digest('a\nb'))
    self.assertNotEqual(text_digest('a\nb'), text_digest('a\nc'))

  def test_blocks_cross_pages_and_columns(self):
    block = {'start': {'page': 1, 'x': 30, 'y': 700},
             'end': {'page': 2, 'x': 30, 'y': 120}, 'first': 4, 'last': 9}
    data = {'columns': 1, 'margin_x': 30, 'margin_y': 30, 'blocks': [block]}
    pages = [(600, 800), (600, 800)]
    self.assertIs(block_at(data, 0, 200, 730, pages), block)
    self.assertIs(block_at(data, 1, 200, 60, pages), block)
    self.assertIsNone(block_at(data, 1, 200, 150, pages))
    self.assertIsNone(block_at(data, 0, 10, 730, pages))
    block['end'] = {'page': 1, 'x': 320, 'y': 120}
    data['columns'] = 2
    self.assertIs(block_at(data, 0, 400, 60, pages), block)
    self.assertIsNone(block_at(data, 0, 100, 60, pages))


if __name__ == '__main__':
  unittest.main()
