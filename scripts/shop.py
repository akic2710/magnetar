import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        assert s.count(old) == 1, '%s: ambiguous -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


# ------------------------------------------------------------------ p1
# Three more keys ride the account rather than the device: what you own, and
# the two things you have equipped.
patch('src/p1.txt', [(
"""var SYNC_KEYS  = ['mgn.earned','mgn.owned','mgn.core','mgn.best','mgn.bestwave','mgn.played'];""",
"""var SYNC_KEYS  = ['mgn.earned','mgn.owned','mgn.core','mgn.best','mgn.bestwave','mgn.played',
                  'mgn.shop','mgn.trail','mgn.arena'];""")])


# ------------------------------------------------------------------ p2
patch('src/p2.txt', [

# ---- the catalogue, sitting after the cores it shares a currency with ----
("""function coreById(id){
  for(var i=0;i<CORES.length;i++) if(CORES[i].id===id) return CORES[i];
  return CORES[0];
}""",
"""function coreById(id){
  for(var i=0;i<CORES.length;i++) if(CORES[i].id===id) return CORES[i];
  return CORES[0];
}

/* --------------------------------- shop ---------------------------------
   Bought with Flux, which is only ever earned by playing. Two rules keep the
   shop from touching the thing the bots spent so long balancing:

     - wakes and arenas are looks only. Nothing in either reaches a number the
       run reads, so no purchase can be mistaken for an advantage.
     - the one line that is not cosmetic, the amplifier, pays out more Flux and
       does nothing else. It buys you the rest of the shop sooner; it can never
       buy you a longer run.

   Wakes deliberately declare no colour of their own and take the equipped
   core's instead. Warm hues belong to enemies here, and a cosmetic that could
   dress the player in an enemy's colour is a cosmetic that gets people killed.
   Arenas may recolour, because the grid is background by definition - but they
   stay dark and low-saturation for the same readability reason. */
var SHOP = [
  { id:'trail.std',   kind:'trail', name:'STANDARD',     cost:0,
    tag:'No wake. Just you and the field.' },
  { id:'trail.ion',   kind:'trail', name:'ION WAKE',     cost:250,
    tag:'A smooth ribbon in your core colour.' },
  { id:'trail.spark', kind:'trail', name:'SPARKFALL',    cost:450,
    tag:'Embers that shake loose behind you.' },
  { id:'trail.echo',  kind:'trail', name:'ECHO',         cost:700,
    tag:'Ghosts of where you just were.' },

  { id:'arena.deep',  kind:'arena', name:'DEEP FIELD',   cost:0,
    tag:'The standard arena.',
    sky:'#05070f', grid:'84,150,255',  top:'60,120,255',  bot:'180,60,255',  edge:'124,200,255' },
  { id:'arena.noct',  kind:'arena', name:'NOCTURNE',     cost:300,
    tag:'Indigo grid, deeper black.',
    sky:'#03030a', grid:'104,96,255',  top:'70,50,200',   bot:'120,40,220',  edge:'150,140,255' },
  { id:'arena.tide',  kind:'arena', name:'TIDE',         cost:550,
    tag:'Cold teal, lit from below.',
    sky:'#040b10', grid:'60,200,190',  top:'20,140,160',  bot:'30,90,180',   edge:'120,240,220' },
  { id:'arena.graph', kind:'arena', name:'GRAPHITE',     cost:800,
    tag:'No colour at all. Only the field.',
    sky:'#08090c', grid:'170,180,200', top:'120,130,150', bot:'90,100,120',  edge:'190,200,215' },

  { id:'boost.amp1',  kind:'boost', name:'AMPLIFIER I',  cost:900,
    tag:'+20% Flux from every run, forever.' },
  { id:'boost.amp2',  kind:'boost', name:'AMPLIFIER II', cost:2200,
    tag:'+45% Flux instead. Needs Amplifier I.', req:'boost.amp1' }
];

function shopById(id){
  for(var i=0;i<SHOP.length;i++) if(SHOP[i].id===id) return SHOP[i];
  return null;
}
function shopOwned(){ var s = store('mgn.shop'); return s ? s.split(',') : []; }
function ownsItem(id){
  var it = shopById(id);
  if(!it) return false;
  return it.cost === 0 || shopOwned().indexOf(id) >= 0;   // defaults are always yours
}
function itemLocked(it){ return !!(it && it.req && !ownsItem(it.req)); }
function spentShop(){
  var l = shopOwned(), t = 0;
  for(var i=0;i<SHOP.length;i++) if(l.indexOf(SHOP[i].id) >= 0) t += SHOP[i].cost;
  return t;
}
function equippedTrail(){
  var id = store('mgn.trail') || 'trail.std';
  return ownsItem(id) ? id : 'trail.std';
}
function equippedArena(){
  var id = store('mgn.arena') || 'arena.deep';
  return ownsItem(id) ? id : 'arena.deep';
}
/* Read once per frame by the background, so it is worth not walking the
   catalogue every time. Cleared by anything that can change the answer. */
var themeCache = null;
function arenaTheme(){
  if(!themeCache) themeCache = shopById(equippedArena()) || shopById('arena.deep');
  return themeCache;
}
function fluxMul(){
  if(ownsItem('boost.amp2')) return 1.45;
  if(ownsItem('boost.amp1')) return 1.20;
  return 1;
}
function buyItem(id){
  var it = shopById(id);
  if(!it || it.cost === 0 || ownsItem(id) || itemLocked(it)) return false;
  if(getFlux() < it.cost) return false;
  var l = shopOwned();      // the spend is implied by ownership, never deducted
  if(l.indexOf(id) < 0) l.push(id);
  store('mgn.shop', l.join(','));
  return true;
}
function equipItem(id){
  var it = shopById(id);
  if(!it || !ownsItem(id)) return;
  if(it.kind === 'trail') store('mgn.trail', id);
  else if(it.kind === 'arena'){ store('mgn.arena', id); themeCache = null; }
}

/* ----------------------------- purchase rail -----------------------------
   Every purchase in the game goes through PURCHASE.buy, so exactly one place
   knows how a player pays for anything.

   Today the only rail is Flux. CrazyGames in-game purchases are invite-only:
   they issue an Xsolla project id per game, and their SDK surface is just two
   calls - SDK.user.getXsollaUserToken() for a short-lived token, and
   SDK.analytics.trackOrder('xsolla', order) to report a finished order. The
   catalogue and the checkout widget live in Xsolla's own API, not theirs.

   A 'cash' rail drops in beside the Flux one when that invite arrives, and
   nothing outside this object has to change. Their rules are the reason
   canPurchase() exists at all: real-money purchases must be limited to
   signed-in players, guests must not even see a buy button, and the shop has
   to be hidden entirely inside the CrazyGames mobile app. On the Flux rail
   none of that applies, because Flux is earned rather than bought. */
var PURCHASE = {
  rail: 'flux',
  signedIn: false,     // fed by the SDK auth listener; only the cash rail reads it
  inCrazyApp: false,   // ditto - the app forbids real-money purchases outright

  canPurchase: function(){
    if(this.rail === 'flux') return true;
    return this.signedIn && !this.inCrazyApp;
  },
  priceLabel: function(it){
    return this.rail === 'flux' ? (it.cost + ' FLUX') : it.price;
  },
  /* done(ok, why) - always called, never throws, so the caller never has to
     guess whether a purchase is still in flight. */
  buy: function(it, done){
    if(!it || !this.canPurchase()){ done(false, 'unavailable'); return; }
    if(this.rail === 'flux'){
      if(itemLocked(it)){ done(false, 'locked'); return; }
      if(getFlux() < it.cost){ done(false, 'funds'); return; }
      done(buyItem(it.id), 'bought');
      return;
    }
    done(false, 'unavailable');   // no cash rail until the invite lands
  }
};"""),

# ---- the derived balance has to account for shop spend too ----
("""function spentFlux(){
  var l = ownedList(), total = 0;
  for(var i=0;i<CORES.length;i++) if(l.indexOf(CORES[i].id)>=0) total += CORES[i].cost;
  return total;
}""",
"""function spentFlux(){
  var l = ownedList(), total = 0;
  for(var i=0;i<CORES.length;i++) if(l.indexOf(CORES[i].id)>=0) total += CORES[i].cost;
  return total + spentShop();
}"""),

# ---- merge: unlocks union, equipped has to survive the union ----
("""  var core = cloud['mgn.core'];
  if(!core || owned.indexOf(core) < 0) core = local['mgn.core'];
  if(!core || owned.indexOf(core) < 0) core = 'prospector';

  return {
    'mgn.owned':    owned.join(','),
    'mgn.core':     core,""",
"""  var core = cloud['mgn.core'];
  if(!core || owned.indexOf(core) < 0) core = local['mgn.core'];
  if(!core || owned.indexOf(core) < 0) core = 'prospector';

  var sids = {}, shop = [];
  l = (local['mgn.shop']||'').split(',');
  for(i=0;i<l.length;i++) if(l[i]) sids[l[i]] = 1;
  l = (cloud['mgn.shop']||'').split(',');
  for(i=0;i<l.length;i++) if(l[i]) sids[l[i]] = 1;
  for(i=0;i<SHOP.length;i++) if(sids[SHOP[i].id]) shop.push(SHOP[i].id);

  /* An equipped item must be one the merged account actually has - a free
     default, or something in the union above. */
  function eqOk(v, kind){
    var it = v && shopById(v);
    return !!it && it.kind === kind && (it.cost === 0 || !!sids[v]);
  }
  var trail = cloud['mgn.trail'];
  if(!eqOk(trail,'trail')) trail = local['mgn.trail'];
  if(!eqOk(trail,'trail')) trail = 'trail.std';
  var arena = cloud['mgn.arena'];
  if(!eqOk(arena,'arena')) arena = local['mgn.arena'];
  if(!eqOk(arena,'arena')) arena = 'arena.deep';

  return {
    'mgn.owned':    owned.join(','),
    'mgn.core':     core,
    'mgn.shop':     shop.join(','),
    'mgn.trail':    trail,
    'mgn.arena':    arena,"""),

# ---- both cache resets have to drop the theme too ----
("""/* The account swaps underneath us on sign-in, so the cache has to go. */
function refreshCloudSave(){ saveCache = {}; }""",
"""/* The account swaps underneath us on sign-in, so the caches have to go. */
function refreshCloudSave(){ saveCache = {}; themeCache = null; }"""),
("""  var merged = mergeSave(local, cloud);
  for(k in merged) if(merged[k] !== null) store(k, merged[k]);
  return merged;""",
"""  var merged = mergeSave(local, cloud);
  for(k in merged) if(merged[k] !== null) store(k, merged[k]);
  themeCache = null;
  return merged;"""),

# ---- player carries its own wake samples ----
("""    killsSinceHeal:0, charge:0, blastCool:0,
    core:'prospector', sides:3
  };""",
"""    killsSinceHeal:0, charge:0, blastCool:0,
    trail:[], trailT:0,
    core:'prospector', sides:3
  };"""),

# ---- shop screen state ----
("""    reviveT:0, adBusy:false, adMsg:'', adMsgT:0
  };""",
"""    reviveT:0, adBusy:false, adMsg:'', adMsgT:0,
    shopT:0, shopMsg:'', shopMsgT:0
  };"""),

# ---- keys: S opens the shop, C leaves it, Enter launches from it ----
("""  if(e.code==='Enter' && (G.mode==='over' || G.mode==='cores')) restart();
  if(e.code==='KeyC' && G.mode==='over') openCores();""",
"""  if(e.code==='Enter' && (G.mode==='over' || G.mode==='cores' || G.mode==='shop')) restart();
  if(e.code==='KeyC' && (G.mode==='over' || G.mode==='shop')) openCores();
  if(e.code==='KeyS' && (G.mode==='over' || G.mode==='cores')) openShop();""")])


