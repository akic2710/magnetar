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

# ------------------------------------------------ layout, rebuilt
("""function shopPortraitLayout(){
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
}""",
"""/* Sizes scale with the viewport but are clamped at both ends: a floor so a
   280-wide phone stays legible and hittable, a ceiling so a 1024-wide tablet
   does not end up with 43px item names on metre-wide cards. */
function fit(v, lo, hi){ return Math.max(lo, Math.min(hi, Math.round(v))); }

function shopPortraitLayout(){
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
  var slot = (listBot - listTop) / 4;
  var gap = Math.min(12, slot * 0.13);
  var cardH = Math.min(slot - gap, 124);
  // A tall phone would otherwise stretch four cards down the whole screen.
  var used = 4*cardH + 3*gap;
  listTop += Math.max(0, (listBot - listTop - used) / 2);

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
}
/* One place decides what the right-hand label says, so the drawing and the
   width test can never disagree about it. */
function shopPortraitLabel(it, L, own, eq, lock){
  if(it.kind === 'boost'){
    if(own) return 'ACTIVE';
    if(lock) return 'LOCKED';
  } else {
    if(eq) return 'EQUIPPED';
    if(own) return 'EQUIP';
  }
  return L.compact ? String(it.cost) : (it.cost + ' FLUX');
}"""),

# ------------------------------------------------ rects follow the centred column
("""function shopPortraitCard(i){
  var L = shopPortraitLayout();
  return { x:L.m, y:L.listTop + i*L.slot, w:L.w, h:L.cardH };
}
function shopPortraitTab(i){
  var L = shopPortraitLayout();
  return { x:L.m + i*L.tab.step, y:L.tab.y, w:L.tab.w, h:L.tab.h };
}""",
"""function shopPortraitCard(i){
  var L = shopPortraitLayout();
  return { x:L.x0, y:L.listTop + i*L.slot, w:L.w, h:L.cardH };
}
function shopPortraitTab(i){
  var L = shopPortraitLayout();
  return { x:L.x0 + i*L.tab.step, y:L.tab.y, w:L.tab.w, h:L.tab.h };
}"""),

# ------------------------------------------------ header uses the centred column
("""  var flux = getFlux();
  text('SHOP', L.m, L.titleY, L.titleSize, C.text, 'left', 900, 1, 4);
  text(String(flux), cssW - L.m, L.titleY, L.titleSize, C.scrap, 'right', 900, 1, 1);
  text(SHOP_TABS[G.shopTab||0].hint, L.m, L.subY, L.subSize, C.dim, 'left', 600, 0.75, 0.3);
  text('FLUX BANKED', cssW - L.m, L.subY, L.subSize, C.dim, 'right', 700, 0.7, 2);""",
"""  var flux = getFlux();
  text('SHOP', L.x0, L.titleY, L.titleSize, C.text, 'left', 900, 1, 4);
  text(String(flux), L.x0 + L.w, L.titleY, L.titleSize, C.scrap, 'right', 900, 1, 1);
  text(SHOP_TABS[G.shopTab||0].hint, L.x0, L.subY, L.subSize, C.dim, 'left', 600, 0.75, 0.3);
  text('FLUX BANKED', L.x0 + L.w, L.subY, L.subSize, C.dim, 'right', 700, 0.7, 2);"""),

# ------------------------------------------------ card body: shared label, tighter tracking
("""    shopGlyph(it, r.x + 40, r.y + r.h/2, ca);

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
    else         text(PURCHASE.priceLabel(it), px, ty, L.priceSize, afford?C.scrap:'rgba(234,242,255,0.32)', 'right', 800, 1, 1.5);""",
"""    shopGlyph(it, r.x + L.gutter/2, r.y + r.h/2, ca);

    var tx = r.x + L.gutter, ty = r.y + r.h*0.36;
    text(it.name, tx, ty, L.nameSize, own?C.text:'rgba(234,242,255,0.8)', 'left', 900, ca, 0.8);
    wrapText(it.tag, tx, r.y + r.h*0.62, L.tagSize, C.dim,
             L.textW, L.tagSize*1.35, 'left', ca*0.8);

    var label = shopPortraitLabel(it, L, own, eq, lock);
    var lcol = (label === 'ACTIVE') ? C.scrap
             : (label === 'EQUIPPED') ? C.player
             : (label === 'EQUIP') ? C.dim
             : (label === 'LOCKED') ? 'rgba(234,242,255,0.32)'
             : (afford ? C.scrap : 'rgba(234,242,255,0.32)');
    var lw = (label === 'ACTIVE' || label === 'EQUIPPED') ? 900 : 800;
    text(label, r.x + r.w - 16, ty, L.priceSize, lcol, 'right', lw, 1, 1.2);""")])

print('portrait shop: 44px tabs, clamped type, centred column, collision-free labels')
