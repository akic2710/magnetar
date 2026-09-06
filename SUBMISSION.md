# CrazyGames submission pack

Everything needed to submit is prepared and in this repo. The steps that
require an account, a login, or payout details are yours — see
[What only you can do](#what-only-you-can-do).

Build the upload artifact any time with:

```bash
node build.mjs
```

That is the whole thing. **Upload `dist/index.html` on its own** — drag the file
straight into the upload zone. CrazyGames rejects archives ("Archive files are
not supported"), and since the game is one self-contained file there is nothing
to bundle anyway.

---

## Files to upload

| What | File | Notes |
|---|---|---|
| Game build | `dist/index.html` | The whole game, one file. Drag it in directly — no zip |
| Landscape cover | `covers/landscape_1920x1080.png` | 1920×1080 |
| Portrait cover | `covers/portrait_800x1200.png` | 800×1200 |
| Square cover | `covers/square_800x800.png` | 800×800 |
| Landscape video | `media/preview-landscape.mp4` | 1280×720, 10s, H.264, no audio |
| Portrait video | `media/preview-portrait.mp4` | 800×1200, 10s, gameplay over a title lockup |

Build size is ~159 KB in one file — far inside the 50 MB initial-download cap
and the 1,500 file limit, and inside the 20 MB threshold for mobile homepage
eligibility.

---

## Form fields, ready to paste

**Title**

```
Magnetar
```

**Short description**

```
Hold to pull, release to blast. Drag scrap and enemy fire into orbit around
you, then let go and send all of it back out at once.
```

**Description**

```
You are a magnetic core alone in a closed arena, and you have exactly one
button.

Hold it and everything loose gets dragged into orbit around you — scrap, and
the bullets fired at you. Let go and all of it launches back out at once,
seeking whatever is nearest. The blast is radial, so there is nothing to aim:
the skill is in what you gather, where you stand, and when you release.

Every wave is faster than the last. Drones charge, spinners weave, shooters
give you ammunition whether they like it or not, brutes soak everything you
have, and lancers fire a spike you cannot catch — only dodge. A Guardian
arrives every fifth wave.

Level up and choose from twelve stacking upgrades across three rarity tiers.
Bank Flux on every run and spend it on starting cores that rewrite how a run
opens: a heavy shell that grinds through the swarm, a hungry ring that holds
eleven objects at once, a glass cannon that punches through everything, or a
drifter that never has to slow down.

Runs last two to five minutes. Dying is part of it.
```

**Controls / instructions**

```
Mouse — move to steer, hold the button to pull, release to blast
Touch — drag to steer, lift your finger to blast (play in landscape)
Keyboard — arrows, WASD or ZQSD to move, Space or Shift to pull

M mute · P pause · 1 / 2 / 3 pick an upgrade · C cores · Enter restart
```

**Category** (CrazyGames' real list: action, adventure, arcade, board, card,
casual, clicker, driving, io, puzzle, shooting, sim, sports, strategy, trivia,
word)

Primary: **Action**. Arcade is the reasonable second choice.

**Input methods**: mouse, keyboard, touch
**Players**: singleplayer
**Orientation**: landscape

**Tags** — max 5. Confirmed against the actual picker in the submission form.

```
Arena, Survival, Skill, 2D, Difficult
```

| Tag | Why |
|---|---|
| `Arena` | Literally what it is: one closed arena, waves closing in |
| `Survival` | The whole objective — outlast escalating waves |
| `Skill` | Timing the release and reading the field is the game |
| `2D` | Factual, and how players filter |
| `Difficult` | True — most runs end in death, and it sets expectations |

**Category:** Action.

**Not in the picker** — do not try these again: play-and-upgrade, upgrade,
one-button, roguelike, roguelite, top-down, upgrades, magnet, waves, neon,
bullet-catching, bullet-hell, shoot-em-up, endless.

> Verification note: a `/t/<tag>` page returning 200 does **not** mean the tag
> is selectable in the developer form — the browse URL space is wider than the
> picker. The list above came from the form itself, which is the only authority.

---|---|
| `arena` | Literally what it is: one closed arena, waves closing in |
| `survive` | The whole objective — outlast escalating waves |
| `play-and-upgrade` | Level-up cards plus Flux and unlockable cores |
| `skill` | Timing the release and reading the field is the game |
| `2d` | Factual, and how players filter |

Alternates if any of those are missing from the picker: `avoid` (dodging
lancer spikes), `5-minute-fun` (runs are 2–5 minutes), `difficult` (most runs
end in death), `casual`, `adrenaline`, `destroy`.

**Do not use** — these were guessed at earlier and are wrong: roguelite,
upgrades, magnet, waves, neon, bullet-catching, bullet-hell,
shoot-em-up, endless, one-button, roguelike, top-down.

> Verification note: a `/t/<tag>` page returning 200 does **not** mean the tag
> is selectable in the developer form. The form's dropdown is the only
> authority. Pick from it; do not infer from site URLs.

---

## Requirements this build already meets

The full checklist with evidence is in the [README](README.md#crazygames-submission-checklist).
Short version: gameplay in zero clicks, onboarding inside gameplay, readable
from 800×450 to 1920×1080, fixed-timestep physics, no reserved keys, AZERTY
safe, full touch parity, zero external requests, PEGI 12, original IP.

SDK v3 is integrated and enabled in `dist/index.html`: cloud saves, gameplay
and loading events, happytime, progress reporting, a midgame ad on death, a
rewarded revive, and banners on the two menu screens only.

---

## What only you can do

I prepared everything above but stopped at these, and they are not
oversights:

1. **Create the developer account** at [developer.crazygames.com](https://developer.crazygames.com/).
   Signup needs an email, a display name, and **payout details (PayPal or bank
   transfer)**. I do not enter financial or account credentials, with or
   without permission.
2. **Sign in.** Same reason.
3. **Accept the developer agreement.** It is a contract in your name, and the
   submission form asks you to attest that you own the IP. Those are yours to
   make, not mine to click through.
4. **Press Submit.**

Then: click *Submit a game*, upload `dist/index.html`, add the three
covers, paste the fields above, and send it. QA usually replies within one to
two days, often with screenshots of anything they want changed.

---

## Licensing note

The repository is public but licensed **[PolyForm Strict 1.0.0](LICENSE)** —
source-available, read-only. Others may look at the code; they may not use,
modify or redistribute it, which closes off the risk of someone publishing a
copy of this build on a portal.

That does not restrict you: you hold the copyright, so you can submit,
monetise and relicense it however you like. The CrazyGames originality
requirement is satisfied — you are the author.

One caveat: earlier commits were published under MIT, and MIT cannot be
revoked for the versions it covered. The window was brief, but anyone who took
a copy during it keeps MIT rights to that snapshot.
