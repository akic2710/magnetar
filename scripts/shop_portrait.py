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
patch('src/p2.txt', [(
"""    shopT:0, shopMsg:'', shopMsgT:0""",
"""    shopT:0, shopMsg:'', shopMsgT:0, shopTab:0""")])


# ------------------------------------------------------------------ p5
patch('src/p5.txt', [

# ---- the landscape shop steps aside in portrait ----
("""function drawShop(){
  G.shopT = (G.shopT||0) + 0.016;""",
 """function drawShop(){
  if(portraitUI()) return;      // drawn in CSS space after the HUD pass instead
  G.shopT = (G.shopT||0) + 0.016;"""),

# ---- the portrait layout itself ----
("""/* ---------------------------- rotate prompt ---------------------------- */""",
 """/* --------------------------- shop, portrait ----------------------------
   The game lives in a fixed 1280x720 field that letterboxes into a 375x211
   strip on a phone. That is fine for an arena you look at and useless for a
   menu you read: item names landed at 4.7px and the LAUNCH button at 15px
   tall. So in portrait the shop leaves that coordinate space altogether and
   lays itself out in CSS pixels across the whole screen, the way the rotate
   prompt already does.

   Ten cards cannot be legible on a 568-tall phone, so the catalogue splits
   into the three groups it already had and shows one at a time. Four cards
   maximum per screen is what buys every card enough room to read and to hit,
   and it means no scrolling - which on a canvas would have to fight the tap
   handler for the same gesture. */
function portraitUI(){ return cssH > cssW * 1.05; }

var SHOP_TABS = [
  { key:'trail', label:'WAKES',  hint:'Looks only. No effect on the run.' },
  { key:'arena', label:'ARENAS', hint:'Looks only. No effect on the run.' },
  { key:'boost', label:'BOOSTS', hint:'Pays more Flux. Never an easier run.' }
];
function shopTabItems(t){
  var kind = SHOP_TABS[t].key, out = [];
  for(var i=0;i<SHOP.length;i++) if(SHOP[i].kind === kind) out.push(SHOP[i]);
  return out;
}

function shopPortraitLayout(){
  var m = Math.max(12, Math.round(cssW * 0.045));
  var w = cssW - m*2;

  var titleSize = Math.max(20, Math.round(cssW * 0.068));
  var headTop = m + Math.round(cssH * 0.012);
  var titleY = headTop + titleSize*0.6;
  var subY = titleY + titleSize*0.78;

  var tabH = Math.max(38, Math.round(cssH * 0.050));
  var tabY = subY + Math.round(cssH * 0.022);
  var tabW = (w - 12) / 3;

  /* The bottom row carries the same three controls the landscape screen ends
     on, so leaving portrait does not change what the buttons are. */
  var btnH = Math.max(46, Math.round(cssH * 0.060));
  var btnY = cssH - m - btnH;
  var muteW = btnH;
  var altW = Math.min(96, Math.round(w * 0.28));
  var mute = { x:m + w - muteW, y:btnY, w:muteW, h:btnH };
  var alt  = { x:mute.x - 8 - altW, y:btnY, w:altW, h:btnH };
  var launch = { x:m, y:btnY, w:alt.x - 8 - m, h:btnH };

  var listTop = tabY + tabH + Math.round(cssH * 0.022);
  var listBot = btnY - Math.round(cssH * 0.020);
  var slot = (listBot - listTop) / 4;
  var gap = Math.min(12, slot * 0.13);
  var cardH = Math.min(slot - gap, 124);
  // A tall phone would otherwise stretch four cards down the whole screen.
  var used = 4*cardH + 3*gap;
  listTop += Math.max(0, (listBot - listTop - used) / 2);

  return {
    m:m, w:w,
    titleSize:titleSize, titleY:titleY, subY:subY,
    subSize: Math.max(10, Math.round(cssW * 0.029)),
    tab:{ y:tabY, h:tabH, w:tabW, step:tabW + 6 },
    tabSize: Math.max(11, Math.round(cssW * 0.032)),
    listTop:listTop, slot:cardH + gap, cardH:cardH,
    nameSize:  Math.max(14, Math.round(cssW * 0.042)),
    tagSize:   Math.max(11, Math.round(cssW * 0.030)),
    priceSize: Math.max(11, Math.round(cssW * 0.031)),
    launch:launch, alt:alt, mute:mute
  };
}
function shopPortraitCard(i){
  var L = shopPortraitLayout();
  return { x:L.m, y:L.listTop + i*L.slot, w:L.w, h:L.cardH };
}
function shopPortraitTab(i){
  var L = shopPortraitLayout();
  return { x:L.m + i*L.tab.step, y:L.tab.y, w:L.tab.w, h:L.tab.h };
}

function drawShopPortrait(){
  var L = shopPortraitLayout();
  ctx.fillStyle = '#03050e';
  ctx.fillRect(0, 0, cssW, cssH);

  var flux = getFlux();
  text('SHOP', L.m, L.titleY, L.titleSize, C.text, 'left', 900, 1, 4);
  text(String(flux), cssW - L.m, L.titleY, L.titleSize, C.scrap, 'right', 900, 1, 1);
  text(SHOP_TABS[G.shopTab||0].hint, L.m, L.subY, L.subSize, C.dim, 'left', 600, 0.75, 0.3);
  text('FLUX BANKED', cssW - L.m, L.subY, L.subSize, C.dim, 'right', 700, 0.7, 2);

  var t, tr;
  for(t=0;t<SHOP_TABS.length;t++){
    tr = shopPortraitTab(t);
    var on = ((G.shopTab||0) === t);
    ctx.fillStyle = on ? hexA(C.player, 0.16) : 'rgba(255,255,255,0.04)';
    roundRect(tr.x, tr.y, tr.w, tr.h, 10); ctx.fill();
    ctx.strokeStyle = on ? C.player : 'rgba(234,242,255,0.16)';
    ctx.lineWidth = on ? 2 : 1.5;
    roundRect(tr.x, tr.y, tr.w, tr.h, 10); ctx.stroke();
    text(SHOP_TABS[t].label, tr.x + tr.w/2, tr.y + tr.h/2, L.tabSize,
         on ? C.text : C.dim, 'center', 800, 1, 1.5);
  }

  var items = shopTabItems(G.shopTab||0);
  var trail = equippedTrail(), arena = equippedArena();
  for(var i=0;i<items.length;i++){
    var it = items[i], r = shopPortraitCard(i);
    var own = ownsItem(it.id);
    var eq = (it.id === trail || it.id === arena);
    var lock = itemLocked(it);
    var afford = flux >= it.cost;
    var live = own || (afford && !lock);
    var ca = live ? 1 : 0.5;

    ctx.fillStyle = eq ? hexA(C.player,0.11) : 'rgba(255,255,255,0.04)';
    roundRect(r.x, r.y, r.w, r.h, 14); ctx.fill();
    ctx.strokeStyle = eq ? C.player : 'rgba(234,242,255,0.14)';
    ctx.lineWidth = eq ? 2.5 : 1.5;
    roundRect(r.x, r.y, r.w, r.h, 14); ctx.stroke();

    shopGlyph(it, r.x + 40, r.y + r.h/2, ca);

    var tx = r.x + 78, ty = r.y + r.h*0.36;
    text(it.name, tx, ty, L.nameSize, own?C.text:'rgba(234,242,255,0.8)', 'left', 900, ca, 1);
    wrapText(it.tag, tx, r.y + r.h*0.62, L.tagSize, C.dim,
             r.w - 78 - 16, L.tagSize*1.35, 'left', ca*0.8);

    var px = r.x + r.w - 16;
    if(it.kind === 'boost'){
      if(own)       text('ACTIVE', px, ty, L.priceSize, C.scrap, 'right', 900, 1, 1.5);
      else if(lock) text('LOCKED', px, ty, L.priceSize, 'rgba(234,242,255,0.32)', 'right', 800, 1, 1.5);
      else          text(PURCHASE.priceLabel(it), px, ty, L.priceSize, afford?C.scrap:'rgba(234,242,255,0.32)', 'right', 800, 1, 1.5);
    }
    else if(eq)  text('EQUIPPED', px, ty, L.priceSize, C.player, 'right', 900, 1, 1.5);
    else if(own) text('EQUIP', px, ty, L.priceSize, C.dim, 'right', 800, 1, 1.5);
    else         text(PURCHASE.priceLabel(it), px, ty, L.priceSize, afford?C.scrap:'rgba(234,242,255,0.32)', 'right', 800, 1, 1.5);
  }

  if(G.shopMsgT > 0){
    text(G.shopMsg, cssW/2, L.launch.y - 14, L.tagSize, '#ff5f7a', 'center', 800,
         clamp(G.shopMsgT*2, 0, 1), 2);
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
  text('CORES', AB.x + AB.w/2, AB.y + AB.h/2, L.tabSize, C.text, 'center', 800, 1, 1.5);

  drawBtn(L.mute, (A.muted||A.forced) ? 'muted' : 'sound');
}

/* Taps land in CSS pixels here, because that is the space this was drawn in -
   the same split the rotate prompt already makes. */
function handleShopPortrait(){
  var x = IN.clickCssX, y = IN.clickCssY;
  var L = shopPortraitLayout();
  function hit(r){ return x >= r.x && x <= r.x+r.w && y >= r.y && y <= r.y+r.h; }

  IN.swallow = true;            // this screen owns the whole viewport
  if(hit(L.mute)){ A.setMute(!A.muted); A.sUi(); return; }
  if(hit(L.launch)){ restart(); return; }
  if(hit(L.alt)){ openCores(); return; }

  var t;
  for(t=0;t<SHOP_TABS.length;t++){
    if(hit(shopPortraitTab(t))){
      if((G.shopTab||0) !== t){ G.shopTab = t; A.sUi(); }
      return;
    }
  }
  var items = shopTabItems(G.shopTab||0);
  for(var i=0;i<items.length;i++){
    if(!hit(shopPortraitCard(i))) continue;
    var it = items[i];
    if(!ownsItem(it.id)) tryBuy(it);
    else if(it.kind !== 'boost' && it.id !== equippedTrail() && it.id !== equippedArena()){
      equipItem(it.id); A.sUi();
    }
    return;
  }
}

/* ---------------------------- rotate prompt ---------------------------- */"""),

# ---- the prompt is about gameplay, and the shop no longer needs it ----
("""function needsRotate(){
  if(!TOUCH_CAPABLE || rotateDismissed || G.adBusy) return false;
  return cssH > cssW * 1.05;          // margin stops it flapping near square
}""",
 """function needsRotate(){
  if(!TOUCH_CAPABLE || rotateDismissed || G.adBusy) return false;
  /* The prompt exists because the ARENA needs landscape. The shop now lays
     itself out for portrait, so asking someone to rotate in order to read a
     menu that already fits would just be in the way. */
  if(G.mode === 'shop') return false;
  return cssH > cssW * 1.05;          // margin stops it flapping near square
}"""),

# ---- draw it in CSS space, before the rotate prompt ----
("""  /* Drawn last and in CSS pixels rather than virtual ones, so it covers the
     letterbox bars too - in portrait the playfield is only a third of the
     screen, and a prompt confined to it would be the size of the problem. */
  if(needsRotate()){""",
 """  /* Both of these are drawn in CSS pixels rather than virtual ones, so they
     cover the letterbox bars too - in portrait the playfield is only a third
     of the screen, and anything confined to it would be the size of the
     problem it is trying to solve. */
  if(G.mode === 'shop' && portraitUI()){
    ctx.setTransform(dpr,0,0,dpr,0,0);
    drawShopPortrait();
  }
  if(needsRotate()){"""),

# ---- route taps before any virtual-space hit test can claim them ----
("""  if(inRect(x,y,BTN_MUTE)){ A.setMute(!A.muted); A.sUi(); IN.swallow=true; return; }
  if(inRect(x,y,BTN_PAUSE)){ togglePause(); IN.swallow=true; return; }""",
 """  if(G.mode === 'shop' && portraitUI()){ handleShopPortrait(); return; }

  if(inRect(x,y,BTN_MUTE)){ A.setMute(!A.muted); A.sUi(); IN.swallow=true; return; }
  if(inRect(x,y,BTN_PAUSE)){ togglePause(); IN.swallow=true; return; }"""),

# ---- no banner band exists once the shop owns the whole screen ----
("""  var want = (G.mode === 'over' || G.mode === 'cores' || G.mode === 'shop') && !G.adBusy;""",
 """  var want = (G.mode === 'over' || G.mode === 'cores' || G.mode === 'shop') && !G.adBusy;
  /* The portrait shop uses the full viewport, so there is no band left to put
     a banner in. Overlaying one on the layout would put an ad against a live
     button, which the ad requirements specifically forbid. */
  if(G.mode === 'shop' && portraitUI()) want = false;""")])

print('portrait shop wired: tabbed CSS-space layout, own hit testing')
