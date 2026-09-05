# CrazyGames submission pack

Everything needed to submit is prepared and in this repo. The steps that
require an account, a login, or payout details are yours — see
[What only you can do](#what-only-you-can-do).

Build the upload artifact any time with:

```bash
node build.mjs && cd dist && zip -j ../submission/magnetar.zip index.html
```

---

## Files to upload

| What | File | Notes |
|---|---|---|
| Game build | `submission/magnetar.zip` | `index.html` at the zip root, no subfolders |
| Landscape cover | `covers/landscape_1920x1080.png` | 1920×1080 |
| Portrait cover | `covers/portrait_800x1200.png` | 800×1200 |
| Square cover | `covers/square_800x800.png` | 800×800 |

Build size is ~104 KB in one file — far inside the 50 MB initial-download cap
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
Touch — drag to steer, lift your finger to blast
Keyboard — arrows, WASD or ZQSD to move, Space or Shift to pull

M mute · P pause · 1 / 2 / 3 pick an upgrade · C cores · Enter restart
```

**Genre / category**

Primary: **Action**. Also fits Arcade and Shooting.

**Input methods**: mouse, keyboard, touch
**Players**: singleplayer
**Orientation**: landscape

**Tags**

```
arena, roguelite, one-button, magnet, survival, upgrades, waves, neon,
bullet-catching, arcade, singleplayer
```

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

Then: click *Submit a game*, upload `submission/magnetar.zip`, add the three
covers, paste the fields above, and send it. QA usually replies within one to
two days, often with screenshots of anything they want changed.

---

## One thing worth deciding first

The repo is public and MIT licensed, which explicitly permits anyone to take
this build and publish it. CrazyGames requires original IP from the submitter.
That is not a conflict for *you* — you are the author — but it does mean
someone else could submit a copy. Submitting sooner is the practical hedge; if
you would rather close that off, switching to a source-available licence is a
one-file change.
