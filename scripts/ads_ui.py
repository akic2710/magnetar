import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


patch('src/p5.txt', [

# ---- SDK: ad availability probe -------------------------------------------
("""    // The SDK missed the real load, so bracket it now that it can hear us.""",
 """    // A revive button that can never fire is a rejection cause, so find out
    // up front whether ads can actually run for this player.
    try{
      this.adsOk = !!(SDK.ad && SDK.ad.requestAd);
      if(this.adsOk && SDK.ad.hasAdblock){
        SDK.ad.hasAdblock()
          .then(function(blocked){ window.CG.adsOk = !blocked; })
          .catch(function(){ window.CG.adsOk = true; });
      }
    }catch(e){ this.adsOk = false; }

    // The SDK missed the real load, so bracket it now that it can hear us."""),

("""  ready:false, cloud:false, sdk:null,""",
 """  ready:false, cloud:false, adsOk:false, sdk:null,"""),

# ---- SDK: requestAd wrapper -----------------------------------------------
("""  gameplayStart:function(){ try{ if(this.ready) this.sdk.game.gameplayStart(); }catch(e){} },""",
 """  /* One guarded path for both ad types. The game is blocked from the moment
     of the request (so nothing is clickable underneath) but only muted once
     the ad actually starts, which is what the docs ask for. Both guards exist
     because a game that freezes waiting on an ad is a rejection cause. */
  requestAd:function(type, onDone, onFail){
    var self = this;
    if(!this.ready || !this.sdk.ad || !this.sdk.ad.requestAd){ if(onFail) onFail('nosdk'); return; }
    var settled = false, startGuard = 0, runGuard = 0;
    function settle(ok, code){
      if(settled) return;
      settled = true;
      clearTimeout(startGuard); clearTimeout(runGuard);
      G.adBusy = false;
      A.duck(false);
      if(ok){ if(onDone) onDone(); }
      else { if(onFail) onFail(code||'other'); }
    }
    G.adBusy = true;
    startGuard = setTimeout(function(){ settle(false,'noStart'); }, 8000);
    try{
      this.sdk.ad.requestAd(type, {
        adStarted:function(){
          clearTimeout(startGuard);
          A.duck(true);
          self.gameplayStop();
          runGuard = setTimeout(function(){ settle(false,'noEnd'); }, 120000);
        },
        adFinished:function(){ settle(true); },
        adError:function(e){ settle(false, e && e.code); }
      });
    }catch(e){ settle(false,'threw'); }
  },

  gameplayStart:function(){ try{ if(this.ready) this.sdk.game.gameplayStart(); }catch(e){} },"""),

# ---- frame(): death -> revive -> finish ------------------------------------
("""  if(G.mode==='dying'){
    G.deathT += rdt;
    if(G.deathT > 1.15){ G.mode='over'; G.overT=0; }
  }""",
 """  if(G.mode==='dying'){
    G.deathT += rdt;
    if(!G.postDeath && G.deathT > 1.15){ G.postDeath = true; afterDeath(); }
  }
  if(G.mode==='revive' && !G.adBusy){
    G.reviveT -= rdt;
    if(G.reviveT <= 0) finishRun();   // silence declines, it never nags
  }
  if(G.adMsgT > 0) G.adMsgT -= rdt;"""),

("""  var sim = (G.mode==='play' || G.mode==='intro' || G.mode==='levelup' || G.mode==='dying');
  if(G.paused) sim = false;""",
 """  var sim = (G.mode==='play' || G.mode==='intro' || G.mode==='levelup' || G.mode==='dying');
  if(G.paused || G.adBusy) sim = false;"""),

("""  A.tick();
  G.uiT += rdt;""",
 """  if(!G.adBusy) A.tick();
  G.uiT += rdt;"""),

# ---- render dispatch -------------------------------------------------------
("""  if(G.mode==='cores') drawCores();""",
 """  if(G.mode==='cores') drawCores();
  if(G.mode==='revive') drawRevive();
  if(G.adMsgT > 0) text(G.adMsg, VW/2, VH-92, 14, C.scrap, 'center', 800, clamp(G.adMsgT,0,1), 3);
  if(G.adBusy) drawAdBusy();"""),

# ---- input -----------------------------------------------------------------
("""  var x = IN.clickX, y = IN.clickY;
  IN.clicked = false;
""",
 """  var x = IN.clickX, y = IN.clickY;
  IN.clicked = false;
  if(G.adBusy){ IN.swallow = true; return; }   // the overlay blocks everything
"""),

("""  if(G.mode==='over'){
    var ob = overBtns();""",
 """  if(G.mode==='revive'){
    var rb = reviveBtns();
    if(inRect(x,y,rb.yes)){ takeRevive(); IN.swallow=true; return; }
    if(inRect(x,y,rb.no)){  finishRun();  IN.swallow=true; return; }
    return;
  }
  if(G.mode==='over'){
    var ob = overBtns();"""),

# ---- screens ---------------------------------------------------------------
("""function drawPaused(){""",
 """/* -------------------------------- ads ---------------------------------- */
function reviveBtns(){
  var by = 190;
  return {
    yes:{x:VW/2-250, y:by+178, w:280, h:58},
    no: {x:VW/2+50,  y:by+178, w:200, h:58}
  };
}

function drawRevive(){
  ctx.fillStyle='rgba(3,5,14,0.78)';
  ctx.fillRect(0,0,VW,VH);

  var bx=VW/2-300, by=190, bw=600, bh=300;
  ctx.fillStyle='rgba(255,255,255,0.05)';
  roundRect(bx,by,bw,bh,20); ctx.fill();
  ctx.strokeStyle=hexA(C.player,0.40); ctx.lineWidth=2;
  roundRect(bx,by,bw,bh,20); ctx.stroke();

  text('CORE LOST', VW/2, by+46, 26, '#ff5f7a', 'center', 900, 1, 4);
  text('WAVE '+G.wave+'   '+G.score+' PTS', VW/2, by+78, 13, C.dim, 'center', 700, 0.8, 2);
  text('Watch a short ad to get back in?', VW/2, by+120, 21, C.text, 'center', 800, 1, 0.5);
  text('Optional \\u2014 declining keeps every point and every Flux you earned.',
       VW/2, by+146, 12, C.dim, 'center', 600, 0.75, 0.4);

  var b = reviveBtns();
  var hy = IN.has && inRect(IN.x,IN.y,b.yes);
  ctx.fillStyle = hexA(C.player, hy?0.24:0.13);
  roundRect(b.yes.x,b.yes.y,b.yes.w,b.yes.h,12); ctx.fill();
  ctx.strokeStyle = hexA(C.player, hy?1:0.7); ctx.lineWidth=2;
  roundRect(b.yes.x,b.yes.y,b.yes.w,b.yes.h,12); ctx.stroke();
  text('WATCH AD   REVIVE', b.yes.x+b.yes.w/2, b.yes.y+23, 17, C.text, 'center', 900, 1, 2);
  text('2 lives, back where you fell   \\u00b7   press Y',
       b.yes.x+b.yes.w/2, b.yes.y+43, 10, C.dim, 'center', 700, 0.7, 0.6);

  var hn = IN.has && inRect(IN.x,IN.y,b.no);
  ctx.fillStyle = hn?'rgba(255,255,255,0.09)':'rgba(255,255,255,0.04)';
  roundRect(b.no.x,b.no.y,b.no.w,b.no.h,12); ctx.fill();
  ctx.strokeStyle = 'rgba(234,242,255,'+(hn?0.5:0.25)+')'; ctx.lineWidth=2;
  roundRect(b.no.x,b.no.y,b.no.w,b.no.h,12); ctx.stroke();
  text('NO THANKS', b.no.x+b.no.w/2, b.no.y+23, 17, C.text, 'center', 800, 1, 2);
  text('press N', b.no.x+b.no.w/2, b.no.y+43, 10, C.dim, 'center', 700, 0.7, 1.5);

  // The docs ask for a visible timer on a rewarded request.
  var frac = clamp(G.reviveT/REVIVE_SECONDS, 0, 1);
  var cx = VW/2, cy = by+bh-34;
  ctx.strokeStyle='rgba(234,242,255,0.15)'; ctx.lineWidth=3;
  ctx.beginPath(); ctx.arc(cx-14,cy,11,0,TAU); ctx.stroke();
  ctx.strokeStyle=C.scrap; ctx.lineWidth=3;
  ctx.beginPath(); ctx.arc(cx-14,cy,11,-Math.PI/2,-Math.PI/2+TAU*frac); ctx.stroke();
  text(String(Math.ceil(Math.max(0,G.reviveT))), cx+6, cy, 13, C.dim, 'left', 800, 0.8, 1);
}

function drawAdBusy(){
  ctx.fillStyle='rgba(3,5,14,0.90)';
  ctx.fillRect(0,0,VW,VH);
  var cx=VW/2, cy=VH/2-8;
  ctx.strokeStyle='rgba(234,242,255,0.14)'; ctx.lineWidth=4;
  ctx.beginPath(); ctx.arc(cx,cy,26,0,TAU); ctx.stroke();
  ctx.strokeStyle=C.player; ctx.lineWidth=4;
  var sp = G.uiT*3.4;
  ctx.beginPath(); ctx.arc(cx,cy,26, sp, sp+1.9); ctx.stroke();
  text('LOADING AD', cx, cy+52, 15, C.dim, 'center', 800, 0.85, 4);
}

function drawPaused(){"""),
])

print('p5 patched: ad requests, revive screen, blocking overlay')
