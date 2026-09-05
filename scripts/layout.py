import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

P5 = 'src/p5.txt'
s = io.open(P5, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')


def swap(start_marker, end_marker, new):
    """Replace the region [start_marker, end_marker) with new text."""
    global s
    a = s.index(start_marker)
    b = s.index(end_marker, a + len(start_marker))
    s = s[:a] + new + s[b:]


def sub(old, new):
    global s
    assert old in s, 'not found -> %r' % (old[:70],)
    s = s.replace(old, new, 1)


# --------------------------------------------------------------- constants
sub("""var BTN_MUTE  = {x:VW-104, y:VH-58, w:42, h:42};
var BTN_PAUSE = {x:VW-54,  y:VH-58, w:42, h:42};
function cardRect(i){ return {x:160 + i*330, y:186, w:300, h:348}; }""",
"""/* One spacing scale for every screen. Panels breathe at PAD, groups separate
   at GAP, and a hairline rule does the work that cramped spacing used to. */
var PAD = 28, GAP = 36;

var BTN_MUTE  = {x:VW-114, y:VH-76, w:44, h:44};
var BTN_PAUSE = {x:VW-60,  y:VH-76, w:44, h:44};

function cardRect(i){ return {x:130 + i*352, y:182, w:316, h:384}; }

/* Hairline divider - groups content without drawing another box around it. */
function hr(x1, x2, y, alpha){
  ctx.globalAlpha = (alpha===undefined?0.10:alpha);
  ctx.strokeStyle = '#eaf2ff';
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(x1, y+0.5); ctx.lineTo(x2, y+0.5); ctx.stroke();
  ctx.globalAlpha = 1;
}""")


# --------------------------------------------------------------- drawHUD
swap('function drawHUD(){', '\nfunction drawBtn(', '''function drawHUD(){
  // lives
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
  }

  // wave + remaining
  if(G.wave>0){
    text('WAVE '+G.wave, VW/2, 40, 21, C.text, 'center', 800, 0.92, 3);
    var remaining = enemies.length + G.spawnQ.length;
    if(remaining>0) text(remaining+' LEFT', VW/2, 66, 11, C.dim, 'center', 700, 0.75, 2.5);
  }

  // score
  text(String(G.score), VW-38, 40, 28, C.text, 'right', 800, 1, 1);
  var best = parseInt(store('mgn.best')||'0',10);
  text('BEST '+Math.max(best,G.score), VW-38, 66, 11, C.dim, 'right', 700, 0.75, 2);

  // boss bar, clear of the wave label above it
  if(G.bossRef && !G.bossRef.dead){
    var b = G.bossRef, w2 = 460, x2 = VW/2-w2/2, y2 = 100;
    text('GUARDIAN', VW/2, y2-14, 11, C.boss, 'center', 800, 0.95, 4);
    ctx.fillStyle='rgba(0,0,0,0.45)'; roundRect(x2,y2,w2,9,5); ctx.fill();
    ctx.fillStyle=C.boss; roundRect(x2,y2,Math.max(4,w2*clamp(b.hp/b.maxHp,0,1)),9,5); ctx.fill();
  }

  /* Wave announcement. The state for this was already being computed and
     decayed every frame but never drawn - it just needed a home. */
  if(G.waveBanner > 0 && G.waveBannerTxt){
    var wb = G.waveBanner;
    var alpha = clamp(Math.min((2.0-wb)/0.22, wb/0.55), 0, 1);
    var rise = (1 - clamp((2.0-wb)/0.45, 0, 1)) * 16;
    text(G.waveBannerTxt, VW/2, 214 - rise, 38, C.text, 'center', 900, alpha*0.9, 11);
  }

  // combo
  if(G.combo>1){
    var ca = clamp(G.comboT/2.6,0,1);
    var sz = 34 + Math.min(G.combo,12)*1.6;
    text('x'+G.combo, VW/2, 134, sz, C.scrap, 'center', 900, 0.35+ca*0.65, 1);
    text('COMBO', VW/2, 134+sz*0.64, 11, C.scrap, 'center', 700, ca*0.55, 4);
  }

  /* XP runs full-bleed along the very bottom edge. It used to be an inset
     rounded bar that passed underneath the mute and pause buttons. */
  var xpH = 5, xpY = VH-xpH;
  ctx.fillStyle='rgba(255,255,255,0.07)';
  ctx.fillRect(0, xpY, VW, xpH);
  ctx.fillStyle=C.player;
  ctx.fillRect(0, xpY, Math.max(3, VW*clamp(G.xp/G.xpNeed,0,1)), xpH);

  text('LV '+G.level, 38, VH-26, 12, C.dim, 'left', 700, 0.75, 2);
  text(coreById(P.core).name, 38+78, VH-26, 11, C.player, 'left', 700, 0.5, 2.5);

  drawBtn(BTN_MUTE, A.muted?'muted':'sound');
  drawBtn(BTN_PAUSE, G.paused?'play':'pause');
}
''')


# --------------------------------------------------------------- drawLevelUp
swap('function drawLevelUp(){', '\nfunction wrapText(', '''function drawLevelUp(){
  G.cardT = (G.cardT||0) + 0.016;
  var a = clamp(G.cardT*5,0,1);
  ctx.fillStyle='rgba(3,5,14,'+(0.82*a)+')';
  ctx.fillRect(0,0,VW,VH);

  var hi = RARITY[G.bestRarity||0];
  text('LEVEL '+G.level, VW/2, 92, 17, (G.bestRarity>=EPIC)?hi.col:C.scrap, 'center', 800, a, 6);
  text('CHOOSE AN UPGRADE', VW/2, 132, 34, C.text, 'center', 900, a, 5);

  for(var i=0;i<G.cards.length;i++){
    var r = cardRect(i), u = G.cards[i];
    var hov = IN.has && inRect(IN.x,IN.y,r);
    var lift = hov?8:0;
    var ca = clamp((G.cardT-i*0.06)*6,0,1);
    var top = r.y-lift;
    ctx.globalAlpha = ca;

    var rar = RARITY[u.r];

    // Epics carry a soft outer bloom so the good card reads across the room.
    if(u.r >= EPIC){
      var puls = 0.5 + 0.5*Math.sin(G.uiT*2.6 + i);
      ctx.globalAlpha = ca*(0.10 + 0.12*puls);
      ctx.strokeStyle = rar.col; ctx.lineWidth = 12;
      roundRect(r.x-3, top-3, r.w+6, r.h+6, 21); ctx.stroke();
      ctx.globalAlpha = ca;
    }

    ctx.fillStyle = hov ? hexA(rar.col,0.15) : 'rgba(255,255,255,0.042)';
    roundRect(r.x, top, r.w, r.h, 18); ctx.fill();
    ctx.strokeStyle = hov ? rar.col : hexA(rar.col, u.r?0.55:0.32);
    ctx.lineWidth = hov?3:(u.r?2:1.5);
    roundRect(r.x, top, r.w, r.h, 18); ctx.stroke();

    var cx = r.x+r.w/2;

    // header row
    text(String(i+1), r.x+PAD, top+34, 14, C.dim, 'left', 700, ca*0.8, 1);
    text(rar.name, r.x+r.w-PAD, top+34, 10, rar.col, 'right', 800, ca*0.95, 3.5);

    // icon
    var cy = top+142;
    ctx.globalCompositeOperation='lighter';
    blob(cx,cy,82, hexA(rar.col, rar.glow));
    ctx.globalCompositeOperation='source-over';
    ctx.strokeStyle = rar.col; ctx.lineWidth=3;
    poly(cx,cy,32, u.sides, G.uiT*(0.8+i*0.3)); ctx.stroke();
    ctx.fillStyle = rar.col; ctx.globalAlpha = ca*0.9;
    ctx.beginPath(); ctx.arc(cx,cy,8,0,TAU); ctx.fill();
    ctx.globalAlpha = ca;

    hr(r.x+PAD, r.x+r.w-PAD, top+212, ca*0.10);

    text(u.name, cx, top+250, 21, C.text, 'center', 900, ca, 1.5);
    wrapText(u.desc, cx, top+288, 15, C.dim, r.w-2*PAD-16, 21);

    // stack pips
    var taken = (G.taken&&G.taken[u.id])||0;
    for(var p=0;p<u.max;p++){
      var px = cx - (u.max-1)*8 + p*16;
      ctx.fillStyle = p<taken ? rar.col : 'rgba(234,242,255,0.18)';
      ctx.beginPath(); ctx.arc(px, top+r.h-42, 4, 0, TAU); ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  text(IN.isTouch?'Tap a card':'Click a card, or press 1 / 2 / 3',
       VW/2, 616, 14, C.dim, 'center', 600, a*0.75, 1.5);
}
''')


# --------------------------------------------------------------- drawGameOver
swap('/* ------------------------------ game over ------------------------------ */',
     '\nvar RANKS =', '''/* ------------------------------ game over ------------------------------ */
/* The panel sits higher when a banner has space reserved beneath it. */
function overY(){ return BANNER.reserved ? 48 : 100; }
var OVER_H = 512;

function overBtns(){
  var y = overY() + 418;
  return {
    play:  {x:VW/2-196, y:y, w:250, h:54},
    cores: {x:VW/2+66,  y:y, w:130, h:54}
  };
}

function drawGameOver(){
  var t = G.overT||0;
  var a = clamp(t*2.5,0,1);
  ctx.fillStyle='rgba(3,5,14,'+(0.84*a)+')';
  ctx.fillRect(0,0,VW,VH);

  var by = overY(), bw = 580, bx = VW/2-bw/2, bh = OVER_H;
  ctx.globalAlpha = a;
  ctx.fillStyle='rgba(255,255,255,0.042)';
  roundRect(bx,by,bw,bh,22); ctx.fill();
  ctx.strokeStyle=hexA(C.player,0.30); ctx.lineWidth=2;
  roundRect(bx,by,bw,bh,22); ctx.stroke();

  var inset = bx+PAD+10, inR = bx+bw-PAD-10;

  // identity
  text('CORE LOST', VW/2, by+54, 36, '#ff5f7a', 'center', 900, 1, 5);
  var bw2 = parseInt(store('mgn.bestwave')||'0',10);
  text('RANK  '+rankFor(bw2), VW/2, by+86, 11, C.dim, 'center', 700, 0.62, 4);

  // the number of the run
  text(String(G.score), VW/2, by+152, 66, C.text, 'center', 900, 1, 2);
  if(G.newBest){
    text('NEW BEST SCORE', VW/2, by+198, 12, C.scrap, 'center', 800, 0.65+0.35*Math.sin(G.uiT*6), 4);
  } else {
    text('SCORE', VW/2, by+198, 11, C.dim, 'center', 700, 0.7, 5);
  }

  hr(inset, inR, by+230, a*0.10);

  // run detail
  var best = parseInt(store('mgn.best')||'0',10);
  stat(VW/2-168, by+268, 'WAVE', String(G.wave));
  stat(VW/2,     by+268, 'BEST COMBO', 'x'+G.bestCombo);
  stat(VW/2+168, by+268, 'BEST', String(Math.max(best, G.score)));

  hr(inset, inR, by+326, a*0.10);

  // The Flux payout counts up, so the reward for the run you just finished is
  // the thing that animates rather than a static number you skim past.
  var earned = G.fluxEarned||0;
  var shown = Math.round(earned * clamp((t-0.35)/0.8, 0, 1));
  text('+'+shown+' FLUX', VW/2, by+366, 29, C.scrap, 'center', 900, 1, 2);
  text(getFlux()+' BANKED', VW/2, by+392, 11, C.dim, 'center', 700, 0.7, 4);

  // actions
  var b = overBtns(), pulse = 0.65+0.35*Math.sin(G.uiT*4);
  var hovP = IN.has && inRect(IN.x,IN.y,b.play);
  ctx.fillStyle=hexA(C.player, hovP?0.26:(0.13+0.05*pulse));
  roundRect(b.play.x,b.play.y,b.play.w,b.play.h,14); ctx.fill();
  ctx.strokeStyle=hexA(C.player, hovP?1:pulse); ctx.lineWidth=2;
  roundRect(b.play.x,b.play.y,b.play.w,b.play.h,14); ctx.stroke();
  text('PLAY AGAIN', b.play.x+b.play.w/2, b.play.y+28, 20, C.text, 'center', 900, 1, 3);

  var hovC = IN.has && inRect(IN.x,IN.y,b.cores);
  ctx.fillStyle = hovC ? hexA(C.scrap,0.16) : 'rgba(255,255,255,0.05)';
  roundRect(b.cores.x,b.cores.y,b.cores.w,b.cores.h,14); ctx.fill();
  ctx.strokeStyle = hovC ? C.scrap : 'rgba(234,242,255,0.26)'; ctx.lineWidth=2;
  roundRect(b.cores.x,b.cores.y,b.cores.w,b.cores.h,14); ctx.stroke();
  text('CORES', b.cores.x+b.cores.w/2, b.cores.y+28, 15, hovC?C.scrap:C.text, 'center', 800, 1, 2.5);

  // With an ad on screen, "click anywhere" would turn the whole page into a
  // button sitting next to it - the button becomes the only pointer target.
  var hint = BANNER.reserved
    ? (IN.isTouch ? 'Tap PLAY AGAIN to retry' : 'Press PLAY AGAIN or Enter to retry')
    : (IN.isTouch ? 'Tap anywhere to retry'   : 'Click anywhere or press Enter to retry');
  text(hint, VW/2, by+bh-30, 12, C.dim, 'center', 600, 0.55*a, 1.5);
  ctx.globalAlpha = 1;
}
''')


# --------------------------------------------------------------- drawCores
sub("""function coreCardRect(i){
  var col = i%3, row = Math.floor(i/3);
  return {x:80 + col*382, y:142 + row*254, w:356, h:228};
}
var BTN_LAUNCH = {x:VW/2-120, y:648, w:240, h:50};""",
"""function coreCardRect(i){
  var col = i%3, row = Math.floor(i/3);
  return {x:66 + col*392, y:152 + row*251, w:364, h:225};
}
var BTN_LAUNCH = {x:VW/2-130, y:650, w:260, h:52};""")

swap('function drawCores(){', '\n/* -------------------------------- ads', '''function drawCores(){
  G.coreT = (G.coreT||0) + 0.016;
  var a = clamp(G.coreT*5,0,1);
  ctx.fillStyle='rgba(3,5,14,0.94)';
  ctx.fillRect(0,0,VW,VH);
  ctx.globalAlpha = a;

  text('CORES', 66, 62, 34, C.text, 'left', 900, 1, 7);
  text('Every run banks Flux. Spend it on a different way to open the next one.',
       66, 98, 13, C.dim, 'left', 600, 0.75, 0.5);

  var flux = getFlux();
  text(String(flux), VW-66, 58, 34, C.scrap, 'right', 900, 1, 1);
  text('FLUX BANKED', VW-66, 88, 10, C.dim, 'right', 700, 0.75, 4);

  // Progression is only worth chasing if the player believes it will still be
  // there tomorrow, so say plainly where it is being kept.
  var synced = !!(window.CG && window.CG.cloud);
  var msg = synced ? 'SYNCED TO YOUR CRAZYGAMES ACCOUNT' : 'SAVED ON THIS DEVICE';
  var col = synced ? '#6effc0' : C.dim;
  ctx.globalAlpha = a*0.8;
  ctx.fillStyle = col;
  ctx.beginPath(); ctx.arc(70, 124, 3.5, 0, TAU); ctx.fill();
  ctx.globalAlpha = 1;
  text(msg, 82, 124, 10, col, 'left', 700, a*0.65, 2.5);

  var sel = selectedCore();
  for(var i=0;i<CORES.length;i++){
    var c = CORES[i], r = coreCardRect(i);
    var own = owns(c.id), eq = (c.id===sel), afford = flux >= c.cost;
    var hov = IN.has && inRect(IN.x,IN.y,r);
    var live = own || afford;          // dim only what you cannot act on yet
    var ca = a * (live ? 1 : 0.5);

    ctx.fillStyle = eq ? hexA(c.col,0.11) : (hov && live ? 'rgba(255,255,255,0.07)' : 'rgba(255,255,255,0.032)');
    roundRect(r.x,r.y,r.w,r.h,18); ctx.fill();
    ctx.strokeStyle = eq ? c.col : (hov && live ? hexA(c.col,0.75) : 'rgba(234,242,255,0.14)');
    ctx.lineWidth = eq ? 2.5 : 1.5;
    roundRect(r.x,r.y,r.w,r.h,18); ctx.stroke();

    coreGlyph(c, r.x+64, r.y+76, 25, ca);

    var tx = r.x+118;
    text(c.name, tx, r.y+44, 20, own?C.text:'rgba(234,242,255,0.8)', 'left', 900, ca, 1.5);
    wrapText(c.tag, tx, r.y+74, 12.5, C.dim, r.w-118-PAD, 18, 'left', ca*0.8);

    hr(r.x+PAD, r.x+r.w-PAD, r.y+134, ca*0.09);

    for(var k=0;k<c.stats.length;k++){
      var sy = r.y+160+k*22;
      ctx.globalAlpha = ca*0.9;
      ctx.fillStyle = c.col;
      ctx.beginPath(); ctx.arc(r.x+PAD+2, sy, 2.5, 0, TAU); ctx.fill();
      ctx.globalAlpha = 1;
      text(c.stats[k], r.x+PAD+14, sy, 12.5, C.dim, 'left', 600, ca*0.85, 0.3);
    }

    var bxr = r.x+r.w-PAD, byr = r.y+r.h-26;
    if(eq)        text('EQUIPPED', bxr, byr, 13, c.col, 'right', 900, a, 3);
    else if(own)  text('SELECT',   bxr, byr, 13, hov?C.text:C.dim, 'right', 800, a, 3);
    else          text(c.cost+' FLUX', bxr, byr, 13, afford?C.scrap:'rgba(234,242,255,0.32)', 'right', 800, a, 2.5);
  }

  var hovL = IN.has && inRect(IN.x,IN.y,BTN_LAUNCH);
  var pulse = 0.6+0.4*Math.sin(G.uiT*4);
  ctx.fillStyle = hexA(C.player, hovL?0.24:0.13);
  roundRect(BTN_LAUNCH.x,BTN_LAUNCH.y,BTN_LAUNCH.w,BTN_LAUNCH.h,14); ctx.fill();
  ctx.strokeStyle = hexA(C.player, hovL?1:pulse); ctx.lineWidth=2;
  roundRect(BTN_LAUNCH.x,BTN_LAUNCH.y,BTN_LAUNCH.w,BTN_LAUNCH.h,14); ctx.stroke();
  text('LAUNCH', VW/2, BTN_LAUNCH.y+27, 19, C.text, 'center', 900, 1, 4);

  drawBtn(BTN_MUTE, A.muted?'muted':'sound');
  ctx.globalAlpha = 1;
}
''')


# --------------------------------------------------------------- drawRevive
swap('function reviveBtns(){', '\nfunction drawAdBusy(', '''function reviveBtns(){
  var by = 186;
  return {
    yes:{x:VW/2-262, y:by+192, w:300, h:60},
    no: {x:VW/2+42,  y:by+192, w:220, h:60}
  };
}

function drawRevive(){
  ctx.fillStyle='rgba(3,5,14,0.80)';
  ctx.fillRect(0,0,VW,VH);

  var by=186, bw=620, bx=VW/2-bw/2, bh=330;
  ctx.fillStyle='rgba(255,255,255,0.048)';
  roundRect(bx,by,bw,bh,22); ctx.fill();
  ctx.strokeStyle=hexA(C.player,0.36); ctx.lineWidth=2;
  roundRect(bx,by,bw,bh,22); ctx.stroke();

  text('CORE LOST', VW/2, by+52, 26, '#ff5f7a', 'center', 900, 1, 5);
  text('WAVE '+G.wave+'    '+G.score+' PTS', VW/2, by+82, 12, C.dim, 'center', 700, 0.7, 3);

  hr(bx+PAD+10, bx+bw-PAD-10, by+108, 0.10);

  text('Watch a short ad to get back in?', VW/2, by+142, 21, C.text, 'center', 800, 1, 0.5);
  text('Optional \\u2014 declining keeps every point and every Flux you earned.',
       VW/2, by+168, 12, C.dim, 'center', 600, 0.7, 0.4);

  var b = reviveBtns();
  var hy = IN.has && inRect(IN.x,IN.y,b.yes);
  ctx.fillStyle = hexA(C.player, hy?0.24:0.13);
  roundRect(b.yes.x,b.yes.y,b.yes.w,b.yes.h,14); ctx.fill();
  ctx.strokeStyle = hexA(C.player, hy?1:0.7); ctx.lineWidth=2;
  roundRect(b.yes.x,b.yes.y,b.yes.w,b.yes.h,14); ctx.stroke();
  text('WATCH AD TO REVIVE', b.yes.x+b.yes.w/2, b.yes.y+24, 17, C.text, 'center', 900, 1, 1.5);
  text('2 lives, back where you fell   \\u00b7   press Y',
       b.yes.x+b.yes.w/2, b.yes.y+44, 10, C.dim, 'center', 700, 0.65, 0.6);

  var hn = IN.has && inRect(IN.x,IN.y,b.no);
  ctx.fillStyle = hn?'rgba(255,255,255,0.09)':'rgba(255,255,255,0.04)';
  roundRect(b.no.x,b.no.y,b.no.w,b.no.h,14); ctx.fill();
  ctx.strokeStyle = 'rgba(234,242,255,'+(hn?0.5:0.24)+')'; ctx.lineWidth=2;
  roundRect(b.no.x,b.no.y,b.no.w,b.no.h,14); ctx.stroke();
  text('NO THANKS', b.no.x+b.no.w/2, b.no.y+24, 17, C.text, 'center', 800, 1, 2);
  text('press N', b.no.x+b.no.w/2, b.no.y+44, 10, C.dim, 'center', 700, 0.65, 1.5);

  // The docs ask for a visible timer on a rewarded request.
  var frac = clamp(G.reviveT/REVIVE_SECONDS, 0, 1);
  var cx = VW/2, cy = by+bh-32;
  ctx.strokeStyle='rgba(234,242,255,0.14)'; ctx.lineWidth=3;
  ctx.beginPath(); ctx.arc(cx-16,cy,11,0,TAU); ctx.stroke();
  ctx.strokeStyle=C.scrap; ctx.lineWidth=3;
  ctx.beginPath(); ctx.arc(cx-16,cy,11,-Math.PI/2,-Math.PI/2+TAU*frac); ctx.stroke();
  text(Math.ceil(Math.max(0,G.reviveT))+'s', cx+4, cy, 12, C.dim, 'left', 800, 0.7, 1);
}
''')


# --------------------------------------------------------------- banner band
s = s.replace('offY + 570*scale', 'offY + 582*scale')

io.open(P5, 'w', encoding='utf-8', newline='\n').write(s)
print('layout pass applied')
