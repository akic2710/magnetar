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

# ---- a measuring helper the game itself can use ----
("""/* Counts the lines wrapText would produce, without drawing any of them. Kept
   next to it so the two cannot disagree about where a break falls. */""",
 """/* Width of a tracked string, matching exactly what text() will draw. Lets a
   layout ask whether something fits before committing to drawing it. */
function textWidth(str, size, weight, track){
  ctx.font = (weight||700)+' '+size+'px system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif';
  if(!track) return ctx.measureText(str).width;
  var t = 0;
  for(var i=0;i<str.length;i++) t += ctx.measureText(str[i]).width + track;
  return t - track;
}

/* Counts the lines wrapText would produce, without drawing any of them. Kept
   next to it so the two cannot disagree about where a break falls. */"""),

# ---- the portrait death screen ----
("""/* -------------------------- cores, portrait ----------------------------""",
 """/* ------------------------ game over, portrait --------------------------
   Not a list like the other two, so it does not use the shared frame: it is a
   column of numbers with the actions underneath. The block is measured from
   its own type sizes and then centred, rather than pinned to fractions of the
   screen, so a 568-tall phone and a 932-tall one both look composed instead of
   one of them looking stretched.

   Unlike the shop and the core menu this screen KEEPS its banner. The death
   screen is the placement that actually earns, so rather than drop it the
   layout reserves a real strip at the bottom and lifts the buttons above it -
   the ad requirements ask for clear separation from the game's own controls,
   and 8px of dead space plus the ADVERTISEMENT label is what provides it. */
function overBannerBand(){
  /* Reserved only when a banner could actually fill: with no SDK - the
     Artifact build, or an adblocker - the roomier layout is what you get.
     320x50 is the narrowest unit, so below 340 CSS px nothing can fill. */
  var can = !!(window.CG && window.CG.ready && window.CG.bannersOk &&
               window.CG.adsOk && BANNER.fails < 3 && cssW >= 340);
  return can ? 74 : 0;
}

function overPortraitLayout(){
  var m = fit(cssW * 0.045, 12, 48);
  var w = Math.min(cssW - m*2, 560);
  var x0 = Math.round((cssW - w) / 2);

  var btnH = fit(cssH * 0.060, 46, 64);
  var bandH = overBannerBand();
  var bandY = cssH - bandH;
  /* Two rows: the thing you almost always want is full width on its own, and
     the two places you might go instead share the row below it. */
  var row2Y = (bandH ? bandY - 8 : cssH - m) - btnH;
  var row1Y = row2Y - 10 - btnH;

  var muteW = btnH;
  var mute = { x:x0 + w - muteW, y:row2Y, w:muteW, h:btnH };
  var half = (w - muteW - 16) / 2;
  var cores = { x:x0, y:row2Y, w:half, h:btnH };
  var shop  = { x:x0 + half + 8, y:row2Y, w:half, h:btnH };
  var play  = { x:x0, y:row1Y, w:w, h:btnH };

  var titleSize = fit(cssW * 0.075, 22, 38);
  var scoreSize = fit(cssW * 0.160, 44, 72);
  var statSize  = fit(cssW * 0.065, 18, 28);
  var fluxSize  = fit(cssW * 0.070, 20, 30);
  var small     = fit(cssW * 0.029, 10, 13);

  var top = m + Math.round(cssH * 0.02);
  var bot = row1Y - Math.round(cssH * 0.02);
  var block = titleSize + scoreSize + statSize + fluxSize + 4*small + 108;
  var y = top + Math.max(0, (bot - top - block) / 2);

  var titleY = y + titleSize*0.5;   y += titleSize + 8;
  var rankY  = y + small*0.5;       y += small + 20;
  var scoreY = y + scoreSize*0.5;   y += scoreSize + 6;
  var scoreLabelY = y + small*0.5;  y += small + 16;
  var hr1Y = y;                     y += 16;
  var statY = y + statSize*0.5;     y += statSize + 4;
  var statLabelY = y + small*0.5;   y += small + 16;
  var hr2Y = y;                     y += 16;
  var fluxY = y + fluxSize*0.5;     y += fluxSize + 6;
  var bankY = y + small*0.5;

  return { m:m, x0:x0, w:w, small:small,
           titleSize:titleSize, titleY:titleY, rankY:rankY,
           scoreSize:scoreSize, scoreY:scoreY, scoreLabelY:scoreLabelY,
           hr1Y:hr1Y,
           statSize:statSize, statY:statY, statLabelY:statLabelY,
           hr2Y:hr2Y,
           fluxSize:fluxSize, fluxY:fluxY, bankY:bankY,
           play:play, cores:cores, shop:shop, mute:mute,
           bandY:bandY, bandH:bandH };
}

/* The amplifier note is dropped to its short form, and then entirely, rather
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

function drawOverPortrait(){
  var L = overPortraitLayout();
  var t = G.overT||0, a = clamp(t*2.5, 0, 1);

  ctx.fillStyle = '#03050e';
  ctx.fillRect(0, 0, cssW, cssH);
  ctx.globalAlpha = a;

  var cx = L.x0 + L.w/2;
  text('CORE LOST', cx, L.titleY, L.titleSize, '#ff5f7a', 'center', 900, 1, 4);
  var bw = parseInt(store('mgn.bestwave')||'0',10);
  text('RANK  '+rankFor(bw), cx, L.rankY, L.small, C.dim, 'center', 700, 0.62, 3);

  text(String(G.score), cx, L.scoreY, L.scoreSize, C.text, 'center', 900, 1, 2);
  if(G.newBest){
    text('NEW BEST SCORE', cx, L.scoreLabelY, L.small, C.scrap, 'center', 800,
         0.65+0.35*Math.sin(G.uiT*6), 3);
  } else {
    text('SCORE', cx, L.scoreLabelY, L.small, C.dim, 'center', 700, 0.7, 4);
  }

  hr(L.x0, L.x0+L.w, L.hr1Y, a*0.10);

  var best = parseInt(store('mgn.best')||'0',10);
  var cols = [['WAVE', String(G.wave)],
              ['BEST COMBO', 'x'+G.bestCombo],
              ['BEST', String(Math.max(best, G.score))]];
  for(var i=0;i<3;i++){
    var sx = L.x0 + L.w*(i*2+1)/6;
    text(cols[i][1], sx, L.statY, L.statSize, C.text, 'center', 900, 1, 1);
    text(cols[i][0], sx, L.statLabelY, L.small, C.dim, 'center', 700, 0.75, 1.5);
  }

  hr(L.x0, L.x0+L.w, L.hr2Y, a*0.10);

  var shown = Math.round((G.fluxEarned||0) * clamp((t-0.35)/0.8, 0, 1));
  text('+'+shown+' FLUX', cx, L.fluxY, L.fluxSize, C.scrap, 'center', 900, 1, 2);
  text(overBankedLine(L), cx, L.bankY, L.small, C.dim, 'center', 700, 0.7, 1.5);

  var pulse = 0.65+0.35*Math.sin(G.uiT*4);
  var PB = L.play;
  ctx.fillStyle = hexA(C.player, 0.13+0.05*pulse);
  roundRect(PB.x, PB.y, PB.w, PB.h, 12); ctx.fill();
  ctx.strokeStyle = hexA(C.player, pulse); ctx.lineWidth = 2;
  roundRect(PB.x, PB.y, PB.w, PB.h, 12); ctx.stroke();
  text('PLAY AGAIN', PB.x+PB.w/2, PB.y+PB.h/2, fit(cssW*0.048, 16, 22), C.text, 'center', 900, 1, 3);

  var sm = fit(cssW*0.032, 11, 15);
  [[L.cores,'CORES'], [L.shop,'SHOP']].forEach(function(b){
    ctx.fillStyle = 'rgba(255,255,255,0.05)';
    roundRect(b[0].x, b[0].y, b[0].w, b[0].h, 12); ctx.fill();
    ctx.strokeStyle = 'rgba(234,242,255,0.26)'; ctx.lineWidth = 2;
    roundRect(b[0].x, b[0].y, b[0].w, b[0].h, 12); ctx.stroke();
    text(b[1], b[0].x+b[0].w/2, b[0].y+b[0].h/2, sm, C.text, 'center', 800, 1, 1.5);
  });

  drawBtn(L.mute, (A.muted||A.forced) ? 'muted' : 'sound');
  ctx.globalAlpha = 1;
}

function handleOverPortrait(){
  var x = IN.clickCssX, y = IN.clickCssY;
  var L = overPortraitLayout();
  function hit(r){ return x >= r.x && x <= r.x+r.w && y >= r.y && y <= r.y+r.h; }

  IN.swallow = true;            // never restart on a stray tap next to an ad
  if(hit(L.mute)){ A.setMute(!A.muted); A.sUi(); return; }
  if(hit(L.cores)){ openCores(); return; }
  if(hit(L.shop)){ openShop(); return; }
  // The same grace period the landscape screen uses, so the tap that killed
  // you cannot immediately start the next run.
  if(hit(L.play) && (G.overT||0) > 0.35){ restart(); return; }
}

/* -------------------------- cores, portrait ----------------------------"""),

