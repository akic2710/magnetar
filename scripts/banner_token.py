import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
P5 = 'src/p5.txt'
s = io.open(P5, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')


def sub(old, new):
    global s
    assert old in s, 'not found -> %r' % (old[:80],)
    s = s.replace(old, new, 1)


sub("  shown:false, reserved:false, requesting:false, screen:'',",
    "  shown:false, reserved:false, requesting:false, filled:false, screen:'', token:0,")

sub("""  show:function(){
    if(!this.wrap) return;
    var size = this.pick();
    if(!size || !this.available()){ this.hide(); return; }
    this.reserved = true;
    this.screen = G.mode;
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
  },""",
"""  /* Reserve the space immediately, but only reveal the labelled container once
     an ad has actually been filled into it - otherwise the player sees an
     ADVERTISEMENT label over an empty box while the request is in flight. */
  show:function(){
    if(!this.wrap) return;
    var size = this.pick();
    if(!size || !this.available()){ this.hide(); return; }
    this.reserved = true;
    this.screen = G.mode;
    this.place(size);

    if(this.requesting) return;                     // one in flight; wait for it
    var now = performance.now(), self = this;
    var sameSize = (this.w === size[0] && this.h === size[1]);
    if(sameSize && this.filled){                    // already filled at this size
      this.wrap.className = 'on'; this.shown = true; return;
    }
    // The SDK enforces a refresh floor; staying well clear of it avoids
    // burning requests on bannerCooldown errors. Stay blank until it lifts.
    if(sameSize && now - this.lastReq < 61000) return;

    this.w = size[0]; this.h = size[1];
    this.filled = false;
    this.lastReq = now;
    this.requesting = true;
    // A hide() between request and response invalidates this token, so a
    // response for the old screen can never reveal an emptied container.
    var tok = ++this.token;
    try{
      window.CG.sdk.banner.requestBanner({ id:this.ID, width:size[0], height:size[1] })
        .then(function(){
          if(self.token !== tok) return;
          self.requesting = false; self.fails = 0; self.filled = true;
          if(self.reserved && self.wrap){ self.wrap.className = 'on'; self.shown = true; }
        })
        .catch(function(e){
          if(self.token !== tok){ self.requesting = false; return; }
          self.requesting = false; self.fail(e && e.code);
        });
    }catch(e){ this.requesting = false; this.fail('threw'); }
  },""")

sub("""  fail:function(code){
    if(code !== 'bannerCooldown') this.fails++;
    this.shown = false;
    if(this.wrap) this.wrap.className = '';
  },""",
"""  fail:function(code){
    if(code !== 'bannerCooldown') this.fails++;
    this.shown = false;
    this.filled = false;
    if(this.wrap) this.wrap.className = '';
  },""")

sub("""  hide:function(){
    this.shown = false;
    this.reserved = false;
    if(this.wrap) this.wrap.className = '';""",
"""  hide:function(){
    this.shown = false;
    this.reserved = false;
    this.filled = false;
    this.screen = '';
    this.token++;              // orphan any in-flight request
    if(this.wrap) this.wrap.className = '';""")

sub("""    if(BANNER.reserved && BANNER.screen !== G.mode) BANNER.hide();
    if(!BANNER.reserved) BANNER.show();
    else if(BANNER.shown) BANNER.place([BANNER.w, BANNER.h]);   // follow resizes""",
"""    if(BANNER.reserved && BANNER.screen !== G.mode) BANNER.hide();
    // Retry while the space is reserved but nothing is on screen yet; show()
    // rate-limits itself, so this cannot spam the SDK.
    if(!BANNER.reserved || (!BANNER.shown && !BANNER.requesting)) BANNER.show();
    else if(BANNER.shown) BANNER.place([BANNER.w, BANNER.h]);   // follow resizes""")

io.open(P5, 'w', encoding='utf-8', newline='\n').write(s)
print('banner: reveal-on-fill + request tokens')
