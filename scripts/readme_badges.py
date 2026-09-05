import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = 'README.md'
s = io.open(p, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')

# --------------------------------------------------------------- badges
# Static shields only. The repo is private, so any dynamic badge that has to
# read it (size, last commit, license) renders as "invalid" for everyone.
old_head = """# Magnetar

**Hold to pull, release to blast.** A one-button neon arena roguelite, built as a
single self-contained HTML file for CrazyGames."""
new_head = """# Magnetar

[![CrazyGames requirements](https://img.shields.io/badge/CrazyGames_requirements-12%2F12_met-7cf3ff?style=flat-square)](#crazygames-submission-checklist)
[![SDK](https://img.shields.io/badge/CrazyGames_SDK-v3_integrated-c88bff?style=flat-square)](#sdk-integration)
[![Build](https://img.shields.io/badge/build-104_KB_single_file-6effc0?style=flat-square)](#magnetar)
[![Dependencies](https://img.shields.io/badge/dependencies-none-b9c7de?style=flat-square)](#magnetar)
[![Network requests](https://img.shields.io/badge/network_requests-0-b9c7de?style=flat-square)](#magnetar)

**Hold to pull, release to blast.** A one-button neon arena roguelite, built as a
single self-contained HTML file for CrazyGames."""
assert old_head in s
s = s.replace(old_head, new_head, 1)

# --------------------------------------------------------------- checklist
old = s[s.index('## CrazyGames compliance'):s.index('Storage is exception-safe at every level')]
new = """## CrazyGames submission checklist

Every box below was verified in this repo, most of them by scripted geometry or
bot runs rather than by eye. The badge counts these twelve.

- [x] **Gameplay in ≤1 click** — loads straight into a playable tutorial wave; no menu, no splash
- [x] **Onboarding inside gameplay** — 3-step scripted intro, visual not textual, auto-skipped for returning players
- [x] **Readable 800×450 → 1920×1080** — fixed 1280×720 virtual canvas, letterboxed scale-to-fit; all screens render at 800×450, 1920×1080 and 531×683
- [x] **Consistent physics at 144/165 Hz** — fixed 1/120s accumulator with a substep cap; no spiral-of-death
- [x] **No reserved keys** — Escape and Ctrl+W unbound
- [x] **International keyboards** — arrows + WASD + ZQSD; the blast is radial, so nothing needs rebinding
- [x] **Touch parity** — drag to move, lift to blast; identical verb on every device
- [x] **Download size** — 104 KB, one file, well under the 50 MB cap
- [x] **Zero external requests** — procedural art, WebAudio-synthesised music and SFX, no CDN, no assets
- [x] **Audio behaviour** — starts only after a user gesture, mute persists, pauses on blur/hidden, ducks for ads
- [x] **PEGI 12** — abstract neon shapes, no gore, no sexual content, no real-money gambling
- [x] **Original IP** — all code, art and audio generated for this game

### Ad and SDK rules

- [x] Midgame ad only on death, never during gameplay
- [x] Rewarded revive is clearly optional, clearly an ad, and carries a countdown
- [x] Reward granted only on `adFinished`, never on `adError`
- [x] No ad chaining — one ad opportunity per run
- [x] Game muted and paused on `adStarted`, restored on finish or error
- [x] Blocking spinner during the request; two timeouts so a silent SDK cannot freeze the game
- [x] Banners on menus only (death screen, core menu), never during play
- [x] Banner clear of the game's buttons; click-anywhere disabled while one is on screen
- [x] Playable with an adblocker — the revive button is hidden rather than dead

### Confirm on your first upload

These three cannot be exercised off-portal, so they are genuinely unverified:

- [ ] **A real ad creative renders** — there is no fill outside CrazyGames, so only the reserved slot and its ADVERTISEMENT label are proven, not an actual ad
- [ ] **Cloud save round-trip** — sign in on two devices and confirm Flux and unlocks follow you; the merge logic is unit-tested against a mock, but the real account hop is not
- [ ] **The ad-loading overlay's appearance** — its behaviour (blocks input, halts the sim) is tested; only how it looks is unconfirmed

"""
s = s.replace(old, new, 1)
s = s.replace('Storage is exception-safe at every level — see **Cloud saves** below.',
              'Storage is exception-safe at every level — see **Cloud saves** below.')

# one consistent size figure everywhere
s = s.replace('| Download size | ~107 KB, one file |', '| Download size | ~104 KB, one file |')
s = s.replace('~107 KB', '~104 KB')

# the SDK section needs an anchor the badge can reach
assert '## SDK integration' in s, 'SDK section heading not found'

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('badges + submission checklist written')
