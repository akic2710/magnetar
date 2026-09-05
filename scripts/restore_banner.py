import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = 'src/p5.txt'
s = io.open(p, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')

assert 'var BANNER' not in s, 'BANNER already present - nothing to restore'
marker = '/* -------------------------------- ads ---------------------------------- */'
assert marker in s

block = '''/* ------------------------------- banner -------------------------------- */
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
    var top = offY + 582*scale;
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
    var top = offY + 582*scale;
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
    // The container is now empty, so the next death has to request again -
    // otherwise the size check would short-circuit and show a labelled but
    // blank box. If that request lands inside the SDK's refresh floor it
    // returns bannerCooldown and fail() simply collapses the container.
    this.w = 0; this.h = 0;
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

'''

s = s.replace(marker, block + marker, 1)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('BANNER + syncBanner restored (582 band, hide() size reset)')
