import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

p = 'src/p5.txt'
s = io.open(p, encoding='utf-8').read()

start = s.index('/* -------------------------- CrazyGames SDK hook ------------------------ */')
end = s.index('/* -------------------------------- boot --------------------------------- */')

new = '''/* -------------------------- CrazyGames SDK ----------------------------- */
/* The game is fully playable with no SDK: store() falls back to localStorage
   and every call below is a guarded no-op. On CrazyGames the SDK gives us
   cloud saves (Flux and unlocks follow the player across devices), gameplay
   analytics, and happytime signals.

   The build flips ENABLE_CG_SDK off for the Artifact copy, whose CSP blocks
   external scripts - loading it there would only log a violation. */
var ENABLE_CG_SDK = true;

window.CG = {
  ready:false, cloud:false, sdk:null,

  init:function(){
    if(!ENABLE_CG_SDK || !document.head) return;
    var s = document.createElement('script');
    s.src = 'https://sdk.crazygames.com/crazygames-sdk-v3.js';
    // Blocked by CSP, offline, or ad-blocked: stay on localStorage silently.
    s.onerror = function(){};
    s.onload = function(){
      try{
        var SDK = window.CrazyGames && window.CrazyGames.SDK;
        if(!SDK || !SDK.init) return;
        // Every other module throws until init() resolves.
        SDK.init().then(function(){ window.CG.onReady(SDK); })
                  .catch(function(){});
      }catch(e){}
    };
    document.head.appendChild(s);
  },

  onReady:function(SDK){
    // "disabled" means we are on a domain the SDK does not serve; its calls
    // throw there, so we keep the local backend and stay quiet.
    try{ if(SDK.environment === 'disabled') return; }catch(e){ return; }

    this.sdk = SDK;
    this.ready = true;

    // Adopt cloud storage, folding in anything this device saved first.
    try{
      if(SDK.data && typeof SDK.data.getItem === 'function'){
        adoptCloudSave(SDK.data);
        this.cloud = true;
        applyCloudSave();
      }
    }catch(e){}

    // Signing in swaps the account under us, so drop the cache and re-apply.
    try{
      if(SDK.user && SDK.user.addAuthListener){
        SDK.user.addAuthListener(function(){
          refreshCloudSave();
          applyCloudSave();
        });
      }
    }catch(e){}

    // The SDK missed the real load, so bracket it now that it can hear us.
    try{ SDK.game.loadingStart(); SDK.game.loadingStop(); }catch(e){}
    if(G.mode==='play' || G.mode==='intro'){ this.gameplayStart(); }
  },

  gameplayStart:function(){ try{ if(this.ready) this.sdk.game.gameplayStart(); }catch(e){} },
  gameplayStop:function(){  try{ if(this.ready) this.sdk.game.gameplayStop();  }catch(e){} },
  happytime:function(){     try{ if(this.ready) this.sdk.game.happytime();     }catch(e){} },
  progress:function(pct){
    try{ if(this.ready) this.sdk.game.reportGameCompletedPercentage(clamp(Math.round(pct),0,100)); }catch(e){}
  }
};

/* Cloud values can land mid-session. Flux, unlocks and best scores are all
   read live so they need nothing; the equipped core is only consulted when a
   run is built. Re-rolling the player mid-run would be theft, so we only
   re-apply while the run is still effectively untouched. */
function applyCloudSave(){
  var core = selectedCore();
  if(P.core === core) return;
  var untouched = (G.mode==='intro') ||
                  (G.mode==='play' && G.wave<=1 && G.score===0 && G.kills===0);
  if(untouched){
    var wasIntro = (G.mode==='intro');
    reset();
    if(!wasIntro && G.mode!=='play'){ G.mode='play'; startWave(1); }
  }
  // Otherwise the cloud core simply takes effect on the next run.
}

window.CG.init();

'''

s = s[:start] + new + s[end:]
assert s.count('var ENABLE_CG_SDK') == 1
assert s.count('window.CG.init();') == 1
io.open(p, 'w', encoding='utf-8').write(s)
print('p5: SDK adapter rewritten')

# --------------------------------------------------------------- boot order
# migrateSave() needs CORES, so it runs at boot rather than inside store().
p = 'src/p5.txt'
s = io.open(p, encoding='utf-8').read()
old = 'reset();\nrequestAnimationFrame(frame);'
new = 'migrateSave();\nreset();\nrequestAnimationFrame(frame);'
assert old in s
io.open(p, 'w', encoding='utf-8').write(s.replace(old, new))
print('p5: migrateSave wired into boot')

# ------------------------------------------------------- progress reporting
p = 'src/p2.txt'
s = io.open(p, encoding='utf-8').read()
old = """function startWave(n){
  G.wave = n;
  G.waveT = 0;
  G.healedThisWave = false;"""
new = """function startWave(n){
  G.wave = n;
  G.waveT = 0;
  G.healedThisWave = false;
  // Wave 30 is a deep run; report progress against that as "complete".
  if(window.CG) window.CG.progress(Math.min(100, n/30*100));"""
assert old in s
io.open(p, 'w', encoding='utf-8').write(s.replace(old, new))
print('p2: progress reporting wired')

# ------------------------------------------- artifact build disables the SDK
p = 'build.mjs'
s = io.open(p, encoding='utf-8').read()
old = """const body = parts.join('\\n');
writeFileSync(join(root, 'game-body.html'), body, 'utf8');"""
new = """const body = parts.join('\\n');

// The Artifact host's CSP blocks external scripts, so the SDK could never
// load there; leaving it enabled would only log a violation on every open.
// The standalone CrazyGames build below keeps it on.
const artifactBody = body.replace(
  'var ENABLE_CG_SDK = true;',
  'var ENABLE_CG_SDK = false;   // disabled for the Artifact build (CSP blocks the SDK)'
);
if (artifactBody === body) throw new Error('build: could not find the SDK flag to disable');
writeFileSync(join(root, 'game-body.html'), artifactBody, 'utf8');"""
assert old in s
io.open(p, 'w', encoding='utf-8').write(s.replace(old, new))
print('build.mjs: artifact build disables the SDK')
