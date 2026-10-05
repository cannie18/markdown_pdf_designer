-- Use a source-position parser only to locate blocks; keep the Markdown reader
-- used for rendering and omit blocks that cannot be matched confidently.
local function signature(block)
  if block.t == 'CodeBlock' then return block.text:gsub('%s+', '') end
  return pandoc.utils.stringify(block):gsub('%s+', '')
end

local function source_range(block)
  local position = block.attributes and block.attributes['data-pos']
  if not position then return end
  local first, last
  for start_line, end_line, end_column in position:gmatch('(%d+):%d+%-(%d+):(%d+)') do
    start_line, end_line, end_column = tonumber(start_line), tonumber(end_line), tonumber(end_column)
    first = math.min(first or start_line, start_line)
    last = math.max(last or start_line, end_column == 1 and end_line - 1 or end_line)
  end
  if first then return first, math.max(first, last) end
end

local function marker(id, edge, first, last)
  return pandoc.RawBlock('typst', string.format(
    '#context [#metadata((block: %d, edge: "%s", first: %d, last: %d, ' ..
    'page: here().page(), x: here().position().x / 1pt, ' ..
    'y: here().position().y / 1pt)) <mdpdf-source>]', id, edge, first, last))
end

function Pandoc(doc)
  local file = assert(io.open(PANDOC_STATE.input_files[1], 'r'))
  local source = file:read('*a')
  file:close()
  local positioned = pandoc.read(source, 'commonmark_x+sourcepos+implicit_figures')
  local candidates = {}
  for _, block in ipairs(positioned.blocks) do
    local first, last = source_range(block)
    if first then
      candidates[#candidates + 1] = {first = first, last = last, text = signature(block)}
    end
  end

  local output, next_candidate = {}, 1
  for id, block in ipairs(doc.blocks) do
    local match
    local text = signature(block)
    if text ~= '' and text ~= 'MDPDFPAGEBREAK' then
      for i = next_candidate, #candidates do
        if candidates[i].text == text then
          match = candidates[i]
          next_candidate = i + 1
          if candidates[i + 1] then match.last = math.min(match.last, candidates[i + 1].first - 1) end
          break
        end
      end
    end
    if match then output[#output + 1] = marker(id, 'start', match.first, match.last) end
    output[#output + 1] = block
    if match then output[#output + 1] = marker(id, 'end', match.first, match.last) end
  end
  doc.blocks = output
  return doc
end
