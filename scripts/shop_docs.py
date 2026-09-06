import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        assert s.count(old) == 1, '%s: ambiguous -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


SIZE = os.path.getsize('dist/index.html')
KB = int(round(SIZE / 1024.0))

patch('README.md', [

# ---- size badge and checklist line ----
('[![Build](https://img.shields.io/badge/build-111_KB_single_file-6effc0?style=flat-square)](#magnetar)',
 '[![Build](https://img.shields.io/badge/build-%d_KB_single_file-6effc0?style=flat-square)](#magnetar)' % KB),
('- [x] **Download size** — 111 KB, one file, well under the 50 MB cap',
 '- [x] **Download size** — %d KB, one file, well under the 50 MB cap' % KB),

# ---- the shop, right after the cores it shares a currency with ----
("""Unlock pacing at a typical ~200 Flux/run: Warden run 1, Maw run 3, Needle run
8, Pulsar run 15, Drifter run 24. Saves are validated on read — a tampered or
corrupt `mgn.core` falls back to Prospector rather than granting a locked core.

---""",
"""Unlock pacing at a typical ~200 Flux/run: Warden run 1, Maw run 3, Needle run
8, Pulsar run 15, Drifter run 24. Saves are validated on read — a tampered or
corrupt `mgn.core` falls back to Prospector rather than granting a locked core.

### The shop

Flux's second sink, reached from the death screen or from the core menu.

| Item | Cost | What it is |
|---|---|---|
| Standard / Ion Wake / Sparkfall / Echo | free / 250 / 450 / 700 | Motion wakes behind the player |
| Deep Field / Nocturne / Tide / Graphite | free / 300 / 550 / 800 | Arena palettes — grid, glow and edge |
| Amplifier I | 900 | +20%% Flux from every run |
| Amplifier II | 2200 | +45%% instead; requires Amplifier I |

**Nothing here can be bought into an advantage.** Wakes and arenas touch no
value the simulation reads, and the amplifiers scale the payout only. That is
asserted rather than asserted-at: with `Math.random` seeded, a run with
everything owned and equipped produces a **bit-identical state fingerprint** to
a run with nothing owned, across five seeds and 45 simulated seconds each.

Wakes deliberately carry no colour of their own and take the equipped core's
instead. Warm hues belong to enemies in this game, and a cosmetic that could
dress the player in an enemy's colour is a cosmetic that gets people killed.
Arenas may recolour, because the grid is background by definition — but they
stay dark and low-saturation for the same readability reason.

### Purchases go through one adapter

Every purchase in the game routes through `PURCHASE.buy(item, done)`, so
exactly one object knows how a player pays for anything. Today the only rail is
Flux, earned by playing.

CrazyGames in-game purchases — the real-money kind — are **invite-only**. They
issue an Xsolla project id per game, and their SDK surface is just two calls:
`SDK.user.getXsollaUserToken()` for a short-lived token, and
`SDK.analytics.trackOrder('xsolla', order)` to report a finished order. The
catalogue and the checkout widget live in Xsolla's API, not theirs. A `cash`
rail drops in beside the Flux one if that invite ever arrives, and nothing
outside `PURCHASE` has to change.

Their rules are why `canPurchase()` exists at all: real-money purchases must be
limited to signed-in players, guests must not even see a buy button, and the
shop has to be hidden entirely inside the CrazyGames mobile app. On the Flux
rail none of that applies, because Flux is earned rather than bought.

---"""),

# ---- merge table now covers the new keys, and the rule that changed ----
("""| Field | Rule |
|---|---|
| `owned` | Union — an unlock is never revoked |
| `earned`, `best`, `bestwave` | Max — monotonic counters |
| `core` | Cloud's choice if owned after the merge, else local's, else Prospector |
| `played` | Set if either side has it |""",
"""| Field | Rule |
|---|---|
| `owned`, `shop` | Union — an unlock is never revoked |
| `earned`, `best`, `bestwave` | Max — monotonic counters |
| `core`, `trail`, `arena` | A real selection beats a default, cloud beats local, then the default |
| `played` | Set if either side has it |

That third rule reads oddly until you hit the bug it exists for. Every default
is permanently "owned", so a device that never customised anything still
*reports* a selection. Preferring the cloud unconditionally meant a phone that
had never opened the shop would overwrite the wake, arena and **core** chosen
on a desktop — a silent revert to defaults on sign-in, and the equipped-core
version of it shipped in the first release. Ranking an actual choice above a
default in both directions means a merge can only ever add information."""),

# ---- and the checklist gains the answer QA will ask for ----
("""### Beyond the requirements

Not documented requirements, but things QA and players notice.

- [x] **Mobile orientation** — portrait on a touch device prompts for landscape instead of silently letterboxing into a strip a third of the screen tall; dismissable, and never shown on desktop or over an ad""",
"""### Beyond the requirements

Not documented requirements, but things QA and players notice.

- [x] **Mobile orientation** — portrait on a touch device prompts for landscape instead of silently letterboxing into a strip a third of the screen tall; dismissable, and never shown on desktop or over an ad
- [x] **No real-money purchases** — the shop spends Flux, which is only ever earned by playing. Answer *no* to in-game purchases on the submission form; that feature is invite-only and is not wired up
- [x] **Nothing is pay-to-win** — proven by bit-identical seeded run fingerprints with everything owned versus nothing owned, not by inspection""")])


patch('SUBMISSION.md', [
("""Build size is ~111 KB in one file — far inside the 50 MB initial-download cap""",
 """Build size is ~%d KB in one file — far inside the 50 MB initial-download cap""" % KB),
])

print('docs updated; build size %d KB' % KB)
