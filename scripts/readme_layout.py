import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = 'README.md'
s = io.open(p, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')

marker = '\n---\n\n## Upgrade rarity'
assert marker in s
doc = """

---

## Layout and spacing

Every screen is drawn on the canvas in a fixed 1280x720 virtual space, so
layout is arithmetic rather than CSS. A single spacing scale (`PAD`, `GAP`) and
a hairline `hr()` rule now do the grouping that cramped spacing used to.

Two real defects came out of this pass:

- **The XP bar ran underneath the mute and pause buttons.** It was an inset
  rounded bar at `VH-22` spanning to `VW-30`, while the buttons sat at
  `VH-58`, 42px tall — they overlapped for ~74px. XP is now a full-bleed 5px
  line along the very bottom edge and the buttons moved up clear of it.
- **The wave banner was dead code.** `waveBanner` and `waveBannerTxt` were set
  on every wave and decayed every frame but never drawn. It now fades in and
  out over the arena at wave start (and is gated to gameplay, so it cannot
  bleed through a menu).

Screen by screen: the top HUD row got a real baseline gap (40 / 66) instead of
30 / 52; the boss bar dropped clear of the wave label; level-up cards grew from
300x348 to 316x384 with a divider between icon and text; the game-over panel
went 520x452 to 580x512 and is now grouped by two hairlines into identity /
run detail / payout / actions, with the hint moved inside the panel; the core
menu's cards grew and its badges share a baseline with the last stat line.

Verified by geometry rather than by eye: no two hit rects overlap on any
screen, every rect sits inside the 1280x720 field, card margins are symmetric,
buttons stay inside their panels, and the banner band still fits at every
tested viewport. All eleven screen states render without throwing at 800x450,
1920x1080 and a 531x683 portrait ratio.
"""
s = s.replace(marker, doc + marker, 1)
s = s.replace('| Download size | ~103 KB, one file |', '| Download size | ~104 KB, one file |')
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('README updated for layout pass')
