import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        s = s.replace(old, new)
    io.open(path, 'w', encoding='utf-8').write(s)


# ------------------------------------------------------------------ p1
# One key-value layer over three backends. Reads are cached because the HUD
# asks for the best score every frame, and an SDK getItem per frame is waste.
patch('src/p1.txt', [(
"""function store(k,v){
  try{
    if(v===undefined) return localStorage.getItem(k);
    localStorage.setItem(k,v); return v;
  }catch(e){ return null; }
}""",
"""/* ----------------------------- persistence -----------------------------
   store() reads and writes through whichever backend is available, in order
   of preference:
     1. the CrazyGames SDK data module - synced to the player's account and
        across their devices (adopted at runtime once the SDK finishes init)
     2. localStorage - per-device, the default before/without the SDK
     3. an in-memory map - private mode, sandboxed iframes, blocked storage
   Reads are served from a cache so per-frame HUD lookups cost nothing, and
   every path is exception-safe: storage that throws degrades to memory
   rather than breaking the run. */
var SYNC_KEYS  = ['mgn.earned','mgn.owned','mgn.core','mgn.best','mgn.bestwave','mgn.played'];
var LOCAL_ONLY = {'mgn.mute':1};   // a device preference, not account state
var saveBackend = null;            // null = localStorage, else SDK data module
var saveCache = {};

function rawGet(k){
  try{
    if(saveBackend && !LOCAL_ONLY[k]) return saveBackend.getItem(k);
    return localStorage.getItem(k);
  }catch(e){ return null; }
}
function rawSet(k,v){
  try{
    if(saveBackend && !LOCAL_ONLY[k]){ saveBackend.setItem(k,v); return; }
    localStorage.setItem(k,v);
  }catch(e){}
}
function store(k,v){
  if(v===undefined){
    if(k in saveCache) return saveCache[k];   // cached misses are null, and `in` still finds them
    var got = rawGet(k);
    saveCache[k] = got;
    return got;
  }
  v = String(v);
  saveCache[k] = v;
  rawSet(k,v);
  return v;
}""")])


# ------------------------------------------------------------------ p2
# Flux becomes a derived value: persist lifetime EARNED plus the owned set and
# compute the balance. A raw balance counter cannot be merged safely - taking
# the max of two devices would hand back Flux already spent on an unlock - and
# it can drift out of step with `owned`. Earned-minus-spent cannot.
patch('src/p2.txt', [(
"""function getFlux(){ return parseInt(store('mgn.flux')||'0',10)||0; }
function setFlux(v){ store('mgn.flux', String(Math.max(0, Math.round(v)))); }""",
"""function num(v){ var n = parseInt(v||'0',10); return isNaN(n) ? 0 : n; }
function spentFlux(){
  var l = ownedList(), total = 0;
  for(var i=0;i<CORES.length;i++) if(l.indexOf(CORES[i].id)>=0) total += CORES[i].cost;
  return total;
}
/* Balance is derived, never stored, so it can never disagree with `owned`. */
function getEarned(){ return num(store('mgn.earned')); }
function getFlux(){ return Math.max(0, getEarned() - spentFlux()); }
function addFlux(n){ store('mgn.earned', String(getEarned() + Math.max(0, Math.round(n)))); }

/* Saves written before the earned/spent model stored a balance. */
function migrateSave(){
  if(store('mgn.earned') !== null) return;
  var old = store('mgn.flux');
  if(old === null) return;
  store('mgn.earned', String(num(old) + spentFlux()));
}

/* Merge local and cloud saves without ever taking something away: unlocks
   union, monotonic counters take the max, and the equipped core has to be one
   the player actually owns afterwards. */
function mergeSave(local, cloud){
  var ids = {}, i, l;
  l = (local['mgn.owned']||'prospector').split(',');
  for(i=0;i<l.length;i++) if(l[i]) ids[l[i]] = 1;
  l = (cloud['mgn.owned']||'prospector').split(',');
  for(i=0;i<l.length;i++) if(l[i]) ids[l[i]] = 1;
  var owned = [];
  for(i=0;i<CORES.length;i++) if(ids[CORES[i].id]) owned.push(CORES[i].id);
  if(owned.indexOf('prospector') < 0) owned.unshift('prospector');

  var core = cloud['mgn.core'];
  if(!core || owned.indexOf(core) < 0) core = local['mgn.core'];
  if(!core || owned.indexOf(core) < 0) core = 'prospector';

  return {
    'mgn.owned':    owned.join(','),
    'mgn.core':     core,
    'mgn.earned':   String(Math.max(num(local['mgn.earned']),   num(cloud['mgn.earned']))),
    'mgn.best':     String(Math.max(num(local['mgn.best']),     num(cloud['mgn.best']))),
    'mgn.bestwave': String(Math.max(num(local['mgn.bestwave']), num(cloud['mgn.bestwave']))),
    'mgn.played':   (local['mgn.played']==='1' || cloud['mgn.played']==='1') ? '1' : null
  };
}

/* Switch store() onto the SDK data module, folding in whatever this device
   already had. The SDK migrates its own guest data on sign-in, but guest
   progress written straight to localStorage before the SDK loaded is invisible
   to it - this is what keeps that from being lost. */
function adoptCloudSave(dataModule){
  var local = {}, cloud = {}, i, k;
  for(i=0;i<SYNC_KEYS.length;i++){ k=SYNC_KEYS[i]; local[k] = store(k); }
  saveBackend = dataModule;
  saveCache = {};
  for(i=0;i<SYNC_KEYS.length;i++){ k=SYNC_KEYS[i]; cloud[k] = store(k); }
  var merged = mergeSave(local, cloud);
  for(k in merged) if(merged[k] !== null) store(k, merged[k]);
  return merged;
}

/* The account swaps underneath us on sign-in, so the cache has to go. */
function refreshCloudSave(){ saveCache = {}; }""")
,(
"""  var f = getFlux();
  if(f < c.cost) return false;
  setFlux(f - c.cost);
  var l = ownedList();""",
"""  if(getFlux() < c.cost) return false;
  var l = ownedList();   // the spend is implied by ownership, never deducted""")])


# ------------------------------------------------------------------ p3
patch('src/p3.txt', [(
"""  G.fluxEarned = fluxFor(G.score, G.wave);
  setFlux(getFlux() + G.fluxEarned);""",
"""  G.fluxEarned = fluxFor(G.score, G.wave);
  addFlux(G.fluxEarned);"""),
(
"""  var bw = parseInt(store('mgn.bestwave')||'0',10);
  if(G.wave > bw) store('mgn.bestwave', String(G.wave));""",
"""  var bw = parseInt(store('mgn.bestwave')||'0',10);
  if(G.wave > bw) store('mgn.bestwave', String(G.wave));
  if(G.newBest && window.CG) window.CG.happytime();"""),
(
"""  if(e.type==='boss'){
    G.bossRef=null; A.sBig(); G.flash=0.6; G.chroma=1;""",
"""  if(e.type==='boss'){
    G.bossRef=null; A.sBig(); G.flash=0.6; G.chroma=1;
    if(window.CG) window.CG.happytime();""")])

print('persistence + flux model + payout hooks done')
