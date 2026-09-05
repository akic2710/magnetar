import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = 'src/p5.txt'
s = io.open(p, encoding='utf-8').read()

start = s.index("/* ------------------------------ game over ------------------------------ */")
end = s.index("function drawPaused(){")

new_block = '''/* ------------------------------ game over ------------------------------ */
var OVER_Y = 112;
function overBtns(){
  return {
    play:  {x:VW/2-190, y:OVER_Y+356, w:248, h:52},
    cores: {x:VW/2+74,  y:OVER_Y+356, w:116, h:52}
  };
}

function drawGameOver(){
  var t = G.overT||0;
  var a = clamp(t*2.5,0,1);
  ctx.fillStyle='rgba(3,5,14,'+(0.84*a)+')';
  ctx.fillRect(0,0,VW,VH);

  var by = OVER_Y, bx = VW/2-260, bw = 520, bh = 452;
  ctx.globalAlpha = a;
  ctx.fillStyle='rgba(255,255,255,0.045)';
  roundRect(bx,by,bw,bh,20); ctx.fill();
  ctx.strokeStyle='rgba(124,243,255,0.35)'; ctx.lineWidth=2;
  roundRect(bx,by,bw,bh,20); ctx.stroke();

  text('CORE LOST', VW/2, by+48, 38, '#ff5f7a', 'center', 900, 1, 5);
  text(String(G.score), VW/2, by+118, 72, C.text, 'center', 900, 1, 2);
  text('SCORE', VW/2, by+164, 12, C.dim, 'center', 700, 0.8, 4);

  var best = parseInt(store('mgn.best')||'0',10);
  var row = by+214;
  stat(VW/2-150, row, 'WAVE', String(G.wave));
  stat(VW/2,     row, 'BEST COMBO', 'x'+G.bestCombo);
  stat(VW/2+150, row, 'BEST', String(Math.max(best, G.score)));

  // The Flux payout counts up, so the reward for the run you just finished is
  // the thing that animates rather than a static number you skim past.
  var earned = G.fluxEarned||0;
  var shown = Math.round(earned * clamp((t-0.35)/0.8, 0, 1));
  text('+'+shown+' FLUX', VW/2, by+286, 30, C.scrap, 'center', 900, 1, 2);
  text(getFlux()+' BANKED', VW/2, by+316, 11, C.dim, 'center', 700, 0.75, 3);

  if(G.newBest){
    text('NEW BEST SCORE', VW/2, by+340, 15, C.scrap, 'center', 800, 0.7+0.3*Math.sin(G.uiT*6), 3);
  } else {
    var bw2 = parseInt(store('mgn.bestwave')||'0',10);
    text('RANK: '+rankFor(bw2), VW/2, by+340, 13, C.dim, 'center', 700, 0.7, 3);
  }

  var b = overBtns(), pulse = 0.65+0.35*Math.sin(G.uiT*4);
  ctx.fillStyle='rgba(124,243,255,'+(0.14+0.06*pulse)+')';
  roundRect(b.play.x,b.play.y,b.play.w,b.play.h,12); ctx.fill();
  ctx.strokeStyle='rgba(124,243,255,'+pulse+')'; ctx.lineWidth=2;
  roundRect(b.play.x,b.play.y,b.play.w,b.play.h,12); ctx.stroke();
  text('PLAY AGAIN', b.play.x+b.play.w/2, b.play.y+27, 20, C.text, 'center', 900, 1, 3);

  var hovC = IN.has && inRect(IN.x,IN.y,b.cores);
  ctx.fillStyle = hovC ? 'rgba(255,215,106,0.16)' : 'rgba(255,255,255,0.05)';
  roundRect(b.cores.x,b.cores.y,b.cores.w,b.cores.h,12); ctx.fill();
  ctx.strokeStyle = hovC ? C.scrap : 'rgba(234,242,255,0.28)'; ctx.lineWidth=2;
  roundRect(b.cores.x,b.cores.y,b.cores.w,b.cores.h,12); ctx.stroke();
  text('CORES', b.cores.x+b.cores.w/2, b.cores.y+27, 15, hovC?C.scrap:C.text, 'center', 800, 1, 2);

  text(IN.isTouch?'Tap anywhere to retry':'Click anywhere or press Enter to retry',
       VW/2, by+bh+24, 13, C.dim, 'center', 600, 0.65*a, 1);
  ctx.globalAlpha = 1;
}

var RANKS = [[20,'EVENT HORIZON'],[15,'SINGULARITY'],[10,'MAGNETAR'],[5,'FIELD TECH'],[1,'SCRAP RAT']];
function rankFor(w){
  for(var i=0;i<RANKS.length;i++) if(w>=RANKS[i][0]) return RANKS[i][1];
  return 'SCRAP RAT';
}
function stat(x,y,label,val){
  text(val, x, y, 26, C.text, 'center', 900, 1, 1);
  text(label, x, y+26, 11, C.dim, 'center', 700, 0.75, 2.5);
}

/* -------------------------------- cores -------------------------------- */
function coreCardRect(i){
  var col = i%3, row = Math.floor(i/3);
  return {x:80 + col*382, y:142 + row*254, w:356, h:228};
}
var BTN_LAUNCH = {x:VW/2-120, y:648, w:240, h:50};

function coreGlyph(c, cx, cy, r, alpha){
  ctx.globalCompositeOperation='lighter';
  blob(cx, cy, r*2.6, hexA(c.col, 0.30*alpha));
  ctx.globalCompositeOperation='source-over';
  ctx.globalAlpha = alpha;
  ctx.fillStyle = c.col;
  poly(cx, cy, r, c.sides, G.uiT*0.5); ctx.fill();
  ctx.fillStyle = '#ffffff';
  ctx.beginPath(); ctx.arc(cx, cy, r*0.30, 0, TAU); ctx.fill();
  ctx.strokeStyle = hexA(c.col, 0.45);
  ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.arc(cx, cy, r*1.55, 0, TAU); ctx.stroke();
  ctx.globalAlpha = 1;
}

function drawCores(){
  G.coreT = (G.coreT||0) + 0.016;
  var a = clamp(G.coreT*5,0,1);
  ctx.fillStyle='rgba(3,5,14,0.94)';
  ctx.fillRect(0,0,VW,VH);
  ctx.globalAlpha = a;

  text('CORES', 80, 68, 34, C.text, 'left', 900, 1, 6);
  text('Every run banks Flux. Spend it on a different way to open the next one.',
       80, 102, 13, C.dim, 'left', 600, 0.8, 0.5);

  var flux = getFlux();
  text(String(flux), VW-80, 62, 34, C.scrap, 'right', 900, 1, 1);
  text('FLUX BANKED', VW-80, 92, 11, C.dim, 'right', 700, 0.8, 3);

  var sel = selectedCore();
  for(var i=0;i<CORES.length;i++){
    var c = CORES[i], r = coreCardRect(i);
    var own = owns(c.id), eq = (c.id===sel), afford = flux >= c.cost;
    var hov = IN.has && inRect(IN.x,IN.y,r);
    var live = own || afford;          // dim only what you cannot act on yet
    var ca = a * (live ? 1 : 0.5);

    ctx.fillStyle = eq ? hexA(c.col,0.12) : (hov && live ? 'rgba(255,255,255,0.075)' : 'rgba(255,255,255,0.035)');
    roundRect(r.x,r.y,r.w,r.h,16); ctx.fill();
    ctx.strokeStyle = eq ? c.col : (hov && live ? hexA(c.col,0.75) : 'rgba(234,242,255,0.16)');
    ctx.lineWidth = eq ? 2.5 : 1.5;
    roundRect(r.x,r.y,r.w,r.h,16); ctx.stroke();

    coreGlyph(c, r.x+62, r.y+76, 24, ca);

    var tx = r.x+112;
    text(c.name, tx, r.y+42, 20, own?C.text:'rgba(234,242,255,0.8)', 'left', 900, ca, 1.5);
    wrapText(c.tag, tx, r.y+70, 12.5, C.dim, 224, 17, 'left', ca*0.85);

    ctx.globalAlpha = ca;
    ctx.strokeStyle = 'rgba(234,242,255,0.10)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(r.x+22, r.y+140); ctx.lineTo(r.x+r.w-22, r.y+140); ctx.stroke();
    ctx.globalAlpha = 1;

    for(var k=0;k<c.stats.length;k++){
      ctx.globalAlpha = ca*0.9;
      ctx.fillStyle = c.col;
      ctx.beginPath(); ctx.arc(r.x+26, r.y+164+k*20, 2.5, 0, TAU); ctx.fill();
      ctx.globalAlpha = 1;
      text(c.stats[k], r.x+38, r.y+164+k*20, 12.5, C.dim, 'left', 600, ca*0.9, 0.3);
    }

    var bxr = r.x+r.w-22, byr = r.y+r.h-28;
    if(eq)        text('EQUIPPED', bxr, byr, 14, c.col, 'right', 900, a, 2.5);
    else if(own)  text('SELECT',   bxr, byr, 14, hov?C.text:C.dim, 'right', 800, a, 2.5);
    else          text(c.cost+' FLUX', bxr, byr, 14, afford?C.scrap:'rgba(234,242,255,0.32)', 'right', 800, a, 2);
  }

  var hovL = IN.has && inRect(IN.x,IN.y,BTN_LAUNCH);
  var pulse = 0.6+0.4*Math.sin(G.uiT*4);
  ctx.fillStyle = 'rgba(124,243,255,'+(hovL?0.22:0.13)+')';
  roundRect(BTN_LAUNCH.x,BTN_LAUNCH.y,BTN_LAUNCH.w,BTN_LAUNCH.h,12); ctx.fill();
  ctx.strokeStyle = 'rgba(124,243,255,'+pulse+')'; ctx.lineWidth=2;
  roundRect(BTN_LAUNCH.x,BTN_LAUNCH.y,BTN_LAUNCH.w,BTN_LAUNCH.h,12); ctx.stroke();
  text('LAUNCH', VW/2, BTN_LAUNCH.y+26, 19, C.text, 'center', 900, 1, 3);

  drawBtn(BTN_MUTE, A.muted?'muted':'sound');
  ctx.globalAlpha = 1;
}

'''

s = s[:start] + new_block + s[end:]

# The old RANKS / rankFor / stat helpers lived inside the replaced region, so
# the slice above already removed them and new_block re-supplies exactly one.
for name, want in [('function rankFor', 1), ('function stat(', 1),
                   ('function drawGameOver', 1), ('function drawCores', 1),
                   ('function drawPaused', 1)]:
    got = s.count(name)
    assert got == want, '%s: expected %d, got %d' % (name, want, got)

io.open(p, 'w', encoding='utf-8').write(s)
print('p5: game-over rework + cores screen written')
