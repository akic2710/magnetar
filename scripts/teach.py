import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        assert s.count(old) == 1, '%s: ambiguous -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


# ------------------------------------------------------------------ p2
patch('src/p2.txt', [

# ---- what each type actually wants you to know ----
("""function makeEnemy(type, x, y){""",
"""/* Six types arrive between waves 2 and 11 and nothing ever named them. Each
   line is the ONE rule that changes what you should do - not flavour, and not
   a stat sheet. The drone is left out on purpose: it is the first thing you
   ever see and it does the obvious thing.

   The shooter and the lancer are the pair that matter most. The whole game
   rests on "their shots are ammunition", and on the single exception to it,
   and neither was ever said out loud. */
var ETYPE_HINT = {
  spinner:  'SPINNER \\u2014 fast, and never in a straight line',
  shooter:  'SHOOTER \\u2014 its shots are magnetic. Catch them and send them back',
  splitter: 'SPLITTER \\u2014 breaks into drones when it dies',
  brute:    'BRUTE \\u2014 heavy. Touching one costs a whole heart',
  lancer:   'LANCER \\u2014 its spike cannot be caught. Dodge it'
};

function makeEnemy(type, x, y){"""),

# ---- queue a hint the first time a type shows up in a run ----
("""function spawnAt(type, pt){
  var e = makeEnemy(type, pt.x, pt.y);
  enemies.push(e);""",
"""function spawnAt(type, pt){
  var e = makeEnemy(type, pt.x, pt.y);
  enemies.push(e);
  // Queued rather than shown, so two new types in one wave do not overlap.
  if(ETYPE_HINT[type] && !G.seen[type]){
    G.seen[type] = 1;
    G.hintQ.push(ETYPE_HINT[type]);
  }"""),

# ---- per-run state ----
("""    charged:false, chargeT:0, passedBest:false""",
 """    charged:false, chargeT:0, passedBest:false,
    seen:{}, hintQ:[], hintTxt:'', hintT:0""")])


# ------------------------------------------------------------------ p5
patch('src/p5.txt', [

# ---- advance the queue on real time ----
("""  G.chargeT  = Math.max(0, G.chargeT  - rdt*1.6);""",
 """  G.chargeT  = Math.max(0, G.chargeT  - rdt*1.6);
  /* One hint at a time, and only once the last has cleared - the point is to
     reduce what you have to take in, not to add a second thing to read. */
  if(G.hintT > 0) G.hintT -= rdt;
  else if(G.hintQ && G.hintQ.length){ G.hintTxt = G.hintQ.shift(); G.hintT = HINT_SECONDS; }"""),

# ---- draw it under the wave banner ----
("""  // combo
  if(G.combo>1){""",
 """  /* Sits below the wave announcement, in the calm band above the fight. */
  if(G.hintT > 0 && G.hintTxt && (G.mode==='play' || G.mode==='intro')){
    var hfade = clamp(Math.min(G.hintT/0.6, (HINT_SECONDS-G.hintT)/0.4), 0, 1);
    text(G.hintTxt, VW/2, 252, 15, C.text, 'center', 700, hfade*0.82, 1.2);
  }

  // combo
  if(G.combo>1){"""),

# ---- a calmer combo readout ----
("""    var sz = 34 + Math.min(G.combo,12)*1.6;""",
 """    // Was 34 + up to 19px, which put a 53px number in the middle of the fight.
    var sz = 30 + Math.min(G.combo,10)*1.3;"""),

# ---- the constant, next to the other HUD tuning ----
("""var PAD = 28, GAP = 36;""",
 """var PAD = 28, GAP = 36;
var HINT_SECONDS = 3.6;      // long enough to read once, short enough to ignore"""),

# ---- and say the exception in the intro, where the rule is first stated ----
("""  else { line1 = 'Catch their shots. Send them back.'; line2 = 'Survive the waves.'; }""",
 """  else { line1 = 'Catch their shots. Send them back.'; line2 = 'White spikes cannot be caught \\u2014 dodge those.'; }""")])

print('teaching pass: first-encounter hints, calmer combo, the exception stated up front')
