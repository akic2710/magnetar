import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

P5 = 'src/p5.txt'
s = io.open(P5, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')


def sub(old, new):
    global s
    assert old in s, 'not found -> %r' % (old[:80],)
    s = s.replace(old, new, 1)


def swap(start, end, new):
    global s
    a = s.index(start)
    b = s.index(end, a + len(start))
    s = s[:a] + new + s[b:]


# ---------------------------------------------------------------- layout
sub("""function coreCardRect(i){
  var col = i%3, row = Math.floor(i/3);
  return {x:66 + col*392, y:152 + row*251, w:364, h:225};
}
var BTN_LAUNCH = {x:VW/2-130, y:650, w:260, h:52};""",
"""/* The core menu is a full screen with no spare band, so a banner has to be
   made room for rather than dropped in. Everything tightens by about 17% and
   only while a banner is actually reserved - with no ad (no SDK, no fill, the
   Artifact build) the roomy layout is what you get. */
function coresLayout(){
  return BANNER.reserved
    ? { title:46, sub:78, sync:100,
        y0:120, h:186, step:202,
        glyphY:64, glyphR:22, nameY:38,
        tagY:62, tagSize:12, tagLh:16,
        divY:110, statY:134, statLh:18, statSize:12,
        launch:{x:VW/2-130, y:524, w:260, h:46} }
    : { title:62, sub:98, sync:124,
        y0:152, h:225, step:251,
        glyphY:76, glyphR:25, nameY:44,
        tagY:74, tagSize:12.5, tagLh:18,
        divY:134, statY:160, statLh:22, statSize:12.5,
        launch:{x:VW/2-130, y:650, w:260, h:52} };
}
function coreCardRect(i){
  var L = coresLayout(), col = i%3, row = Math.floor(i/3);
  return {x:66 + col*392, y:L.y0 + row*L.step, w:364, h:L.h};
}
function launchRect(){ return coresLayout().launch; }""")

s = s.replace('BTN_LAUNCH', 'launchRect()')
# the declaration itself must not be rewritten by that sweep
s = s.replace('function launchRect(){ return coresLayout().launch; }',
              'function launchRect(){ return coresLayout().launch; }')
assert 'var launchRect()' not in s

# ---------------------------------------------------------------- drawCores
swap('function drawCores(){', '\n/* ------------------------------- banner', '''function drawCores(){
  G.coreT = (G.coreT||0) + 0.016;
  var a = clamp(G.coreT*5,0,1);
  var L = coresLayout();
  ctx.fillStyle='rgba(3,5,14,0.94)';
  ctx.fillRect(0,0,VW,VH);
  ctx.globalAlpha = a;

  text('CORES', 66, L.title, 34, C.text, 'left', 900, 1, 7);
  text('Every run banks Flux. Spend it on a different way to open the next one.',
       66, L.sub, 13, C.dim, 'left', 600, 0.75, 0.5);

  var flux = getFlux();
  text(String(flux), VW-66, L.title-4, 34, C.scrap, 'right', 900, 1, 1);
  text('FLUX BANKED', VW-66, L.title+26, 10, C.dim, 'right', 700, 0.75, 4);

  // Progression is only worth chasing if the player believes it will still be
  // there tomorrow, so say plainly where it is being kept.
  var synced = !!(window.CG && window.CG.cloud);
  var msg = synced ? 'SYNCED TO YOUR CRAZYGAMES ACCOUNT' : 'SAVED ON THIS DEVICE';
  var col = synced ? '#6effc0' : C.dim;
  ctx.globalAlpha = a*0.8;
  ctx.fillStyle = col;
  ctx.beginPath(); ctx.arc(70, L.sync, 3.5, 0, TAU); ctx.fill();
  ctx.globalAlpha = 1;
  text(msg, 82, L.sync, 10, col, 'left', 700, a*0.65, 2.5);

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

    coreGlyph(c, r.x+64, r.y+L.glyphY, L.glyphR, ca);

    var tx = r.x+118;
    text(c.name, tx, r.y+L.nameY, 20, own?C.text:'rgba(234,242,255,0.8)', 'left', 900, ca, 1.5);
    wrapText(c.tag, tx, r.y+L.tagY, L.tagSize, C.dim, r.w-118-PAD, L.tagLh, 'left', ca*0.8);

    hr(r.x+PAD, r.x+r.w-PAD, r.y+L.divY, ca*0.09);

    for(var k=0;k<c.stats.length;k++){
      var sy = r.y+L.statY+k*L.statLh;
      ctx.globalAlpha = ca*0.9;
      ctx.fillStyle = c.col;
      ctx.beginPath(); ctx.arc(r.x+PAD+2, sy, 2.5, 0, TAU); ctx.fill();
      ctx.globalAlpha = 1;
      text(c.stats[k], r.x+PAD+14, sy, L.statSize, C.dim, 'left', 600, ca*0.85, 0.3);
    }

    // Share a baseline with the last stat line so the row reads as one.
    var bxr = r.x+r.w-PAD, byr = r.y+L.statY+(c.stats.length-1)*L.statLh;
    if(eq)        text('EQUIPPED', bxr, byr, 13, c.col, 'right', 900, a, 3);
    else if(own)  text('SELECT',   bxr, byr, 13, hov?C.text:C.dim, 'right', 800, a, 3);
    else          text(c.cost+' FLUX', bxr, byr, 13, afford?C.scrap:'rgba(234,242,255,0.32)', 'right', 800, a, 2.5);
  }

  var LB = L.launch;
  var hovL = IN.has && inRect(IN.x,IN.y,LB);
  var pulse = 0.6+0.4*Math.sin(G.uiT*4);
  ctx.fillStyle = hexA(C.player, hovL?0.24:0.13);
  roundRect(LB.x,LB.y,LB.w,LB.h,14); ctx.fill();
  ctx.strokeStyle = hexA(C.player, hovL?1:pulse); ctx.lineWidth=2;
  roundRect(LB.x,LB.y,LB.w,LB.h,14); ctx.stroke();
  text('LAUNCH', VW/2, LB.y+LB.h/2, 19, C.text, 'center', 900, 1, 4);

  drawBtn(BTN_MUTE, A.muted?'muted':'sound');
  ctx.globalAlpha = 1;
}

''')

# ---------------------------------------------------------------- banner band
sub("""  /* Largest supported size that fits under the panel, or null. */
  pick:function(){
    var labelH = 14, pad = 10;
    var top = offY + 582*scale;""",
"""  /* Each screen leaves the band in a different place. */
  bandTop:function(){ return (G.mode === 'cores') ? 600 : 582; },

  /* Largest supported size that fits under the panel, or null. */
  pick:function(){
    var labelH = 14, pad = 10;
    var top = offY + this.bandTop()*scale;""")

sub("""  place:function(size){
    if(!this.wrap) return;
    var labelH = 14;
    var top = offY + 582*scale;""",
"""  place:function(size){
    if(!this.wrap) return;
    var labelH = 14;
    var top = offY + this.bandTop()*scale;""")

sub("""  shown:false, reserved:false, requesting:false,""",
"""  shown:false, reserved:false, requesting:false, screen:'',""")

sub("""    this.reserved = true;
    this.place(size);""",
"""    this.reserved = true;
    this.screen = G.mode;
    this.place(size);""")

sub("""function syncBanner(){
  // Never during gameplay, and never behind a video ad (the SDK rejects that
  // with videoAdPlaying anyway).
  var want = (G.mode === 'over') && !G.adBusy;
  if(want){
    if(!BANNER.reserved) BANNER.show();
    else if(BANNER.shown) BANNER.place([BANNER.w, BANNER.h]);   // follow resizes
  } else if(BANNER.reserved || BANNER.shown){
    BANNER.hide();
  }
}""",
"""function syncBanner(){
  // Menus only - never during gameplay, and never behind a video ad (the SDK
  // rejects that with videoAdPlaying anyway). The core menu is a shop, which
  // the ad requirements list as an allowed placement.
  var want = (G.mode === 'over' || G.mode === 'cores') && !G.adBusy;
  if(want){
    // The two screens park the band at different heights, so moving between
    // them has to re-place rather than reuse the old slot.
    if(BANNER.reserved && BANNER.screen !== G.mode) BANNER.hide();
    if(!BANNER.reserved) BANNER.show();
    else if(BANNER.shown) BANNER.place([BANNER.w, BANNER.h]);   // follow resizes
  } else if(BANNER.reserved || BANNER.shown){
    BANNER.hide();
  }
}""")

io.open(P5, 'w', encoding='utf-8', newline='\n').write(s)
print('cores banner wired with compact reflow')
