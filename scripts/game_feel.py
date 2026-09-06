import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        assert s.count(old) == 1, '%s: ambiguous -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


# ------------------------------------------------------------------ p1: two cues
patch('src/p1.txt', [(
"""  sUi:function(){ this.tone(700,0.06,'square',0.10,900); },""",
"""  sUi:function(){ this.tone(700,0.06,'square',0.10,900); },
  /* The orbit hitting capacity is the one moment the game wants you to act on,
     so it gets its own two-note lift rather than being left to the hum. */
  sCharged:function(){
    this.tone(880,0.09,'triangle',0.11,1180);
    this.tone(1318,0.16,'sine',0.08,null,0.055);
  },
  /* Passing your own best mid-run - short and bright, not a fanfare. */
  sBest:function(){
    var n=[784,1046,1318];
    for(var i=0;i<3;i++) this.tone(n[i],0.26,'triangle',0.15,null,i*0.06);
  },""")])


# ------------------------------------------------------------------ p2: state
patch('src/p2.txt', [(
"""    shopT:0, menuMsg:'', menuMsgT:0, shopTab:0""",
"""    shopT:0, menuMsg:'', menuMsgT:0, shopTab:0,
    charged:false, chargeT:0, passedBest:false""")])


# ------------------------------------------------------------------ p3
patch('src/p3.txt', [

# ---- the charged moment ----
("""function captureInto(kind, x, y, r){
  if(orbit.length >= P.cap) return false;
  orbit.push({kind:kind, ang:0, cur:len(x-P.x,y-P.y), r:r, x:x, y:y, spin:rnd(-4,4), t:0});
  redistribute();
  return true;
}""",
"""function captureInto(kind, x, y, r){
  if(orbit.length >= P.cap) return false;
  orbit.push({kind:kind, ang:0, cur:len(x-P.x,y-P.y), r:r, x:x, y:y, spin:rnd(-4,4), t:0});
  redistribute();
  /* Filling the orbit is the moment the whole verb is building towards, and it
     used to pass in silence - you found out by watching a thin arc change
     colour. One cue, once, on the frame it fills. */
  if(orbit.length >= P.cap && !G.charged){
    G.charged = true;
    G.chargeT = 0.55;
    A.sCharged();
    ring(P.x, P.y, P.orbR*2.8, hexA(C.scrap,0.65), 0.42, 3);
  }
  return true;
}"""),

# ---- passing your own best, mid-run ----
("""  var mult = 1 + (G.combo-1)*0.12;
  var pts = Math.round(e.sc * mult);
  G.score += pts;
  G.xp += e.xp;""",
"""  var mult = 1 + (G.combo-1)*0.12;
  var pts = Math.round(e.sc * mult);
  G.score += pts;
  G.xp += e.xp;

  /* The run stops being "a run" and becomes "the run" the moment it passes
     your own record, so say so then rather than only on the death screen. */
  if(!G.passedBest){
    var pb = parseInt(store('mgn.best')||'0',10);
    if(pb > 0 && G.score > pb){
      G.passedBest = true;
      A.sBest();
      popText(P.x, P.y-54, 'NEW BEST', C.scrap, 28);
      ring(P.x, P.y, 230, hexA(C.scrap,0.65), 0.7, 4);
      G.flash = Math.max(G.flash, 0.35);
    }
  }"""),

# ---- the charge flag has to clear when the orbit is no longer full ----
("""  /* ---- cosmetic wake ---- */""",
"""  if(orbit.length < P.cap) G.charged = false;

  /* ---- cosmetic wake ---- */""")])


