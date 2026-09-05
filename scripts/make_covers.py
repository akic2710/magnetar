"""Build the three cover images CrazyGames asks for from one 1920x1080 master.

Landscape 1920x1080, portrait 800x1200, square 800x800. Each is a fill-crop of
the master (never letterboxed, never stretched) plus a title lockup over a
gradient scrim so the text stays legible on the busy neon background.
"""
import io, json, base64, os, sys, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

SRC = sys.argv[1]
OUT = 'covers'
os.makedirs(OUT, exist_ok=True)

text = ''.join(i.get('text', '') for i in json.load(io.open(SRC, encoding='utf-8')))
m = re.search(r'__C__(.*?)__END__', text, re.S)
assert m, 'marker not found'
master = Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGB')
assert master.size == (1920, 1080), master.size
print('master:', master.size)


def font(px, bold=True):
    for name in (('seguibl.ttf', 'segoeuib.ttf', 'arialbd.ttf') if bold
                 else ('segoeui.ttf', 'arial.ttf')):
        p = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts', name)
        if os.path.exists(p):
            return ImageFont.truetype(p, px)
    return ImageFont.load_default()


def fill_crop(im, w, h, focus=0.5):
    """Scale to cover the target box, then crop around a focal point."""
    src_r, dst_r = im.width / im.height, w / h
    if src_r > dst_r:                       # source wider: crop the sides
        nh = h
        nw = int(round(h * src_r))
    else:                                   # source taller: crop top/bottom
        nw = w
        nh = int(round(w / src_r))
    im = im.resize((nw, nh), Image.LANCZOS)
    left = int((nw - w) * focus)
    top = int((nh - h) * focus)
    return im.crop((left, top, left + w, top + h))


def scrim(im, frac, strength=235):
    """Darken the bottom `frac` of the image so the title reads cleanly."""
    w, h = im.size
    band = int(h * frac)
    grad = Image.new('L', (1, band))
    for y in range(band):
        grad.putpixel((0, y), int(strength * (y / max(1, band - 1)) ** 1.5))
    mask = Image.new('L', (w, h), 0)
    mask.paste(grad.resize((w, band), Image.BILINEAR), (0, h - band))
    return Image.composite(Image.new('RGB', (w, h), (2, 4, 12)), im, mask)


def tracked(draw, xy, s, f, fill, track, anchor_center=False, W=None):
    widths = [draw.textlength(ch, font=f) for ch in s]
    total = sum(widths) + track * (len(s) - 1)
    x, y = xy
    if anchor_center:
        x = (W - total) / 2
    for ch, cw in zip(s, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += cw + track
    return total


CYAN = (124, 243, 255)
DIM = (150, 172, 200)

# name, w, h, crop focus, scrim band, title px, subtitle px, pad, glow
specs = [
    ('landscape_1920x1080', 1920, 1080, 0.50, 0.46, 130, 30, 40, 0.055),
    ('portrait_800x1200',    800, 1200, 0.50, 0.30,  62, 15, 22, 0.075),
    ('square_800x800',       800,  800, 0.50, 0.36,  64, 15, 22, 0.075),
]

for name, w, h, focus, band, tsize, ssize, pad, glow in specs:
    im = fill_crop(master, w, h, focus)
    im = scrim(im, band)

    # Neon bloom: draw the wordmark on a black layer, blur it, and screen it
    # onto the art. Screening keeps the glow additive over the dark background
    # instead of muddying it the way an alpha blend would.
    f_title = font(tsize)
    baseline = h - int(h * 0.5 * band) - tsize // 2
    lay = Image.new('RGB', (w, h), (0, 0, 0))
    tracked(ImageDraw.Draw(lay), (0, baseline), 'MAGNETAR', f_title, CYAN,
            tsize * 0.14, anchor_center=True, W=w)
    lay = lay.filter(ImageFilter.GaussianBlur(tsize * glow))
    im = ImageChops.screen(im, lay)

    d = ImageDraw.Draw(im)
    tracked(d, (0, baseline), 'MAGNETAR', f_title, (240, 252, 255), tsize * 0.14,
            anchor_center=True, W=w)
    f_sub = font(ssize, bold=False)
    tracked(d, (0, baseline + tsize + pad // 2), 'HOLD TO PULL   RELEASE TO BLAST',
            f_sub, DIM, ssize * 0.22, anchor_center=True, W=w)

    p = os.path.join(OUT, name + '.png')
    im.save(p, optimize=True)
    print('%-24s %s  %6.0f KB' % (name, im.size, os.path.getsize(p) / 1024))
