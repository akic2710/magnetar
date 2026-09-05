import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = 'README.md'
s = io.open(p, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')

old = s[s.index('Still worth adding before launch:'):]
new = """### Ads

The end-of-run sequence is:

```
die  ->  [revive offer]  ->  finishRun  ->  [midgame ad]  ->  game over
```

**Rewarded revive.** Offered once per run, and only from wave 3 up — a run that
ended in ten seconds is not worth an ad. The screen states plainly that it is an
ad, that it is optional, and that declining costs nothing, and it carries the
countdown the docs ask for; it auto-declines after 8 seconds rather than
nagging. Reviving restores 2 lives, clears bolts and nearby enemies, and grants
3 seconds of invulnerability at the same wave with the same build.

The reward is granted **only** on `adFinished`. On `adError` the run simply
ends — no reward, and a short "no ad available" note so the player knows why.

**Midgame ad.** On death, an allowed placement. Skipped when the run was under
45 seconds, and skipped entirely if the player already engaged with the rewarded
offer that run — watched it *or* had it fail on them. The game-over panel waits
for the ad and appears on `adFinished` **and** on `adError`, because freezing
between an ad and the next screen is a listed rejection cause. The SDK enforces
its own 3-minute cap, so no interval tracking here.

**Payout moved out of `die()`.** Flux and best scores are banked in `finishRun`,
which is the true end of a run. Left in `die()`, a revived run would have paid
out twice — once at the first death and again at the second.

**Audio and pausing.** `A.duck()` is separate from the player's mute setting, so
restoring audio after an ad cannot clobber what they chose. The game mutes and
pauses on `adStarted` (not on request, per the docs) and restores on
`adFinished` or `adError`. A blocking overlay with a spinner covers the request
so nothing underneath is clickable.

**Two timeouts, because a game that hangs on an ad gets rejected.** If
`adStarted` never fires within 8 seconds the request is abandoned and the run
continues; if an ad starts but never reports back, a 120-second backstop
releases the player. Either way the panel appears.

**Adblock.** `hasAdblock()` is checked at init. If ads cannot run, the revive
button is never shown — a button that can never work is itself a rejection
cause — and the game plays exactly as it does off-portal.

Verified with a mock ad module: revive grant and denial, no reward on error,
no ad chaining, payout exactly once across a revive, mute preference surviving a
duck cycle, adblock suppression, click swallowing behind the overlay, and a live
8.6-second wait proving the start guard releases a request that never begins.
Then 8 bot runs with no SDK at all, confirming the ad-free path is unchanged.

Still worth adding before launch:

- **A non-ad way to earn Flux.** The requirements ask that rewards be
  obtainable without ads; Flux already is (every run pays out), but if a
  rewarded Flux bonus is ever added, keep that true.
- **Banner ads** on the death screen, if you want them — not wired.
"""
s = s.replace(old, new)
s = s.replace('| Download size | ~86 KB, one file |', '| Download size | ~95 KB, one file |')

old_tbl = """| `game.happytime` | Guardian kills and new best scores |
| `game.reportGameCompletedPercentage` | Each wave, against wave 30 as 100% |"""
new_tbl = """| `game.happytime` | Guardian kills and new best scores |
| `game.reportGameCompletedPercentage` | Each wave, against wave 30 as 100% |
| `ad.requestAd('rewarded')` | Optional revive, offered once per run |
| `ad.requestAd('midgame')` | On death, subject to the rules below |
| `ad.hasAdblock` | Hides the revive button when ads cannot run |"""
assert old_tbl in s
s = s.replace(old_tbl, new_tbl)

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('README updated for ads')
