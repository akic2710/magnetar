import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        assert s.count(old) == 1, '%s: ambiguous -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


patch('src/p5.txt', [(
"""  var u = Math.min(cssW, cssH) / 100;
  var uc = Math.min(u, 5);
  var cy = cssH/2 - 14*uc;""",
"""  var u = Math.min(cssW, cssH) / 100;
  /* The unit comes off the narrow edge, but the lockup is laid out DOWN the
     screen - so a short viewport has to shrink it or the dismiss button walks
     off the bottom. Everything below centre is 52*uc plus the button plus a
     margin, and that has to fit in the lower half. A 360x400 frame put the
     button 27px past the bottom edge before this. Real phones are nowhere near
     the limit, so none of them change. */
  var uc = Math.max(2, Math.min(u, 5, (cssH/2 - 52) / 52));
  var cy = cssH/2 - 14*uc;"""),
(
"""  var bw = Math.min(cssW*0.62, 58*uc);
  return { u:u, uc:uc, cy:cy,
           titleY: cy + 46*uc,
           subY:   cy + 57*uc,
           btn: { x:(cssW-bw)/2, y:cy + 66*uc, w:bw, h:bh } };""",
"""  var bw = Math.min(cssW*0.62, 58*uc);
  /* Last resort below the size the shrink can rescue: crowded text is ugly,
     but a dismiss button under the fold is a trap - the prompt swallows every
     tap, so an unreachable button means an unplayable game. Keep it on screen. */
  var by = Math.min(cy + 66*uc, cssH - bh - 8);
  return { u:u, uc:uc, cy:cy,
           titleY: cy + 46*uc,
           subY:   cy + 57*uc,
           btn: { x:(cssW-bw)/2, y:by, w:bw, h:bh } };""")])

print('rotate prompt: lockup shrinks to fit short viewports, button never off screen')
