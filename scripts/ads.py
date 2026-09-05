import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


# ------------------------------------------------------------------ p1
# Ads must silence the game without touching the player's own mute setting,
# so ducking is tracked separately and both feed one gain calculation.
patch('src/p1.txt', [(
"""  setMute:function(m){
    this.muted = m; store('mgn.mute', m?'1':'0');
    if(this.master) this.master.gain.setTargetAtTime(m?0:0.5, this.ctx.currentTime, 0.03);
  },""",
"""  ducked:false,
  setMute:function(m){
    this.muted = m; store('mgn.mute', m?'1':'0');
    this.applyGain();
  },
  /* CrazyGames requires the game to be silent for the duration of a video ad.
     Ducking is separate from mute so restoring audio afterwards cannot
     clobber what the player actually chose. */
  duck:function(on){ this.ducked = !!on; this.applyGain(); },
  applyGain:function(){
    if(!this.master || !this.ctx) return;
    this.master.gain.setTargetAtTime((this.muted||this.ducked)?0:0.5, this.ctx.currentTime, 0.03);
  },"""),
(
"""  tick:function(){
    if(!this.ctx || this.muted){ this.musT = 0; return; }""",
"""  tick:function(){
    if(!this.ctx || this.muted || this.ducked){ this.musT = 0; return; }""")])


# ------------------------------------------------------------------ p2
patch('src/p2.txt', [(
"""    deathT:0, ended:false, dmgFlash:0
  };""",
"""    deathT:0, ended:false, dmgFlash:0,
    postDeath:false, runFinished:false, revived:false, watchedAd:false,
    reviveT:0, adBusy:false, adMsg:'', adMsgT:0
  };"""),
(
"""  if(e.code==='KeyC' && G.mode==='over') openCores();""",
"""  if(e.code==='KeyC' && G.mode==='over') openCores();
  if(G.mode==='revive' && !G.adBusy){
    if(e.code==='KeyY') takeRevive();
    if(e.code==='KeyN') finishRun();
  }""")])


# ------------------------------------------------------------------ p3
patch('src/p3.txt', [(
"""function die(){
  if(G.ended) return;
  G.ended = true;
  G.mode = 'dying';
  G.deathT = 0;
  A.sDead();
  A.setHum(0,0);
  shakeIt(30); G.flash=0.8;
  spark(P.x,P.y,70,C.player,120,520,0.4,1.1,4);
  ring(P.x,P.y,260,'rgba(124,243,255,0.7)',0.8,5);
  G.fluxEarned = fluxFor(G.score, G.wave);
  addFlux(G.fluxEarned);
  var best = parseInt(store('mgn.best')||'0',10);
  if(G.score > best){ store('mgn.best', String(G.score)); G.newBest = true; }
  var bw = parseInt(store('mgn.bestwave')||'0',10);
  if(G.wave > bw) store('mgn.bestwave', String(G.wave));
  if(G.newBest && window.CG) window.CG.happytime();
  if(window.CG) window.CG.gameplayStop();
}""",
"""var REVIVE_SECONDS = 8;

/* Death is now only the start of the end-of-run sequence:
     die -> [revive offer] -> finishRun -> [midgame ad] -> game over
   Payout lives in finishRun, not here, so a revived run is not paid twice. */
function die(){
  if(G.ended) return;
  G.ended = true;
  G.mode = 'dying';
  G.deathT = 0;
  G.postDeath = false;
  A.sDead();
  A.setHum(0,0);
  shakeIt(30); G.flash=0.8;
  spark(P.x,P.y,70,C.player,120,520,0.4,1.1,4);
  ring(P.x,P.y,260,hexA(C.player,0.7),0.8,5);
  if(window.CG) window.CG.gameplayStop();
}

/* Only offer a revive on a run worth saving, once per run, and never when we
   know the request cannot succeed - a button that can never work is a
   CrazyGames rejection cause. */
function reviveAvailable(){
  return !!(window.CG && window.CG.ready && window.CG.adsOk && !G.revived && G.wave >= 3);
}
/* The SDK enforces its own 3-minute midgame cap, so this only adds the rules
   it cannot know: not after a trivially short run, and never a second ad in a
   run where the player already sat through a rewarded one. */
function midgameEligible(){
  return !!(window.CG && window.CG.ready && window.CG.adsOk && !G.watchedAd && G.t >= 45);
}

function afterDeath(){
  if(reviveAvailable()){ G.mode = 'revive'; G.reviveT = REVIVE_SECONDS; }
  else finishRun();
}

function showOver(){ G.mode = 'over'; G.overT = 0; }

function finishRun(){
  if(G.runFinished){ showOver(); return; }
  G.runFinished = true;

  G.fluxEarned = fluxFor(G.score, G.wave);
  addFlux(G.fluxEarned);
  var best = parseInt(store('mgn.best')||'0',10);
  if(G.score > best){ store('mgn.best', String(G.score)); G.newBest = true; }
  var bw = parseInt(store('mgn.bestwave')||'0',10);
  if(G.wave > bw) store('mgn.bestwave', String(G.wave));
  if(G.newBest && window.CG) window.CG.happytime();
  if(window.CG) window.CG.gameplayStop();

  // Death is an allowed midgame placement; the panel appears when it is done.
  if(midgameEligible()) window.CG.requestAd('midgame', showOver, showOver);
  else showOver();
}

function takeRevive(){
  if(G.adBusy || G.revived || G.mode!=='revive') return;
  window.CG.requestAd('rewarded', doRevive, function(code){
    // Never reward on adError - the run simply ends.
    G.adMsg = (code==='unfilled') ? 'NO AD AVAILABLE RIGHT NOW' : 'AD UNAVAILABLE';
    G.adMsgT = 2.2;
    finishRun();
  });
}

function doRevive(){
  G.revived = true;
  G.watchedAd = true;
  G.ended = false;
  G.postDeath = false;
  G.mode = 'play';
  P.hp = Math.max(1, Math.min(2, P.maxHp));
  P.inv = 3.0;
  bolts.length = 0;
  clearArea(300);
  A.sHeal();
  G.flash = 0.7;
  shakeIt(18);
  ring(P.x, P.y, 340, hexA(C.player,0.8), 0.8, 6);
  popText(P.x, P.y-46, 'REVIVED', C.player, 30);
  if(window.CG) window.CG.gameplayStart();
}

/* Buys breathing room, not points. Watching an ad must never move the
   scoreboard or the leaderboard stops meaning anything. */
function clearArea(r){
  for(var i=enemies.length-1;i>=0;i--){
    var e = enemies[i];
    var d = Math.max(1, len(e.x-P.x, e.y-P.y));
    if(e.type==='boss'){
      e.vx += (e.x-P.x)/d*280; e.vy += (e.y-P.y)/d*280;
      continue;
    }
    if(d < r){
      spark(e.x, e.y, 10, e.col, 90, 300, 0.2, 0.5, 3);
      enemies.splice(i,1);
    }
  }
}""")])

print('p1/p2/p3 patched for ads')
