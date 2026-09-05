import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


# ------------------------------------------------------------------ p1
# The banner is real DOM, not canvas, so it needs its own element. The SDK
# fills #mgn-banner at exactly the requested size; the wrapper handles
# placement and carries the label that keeps it distinguishable from the game.
patch('src/p1.txt', [(
"""  #stage{position:fixed;inset:0;width:100%;height:100%;display:block;background:#04050c;cursor:crosshair;}
  #stage.reticle{cursor:none;}
</style>
<canvas id="stage"></canvas>""",
"""  #stage{position:fixed;inset:0;width:100%;height:100%;display:block;background:#04050c;cursor:crosshair;}
  #stage.reticle{cursor:none;}

  /* Banner ad, shown only on the death screen. Kept clear of the game's
     buttons so a mis-tap can never land on an ad. */
  #mgn-banner-wrap{
    position:fixed; display:none; z-index:5;
    flex-direction:column; align-items:center; gap:4px;
    touch-action:auto;
  }
  #mgn-banner-wrap.on{ display:flex; }
  #mgn-banner-label{
    font:700 9px/1 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
    letter-spacing:.18em; color:rgba(234,242,255,.38); user-select:none;
  }
  #mgn-banner{ overflow:hidden; background:transparent; }
</style>
<canvas id="stage"></canvas>
<div id="mgn-banner-wrap" aria-hidden="true">
  <div id="mgn-banner-label">ADVERTISEMENT</div>
  <div id="mgn-banner"></div>
</div>""")])


