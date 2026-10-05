local default_width = 'auto'

local function point_value(value, name, allow_zero)
  local number = tonumber(value:match('^([%d.]+)pt$') or value)
  if not number or number == math.huge or number < 0 or
      (number == 0 and not allow_zero) then
    error('Tabla: ' .. name .. ' debe ser un numero ' ..
      (allow_zero and 'mayor o igual que cero' or 'mayor que cero') ..
      ', en puntos. Ejemplo: ' .. name .. '=8pt.')
  end
  return tostring(number) .. 'pt'
end

local function configure_columns(tbl, attributes)
  local mode = attributes['table-width'] or default_width
  if mode ~= 'auto' and mode ~= 'full' then
    error('Tabla: usa table-width=auto o table-width=full.')
  end

  local weights = {}
  if attributes.columns then
    for value in (attributes.columns .. ','):gmatch('(.-),') do
      local number = tonumber(value)
      if not number or number <= 0 or number == math.huge then
        error('Tabla: columns debe contener proporciones positivas, como columns="1,3,2".')
      end
      weights[#weights + 1] = number
    end
    if #weights ~= #tbl.colspecs then
      error('Tabla: columns debe indicar una proporcion por columna (' .. #tbl.colspecs .. ').')
    end
  elseif attributes['table-width'] or mode == 'full' then
    -- Preserve explicit Markdown column widths unless the local mode overrides them.
    local has_width = false
    for _, spec in ipairs(tbl.colspecs) do
      has_width = has_width or (spec[2] or 0) > 0
    end
    if attributes['table-width'] or not has_width then
      for i = 1, #tbl.colspecs do
        weights[i] = mode == 'full' and 1 or 0
      end
    end
  end

  if #weights > 0 then
    local total = 0
    for _, weight in ipairs(weights) do total = total + weight end
    if total == math.huge then error('Tabla: las proporciones de columns son demasiado grandes.') end
    local specs = {}
    for i, weight in ipairs(weights) do
      specs[i] = {tbl.colspecs[i][1]}
      if total > 0 then specs[i][2] = weight / total end
    end
    tbl.colspecs = specs
  end
  return tbl
end

local function style_table(div)
  if not div.classes:includes('table-style') then return end
  if #div.content ~= 1 or div.content[1].t ~= 'Table' then
    error('El bloque table-style debe contener exactamente una tabla Markdown.')
  end
  local allowed = {['font-size'] = true, ['cell-padding'] = true,
    ['table-width'] = true, columns = true}
  for key in pairs(div.attributes) do
    if not allowed[key] then error('Tabla: opcion desconocida: ' .. key .. '.') end
  end

  local tbl = configure_columns(div.content[1], div.attributes)
  local rules = {'#['}
  if div.attributes['font-size'] then
    rules[#rules + 1] = '#show table.cell: set text(size: ' ..
      point_value(div.attributes['font-size'], 'font-size', false) .. ')'
  end
  if div.attributes['cell-padding'] then
    tbl.attributes['typst:inset'] = point_value(div.attributes['cell-padding'], 'cell-padding', true)
  end
  if div.identifier ~= '' and tbl.identifier == '' then tbl.identifier = div.identifier end
  return {
    pandoc.RawBlock('typst', table.concat(rules, '\n')),
    tbl,
    pandoc.RawBlock('typst', ']'),
  }, false
end

return {
  {Meta = function(meta)
    if meta['mdpdf-table-width'] then
      default_width = pandoc.utils.stringify(meta['mdpdf-table-width'])
    end
  end},
  {traverse = 'topdown', Div = style_table,
    Table = function(tbl) return configure_columns(tbl, {}) end},
}
