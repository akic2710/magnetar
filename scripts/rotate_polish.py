import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        assert s.count(old) == 1, '%s: ambiguous -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


patch('src/p5.txt', [

# ---- the dismiss button has to clear the 44px touch minimum ----
("""  var bh = Math.max(40, 11*uc);""",
 """  /* 44 is the floor every touch guideline agrees on, and 11*uc only clears it
     above a ~400px narrow edge - so on a 375-wide phone this button was 41px
     and the one control on the screen was the one under the minimum. */
  var bh = Math.max(44, 11*uc);"""),

# ---- opaque over a menu, translucent over the arena ----
("""function drawRotate(){
  var L = rotateLayout(), uc = L.uc, cx = cssW/2, cy = L.cy;
  ctx.fillStyle = 'rgba(3,5,14,0.94)';
  ctx.fillRect(0, 0, cssW, cssH);""",
 """function drawRotate(){
  var L = rotateLayout(), uc = L.uc, cx = cssW/2, cy = L.cy;
  /* Over the arena the backdrop stays a little translucent, so the run reads
     as still there behind the prompt. Over a menu that hint is just noise: a
     card grid showing through at 6% is a smudge rather than depth, and the
     menu is not a thing you are in the middle of. */
  var overMenu = (G.mode === 'shop'  || G.mode === 'cores' || G.mode === 'over' ||
                  G.mode === 'levelup' || G.mode === 'revive');
  ctx.fillStyle = overMenu ? '#03050e' : 'rgba(3,5,14,0.94)';
  ctx.fillRect(0, 0, cssW, cssH);""")])

print('rotate prompt: 44px dismiss target, opaque backdrop over menus')
