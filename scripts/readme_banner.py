import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = 'README.md'
s = io.open(p, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')

anchor = "Still worth adding before launch:"
old = s[s.index(anchor):]
new = """**Banner.** Death screen only, in the empty band below the game-over panel.
Banners are forbidden during gameplay, so `syncBanner` shows one only in mode
`over` and never in play, intro, level-up or the core menu, and pulls it during
a video ad.

The banner is real DOM, not canvas, so it needs its own element and its own
layout. Size is chosen from the space actually available under the panel:
728x90, 468x60 or 320x50, or nothing at all if the viewport is too short. The
panel shifts up from y112 to y76 when a banner has space, and that space is
**reserved as soon as we know a banner could fill** — so an unfilled ad
collapses the container without the panel jumping.

Two rules from the ad requirements shaped the code:

- *"Ensure your game's buttons are far away from the banner."* The death screen
  previously restarted on a click **anywhere**, which would have made the whole
  page a button sitting next to an ad. With a banner present, the pointer target
  is now the PLAY AGAIN button alone, and the hint text says so. Enter still
  works — a keypress cannot mis-hit an ad. Without a banner, click-anywhere is
  unchanged. Measured clearance: 56px below the button at 964x419.
- *"Banners must be clearly distinguishable from game content."* Hence the
  ADVERTISEMENT label above the slot.

`hide()` clears the banner **and resets the cached size**, so the next death
re-requests instead of re-showing an emptied container under a label. A request
inside the SDK's refresh floor comes back `bannerCooldown`, which collapses the
slot and is not counted as a failure; three real failures stop requests for the
session.

Verified: hidden at boot and through 1200 frames of real gameplay, level-up,
intro and the core menu; shown only on death; correct size and no overflow
across nine viewports from 1920x1080 down to 375x667 and the 800x450 minimum;
cleared on leaving; unfilled collapses without moving the panel; rapid
re-death re-requests rather than showing an empty box; give-up after three
failures restores the normal layout.

Still worth adding before launch:

- **A banner on the core menu.** Shops and menus are an explicitly allowed
  placement and the wiring is already there — `syncBanner`'s condition would
  just gain `|| G.mode === 'cores'`. Left out because only the death screen
  was asked for.
- **A non-ad way to earn Flux.** The requirements ask that rewards be
  obtainable without ads; Flux already is (every run pays out), so keep that
  true if a rewarded Flux bonus is ever added.
"""
s = s.replace(old, new)
s = s.replace('| Download size | ~95 KB, one file |', '| Download size | ~100 KB, one file |')

old_tbl = "| `ad.hasAdblock` | Hides the revive button when ads cannot run |"
new_tbl = ("| `ad.hasAdblock` | Hides the revive button when ads cannot run |\n"
           "| `banner.requestBanner` / `clearBanner` | Death screen only |")
assert old_tbl in s
s = s.replace(old_tbl, new_tbl)

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('README updated for banners')
