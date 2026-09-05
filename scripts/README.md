# scripts/

One-shot patch scripts used to transform `src/` during development, kept as a
record of how each feature landed. **They are history, not tooling.**

## Do not try to re-run these

Each script was applied exactly once. They work by asserting on an exact
snippet of `src/` and replacing it:

```python
assert old in s, 'not found -> %r' % (old[:70],)
s = s.replace(old, new, 1)
```

Once applied, `old` no longer exists, so a second run fails its assertion by
design — that assertion is the only thing that kept a silent partial edit from
shipping. Running them against the current `src/` will not reproduce anything.

**`src/` is the source of truth.** The only command that matters is:

```bash
node build.mjs
```

## This is not a complete replay

Plenty of smaller edits were made with inline shell one-liners that were never
saved here, and at least one script (`restore_banner.py`) exists purely to undo
damage from another one. Applying these in order against an empty tree would
not rebuild the game. Read them for intent, not as a migration chain.

## Rough order applied

| # | Script | What it did |
|---|---|---|
| 1-2 | `add_cores_ui.py`, `wire_cores_input.py` | Game-over rework and the core select screen |
| 3-4 | `tune_economy.py`, `balance_cores.py` | Flux pacing; cores rebalanced as sidegrades |
| 5-6 | `cloud_saves.py`, `sdk_adapter.py` | Persistence layer, derived Flux, CrazyGames SDK adapter |
| 7 | `fix_build_unwrap.py` | Made the test-build unwrap newline-agnostic and checked per step |
| 9-10 | `ads.py`, `ads_ui.py` | Midgame ad and rewarded revive |
| 12 | `banners.py` | Death-screen banner |
| 14 | `rarity.py` | Upgrade rarity tiers |
| 16 | `layout.py` | Spacing and layout pass |
| 17 | `restore_banner.py` | Restored the BANNER block that `layout.py` deleted by accident |
| 19-20 | `cores_banner.py`, `banner_token.py` | Core-menu banner; reveal-on-fill and request tokens |

`readme_*.py` scripts (8, 11, 13, 15, 18) only edited `README.md`.

Two of these are worth reading as cautionary tales: `fix_build_unwrap.py` and
`restore_banner.py` both exist because a patch passed `node --check` while
being silently wrong — valid JavaScript is not the same as correct output.
