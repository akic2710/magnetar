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

('[![Build](https://img.shields.io/badge/build-141_KB_single_file-6effc0?style=flat-square)](#magnetar)',
 '[![Build](https://img.shields.io/badge/build-%d_KB_single_file-6effc0?style=flat-square)](#magnetar)' % KB),
('- [x] **Download size** — 141 KB, one file, well under the 50 MB cap',
 '- [x] **Download size** — %d KB, one file, well under the 50 MB cap' % KB),

# ---- retitle the section and cover both screens ----
("""### The shop does not letterbox

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
which on a canvas would have to fight the tap handler for the same gesture.""",
"""### The menus do not letterbox

Asking for landscape is right for an arena. It is the wrong answer for a menu,
which is a thing you read rather than a thing you play — and inside the
letterbox both menus were unreadable: item names at **4.7px**, prices at 3.5px,
and a LAUNCH button 15px tall.

| Shop | Cores |
|---|---|
| <img src="docs/screenshot-shop-portrait.webp" width="240" alt="The shop on a 375x812 phone in portrait: a SHOP header with the Flux balance, a WAKES / ARENAS / BOOSTS tab bar, and four full-width cards - Standard, Ion Wake equipped, Sparkfall at 450 Flux and Echo at 700 Flux - above LAUNCH, CORES and mute buttons"> | <img src="docs/screenshot-cores-portrait.webp" width="240" alt="The core menu on the same phone: a CORES header with the Flux balance and a synced-to-your-account line, then six full-width cards - Prospector, Warden equipped in green, Maw affordable at 450 Flux, and Needle, Pulsar and Drifter dimmed - above LAUNCH, SHOP and mute buttons"> |

So in portrait both screens leave the 1280×720 space altogether and lay
themselves out in **CSS pixels across the whole screen**, the way the rotate
prompt already did. The prompt stands down while you are in either — there is
nothing left to rotate for.

They share one frame — a centred column, a header, a list, and the same three
controls along the bottom — because two copies of that clamping would have
drifted apart by the second change to either. Only what sits between the
header and the buttons differs.

**The shop** cannot show ten legible cards on a 568-tall phone, so the
catalogue splits into the three groups it already had and shows one at a time.
Four cards maximum is what buys each one enough room to read *and* to hit, and
it avoids scrolling, which on a canvas would have to fight the tap handler for
the same gesture.

**The core menu** has the harder problem: six items, each carrying three stat
lines. On a 568-tall phone that leaves about 64px a card — room for one line of
stats, not three. So each card asks how many lines it can afford and renders
the longest run of stats that actually fits, measured rather than guessed,
falling back to the lives/slots line which is always the trade that matters.
The flavour tag is the one thing dropped in portrait.""")])


patch('README.md', [
("""Sizes are clamped at both ends — a floor so a 280-wide Galaxy Fold cover stays
legible, a ceiling so a 1024-wide iPad does not end up with 43px names on
metre-wide cards, and the column stops widening at 560 and centres. Verified
across ten viewports from 280×653 to 1024×1366: nothing overlaps or leaves the
screen, every touch target clears 44px, and the longest item name never
collides with its price in any ownership state (tightest measured slack: 22px).

One deliberate omission: **no banner on the portrait shop.** The layout uses
the whole viewport, so there is no band left to put one in, and overlaying it
would put an ad against a live button — which the ad requirements specifically
forbid. The landscape shop still carries one.""",
"""Sizes are clamped at both ends — a floor so a 280-wide Galaxy Fold cover stays
legible, a ceiling so a 1024-wide iPad does not end up with 43px names on
metre-wide cards, and the column stops widening at 560 and centres. Where a
short viewport cannot give every row 44px at the default spacing, the **gap
gives way before the touch target does**: six core rows miss 44 by 4px on a
400-tall frame and clear it once the gap collapses.

Verified across ten viewports from 280×653 to 1024×1366, for both screens:
nothing overlaps or leaves the screen, every touch target clears 44px, the
longest name never collides with its label in any ownership state, and no stat
line overflows the card it was fitted to. Tightest measured slack: 9px.

One deliberate omission: **no banner on either portrait menu.** The layout uses
the whole viewport, so there is no band left to put one in, and overlaying it
would put an ad against a live button — which the ad requirements specifically
forbid. Both landscape menus still carry one.""")])


patch('README.md', [
("""- [x] **Portrait shop** — the shop has a real portrait layout in CSS pixels rather than a letterboxed one, so it is readable and tappable without rotating; the rotate prompt stands down while you are in it""",
 """- [x] **Portrait menus** — the shop and the core menu both have real portrait layouts in CSS pixels rather than letterboxed ones, so they are readable and tappable without rotating; the rotate prompt stands down while you are in either""")])


patch('SUBMISSION.md', [
("""Build size is ~141 KB in one file""",
 """Build size is ~%d KB in one file""" % KB)])

print('docs updated for the portrait core menu; build %d KB' % KB)
