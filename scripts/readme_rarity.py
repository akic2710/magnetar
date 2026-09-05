import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = 'README.md'
s = io.open(p, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')

anchor = "- Clear waves, level up, pick 1 of 3 upgrades from 12 stacking options."
assert anchor in s
s = s.replace(anchor, "- Clear waves, level up, pick 1 of 3 upgrades drawn by rarity from 12 options.")

marker = "\n---\n\n## Meta-progression"
assert marker in s
rarity_doc = """

---

## Upgrade rarity

Three tiers, drawn by weight without replacement so a hand never repeats a card.

| Tier | Weight each | Upgrades | Character |
|---|---|---|---|
| Common | 56 | Magnet Field, Orbit Slots, Thrusters, Scavenger, Reinforced Hull | Incremental, always useful |
| Rare | 30 | Overcharge, Spin Cycle, Heavy Slugs, Siphon | Real power spikes |
| Epic | 12 | Repulse Wave, Static Charge, Ricochet | Behaviour-changing |

Measured over 4000 draws: **62% common, 29% rare, 9% epic**, with an epic in
**25% of level-ups**. That share rises naturally as commons max out, so late
runs deal better cards without any special-casing.

**Rarity has to mean power, or it is just decoration.** The epic tier is the
three upgrades that change how the game plays rather than scaling a number, and
two were buffed to earn the tier: Ricochet now grants two wall bounces per stack
instead of one, and Static Charge's lightning scales with stacks instead of
always dealing 1. Repulse Wave was already the strongest thing in the pool —
bot testing during the core rebalance had it carrying runs to wave 39 — so it
set the bar the others were raised to.

Visually each tier gets its own colour (steel / cyan / violet) on the border,
icon, glow and stack pips, plus a tier label on the card. Epics carry a pulsing
outer bloom, the LEVEL header tints violet when one is in the hand, and a
separate audio sting plays — you hear the good hand before you finish reading
it. Each upgrade also has a fixed icon shape now; previously the polygon came
from the card slot, so the same upgrade looked different every level.

### It changed the difficulty, so I corrected for it

Rarity is a presentation change, but weighting the draw toward commons made the
average level-up weaker than the old uniform draw over 12 cards. Bot runs went
from median wave 37 to median 20, and every run started ending in death.

Weights were moved from 62/28/10 to 56/30/12 and the commons buffed a little
(pull radius +52, move speed +15%, Reinforced Hull heals 2) so rarity changes
*which* cards you see rather than how strong you end up. Result over 15 runs
each:

| Picker | Median wave | Mean | Deaths |
|---|---|---|---|
| Before rarity | 37 | 34 | 7/15 |
| Random pick | 20 | 28 | 15/15 |
| Always take the rarest | 46 | 38 | 15/15 |

The gap between the two pickers is the point: recognising the good card is now
worth more than twice the depth. And unlike the pre-rarity build, no run
survives the six-minute cap — the immortal tail is gone. Median run for random
picking is 3.1 minutes.

The usual caveat applies: these are 15-run samples of a bimodal distribution, so
treat ±10 waves as noise. The 46-vs-20 gap is far outside that.
"""
s = s.replace(marker, rarity_doc + marker, 1)
s = s.replace('| Download size | ~100 KB, one file |', '| Download size | ~103 KB, one file |')

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('README updated for rarity')