# ---- landscape game over steps aside ----
("""function drawGameOver(){
  var t = G.overT||0;""",
 """function drawGameOver(){
  if(portraitUI()) return;      // drawn in CSS space after the HUD pass instead
  var t = G.overT||0;"""),

# ---- the prompt stands down here too ----
("""  if(G.mode === 'shop' || G.mode === 'cores') return false;""",
 """  if(G.mode === 'shop' || G.mode === 'cores' || G.mode === 'over') return false;"""),

# ---- draw ----
("""  if(portraitUI() && (G.mode === 'shop' || G.mode === 'cores')){
    ctx.setTransform(dpr,0,0,dpr,0,0);
    if(G.mode === 'shop') drawShopPortrait(); else drawCoresPortrait();
  }""",
 """  if(portraitUI() && (G.mode === 'shop' || G.mode === 'cores' || G.mode === 'over')){
    ctx.setTransform(dpr,0,0,dpr,0,0);
    if(G.mode === 'shop') drawShopPortrait();
    else if(G.mode === 'cores') drawCoresPortrait();
    else drawOverPortrait();
  }"""),

# ---- route taps ----
("""  if(portraitUI() && G.mode === 'cores'){ handleCoresPortrait(); return; }""",
 """  if(portraitUI() && G.mode === 'cores'){ handleCoresPortrait(); return; }
  if(portraitUI() && G.mode === 'over'){ handleOverPortrait(); return; }"""),

# ---- the banner band moves to CSS space on the portrait death screen ----
("""  /* Largest supported size that fits under the panel, or null. */
  pick:function(){
    var labelH = 14, pad = 10;
    var top = offY + this.bandTop()*scale;""",
 """  /* The portrait death screen reserves its band in CSS pixels rather than
     inside the letterboxed field, so it is the layout that says where the
     strip starts. */
  bandTopCss:function(){
    if(portraitUI() && G.mode === 'over') return overPortraitLayout().bandY;
    return offY + this.bandTop()*scale;
  },

  /* Largest supported size that fits under the panel, or null. */
  pick:function(){
    var labelH = 14, pad = 10;
    var top = this.bandTopCss();"""),
("""  place:function(size){
    if(!this.wrap) return;
    var labelH = 14;
    var top = offY + this.bandTop()*scale;""",
 """  place:function(size){
    if(!this.wrap) return;
    var labelH = 14;
    var top = this.bandTopCss();""")])

print('portrait game over wired, banner band reserved in CSS space')
