import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = 'README.md'
# Earlier writes left this file CRLF; normalise so LF-based matching works.
s = io.open(p, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')

old_ls = """`localStorage` is wrapped in try/catch and the game runs correctly when it
throws (private mode, sandboxed iframes): the intro replays and Flux does not
persist, but nothing errors. Wire up SDK cloud saves before launch so
progression survives a cleared cache."""
new_ls = """Storage is exception-safe at every level — see **Cloud saves** below."""
assert old_ls in s
s = s.replace(old_ls, new_ls)

old_sdk = s[s.index('## Enabling the CrazyGames SDK'):]
new_sdk = """## Cloud saves

`store()` is one small key-value layer over three backends, preferred in order:

1. **CrazyGames SDK data module** — synced to the player's account and across
   their devices. Adopted at runtime once `SDK.init()` resolves.
2. **localStorage** — per-device; the default before and without the SDK.
3. **In-memory map** — private mode, sandboxed iframes, blocked storage.

Reads are cached, because the HUD asks for the best score every frame and an
SDK `getItem` per frame is pure waste. Every path is exception-safe: storage
that throws degrades to memory rather than breaking the run.

Synced keys: `mgn.earned`, `mgn.owned`, `mgn.core`, `mgn.best`, `mgn.bestwave`,
`mgn.played`. `mgn.mute` is deliberately **device-local** — muting your phone
on a bus should not mute your desktop.

### Flux is derived, not stored

The save holds **lifetime Flux earned** plus the owned set, and the balance is
computed as `earned − sum(cost of owned)`. Buying a core writes only the new
`owned` entry; nothing is ever deducted.

This exists because a stored balance cannot be merged safely. Taking the max of
two devices would hand back Flux already spent on an unlock, and taking the min
would destroy progress. It also means the balance can never drift out of step
with what you own. Old saves that stored a balance are migrated once on boot
(`migrateSave`).

### Merging never takes anything away

The SDK migrates its *own* guest data on sign-in, but guest progress written
straight to localStorage before the SDK loaded is invisible to it. `adoptCloudSave`
covers that gap by folding the local save into the cloud one:

| Field | Rule |
|---|---|
| `owned` | Union — an unlock is never revoked |
| `earned`, `best`, `bestwave` | Max — monotonic counters |
| `core` | Cloud's choice if owned after the merge, else local's, else Prospector |
| `played` | Set if either side has it |

A cloud value can land mid-session. Flux, unlocks and best scores are all read
live so they need nothing, but the equipped core is only consulted when a run is
built — so `applyCloudSave` re-rolls the player **only** while the run is still
untouched (intro, or wave 1 with no kills and no score). A run in progress keeps
the core it started with and picks up the cloud choice on the next launch.
Re-rolling someone's build at wave 20 would be theft.

### The environment gate is load-bearing

`SDK.environment` returns `local`, `crazygames`, or `disabled`. Testing against
the **real** SDK confirmed that on a `disabled` domain `SDK.data.getItem()`
throws `sdkDisabled` — so without the guard, every save read would throw on any
non-CrazyGames host (embeds, mirrors, local files) and persistence would break
outright. The adapter checks `environment` before touching any module.

Verified with a mock data module across 50 assertions: migration, derived
balance, guest→cloud upload, fresh-device download, divergent-device merge,
tampered core, disabled environment, a data module that throws on every call,
mid-run protection, and sign-in cache invalidation. Plus a live check against
the real SDK on a disabled domain.

---

## SDK integration

`ENABLE_CG_SDK` is **on** in `dist/index.html`. The build flips it off for
`game-body.html`, since the Artifact host's CSP blocks external scripts and
loading it there would only log a violation.

Already wired:

| Call | When |
|---|---|
| `data.*` | All persistence, via `store()` |
| `user.addAuthListener` | Drops the read cache and re-applies on sign-in |
| `game.gameplayStart` / `gameplayStop` | Run start and death |
| `game.loadingStart` / `loadingStop` | Bracketed once the SDK can hear us |
| `game.happytime` | Guardian kills and new best scores |
| `game.reportGameCompletedPercentage` | Each wave, against wave 30 as 100% |

Still worth adding before launch:

- **Midgame ad** in `die()`, before the game-over panel.
- **Rewarded ad** as a one-time revive, and/or a Flux bonus on the death
  screen — the payout is already that screen's animated moment.
"""
s = s.replace(old_sdk, new_sdk)
s = s.replace('| Download size | ~81 KB, one file |', '| Download size | ~86 KB, one file |')
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('README updated for cloud saves')
