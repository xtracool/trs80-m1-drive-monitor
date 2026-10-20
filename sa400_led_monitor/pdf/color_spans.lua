-- color_spans.lua — pandoc Lua filter for the test-plan PDF.
-- Markdown  <span style="color:#rrggbb">…</span>  ->  LaTeX  \textcolor[HTML]{RRGGBB}{…}
-- pandoc parses the HTML span as a native Span (native_spans is on by default); the raw-inline
-- branch covers a span that pandoc could not pair up.  Needs \usepackage{xcolor} in the header.

local function hex_of(style)
  if not style then return nil end
  local h = style:match("color:%s*#(%x%x%x%x%x%x)")
  return h and h:upper() or nil
end

function Span(el)
  local hex = hex_of(el.attributes["style"])
  if not hex then return nil end
  local out = pandoc.List({ pandoc.RawInline("latex", "\\textcolor[HTML]{" .. hex .. "}{") })
  out:extend(el.content)
  out:insert(pandoc.RawInline("latex", "}"))
  return out
end

function RawInline(el)
  if el.format ~= "html" then return nil end
  local hex = hex_of(el.text:match('^<span%s+style="([^"]*)"%s*>$'))
  if hex then return pandoc.RawInline("latex", "\\textcolor[HTML]{" .. hex .. "}{") end
  if el.text:match("^</span>$") then return pandoc.RawInline("latex", "}") end
  return nil
end
