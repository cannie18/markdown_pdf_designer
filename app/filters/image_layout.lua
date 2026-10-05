-- Align standalone images without changing inline images or parsing Markdown.
local function aligned_image_block(block, image)
  local alignment = image.attributes.align or 'center'
  if alignment ~= 'left' and alignment ~= 'center' and alignment ~= 'right' then
    error('Alineacion de imagen no valida: ' .. alignment ..
      '. Usa align=left, align=center o align=right.')
  end

  return {
    pandoc.RawBlock('typst', '#align(' .. alignment .. ')[\n' ..
      '#show figure.where(kind: image): set align(' .. alignment .. ')'),
    block,
    pandoc.RawBlock('typst', ']'),
  }
end

local function align_figure(figure)
  if #figure.content == 1 then
    local paragraph = figure.content[1]
    if (paragraph.t == 'Plain' or paragraph.t == 'Para') and
        #paragraph.content == 1 and paragraph.content[1].t == 'Image' then
      return aligned_image_block(figure, paragraph.content[1]), false
    end
  end
end

local function align_paragraph(paragraph)
  if #paragraph.content == 1 and paragraph.content[1].t == 'Image' then
    return aligned_image_block(paragraph, paragraph.content[1]), false
  end
end

return {{
  traverse = 'topdown',
  Figure = align_figure,
  Para = align_paragraph,
  Plain = align_paragraph,
}}
