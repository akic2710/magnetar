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

('[![Build](https://img.shields.io/badge/build-148_KB_single_file-6effc0?style=flat-square)](#magnetar)',
 '[![Build](https://img.shields.io/badge/build-%d_KB_single_file-6effc0?style=flat-square)](#magnetar)' % KB),
('- [x] **Download size** — 148 KB, one file, well under the 50 MB cap',
 '- [x] **Download size** — %d KB, one file, well under the 50 MB cap' % KB),

("""| Shop | Cores |
|---|---|
| <img src="docs/screenshot-shop-portrait.webp" width="240" alt="The shop on a 375x812 phone in portrait: a SHOP header with the Flux balance, a WAKES / ARENAS / BOOSTS tab bar, and four full-width cards - Standard, Ion Wake equipped, Sparkfall at 450 Flux and Echo at 700 Flux - above LAUNCH, CORES and mute buttons"> | <img src="docs/screenshot-cores-portrait.webp" width="240" alt="The core menu on the same phone: a CORES header with the Flux balance and a synced-to-your-account line, then six full-width cards - Prospector, Warden equipped in green, Maw affordable at 450 Flux, and Needle, Pulsar and Drifter dimmed - above LAUNCH, SHOP and mute buttons"> |""",
"""| Shop | Cores | Game over |
|---|---|---|
| <img src="docs/screenshot-shop-portrait.webp" width="200" alt="The shop on a 375x812 phone in portrait: a SHOP header with the Flux balance, a WAKES / ARENAS / BOOSTS tab bar, and four full-width cards - Standard, Ion Wake equipped, Sparkfall at 450 Flux and Echo at 700 Flux - above LAUNCH, CORES and mute buttons"> | <img src="docs/screenshot-cores-portrait.webp" width="200" alt="The core menu on the same phone: a CORES header with the Flux balance and a synced-to-your-account line, then six full-width cards - Prospector, Warden equipped in green, Maw affordable at 450 Flux, and Needle, Pulsar and Drifter dimmed - above LAUNCH, SHOP and mute buttons"> | <img src="docs/screenshot-over-portrait.webp" width="200" alt="The death screen on the same phone: CORE LOST above the rank, a large 1460 score marked NEW BEST SCORE, a row of wave, best combo and best stats, the Flux payout with its amplifier note, then a full-width PLAY AGAIN above CORES, SHOP and mute"> |"""),

("""**The core menu** has the harder problem: six items, each carrying three stat
lines. On a 568-tall phone that leaves about 64px a card — room for one line of
stats, not three. So each card asks how many lines it can afford and renders
the longest run of stats that actually fits, measured rather than guessed,
falling back to the lives/slots line which is always the trade that matters.
The flavour tag is the one thing dropped in portrait.""",
"""**The core menu** has the harder problem: six items, each carrying three stat
lines. On a 568-tall phone that leaves about 64px a card — room for one line of
stats, not three. So each card asks how many lines it can afford and renders
the longest run of stats that actually fits, measured rather than guessed,
falling back to the lives/slots line which is always the trade that matters.
The flavour tag is the one thing dropped in portrait.

**The death screen** is not a list, so it does not use that frame: it is a
column of numbers with the actions underneath. The block is measured from its
own type sizes and then centred, rather than pinned to fractions of the screen,
so a 568-tall phone and a 932-tall one both look composed instead of one of
them looking stretched. Below about 400px tall the display type and the gaps
shrink together until the column clears the buttons — the small labels hold
their floor, and the score never goes under 32px.

It is also the one portrait screen that **keeps its banner**. The death screen
is the placement that actually earns, so rather than drop it the layout
reserves a real 74px strip along the bottom and lifts the buttons above it,
with 8px of dead space and the ADVERTISEMENT label providing the separation the
ad requirements ask for. The strip is only taken when a banner could fill it —
never under 340px wide, where nothing fits, and never on a screen so short that
reserving it would push the score under the buttons. On those, the banner gives
way, not the score."""),

("""- [x] **Portrait menus** — the shop and the core menu both have real portrait layouts in CSS pixels rather than letterboxed ones, so they are readable and tappable without rotating; the rotate prompt stands down while you are in either""",
 """- [x] **Portrait menus** — the shop, the core menu and the death screen all have real portrait layouts in CSS pixels rather than letterboxed ones, so they are readable and tappable without rotating; the rotate prompt stands down while you are in any of them
- [x] **Portrait banner** — the death screen keeps its banner in portrait in a reserved strip, clear of every button by 8px and the ADVERTISEMENT label; it is only reserved where one could actually fill""")])


patch('SUBMISSION.md', [
("""Build size is ~148 KB in one file""",
 """Build size is ~%d KB in one file""" % KB)])

print('docs updated for the portrait death screen; build %d KB' % KB)