# ------------------------------------------------------------------ p3
patch('src/p3.txt', [

# ---- the amplifier is applied once, where the payout is decided ----
("""  G.fluxEarned = fluxFor(G.score, G.wave);
  addFlux(G.fluxEarned);""",
"""  G.fluxEarned = Math.round(fluxFor(G.score, G.wave) * fluxMul());
  addFlux(G.fluxEarned);"""),

# ---- wake samples, on the fixed step so length is frame-rate independent ----
("""  /* ---- scrap field ---- */""",
"""  /* ---- cosmetic wake ---- */
  /* Sampled on the fixed timestep rather than per frame, so the wake is the
     same length on a 60 Hz laptop as on a 165 Hz monitor. */
  if(alive){
    P.trailT -= dt;
    if(P.trailT <= 0){
      P.trailT = 0.018;
      P.trail.unshift({x:P.x, y:P.y, a:P.orbBase});
      while(P.trail.length > 30) P.trail.pop();
    }
  } else if(P.trail.length){
    P.trail.length = 0;
  }

  /* ---- scrap field ---- */""")])


# ------------------------------------------------------------------ p5
patch('src/p5.txt', [

# ---- dispatch ----
("""  if(G.mode==='cores') drawCores();""",
"""  if(G.mode==='cores') drawCores();
  if(G.mode==='shop') drawShop();"""),

# ---- the arena is a purchase now, so the background reads it ----
("""function drawBackground(){
  var pulse = G.pulse;
  ctx.fillStyle = '#05070f';
  ctx.fillRect(0,0,VW,VH);

  // subtle drifting grid
  var step = 64, t = G.t*10;
  ctx.lineWidth = 1;
  ctx.strokeStyle = 'rgba(84,150,255,'+(0.055+pulse*0.10)+')';""",
"""function drawBackground(){
  var pulse = G.pulse, th = arenaTheme();
  ctx.fillStyle = th.sky;
  ctx.fillRect(0,0,VW,VH);

  // subtle drifting grid
  var step = 64, t = G.t*10;
  ctx.lineWidth = 1;
  ctx.strokeStyle = 'rgba('+th.grid+','+(0.055+pulse*0.10)+')';"""),
("""  var g = ctx.createLinearGradient(0,0,0,VH);
  g.addColorStop(0,'rgba(60,120,255,0.10)');
  g.addColorStop(0.5,'rgba(60,120,255,0.00)');
  g.addColorStop(1,'rgba(180,60,255,0.10)');
  ctx.fillStyle=g; ctx.fillRect(0,0,VW,VH);
  ctx.globalCompositeOperation='source-over';

  ctx.lineWidth = 3;
  ctx.strokeStyle = 'rgba(124,200,255,'+(0.22+pulse*0.4)+')';""",
"""  var g = ctx.createLinearGradient(0,0,0,VH);
  g.addColorStop(0,'rgba('+th.top+',0.10)');
  g.addColorStop(0.5,'rgba('+th.top+',0.00)');
  g.addColorStop(1,'rgba('+th.bot+',0.10)');
  ctx.fillStyle=g; ctx.fillRect(0,0,VW,VH);
  ctx.globalCompositeOperation='source-over';

  ctx.lineWidth = 3;
  ctx.strokeStyle = 'rgba('+th.edge+','+(0.22+pulse*0.4)+')';"""),

# ---- the wake itself, behind the player ----
("""  if(!alive) return;

  var blink = P.inv>0 && (Math.floor(G.t*22)%2===0);""",
"""  if(!alive) return;
  drawTrail();

  var blink = P.inv>0 && (Math.floor(G.t*22)%2===0);"""),
("""/* -------------------------------- cores -------------------------------- */""",
"""/* The wake borrows C.player, which follows the equipped core, so it can never
   come out in a colour the arena has already given to something hostile. */
function drawTrail(){
  var id = equippedTrail(), tr = P.trail;
  if(id === 'trail.std' || !tr || tr.length < 3) return;
  var n = tr.length, i, f, p;

  if(id === 'trail.ion'){
    ctx.globalCompositeOperation = 'lighter';
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for(i=1;i<n;i++){
      f = 1 - i/n;
      ctx.strokeStyle = hexA(C.player, 0.28*f*f);
      ctx.lineWidth = P.r*1.4*f + 0.5;
      ctx.beginPath();
      ctx.moveTo(tr[i-1].x, tr[i-1].y); ctx.lineTo(tr[i].x, tr[i].y);
      ctx.stroke();
    }
    ctx.lineCap = 'butt'; ctx.lineJoin = 'miter';
    ctx.globalCompositeOperation = 'source-over';
  } else if(id === 'trail.spark'){
    ctx.globalCompositeOperation = 'lighter';
    for(i=0;i<n;i+=2){
      p = tr[i]; f = 1 - i/n;
      var s = P.r*0.30*f + 0.4;
      ctx.fillStyle = hexA(C.player, 0.60*f*f);
      ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.a*2 + i*0.7);
      ctx.fillRect(-s,-s,s*2,s*2);
      ctx.restore();
    }
    ctx.globalCompositeOperation = 'source-over';
  } else {
    ctx.lineWidth = 1.5;
    for(i=4;i<n;i+=6){
      p = tr[i]; f = 1 - i/n;
      ctx.strokeStyle = hexA(C.player, 0.38*f);
      poly(p.x, p.y, P.r*1.5*(0.55+0.55*f), P.sides, -p.a*0.8);
      ctx.stroke();
    }
  }
}

/* -------------------------------- cores -------------------------------- */"""),

# ---- cores gets a second button, so its launch row moves left ----
("""        divY:110, statY:134, statLh:18, statSize:12,
        launch:{x:VW/2-130, y:524, w:260, h:46} }""",
"""        divY:110, statY:134, statLh:18, statSize:12,
        launch:{x:VW/2-213, y:524, w:260, h:46},
        alt:{x:VW/2+63, y:524, w:150, h:46} }"""),
("""        divY:134, statY:160, statLh:22, statSize:12.5,
        launch:{x:VW/2-130, y:650, w:260, h:52} };""",
"""        divY:134, statY:160, statLh:22, statSize:12.5,
        launch:{x:VW/2-213, y:650, w:260, h:52},
        alt:{x:VW/2+63, y:650, w:150, h:52} };"""),
("""function launchRect(){ return coresLayout().launch; }""",
"""function launchRect(){ return coresLayout().launch; }

/* Both meta screens end on the same pair - start a run, or step sideways to
   the other one - so they share the drawing rather than drifting apart. */
function drawMetaButtons(L, altLabel){
  var LB = L.launch, hovL = IN.has && inRect(IN.x,IN.y,LB);
  var pulse = 0.6+0.4*Math.sin(G.uiT*4);
  ctx.fillStyle = hexA(C.player, hovL?0.24:0.13);
  roundRect(LB.x,LB.y,LB.w,LB.h,14); ctx.fill();
  ctx.strokeStyle = hexA(C.player, hovL?1:pulse); ctx.lineWidth=2;
  roundRect(LB.x,LB.y,LB.w,LB.h,14); ctx.stroke();
  text('LAUNCH', LB.x+LB.w/2, LB.y+LB.h/2, 19, C.text, 'center', 900, 1, 4);

  var AB = L.alt, hovA = IN.has && inRect(IN.x,IN.y,AB);
  ctx.fillStyle = hovA ? hexA(C.scrap,0.16) : 'rgba(255,255,255,0.05)';
  roundRect(AB.x,AB.y,AB.w,AB.h,14); ctx.fill();
  ctx.strokeStyle = hovA ? C.scrap : 'rgba(234,242,255,0.26)'; ctx.lineWidth=2;
  roundRect(AB.x,AB.y,AB.w,AB.h,14); ctx.stroke();
  text(altLabel, AB.x+AB.w/2, AB.y+AB.h/2, 14, hovA?C.scrap:C.text, 'center', 800, 1, 2.5);
}"""),
("""  var LB = L.launch;
  var hovL = IN.has && inRect(IN.x,IN.y,LB);
  var pulse = 0.6+0.4*Math.sin(G.uiT*4);
  ctx.fillStyle = hexA(C.player, hovL?0.24:0.13);
  roundRect(LB.x,LB.y,LB.w,LB.h,14); ctx.fill();
  ctx.strokeStyle = hexA(C.player, hovL?1:pulse); ctx.lineWidth=2;
  roundRect(LB.x,LB.y,LB.w,LB.h,14); ctx.stroke();
  text('LAUNCH', VW/2, LB.y+LB.h/2, 19, C.text, 'center', 900, 1, 4);

  drawBtn(BTN_MUTE, (A.muted||A.forced)?'muted':'sound');
  ctx.globalAlpha = 1;
}
""",
"""  drawMetaButtons(L, 'SHOP');
  drawBtn(BTN_MUTE, (A.muted||A.forced)?'muted':'sound');
  ctx.globalAlpha = 1;
}

/* --------------------------------- shop --------------------------------- */
/* Same vertical rhythm as the cores screen, so moving between the two does not
   feel like moving between two different games. Three shorter rows of four
   rather than two tall rows of three: a cosmetic sells itself on its preview
   and needs a fraction of the words a core does. */
function shopLayout(){
  return BANNER.reserved
    ? { title:46, sub:78,
        y0:112, h:120, step:132,
        glyphY:40, nameY:32, tagY:56, tagSize:11, tagLh:14, priceY:100,
        launch:{x:VW/2-213, y:524, w:260, h:46},
        alt:{x:VW/2+63, y:524, w:150, h:46} }
    : { title:62, sub:98,
        y0:140, h:148, step:164,
        glyphY:48, nameY:36, tagY:64, tagSize:12, tagLh:16, priceY:124,
        launch:{x:VW/2-213, y:650, w:260, h:52},
        alt:{x:VW/2+63, y:650, w:150, h:52} };
}
function shopCardRect(i){
  var L = shopLayout(), col = i%4, row = Math.floor(i/4);
  return {x:66 + col*292, y:L.y0 + row*L.step, w:272, h:L.h};
}

/* Every card previews the thing it is selling: a wake as a real wake, an
   arena as its own grid and glow, the amplifier as Flux going up. */
function shopGlyph(it, cx, cy, alpha){
  ctx.globalAlpha = alpha;
  var i, f, gx, gy;

  if(it.kind === 'trail'){
    if(it.id === 'trail.std'){
      ctx.strokeStyle = hexA(C.player, 0.30); ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(cx, cy, 9, 0, TAU); ctx.stroke();
      ctx.fillStyle = C.player;
      ctx.beginPath(); ctx.arc(cx, cy, 4, 0, TAU); ctx.fill();
    } else {
      ctx.globalCompositeOperation = 'lighter';
      for(i=0;i<9;i++){
        f = 1 - i/9;
        gx = cx + 11 - i*3; gy = cy + Math.sin(i*0.7 + G.uiT*3)*4;
        if(it.id === 'trail.ion'){
          ctx.fillStyle = hexA(C.player, 0.55*f*f);
          ctx.beginPath(); ctx.arc(gx, gy, 4.2*f + 0.6, 0, TAU); ctx.fill();
        } else if(it.id === 'trail.spark'){
          var s = 2.6*f + 0.4;
          ctx.fillStyle = hexA(C.player, 0.75*f*f);
          ctx.save(); ctx.translate(gx, gy); ctx.rotate(i*0.9 + G.uiT);
          ctx.fillRect(-s,-s,s*2,s*2);
          ctx.restore();
        } else {
          ctx.strokeStyle = hexA(C.player, 0.55*f); ctx.lineWidth = 1.2;
          poly(gx, gy, 4.5*f + 1.2, 3, G.uiT*0.6); ctx.stroke();
        }
      }
      ctx.globalCompositeOperation = 'source-over';
    }

  } else if(it.kind === 'arena'){
    var w = 17, h = 13;
    ctx.fillStyle = it.sky;
    roundRect(cx-w, cy-h, w*2, h*2, 4); ctx.fill();
    ctx.save();
    roundRect(cx-w, cy-h, w*2, h*2, 4); ctx.clip();
    ctx.strokeStyle = 'rgba('+it.grid+',0.55)'; ctx.lineWidth = 1;
    ctx.beginPath();
    for(i=0;i<4;i++){ ctx.moveTo(cx-w+4+i*9, cy-h); ctx.lineTo(cx-w+4+i*9, cy+h); }
    for(i=0;i<3;i++){ ctx.moveTo(cx-w, cy-h+4+i*9); ctx.lineTo(cx+w, cy-h+4+i*9); }
    ctx.stroke();
    var gg = ctx.createLinearGradient(0, cy-h, 0, cy+h);
    gg.addColorStop(0,   'rgba('+it.top+',0.55)');
    gg.addColorStop(0.5, 'rgba('+it.top+',0)');
    gg.addColorStop(1,   'rgba('+it.bot+',0.55)');
    ctx.fillStyle = gg; ctx.fillRect(cx-w, cy-h, w*2, h*2);
    ctx.restore();
    ctx.strokeStyle = 'rgba('+it.edge+',0.75)'; ctx.lineWidth = 1.5;
    roundRect(cx-w, cy-h, w*2, h*2, 4); ctx.stroke();

  } else {
    ctx.globalCompositeOperation = 'lighter';
    blob(cx, cy-3, 26, hexA(C.scrap, 0.30*alpha));
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = C.scrap;
    ctx.save(); ctx.translate(cx, cy-3); ctx.rotate(G.uiT*0.6);
    ctx.fillRect(-5,-5,10,10);
    ctx.restore();
    ctx.strokeStyle = hexA(C.scrap, 0.70); ctx.lineWidth = 2;
    for(i=0;i<3;i++){
      var bh = 3 + i*3.5;
      ctx.beginPath();
      ctx.moveTo(cx-13+i*13, cy+16);
      ctx.lineTo(cx-13+i*13, cy+16-bh);
      ctx.stroke();
    }
  }
  ctx.globalAlpha = 1;
}

function openShop(){
  G.mode = 'shop';
  G.shopT = 0;
  A.sUi();
}

/* Purchases funnel through PURCHASE rather than buyItem, so the day a cash
   rail exists this call site does not have to learn about it. */
function tryBuy(it){
  PURCHASE.buy(it, function(ok, why){
    if(ok){
      equipItem(it.id);          // a no-op for boosts, which are never equipped
      A.sLevel();
      G.boughtT = G.uiT;
      return;
    }
    A.tone(150,0.20,'square',0.09,100);
    G.shopMsg = (why === 'funds')  ? 'NOT ENOUGH FLUX'
              : (why === 'locked') ? 'AMPLIFIER I FIRST'
              : 'UNAVAILABLE';
    G.shopMsgT = 1.8;
  });
}

function drawShop(){
  G.shopT = (G.shopT||0) + 0.016;
  var a = clamp(G.shopT*5,0,1);
  var L = shopLayout();
  ctx.fillStyle='rgba(3,5,14,0.94)';
  ctx.fillRect(0,0,VW,VH);
  ctx.globalAlpha = a;

  text('SHOP', 66, L.title, 34, C.text, 'left', 900, 1, 7);
  text('Wakes and arenas are looks only. The amplifier banks more Flux - it never makes a run easier.',
       66, L.sub, 13, C.dim, 'left', 600, 0.75, 0.5);

  var flux = getFlux();
  text(String(flux), VW-66, L.title-4, 34, C.scrap, 'right', 900, 1, 1);
  text('FLUX BANKED', VW-66, L.title+26, 10, C.dim, 'right', 700, 0.75, 4);

  var trail = equippedTrail(), arena = equippedArena();
  for(var i=0;i<SHOP.length;i++){
    var it = SHOP[i], r = shopCardRect(i);
    var own = ownsItem(it.id);
    var eq = (it.id === trail || it.id === arena);
    var lock = itemLocked(it);
    var afford = flux >= it.cost;
    var live = own || (afford && !lock);   // dim only what you cannot act on yet
    var hov = IN.has && inRect(IN.x,IN.y,r);
    var ca = a * (live ? 1 : 0.5);

    ctx.fillStyle = eq ? hexA(C.player,0.11) : (hov && live ? 'rgba(255,255,255,0.07)' : 'rgba(255,255,255,0.032)');
    roundRect(r.x,r.y,r.w,r.h,16); ctx.fill();
    ctx.strokeStyle = eq ? C.player : (hov && live ? hexA(C.player,0.75) : 'rgba(234,242,255,0.14)');
    ctx.lineWidth = eq ? 2.5 : 1.5;
    roundRect(r.x,r.y,r.w,r.h,16); ctx.stroke();

    shopGlyph(it, r.x+40, r.y+L.glyphY, ca);

    var tx = r.x+74;
    text(it.name, tx, r.y+L.nameY, 16, own?C.text:'rgba(234,242,255,0.8)', 'left', 900, ca, 1.2);
    wrapText(it.tag, tx, r.y+L.tagY, L.tagSize, C.dim, r.w-74-18, L.tagLh, 'left', ca*0.8);

    hr(r.x+18, r.x+r.w-18, r.y+L.priceY-22, ca*0.09);

    var px = r.x+r.w-18, py = r.y+L.priceY;
    if(it.kind === 'boost'){
      if(own)       text('ACTIVE', px, py, 12, C.scrap, 'right', 900, a, 3);
      else if(lock) text('LOCKED', px, py, 12, 'rgba(234,242,255,0.32)', 'right', 800, a, 3);
      else          text(PURCHASE.priceLabel(it), px, py, 12, afford?C.scrap:'rgba(234,242,255,0.32)', 'right', 800, a, 2.5);
    }
    else if(eq)  text('EQUIPPED', px, py, 12, C.player, 'right', 900, a, 3);
    else if(own) text('EQUIP', px, py, 12, hov?C.text:C.dim, 'right', 800, a, 3);
    else         text(PURCHASE.priceLabel(it), px, py, 12, afford?C.scrap:'rgba(234,242,255,0.32)', 'right', 800, a, 2.5);
  }

  if(G.shopMsgT > 0){
    text(G.shopMsg, VW/2, L.launch.y-22, 12, '#ff5f7a', 'center', 800,
         clamp(G.shopMsgT*2,0,1)*a, 3);
  }

  drawMetaButtons(L, 'CORES');
  drawBtn(BTN_MUTE, (A.muted||A.forced)?'muted':'sound');
  ctx.globalAlpha = 1;
}
"""),

# ---- game over: a third button, because a shop nobody finds sells nothing ----
("""function overBtns(){
  var y = overY() + 410;
  return {
    play:  {x:VW/2-196, y:y, w:250, h:54},
    cores: {x:VW/2+66,  y:y, w:130, h:54}
  };
}""",
"""function overBtns(){
  var y = overY() + 410;
  return {
    play:  {x:VW/2-206, y:y, w:210, h:54},
    cores: {x:VW/2+14,  y:y, w:88,  h:54},
    shop:  {x:VW/2+112, y:y, w:94,  h:54}
  };
}"""),
("""  var hovC = IN.has && inRect(IN.x,IN.y,b.cores);
  ctx.fillStyle = hovC ? hexA(C.scrap,0.16) : 'rgba(255,255,255,0.05)';
  roundRect(b.cores.x,b.cores.y,b.cores.w,b.cores.h,14); ctx.fill();
  ctx.strokeStyle = hovC ? C.scrap : 'rgba(234,242,255,0.26)'; ctx.lineWidth=2;
  roundRect(b.cores.x,b.cores.y,b.cores.w,b.cores.h,14); ctx.stroke();
  text('CORES', b.cores.x+b.cores.w/2, b.cores.y+28, 15, hovC?C.scrap:C.text, 'center', 800, 1, 2.5);""",
"""  var hovC = IN.has && inRect(IN.x,IN.y,b.cores);
  ctx.fillStyle = hovC ? hexA(C.scrap,0.16) : 'rgba(255,255,255,0.05)';
  roundRect(b.cores.x,b.cores.y,b.cores.w,b.cores.h,14); ctx.fill();
  ctx.strokeStyle = hovC ? C.scrap : 'rgba(234,242,255,0.26)'; ctx.lineWidth=2;
  roundRect(b.cores.x,b.cores.y,b.cores.w,b.cores.h,14); ctx.stroke();
  text('CORES', b.cores.x+b.cores.w/2, b.cores.y+28, 14, hovC?C.scrap:C.text, 'center', 800, 1, 1.5);

  var hovS = IN.has && inRect(IN.x,IN.y,b.shop);
  ctx.fillStyle = hovS ? hexA(C.scrap,0.16) : 'rgba(255,255,255,0.05)';
  roundRect(b.shop.x,b.shop.y,b.shop.w,b.shop.h,14); ctx.fill();
  ctx.strokeStyle = hovS ? C.scrap : 'rgba(234,242,255,0.26)'; ctx.lineWidth=2;
  roundRect(b.shop.x,b.shop.y,b.shop.w,b.shop.h,14); ctx.stroke();
  text('SHOP', b.shop.x+b.shop.w/2, b.shop.y+28, 14, hovS?C.scrap:C.text, 'center', 800, 1, 1.5);"""),

# ---- and say so when the amplifier is what paid ----
("""  text(getFlux()+' BANKED', VW/2, by+392, 11, C.dim, 'center', 700, 0.7, 4);""",
"""  var mul = fluxMul();
  var banked = getFlux()+' BANKED';
  if(mul > 1) banked += '   \\u00b7   AMPLIFIER x'+mul.toFixed(2);
  text(banked, VW/2, by+392, 11, C.dim, 'center', 700, 0.7, 4);"""),

# ---- banner: the shop is a shop, which the ad rules allow ----
("""  bandTop:function(){ return (G.mode === 'cores') ? 600 : 582; },""",
"""  bandTop:function(){ return (G.mode === 'cores' || G.mode === 'shop') ? 600 : 582; },"""),
("""  var want = (G.mode === 'over' || G.mode === 'cores') && !G.adBusy;""",
"""  var want = (G.mode === 'over' || G.mode === 'cores' || G.mode === 'shop') && !G.adBusy;"""),

# ---- clicks ----
("""  if(G.mode==='over'){
    var ob = overBtns();
    if(inRect(x,y,ob.cores)){ openCores(); IN.swallow=true; return; }""",
"""  if(G.mode==='over'){
    var ob = overBtns();
    if(inRect(x,y,ob.cores)){ openCores(); IN.swallow=true; return; }
    if(inRect(x,y,ob.shop)){  openShop();  IN.swallow=true; return; }"""),
("""  if(G.mode==='cores'){
    if(inRect(x,y,launchRect())){ restart(); IN.swallow=true; return; }""",
"""  if(G.mode==='shop'){
    var SL = shopLayout();
    if(inRect(x,y,SL.launch)){ restart();   IN.swallow=true; return; }
    if(inRect(x,y,SL.alt)){    openCores(); IN.swallow=true; return; }
    for(var si=0; si<SHOP.length; si++){
      if(!inRect(x,y,shopCardRect(si))) continue;
      var si2 = SHOP[si];
      if(!ownsItem(si2.id)) tryBuy(si2);
      else if(si2.kind !== 'boost' && si2.id !== equippedTrail() && si2.id !== equippedArena()){
        equipItem(si2.id); A.sUi();
      }
      IN.swallow=true;
      return;
    }
    return;
  }
  if(G.mode==='cores'){
    if(inRect(x,y,coresLayout().alt)){ openShop(); IN.swallow=true; return; }
    if(inRect(x,y,launchRect())){ restart(); IN.swallow=true; return; }"""),

# ---- let the purchase message age out ----
("""  if(G.mode==='over') G.overT = (G.overT||0) + rdt;""",
"""  if(G.mode==='over') G.overT = (G.overT||0) + rdt;
  if(G.shopMsgT > 0) G.shopMsgT -= rdt;""")])

print('shop wired: catalogue, purchase rail, screen, wakes, arenas')
