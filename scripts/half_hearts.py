import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        assert s.count(old) == 1, '%s: ambiguous -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


# ------------------------------------------------------------------ p3
patch('src/p3.txt', [

# ---- healing has to clamp now that hp can sit on a half ----
("""    if(P.hp < P.maxHp){ P.hp++; A.sHeal(); popText(P.x,P.y-34,'+1 LIFE','#78ffa8',22); ring(P.x,P.y,90,'rgba(120,255,168,0.6)',0.5,3); }""",
 """    if(P.hp < P.maxHp){
      // Clamped: healing a whole heart off a half would overshoot the maximum.
      P.hp = Math.min(P.maxHp, P.hp + 1);
      A.sHeal(); popText(P.x,P.y-34,'+1 LIFE','#78ffa8',22); ring(P.x,P.y,90,'rgba(120,255,168,0.6)',0.5,3);
    }"""),

# ---- the damage model ----
("""function hurtPlayer(){
  if(P.inv>0 || G.mode!=='play' && G.mode!=='intro') return;
  P.hp--;
  P.inv = 1.35;
  G.combo = 0;
  G.dmgFlash = 1;
  A.sHurt();
  shakeIt(20);
  G.hitStop = Math.max(G.hitStop, 0.11);
  spark(P.x,P.y,22,'#ff5566',90,380,0.25,0.6,3.5);
  ring(P.x,P.y,140,'rgba(255,80,100,0.7)',0.5,4);
  // drop half the orbit on hit
  var drop = Math.floor(orbit.length/2);
  for(var i=0;i<drop;i++) orbit.pop();
  redistribute();
  if(P.hp<=0) die();
}""",
"""/* Damage comes in half hearts. The split is meant to be readable off the
   screen rather than memorised: the things that CHIP at you take half - the
   light swarm running into you, and the magnetic bullets you were supposed to
   be catching - and the things you are meant to actually fear take a whole
   one: a brute or the Guardian landing on you, and the lancer's spike, which
   is the single attack in the game you cannot catch and can only dodge.

   Halves are exact in binary, so hp stays on clean 0.5 steps and `<= 0` is a
   safe death test - no epsilon needed. */
function hurtPlayer(dmg){
  if(P.inv>0 || G.mode!=='play' && G.mode!=='intro') return;
  dmg = dmg || 1;
  P.hp -= dmg;
  P.inv = 1.35;
  G.combo = 0;
  /* Every bit of feedback scales with the hit, so a chip does not land like a
     killing blow. Losing a heart should still feel like losing a heart. */
  G.dmgFlash = dmg;
  A.sHurt();
  shakeIt(10 + 10*dmg);
  G.hitStop = Math.max(G.hitStop, 0.06 + 0.05*dmg);
  spark(P.x, P.y, Math.round(10 + 12*dmg), '#ff5566', 90, 380, 0.25, 0.6, 3.5);
  ring(P.x, P.y, 90 + 50*dmg, 'rgba(255,80,100,0.7)', 0.5, 4);
  // Orbit lost scales too: a graze should not cost a full release.
  var drop = Math.floor(orbit.length * 0.5 * dmg);
  for(var i=0;i<drop;i++) orbit.pop();
  redistribute();
  if(P.hp <= 0) die();
}""")])


# ------------------------------------------------------------------ p4
patch('src/p4.txt', [

("""var SHOT_SEEK = 330, SHOT_TURN = 7.5;""",
 """/* Half a heart from the swarm, a whole one from the things with weight behind
   them. Anything not listed chips for half. */
var CONTACT_DMG = { brute:1, boss:1 };

var SHOT_SEEK = 330, SHOT_TURN = 7.5;"""),

("""    if(G.mode!=='levelup' && len(P.x-e.x, P.y-e.y) < P.r + e.r*0.86){
      hurtPlayer();""",
 """    if(G.mode!=='levelup' && len(P.x-e.x, P.y-e.y) < P.r + e.r*0.86){
      hurtPlayer(CONTACT_DMG[e.type] || 0.5);"""),

("""    if(G.mode!=='levelup' && len(P.x-b.x,P.y-b.y) < P.r+b.r*0.8){
      bolts.splice(i,1);
      hurtPlayer();
      continue;
    }""",
 """    if(G.mode!=='levelup' && len(P.x-b.x,P.y-b.y) < P.r+b.r*0.8){
      bolts.splice(i,1);
      // A magnetic bolt was catchable, so eating one is a half. The lancer's
      // spike is not catchable, so it is the full heart.
      hurtPlayer(b.mag === false ? 1 : 0.5);
      continue;
    }""")])


# ------------------------------------------------------------------ p5
patch('src/p5.txt', [
("""  // lives
  for(var i=0;i<P.maxHp;i++){
    var x = 38+i*28, y = 40;
    var on = i<P.hp;
    ctx.save(); ctx.translate(x,y); ctx.rotate(Math.PI/4);
    if(on){
      ctx.fillStyle = P.hp<=1 ? '#ff5f7a' : C.player;
      ctx.fillRect(-7.5,-7.5,15,15);
    } else {
      ctx.strokeStyle='rgba(234,242,255,0.26)'; ctx.lineWidth=2;
      ctx.strokeRect(-7.5,-7.5,15,15);
    }
    ctx.restore();
  }""",
"""  // lives, in half hearts
  for(var i=0;i<P.maxHp;i++){
    var x = 38+i*28, y = 40;
    var full = P.hp >= i+1;
    var half = !full && P.hp > i;
    var lcol = P.hp<=1 ? '#ff5f7a' : C.player;
    ctx.save(); ctx.translate(x,y);
    if(half){
      /* Clipped BEFORE the rotation, so the cut runs vertically down the
         screen rather than along the diamond's own edge - a diagonal split
         reads as a smaller diamond rather than as half of one. */
      ctx.save();
      ctx.beginPath(); ctx.rect(-12,-12,12,24); ctx.clip();
      ctx.rotate(Math.PI/4);
      ctx.fillStyle = lcol;
      ctx.fillRect(-7.5,-7.5,15,15);
      ctx.restore();
      ctx.rotate(Math.PI/4);
      ctx.strokeStyle = hexA(lcol, 0.55); ctx.lineWidth = 2;
      ctx.strokeRect(-7.5,-7.5,15,15);
    } else {
      ctx.rotate(Math.PI/4);
      if(full){
        ctx.fillStyle = lcol;
        ctx.fillRect(-7.5,-7.5,15,15);
      } else {
        ctx.strokeStyle='rgba(234,242,255,0.26)'; ctx.lineWidth=2;
        ctx.strokeRect(-7.5,-7.5,15,15);
      }
    }
    ctx.restore();
  }""")])

print('half-heart damage wired: chip hits take 0.5, heavy hits take 1')
