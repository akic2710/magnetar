import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def read(p):
    return io.open(p, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')


def write(p, s):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)


def patch(path, pairs):
    s = read(path)
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        assert s.count(old) == 1, '%s: ambiguous -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    write(path, s)


# ---------------------------------------------------------------- rename
# The message is shown by both meta screens now, so it stops being the shop's.
for f in ('src/p2.txt', 'src/p5.txt'):
    s = read(f)
    n = s.count('shopMsg')
    s = s.replace('shopMsg', 'menuMsg')          # also fixes shopMsgT -> menuMsgT
    write(f, s)
    print('%s: renamed %d shopMsg -> menuMsg' % (f, n))


# ---------------------------------------------------------------- p5
patch('src/p5.txt', [

# ---- shared frame, extracted from the shop's layout ----
("""function shopPortraitLayout(){
  var m = fit(cssW * 0.045, 12, 48);
  // Past ~560 the column stops widening and centres instead - a full-width
  // card on a tablet is a very long line for four words of tag text.
  var w = Math.min(cssW - m*2, 560);
  var x0 = Math.round((cssW - w) / 2);

  var titleSize = fit(cssW * 0.068, 20, 34);
  var headTop = m + Math.round(cssH * 0.012);
  var titleY = headTop + titleSize*0.6;
  var subY = titleY + titleSize*0.78;

  var tabH = fit(cssH * 0.050, 44, 56);          // 44 is the touch minimum
  var tabY = subY + Math.round(cssH * 0.022);
  var tabW = (w - 12) / 3;

  /* The bottom row carries the same three controls the landscape screen ends
     on, so leaving portrait does not change what the buttons are. */
  var btnH = fit(cssH * 0.060, 46, 64);
  var btnY = cssH - m - btnH;
  var muteW = btnH;
  var altW = Math.min(96, Math.round(w * 0.28));
  var mute = { x:x0 + w - muteW, y:btnY, w:muteW, h:btnH };
  var alt  = { x:mute.x - 8 - altW, y:btnY, w:altW, h:btnH };
  var launch = { x:x0, y:btnY, w:alt.x - 8 - x0, h:btnH };

  var listTop = tabY + tabH + Math.round(cssH * 0.022);
  var listBot = btnY - Math.round(cssH * 0.020);
  /* A tall phone has more room than four cards need. Capping the card and
     then spreading what is left into the gaps keeps the list evenly paced -
     centring the block on its own just banked all the slack into one lump
     between the tabs and the first card, which read as a missing row. */
  var avail = listBot - listTop;
  var gap = Math.min(14, avail * 0.03);
  var cardH = Math.min((avail - 3*gap) / 4, 124);
  gap = Math.max(0, Math.min(28, (avail - 4*cardH) / 3));
  listTop += Math.max(0, (avail - (4*cardH + 3*gap)) / 2);

  /* The glyph gutter gives way before the text does, and on the narrowest
     screens the price drops the word FLUX - the number is already in the
     Flux colour under a header that says FLUX BANKED. Without that,
     "AMPLIFIER II" and "2200 FLUX" collide on a 280-wide phone. */
  var gutter = fit(cssW * 0.20, 56, 78);
  var textW = w - gutter - 16;

  return {
    m:m, x0:x0, w:w,
    titleSize:titleSize, titleY:titleY, subY:subY,
    subSize: fit(cssW * 0.029, 10, 13),
    tab:{ y:tabY, h:tabH, w:tabW, step:tabW + 6 },
    tabSize: fit(cssW * 0.032, 11, 15),
    listTop:listTop, slot:cardH + gap, cardH:cardH,
    gutter:gutter, textW:textW,
    compact: textW < 200,
    nameSize:  fit(cssW * 0.042, 14, 20),
    tagSize:   fit(cssW * 0.030, 11, 14),
    priceSize: fit(cssW * 0.031, 11, 14),
    launch:launch, alt:alt, mute:mute
  };
}""",
"""/* Both meta screens share a portrait frame: a centred column, a header, a
   list, and the same three controls along the bottom. Only what sits between
   the header and the buttons differs, so only that lives in each screen's own
   layout - two copies of this clamping would have drifted apart by the second
   change to either. `topExtra` is the space a screen needs under its subtitle
   (the shop puts its tab bar there; the core menu puts nothing). */
function portraitFrame(topExtra, rows, maxCardH){
  var m = fit(cssW * 0.045, 12, 48);
  // Past ~560 the column stops widening and centres instead - a full-width
  // card on a tablet is a very long line for four words of tag text.
  var w = Math.min(cssW - m*2, 560);
  var x0 = Math.round((cssW - w) / 2);

  var titleSize = fit(cssW * 0.068, 20, 34);
  var headTop = m + Math.round(cssH * 0.012);
  var titleY = headTop + titleSize*0.6;
  var subY = titleY + titleSize*0.78;

  /* The bottom row carries the same three controls the landscape screen ends
     on, so leaving portrait does not change what the buttons are. */
  var btnH = fit(cssH * 0.060, 46, 64);
  var btnY = cssH - m - btnH;
  var muteW = btnH;
  var altW = Math.min(96, Math.round(w * 0.28));
  var mute = { x:x0 + w - muteW, y:btnY, w:muteW, h:btnH };
  var alt  = { x:mute.x - 8 - altW, y:btnY, w:altW, h:btnH };
  var launch = { x:x0, y:btnY, w:alt.x - 8 - x0, h:btnH };

  var listTop = subY + topExtra;
  var listBot = btnY - Math.round(cssH * 0.020);
  /* A tall phone has more room than the list needs. Capping the card and then
     spreading what is left into the gaps keeps it evenly paced - centring the
     block on its own banked all the slack into one lump under the header,
     which read as a missing row. */
  var avail = listBot - listTop;
  var gap = Math.min(14, avail * (0.12 / rows));
  var cardH = Math.min((avail - (rows-1)*gap) / rows, maxCardH);
  gap = Math.max(0, Math.min(28, (avail - rows*cardH) / (rows-1)));
  listTop += Math.max(0, (avail - (rows*cardH + (rows-1)*gap)) / 2);

  /* The glyph gutter gives way before the text does, and on the narrowest
     screens a price drops the word FLUX - the number is already in the Flux
     colour under a header that says FLUX BANKED. Without that, "AMPLIFIER II"
     and "2200 FLUX" collide on a 280-wide phone. */
  var gutter = fit(cssW * 0.20, 56, 78);
  var textW = w - gutter - 16;

  return {
    m:m, x0:x0, w:w,
    titleSize:titleSize, titleY:titleY, subY:subY,
    subSize: fit(cssW * 0.029, 10, 13),
    listTop:listTop, slot:cardH + gap, cardH:cardH,
    gutter:gutter, textW:textW,
    compact: textW < 200,
    glyphR:    fit(cssW * 0.042, 13, 20),
    nameSize:  fit(cssW * 0.042, 14, 20),
    tagSize:   fit(cssW * 0.030, 11, 14),
    priceSize: fit(cssW * 0.031, 11, 14),
    launch:launch, alt:alt, mute:mute
  };
}

/* Counts the lines wrapText would produce, without drawing any of them. Kept
   next to it so the two cannot disagree about where a break falls. */
function wrapCount(str, size, maxW){
  ctx.font = '600 '+size+'px system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif';
  var words = str.split(' '), line = '', n = 1;
  for(var i=0;i<words.length;i++){
    var test = line ? line+' '+words[i] : words[i];
    if(ctx.measureText(test).width > maxW && line){ n++; line = words[i]; }
    else line = test;
  }
  return n;
}

function shopPortraitLayout(){
  var tabH = fit(cssH * 0.050, 44, 56);          // 44 is the touch minimum
  var pad = Math.round(cssH * 0.022);
  var L = portraitFrame(pad + tabH + pad, 4, 124);
  L.tab = { y:L.subY + pad, h:tabH, w:(L.w - 12) / 3, step:(L.w - 12) / 3 + 6 };
  L.tabSize = fit(cssW * 0.032, 11, 15);
  return L;
}"""),

# ---- cores: layout, drawing, hit testing ----
("""/* --------------------------- shop, portrait ----------------------------""",
 """/* -------------------------- cores, portrait ----------------------------
   Same reasoning as the shop below, one problem harder: a core carries three
   stat lines as well as a name, and there are six of them rather than four.
   On a 568-tall phone that leaves about 65px a card, which is one line of
   stats, not three - so the card asks how many lines it can afford and shows
   the longest prefix of the stats that actually fits. The tag is the one
   thing dropped in portrait: it is flavour, and the stats are the trade. */
function coresPortraitLayout(){
  return portraitFrame(Math.round(cssH * 0.028), CORES.length, 104);
}
function coresPortraitCard(i){
  var L = coresPortraitLayout();
  return { x:L.x0, y:L.listTop + i*L.slot, w:L.w, h:L.cardH };
}
function corePortraitLabel(c, own, eq){
  if(eq) return 'EQUIPPED';
  if(own) return 'SELECT';
  return c.cost + ' FLUX';
}
/* The longest run of stats that fits the lines this card can spare. Falls
   back to the first line alone, which is always the lives/slots trade. */
function coreStatLine(c, L, maxLines){
  for(var n=c.stats.length; n>=1; n--){
    var s = c.stats.slice(0, n).join('  \\u00b7  ');
    if(wrapCount(s, L.tagSize, L.textW) <= maxLines) return s;
  }
  return c.stats[0];
}

function tryBuyCore(c){
  if(buyCore(c.id)){
    equipCore(c.id);
    A.sLevel();
    G.boughtT = G.uiT;
    return;
  }
  A.tone(150,0.20,'square',0.09,100);
  G.menuMsg = 'NOT ENOUGH FLUX';
  G.menuMsgT = 1.8;
}

function drawCoresPortrait(){
  var L = coresPortraitLayout();
  ctx.fillStyle = '#03050e';
  ctx.fillRect(0, 0, cssW, cssH);

  var flux = getFlux();
  text('CORES', L.x0, L.titleY, L.titleSize, C.text, 'left', 900, 1, 4);
  text(String(flux), L.x0 + L.w, L.titleY, L.titleSize, C.scrap, 'right', 900, 1, 1);
  text('FLUX BANKED', L.x0 + L.w, L.subY, L.subSize, C.dim, 'right', 700, 0.7, 2);

  // Where progress is kept matters as much here as it does in landscape.
  var synced = !!(window.CG && window.CG.cloud);
  var msg = synced ? 'SYNCED TO YOUR ACCOUNT' : 'SAVED ON THIS DEVICE';
  var scol = synced ? '#6effc0' : C.dim;
  ctx.globalAlpha = 0.8;
  ctx.fillStyle = scol;
  ctx.beginPath(); ctx.arc(L.x0 + 3, L.subY, 3, 0, TAU); ctx.fill();
  ctx.globalAlpha = 1;
  text(msg, L.x0 + 13, L.subY, L.subSize, scol, 'left', 700, 0.7, 1.5);

  var sel = selectedCore();
  for(var i=0;i<CORES.length;i++){
    var c = CORES[i], r = coresPortraitCard(i);
    var own = owns(c.id), eq = (c.id === sel), afford = flux >= c.cost;
    var live = own || afford;
    var ca = live ? 1 : 0.5;

    ctx.fillStyle = eq ? hexA(c.col, 0.11) : 'rgba(255,255,255,0.04)';
    roundRect(r.x, r.y, r.w, r.h, 14); ctx.fill();
    ctx.strokeStyle = eq ? c.col : 'rgba(234,242,255,0.14)';
    ctx.lineWidth = eq ? 2.5 : 1.5;
    roundRect(r.x, r.y, r.w, r.h, 14); ctx.stroke();

    coreGlyph(c, r.x + L.gutter/2, r.y + r.h/2, L.glyphR, ca);

    var tx = r.x + L.gutter, ty = r.y + r.h*0.30;
    text(c.name, tx, ty, L.nameSize, own?C.text:'rgba(234,242,255,0.8)', 'left', 900, ca, 0.8);

    var label = corePortraitLabel(c, own, eq);
    var lcol = eq ? c.col : (own ? C.dim : (afford ? C.scrap : 'rgba(234,242,255,0.32)'));
    text(label, r.x + r.w - 16, ty, L.priceSize, lcol, 'right', eq?900:800, 1, 1.2);

    var statTop = r.y + r.h*0.54;
    var lines = Math.max(1, Math.floor((r.y + r.h - 6 - statTop) / (L.tagSize*1.3)));
    wrapText(coreStatLine(c, L, lines), tx, statTop, L.tagSize, C.dim,
             L.textW, L.tagSize*1.3, 'left', ca*0.8);
  }

  if(G.menuMsgT > 0){
    text(G.menuMsg, cssW/2, L.launch.y - 14, L.tagSize, '#ff5f7a', 'center', 800,
         clamp(G.menuMsgT*2, 0, 1), 2);
  }

  var LB = L.launch, pulse = 0.6 + 0.4*Math.sin(G.uiT*4);
  ctx.fillStyle = hexA(C.player, 0.13);
  roundRect(LB.x, LB.y, LB.w, LB.h, 12); ctx.fill();
  ctx.strokeStyle = hexA(C.player, pulse); ctx.lineWidth = 2;
  roundRect(LB.x, LB.y, LB.w, LB.h, 12); ctx.stroke();
  text('LAUNCH', LB.x + LB.w/2, LB.y + LB.h/2, Math.max(15, L.nameSize), C.text, 'center', 900, 1, 3);

  var AB = L.alt;
  ctx.fillStyle = 'rgba(255,255,255,0.05)';
  roundRect(AB.x, AB.y, AB.w, AB.h, 12); ctx.fill();
  ctx.strokeStyle = 'rgba(234,242,255,0.26)'; ctx.lineWidth = 2;
  roundRect(AB.x, AB.y, AB.w, AB.h, 12); ctx.stroke();
  text('SHOP', AB.x + AB.w/2, AB.y + AB.h/2, fit(cssW*0.032, 11, 15), C.text, 'center', 800, 1, 1.5);

  drawBtn(L.mute, (A.muted||A.forced) ? 'muted' : 'sound');
}

function handleCoresPortrait(){
  var x = IN.clickCssX, y = IN.clickCssY;
  var L = coresPortraitLayout();
  function hit(r){ return x >= r.x && x <= r.x+r.w && y >= r.y && y <= r.y+r.h; }

  IN.swallow = true;            // this screen owns the whole viewport
  if(hit(L.mute)){ A.setMute(!A.muted); A.sUi(); return; }
  if(hit(L.launch)){ restart(); return; }
  if(hit(L.alt)){ openShop(); return; }

  for(var i=0;i<CORES.length;i++){
    if(!hit(coresPortraitCard(i))) continue;
    var c = CORES[i];
    if(owns(c.id)){
      if(c.id !== selectedCore()){ equipCore(c.id); A.sUi(); }
    } else {
      tryBuyCore(c);
    }
    return;
  }
}

/* --------------------------- shop, portrait ----------------------------"""),

# ---- landscape cores steps aside ----
("""function drawCores(){
  G.coreT = (G.coreT||0) + 0.016;""",
 """function drawCores(){
  if(portraitUI()) return;      // drawn in CSS space after the HUD pass instead
  G.coreT = (G.coreT||0) + 0.016;"""),

# ---- neither meta screen needs the rotate prompt now ----
("""  /* The prompt exists because the ARENA needs landscape. The shop now lays
     itself out for portrait, so asking someone to rotate in order to read a
     menu that already fits would just be in the way. */
  if(G.mode === 'shop') return false;""",
 """  /* The prompt exists because the ARENA needs landscape. Both meta screens
     now lay themselves out for portrait, so asking someone to rotate in order
     to read a menu that already fits would just be in the way. */
  if(G.mode === 'shop' || G.mode === 'cores') return false;"""),

# ---- draw it ----
("""  if(G.mode === 'shop' && portraitUI()){
    ctx.setTransform(dpr,0,0,dpr,0,0);
    drawShopPortrait();
  }""",
 """  if(portraitUI() && (G.mode === 'shop' || G.mode === 'cores')){
    ctx.setTransform(dpr,0,0,dpr,0,0);
    if(G.mode === 'shop') drawShopPortrait(); else drawCoresPortrait();
  }"""),

# ---- route taps ----
("""  if(G.mode === 'shop' && portraitUI()){ handleShopPortrait(); return; }""",
 """  if(portraitUI() && G.mode === 'shop'){ handleShopPortrait(); return; }
  if(portraitUI() && G.mode === 'cores'){ handleCoresPortrait(); return; }"""),

# ---- no band for a banner on either ----
("""  /* The portrait shop uses the full viewport, so there is no band left to put
     a banner in. Overlaying one on the layout would put an ad against a live
     button, which the ad requirements specifically forbid. */
  if(G.mode === 'shop' && portraitUI()) want = false;""",
 """  /* The portrait meta screens use the full viewport, so there is no band left
     to put a banner in. Overlaying one on the layout would put an ad against a
     live button, which the ad requirements specifically forbid. */
  if(portraitUI() && (G.mode === 'shop' || G.mode === 'cores')) want = false;""")])

print('portrait cores wired; portrait frame shared with the shop')
