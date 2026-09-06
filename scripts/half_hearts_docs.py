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

('[![Build](https://img.shields.io/badge/build-157_KB_single_file-6effc0?style=flat-square)](#magnetar)',
 '[![Build](https://img.shields.io/badge/build-%d_KB_single_file-6effc0?style=flat-square)](#magnetar)' % KB),
('- [x] **Download size** — 157 KB, one file, well under the 50 MB cap',
 '- [x] **Download size** — %d KB, one file, well under the 50 MB cap' % KB),

("""### Current balance

Latest sample is 15 bot runs per core, 90 runs total, capped at 6 minutes:""",
"""### Half hearts

Damage comes in half hearts. The split is meant to be readable off the screen
rather than memorised:

| | Costs | Why |
|---|---|---|
| Contact with the swarm — drone, spinner, shooter, splitter, lancer | **½** | Light things that chip at you |
| Contact with a brute or the Guardian | **1** | The things with weight behind them |
| A magnetic bolt | **½** | You were supposed to catch it |
| A lancer spike | **1** | The one attack you cannot catch and can only dodge |

Everything else about a hit scales with it too — the screen flash, the shake,
the hit-stop, and how much of the orbit you drop (half the orbit on a full
heart, a quarter on a chip). Losing a heart should still land like losing a
heart.

Hearts sit on exact 0.5 steps, so `hp <= 0` is a safe death test with no
epsilon, and the HUD draws a half diamond by clipping *before* the 45° rotation
— a diagonal cut reads as a smaller diamond rather than as half of one.

### Current balance

> **These numbers predate half hearts and are now optimistic.** In a controlled
> A/B — same bot, same seeds, only the damage model differing — median survival
> went from 52.5s to 123.5s (**+135%**) and mean from 78.1s to 137.1s (+76%),
> with several runs hitting the cap so the real effect is larger. The curve
> below has not been retuned to compensate; the game is meaningfully more
> forgiving than this table says.

Latest sample is 15 bot runs per core, 90 runs total, capped at 6 minutes:""")])


patch('SUBMISSION.md', [
("""Build size is ~157 KB in one file""",
 """Build size is ~%d KB in one file""" % KB)])

print('docs updated; build %d KB' % KB)
