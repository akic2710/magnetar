import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
KB = int(round(os.path.getsize('dist/index.html') / 1024.0))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        assert s.count(old) == 1, '%s: ambiguous -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


patch('README.md', [

# ---- size refs ----
('[![Build](https://img.shields.io/badge/build-131_KB_single_file-6effc0?style=flat-square)](#magnetar)',
 '[![Build](https://img.shields.io/badge/build-%d_KB_single_file-6effc0?style=flat-square)](#magnetar)' % KB),
('- [x] **Download size** — 131 KB, one file, well under the 50 MB cap',
 '- [x] **Download size** — %d KB, one file, well under the 50 MB cap' % KB),

# ---- portrait section gains the shop ----
("""| **The problem.** The arena is a fixed 16:9 field scaled to fit, so a 375×667 screen gets a 375×211 strip — **32% of the display**, with 228px of black above and below. Nothing breaks and the layout holds, but it is small. | **The fix.** Landscape gives the playfield the full width at roughly double the scale, so the game asks for it rather than letterboxing silently. Touch devices in portrait only — never on desktop, never over an ad — and always dismissable via **Play anyway**, since orientation can be locked at the OS level. |
""",
"""| **The problem.** The arena is a fixed 16:9 field scaled to fit, so a 375×667 screen gets a 375×211 strip — **32% of the display**, with 228px of black above and below. Nothing breaks and the layout holds, but it is small. | **The fix.** Landscape gives the playfield the full width at roughly double the scale, so the game asks for it rather than letterboxing silently. Touch devices in portrait only — never on desktop, never over an ad — and always dismissable via **Play anyway**, since orientation can be locked at the OS level. |

### The shop does not letterbox

Asking for landscape is right for an arena. It is the wrong answer for a menu,
which is a thing you read rather than a thing you play — and inside the
letterbox the shop was unreadable: item names at **4.7px**, prices at 3.5px,
and a LAUNCH button 15px tall.

<img src="docs/screenshot-shop-portrait.webp" width="250" alt="The shop on a 375x812 phone in portrait: a SHOP header with the Flux balance, a WAKES / ARENAS / BOOSTS tab bar, and four full-width cards - Standard, Ion Wake equipped, Sparkfall at 450 Flux and Echo at 700 Flux - above LAUNCH, CORES and mute buttons">

So in portrait the shop leaves the 1280×720 space altogether and lays itself
out in **CSS pixels across the whole screen**, the way the rotate prompt
already did. The rotate prompt stands down while you are in it — there is
nothing left to rotate for.

Ten cards cannot be legible on a 568-tall phone, so the catalogue splits into
the three groups it already had and shows one at a time. Four cards maximum is
what buys each one enough room to read *and* to hit, and it avoids scrolling,
which on a canvas would have to fight the tap handler for the same gesture.

| | Letterboxed | Portrait layout |
|---|---|---|
| Item name | 4.7px | **14–20px** |
| Price | 3.5px | **11–14px** |
| Card | 80×43 | **254–560 wide, 47–124 tall** |
| Smallest tap target | 13×13 | **44px** |

Sizes are clamped at both ends — a floor so a 280-wide Galaxy Fold cover stays
legible, a ceiling so a 1024-wide iPad does not end up with 43px names on
metre-wide cards, and the column stops widening at 560 and centres. Verified
across ten viewports from 280×653 to 1024×1366: nothing overlaps or leaves the
screen, every touch target clears 44px, and the longest item name never
collides with its price in any ownership state (tightest measured slack: 22px).

One deliberate omission: **no banner on the portrait shop.** The layout uses
the whole viewport, so there is no band left to put one in, and overlaying it
would put an ad against a live button — which the ad requirements specifically
forbid. The landscape shop still carries one.
"""),

# ---- checklist bullet ----
("""- [x] **Mobile orientation** — portrait on a touch device prompts for landscape instead of silently letterboxing into a strip a third of the screen tall; dismissable, and never shown on desktop or over an ad. The dismiss button clears the 44px touch minimum on every phone tested, the lockup shrinks rather than pushing that button off a short viewport, and the backdrop is opaque over menus so a card grid never ghosts through it""",
 """- [x] **Mobile orientation** — portrait on a touch device prompts for landscape instead of silently letterboxing into a strip a third of the screen tall; dismissable, and never shown on desktop or over an ad. The dismiss button clears the 44px touch minimum on every phone tested, the lockup shrinks rather than pushing that button off a short viewport, and the backdrop is opaque over menus so a card grid never ghosts through it
- [x] **Portrait shop** — the shop has a real portrait layout in CSS pixels rather than a letterboxed one, so it is readable and tappable without rotating; the rotate prompt stands down while you are in it""")])


patch('SUBMISSION.md', [
("""Build size is ~131 KB in one file""",
 """Build size is ~%d KB in one file""" % KB)])

print('docs updated; build %d KB' % KB)