# ------------------------------------------------------------------ p5
patch('src/p5.txt', [

# ---- CG flag ---------------------------------------------------------------
("""  ready:false, cloud:false, adsOk:false, sdk:null,""",
 """  ready:false, cloud:false, adsOk:false, bannersOk:false, sdk:null,"""),

("""      this.adsOk = !!(SDK.ad && SDK.ad.requestAd);""",
 """      this.adsOk = !!(SDK.ad && SDK.ad.requestAd);
      this.bannersOk = !!(SDK.banner && SDK.banner.requestBanner);"""),

# ---- banner controller -----------------------------------------------------
("""/* -------------------------------- ads ---------------------------------- */
function reviveBtns(){""",
 """/* ------------------------------- banner -------------------------------- */
/* Death screen only. The ad requirements forbid banners during gameplay and
   ask that they sit clear of the game's own buttons, so this lives in the
   empty band below the game-over panel and never appears anywhere else.
   Space is reserved as soon as we know a banner *could* fill, so a failed
   fill does not make the panel jump. */
var BANNER = {
  ID:'mgn-banner',
  wrap:null, el:null,
  shown:false, reserved:false, requesting:false,
  w:0, h:0, lastReq:-1e9, fails:0,

  init:function(){
    this.wrap = document.getElementById('mgn-banner-wrap');
    this.el = document.getElementById(this.ID);
  },

  /* Largest supported size that fits under the panel, or null. */
  pick:function(){
    var labelH = 14, pad = 10;
    var top = offY + 570*scale;
    var avail = cssH - top - pad;
    if(cssW >= 768 && avail >= 90 + labelH) return [728,90];
    if(cssW >= 500 && avail >= 60 + labelH) return [468,60];
    if(cssW >= 340 && avail >= 50 + labelH) return [320,50];
    return null;
  },

  available:function(){
    return !!(window.CG && window.CG.ready && window.CG.bannersOk &&
              window.CG.adsOk && this.fails < 3 && this.pick());
  },

  place:function(size){
    if(!this.wrap) return;
    var labelH = 14;
    var top = offY + 570*scale;
    var room = cssH - top;
    this.el.style.width = size[0]+'px';
    this.el.style.height = size[1]+'px';
    this.wrap.style.left = Math.round((cssW - size[0])/2)+'px';
    this.wrap.style.top = Math.round(top + Math.max(0,(room - size[1] - labelH)/2))+'px';
  },

  show:function(){
    if(!this.wrap) return;
    var size = this.pick();
    if(!size || !this.available()){ this.hide(); return; }
    this.reserved = true;
    this.place(size);
    this.wrap.className = 'on';
    this.shown = true;

    var now = performance.now(), self = this;
    var sameSize = (this.w === size[0] && this.h === size[1]);
    // The SDK enforces a refresh floor; staying well clear of it avoids
    // burning requests on bannerCooldown errors.
    if(this.requesting || (sameSize && now - this.lastReq < 61000)) return;
    this.w = size[0]; this.h = size[1];
    this.lastReq = now;
    this.requesting = true;
    try{
      window.CG.sdk.banner.requestBanner({ id:this.ID, width:size[0], height:size[1] })
        .then(function(){ self.requesting = false; self.fails = 0; })
        .catch(function(e){ self.requesting = false; self.fail(e && e.code); });
    }catch(e){ this.requesting = false; this.fail('threw'); }
  },

  /* No fill: collapse the container rather than leave an empty rectangle.
     The reserved space stays, so the panel does not jump. */
  fail:function(code){
    if(code !== 'bannerCooldown') this.fails++;
    this.shown = false;
    if(this.wrap) this.wrap.className = '';
  },

  hide:function(){
    this.shown = false;
    this.reserved = false;
    if(this.wrap) this.wrap.className = '';
    try{
      if(window.CG.ready && window.CG.sdk.banner) window.CG.sdk.banner.clearBanner(this.ID);
    }catch(e){}
  }
};

function syncBanner(){
  // Never during gameplay, and never behind a video ad (the SDK rejects that
  // with videoAdPlaying anyway).
  var want = (G.mode === 'over') && !G.adBusy;
  if(want){
    if(!BANNER.reserved) BANNER.show();
    else if(BANNER.shown) BANNER.place([BANNER.w, BANNER.h]);   // follow resizes
  } else if(BANNER.reserved || BANNER.shown){
    BANNER.hide();
  }
}

/* -------------------------------- ads ---------------------------------- */
function reviveBtns(){"""),

# ---- panel moves up to make room -------------------------------------------
("""var OVER_Y = 112;
function overBtns(){
  return {
    play:  {x:VW/2-190, y:OVER_Y+356, w:248, h:52},
    cores: {x:VW/2+74,  y:OVER_Y+356, w:116, h:52}
  };
}""",
 """/* The panel sits higher when a banner has space reserved beneath it. */
function overY(){ return BANNER.reserved ? 76 : 112; }
function overBtns(){
  var y = overY() + 356;
  return {
    play:  {x:VW/2-190, y:y, w:248, h:52},
    cores: {x:VW/2+74,  y:y, w:116, h:52}
  };
}"""),

("""  var by = OVER_Y, bx = VW/2-260, bw = 520, bh = 452;""",
 """  var by = overY(), bx = VW/2-260, bw = 520, bh = 452;"""),

("""  text(IN.isTouch?'Tap anywhere to retry':'Click anywhere or press Enter to retry',
       VW/2, by+bh+24, 13, C.dim, 'center', 600, 0.65*a, 1);""",
 """  // With an ad on screen, "click anywhere" would turn the whole page into a
  // button sitting next to it - exactly the accidental-click case the ad
  // requirements warn about. The button becomes the only pointer target.
  var hint = BANNER.reserved
    ? (IN.isTouch ? 'Tap PLAY AGAIN to retry' : 'Press PLAY AGAIN or Enter to retry')
    : (IN.isTouch ? 'Tap anywhere to retry'   : 'Click anywhere or press Enter to retry');
  text(hint, VW/2, by+bh+22, 13, C.dim, 'center', 600, 0.65*a, 1);"""),

# ---- input: no click-anywhere while an ad is on screen ---------------------
("""  if(G.mode==='over'){
    var ob = overBtns();
    if(inRect(x,y,ob.cores)){ openCores(); IN.swallow=true; return; }
    if((G.overT||0) > 0.55){ restart(); IN.swallow=true; }
    return;
  }""",
 """  if(G.mode==='over'){
    var ob = overBtns();
    if(inRect(x,y,ob.cores)){ openCores(); IN.swallow=true; return; }
    if(inRect(x,y,ob.play)){
      if((G.overT||0) > 0.35){ restart(); IN.swallow=true; }
      return;
    }
    if(!BANNER.reserved && (G.overT||0) > 0.55){ restart(); IN.swallow=true; }
    return;
  }"""),

# ---- drive it from the loop ------------------------------------------------
("""  handleUI();""",
 """  handleUI();
  syncBanner();"""),

# ---- boot ------------------------------------------------------------------
("""migrateSave();
reset();""",
 """BANNER.init();
migrateSave();
reset();"""),
])

print('banner ads wired')