# ------------------------------------------------------------------ p5
patch('src/p5.txt', [

# ---- charge timer decays on real time with the other presentation timers ----
("""  G.chroma   = Math.max(0, G.chroma   - rdt*1.4);""",
 """  G.chroma   = Math.max(0, G.chroma   - rdt*1.4);
  G.chargeT  = Math.max(0, G.chargeT  - rdt*1.6);"""),

# ---- a full orbit reads as full at a glance ----
("""  if(orbit.length>0){
    var frac = orbit.length/P.cap;
    ctx.strokeStyle = frac>=1 ? C.scrap : hexA(C.player,0.75);
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(P.x,P.y,pr*2.2,-Math.PI/2, -Math.PI/2 + TAU*Math.min(1,frac));
    ctx.stroke();
  }""",
"""  if(orbit.length>0){
    var frac = orbit.length/P.cap;
    var full = frac >= 1;
    // At capacity the ring breathes, so "let go now" is readable peripherally.
    ctx.strokeStyle = full ? hexA(C.scrap, 0.65+0.35*Math.sin(G.t*11)) : hexA(C.player,0.75);
    ctx.lineWidth = full ? 4 : 3;
    ctx.beginPath();
    ctx.arc(P.x,P.y,pr*2.2,-Math.PI/2, -Math.PI/2 + TAU*Math.min(1,frac));
    ctx.stroke();
    if(G.chargeT > 0){
      ctx.globalAlpha = clamp(G.chargeT/0.55, 0, 1) * 0.5;
      ctx.strokeStyle = C.scrap; ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(P.x, P.y, pr*2.2 + (1-clamp(G.chargeT/0.55,0,1))*26, 0, TAU);
      ctx.stroke();
      ctx.globalAlpha = 1;
    }
  }"""),

# ---- the combo becomes something you can play to ----
("""  if(G.combo>1){
    var ca = clamp(G.comboT/2.6,0,1);
    var sz = 34 + Math.min(G.combo,12)*1.6;
    text('x'+G.combo, VW/2, 134, sz, C.scrap, 'center', 900, 0.35+ca*0.65, 1);
    text('COMBO', VW/2, 134+sz*0.64, 11, C.scrap, 'center', 700, ca*0.55, 4);
  }""",
"""  if(G.combo>1){
    var ca = clamp(G.comboT/2.6,0,1);
    var sz = 34 + Math.min(G.combo,12)*1.6;
    text('x'+G.combo, VW/2, 134, sz, C.scrap, 'center', 900, 0.35+ca*0.65, 1);
    text('COMBO', VW/2, 134+sz*0.64, 11, C.scrap, 'center', 700, ca*0.55, 4);
    /* A chain that expires invisibly is a chain you cannot play to. The bar is
       the same information the alpha was already carrying, made readable. */
    var cbw = 72, cbx = VW/2 - cbw/2, cby = Math.round(134 + sz*0.64 + 13);
    ctx.globalAlpha = ca*0.75;
    ctx.fillStyle = hexA(C.scrap, 0.20); ctx.fillRect(cbx, cby, cbw, 3);
    ctx.fillStyle = C.scrap;             ctx.fillRect(cbx, cby, cbw*ca, 3);
    ctx.globalAlpha = 1;
  }"""),

# ---- the next thing to play for ----
("""/* Width of a tracked string, matching exactly what text() will draw.""",
 """/* The cheapest thing you do not own and could buy next. Shown when the run
   ends, because the moment you have just banked Flux is the moment the next
   unlock actually means something - and "250 more" is a reason to press play
   that a bare balance is not. */
function nextUnlock(){
  var best = null, i, c;
  for(i=0;i<CORES.length;i++){
    c = CORES[i];
    if(c.cost > 0 && !owns(c.id) && (!best || c.cost < best.cost)) best = {name:c.name, cost:c.cost};
  }
  for(i=0;i<SHOP.length;i++){
    var it = SHOP[i];
    if(it.cost > 0 && !ownsItem(it.id) && !itemLocked(it) && (!best || it.cost < best.cost)){
      best = {name:it.name, cost:it.cost};
    }
  }
  return best;
}

/* One line for what you have, what it is nearly enough for, and whether an
   amplifier padded it - composed longest-first and trimmed until it fits, so a
   280-wide phone drops the least important part instead of overflowing. */
function bankedLine(maxW, size){
  var flux = getFlux();
  var base = flux + ' BANKED';
  var nx = nextUnlock(), mul = fluxMul();
  var goal = '', amp = '';
  if(nx){
    var need = nx.cost - flux;
    goal = (need > 0) ? ('   \\u00b7   ' + need + ' TO ' + nx.name)
                      : ('   \\u00b7   ENOUGH FOR ' + nx.name);
  }
  if(mul > 1) amp = '   \\u00b7   x' + mul.toFixed(2);
  var tries = [base+goal+amp, base+goal, base+amp, base];
  for(var i=0;i<tries.length;i++){
    if(textWidth(tries[i], size, 700, 1.5) <= maxW) return tries[i];
  }
  return base;
}

/* Width of a tracked string, matching exactly what text() will draw."""),

# ---- landscape death screen uses it ----
("""  var mul = fluxMul();
  var banked = getFlux()+' BANKED';
  if(mul > 1) banked += '   \\u00b7   AMPLIFIER x'+mul.toFixed(2);
  text(banked, VW/2, by+392, 11, C.dim, 'center', 700, 0.7, 4);""",
 """  text(bankedLine(bw - PAD*2, 11), VW/2, by+392, 11, C.dim, 'center', 700, 0.7, 1.5);"""),

# ---- and so does the portrait one ----
("""/* The amplifier note is dropped to its short form, and then entirely, rather
   than allowed to run off a narrow screen. */
function overBankedLine(L){
  var mul = fluxMul();
  var base = getFlux() + ' BANKED';
  if(mul <= 1) return base;
  var full = base + '   \\u00b7   AMPLIFIER x' + mul.toFixed(2);
  if(textWidth(full, L.small, 700, 1.5) <= L.w) return full;
  var short = base + '   \\u00b7   x' + mul.toFixed(2);
  if(textWidth(short, L.small, 700, 1.5) <= L.w) return short;
  return base;
}

""", ""),
("""  text(overBankedLine(L), cx, L.bankY, L.small, C.dim, 'center', 700, 0.7, 1.5);""",
 """  text(bankedLine(L.w, L.small), cx, L.bankY, L.small, C.dim, 'center', 700, 0.7, 1.5);""")])

print('game feel: charged cue, combo timer, mid-run best callout, next-unlock line')
