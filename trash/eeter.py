from fontTools.ttLib import TTFont, newTable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from PIL import Image

# --- CONFIG ---
spritesheet_path = "edited_image.png"  # your sheet
glyph_order = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,:;!?()[]{}=+-%*/\\_\"abcdefghijklmnopqrstuvwxyz"  # order of chars in sheet
sprite_width = 3
sprite_height = 5
spacing = 0  # pixels between sprites if any
em = 1000
scale = em // sprite_height  # scale each pixel to fit font height

# --- LOAD TEMPLATE FONT ---
template_font = TTFont("pXld.ttf")
font = TTFont()
for tag in template_font.keys():
    if tag not in ("glyf", "hmtx", "cmap", "maxp"):
        font[tag] = template_font[tag]


font.setGlyphOrder([".notdef"] + list(glyph_order + " "))  # + space
# --- LOAD IMAGE ---
sheet = Image.open(spritesheet_path).convert("RGBA")

# --- CREATE GLYPHS ---
font['glyf'] = newTable('glyf')
font['glyf'].glyphs = {}
font['hmtx'] = newTable('hmtx')
font['hmtx'].metrics = {}

for i, char in enumerate(glyph_order):
    pen = TTGlyphPen(None)
    x_offset = i * (sprite_width + spacing)
    if char in "abcdefghijklmnopqrstuvwxyz":
        x_offset -= (sprite_width + spacing) * glyph_order.index('a')  # shift lowercase to uppercase
    print("DEBUG:   ", char, x_offset)
    for y in range(sprite_height):
        for x in range(sprite_width):
            pixel = sheet.getpixel((x_offset + x, y))
            if pixel[3] > 0:  # non-transparent
                x0 = x * scale
                y0 = (sprite_height - y - 2) * scale  # <-- moved up by 1 pixel
                x1 = x0 + scale
                y1 = y0 + scale
                pen.moveTo((x0, y0))
                pen.lineTo((x1, y0))
                pen.lineTo((x1, y1))
                pen.lineTo((x0, y1))
                pen.closePath()
                
    glyph = pen.glyph()
    font['glyf'].glyphs[char] = glyph
    font['hmtx'].metrics[char] = ((sprite_width+1) * scale, 0)

glyph_order = glyph_order + " "  # add space to order

# After your glyph loop, but before saving:
if " " in font['glyf'].glyphs:
    font['hmtx'].metrics[" "] = ((sprite_width+1) * scale, 0)
if " " not in font['glyf'].glyphs:
    pen = TTGlyphPen(None)
    font['glyf'].glyphs[" "] = pen.glyph()
font['hmtx'].metrics[" "] = (sprite_width * scale, 0)
# notdef = ?
font['glyf'].glyphs[".notdef"] = font['glyf'].glyphs["?"]
font['hmtx'].metrics[".notdef"] = font['hmtx'].metrics["?"]



# Ensure every glyph in the order exists in glyf
for glyph_name in font.getGlyphOrder():
    if glyph_name not in font['glyf'].glyphs:
        pen = TTGlyphPen(None)
        font['glyf'].glyphs[glyph_name] = pen.glyph()
        font['hmtx'].metrics[glyph_name] = (sprite_width * scale, 0)

# ensure every glyf in the glyf exists in the order
for glyph_name in font['glyf'].glyphs.keys():
    if glyph_name not in font.getGlyphOrder():
        # print a warn
        print(f"⚠️ Warning: Glyph '{glyph_name}' not in glyph order")



# --- CREATE CMAP ---
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
font['cmap'] = newTable('cmap')
font['cmap'].tableVersion = 0  # <-- Add this line
font['cmap'].tables = []
cmap_subtable = CmapSubtable.newSubtable(4)  # Windows Unicode BMP
cmap_subtable.platformID = 3
cmap_subtable.platEncID = 1
cmap_subtable.language = 0
cmap_subtable.cmap = {ord(char): char for char in glyph_order}
font['cmap'].tables.append(cmap_subtable)

# --- CREATE MAXP ---
font['maxp'] = newTable('maxp')
font['maxp'].tableVersion = 0x00005000
font['maxp'].numGlyphs = len(font.getGlyphOrder())

# --- SAVE FONT ---
print(font.recalcBBoxes)
font['head'].checkSumAdjustment = 0  # Let fontTools recalculate this
font.save("spritesheet_font.ttf")
print("✅ Spritesheet converted to TTF!")
