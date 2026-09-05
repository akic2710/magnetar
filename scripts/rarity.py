import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


# ------------------------------------------------------------------ p2
old_upgrades = """var UPGRADES = [
  {id:'range',  name:'MAGNET FIELD',    desc:'Pull radius +45',                 max:6, ap:function(){ P.magR+=45; }},
  {id:'cap',    name:'ORBIT SLOTS',     desc:'Hold +2 more objects',            max:5, ap:function(){ P.cap+=2; }},
  {id:'speed',  name:'THRUSTERS',       desc:'Move speed +13%',                 max:5, ap:function(){ P.spd*=1.13; }},
  {id:'over',   name:'OVERCHARGE',      desc:'Blast +22% speed, pierce +1',     max:3, ap:function(){ P.blastSpd*=1.22; P.pierce+=1; }},
  {id:'heavy',  name:'HEAVY SLUGS',     desc:'Blasted objects +1 damage',       max:2, ap:function(){ P.dmg+=1; }},
  {id:'repulse',name:'REPULSE WAVE',    desc:'Blast releases a shockwave',      max:3, ap:function(){ P.repulse+=1; }},
  {id:'hull',   name:'REINFORCED HULL', desc:'+1 max life, heal 1',             max:3, ap:function(){ P.maxHp++; P.hp=Math.min(P.maxHp,P.hp+1); }},
  {id:'siphon', name:'SIPHON',          desc:'Restores 1 life once per wave',   max:2, ap:function(){ P.siphon+=1; }},
  {id:'spin',   name:'SPIN CYCLE',      desc:'Orbit spins faster and grinds',   max:4, ap:function(){ P.omega+=0.55; P.orbR+=5; P.orbDmg+=1; }},
  {id:'ric',    name:'RICOCHET',        desc:'Blasted objects bounce off walls',max:2, ap:function(){ P.bounce+=1; }},
  {id:'scav',   name:'SCAVENGER',       desc:'Faster pull, denser scrap field', max:4, ap:function(){ P.pullMul*=1.32; G.scrapCap+=10; }},
  {id:'static', name:'STATIC CHARGE',   desc:'Orbit arcs lightning at enemies', max:3, ap:function(){ P.stat+=1; }}
];"""

new_upgrades = """/* ------------------------------- rarity -------------------------------- */
/* Three tiers. `w` is the draw weight for one upgrade of that tier, so the
   pool composition matters less than the tier: commons come up constantly,
   epics are the cards you build a run around. Rarity only means anything if
   the rare things are actually stronger, so the epics below are the
   behaviour-changing upgrades, not just bigger numbers. */
var RARITY = [
  { name:'COMMON', w:62, col:'#b9c7de', glow:0.12 },
  { name:'RARE',   w:28, col:'#5ad2ff', glow:0.20 },
  { name:'EPIC',   w:10, col:'#c88bff', glow:0.32 }
];
var COMMON = 0, RARE = 1, EPIC = 2;

/* `sides` gives each upgrade a stable icon shape - previously the polygon came
   from the card slot, so the same upgrade looked different every level. */
var UPGRADES = [
  {id:'range',  r:COMMON, sides:6, name:'MAGNET FIELD',    desc:'Pull radius +45',                 max:6, ap:function(){ P.magR+=45; }},
  {id:'cap',    r:COMMON, sides:8, name:'ORBIT SLOTS',     desc:'Hold +2 more objects',            max:5, ap:function(){ P.cap+=2; }},
  {id:'speed',  r:COMMON, sides:3, name:'THRUSTERS',       desc:'Move speed +13%',                 max:5, ap:function(){ P.spd*=1.13; }},
  {id:'scav',   r:COMMON, sides:7, name:'SCAVENGER',       desc:'Faster pull, denser scrap field', max:4, ap:function(){ P.pullMul*=1.32; G.scrapCap+=10; }},
  {id:'hull',   r:COMMON, sides:5, name:'REINFORCED HULL', desc:'+1 max life, heal 1',             max:3, ap:function(){ P.maxHp++; P.hp=Math.min(P.maxHp,P.hp+1); }},

  {id:'over',   r:RARE,   sides:4, name:'OVERCHARGE',      desc:'Blast +22% speed, pierce +1',     max:3, ap:function(){ P.blastSpd*=1.22; P.pierce+=1; }},
  {id:'spin',   r:RARE,   sides:8, name:'SPIN CYCLE',      desc:'Orbit spins faster and grinds',   max:4, ap:function(){ P.omega+=0.55; P.orbR+=5; P.orbDmg+=1; }},
  {id:'heavy',  r:RARE,   sides:6, name:'HEAVY SLUGS',     desc:'Blasted objects +1 damage',       max:2, ap:function(){ P.dmg+=1; }},
  {id:'siphon', r:RARE,   sides:5, name:'SIPHON',          desc:'Restores 1 life once per wave',   max:2, ap:function(){ P.siphon+=1; }},

  {id:'repulse',r:EPIC,   sides:7, name:'REPULSE WAVE',    desc:'Every blast releases a shockwave',max:3, ap:function(){ P.repulse+=1; }},
  {id:'static', r:EPIC,   sides:3, name:'STATIC CHARGE',   desc:'Orbit arcs lightning, harder each stack', max:3, ap:function(){ P.stat+=1; }},
  {id:'ric',    r:EPIC,   sides:4, name:'RICOCHET',        desc:'Blasted objects bounce off walls twice',  max:2, ap:function(){ P.bounce+=2; }}
];"""
patch('src/p2.txt', [(old_upgrades, new_upgrades)])


# ------------------------------------------------------------------ p1  (audio)
patch('src/p1.txt', [(
"""  sLevel:function(){ var n=[523,659,784,1046]; for(var i=0;i<4;i++) this.tone(n[i],0.30,'triangle',0.17,null,i*0.075); },""",
"""  sLevel:function(){ var n=[523,659,784,1046]; for(var i=0;i<4;i++) this.tone(n[i],0.30,'triangle',0.17,null,i*0.075); },
  /* A distinct sting when an epic is in the hand - you should hear it before
     you have finished reading the cards. */
  sEpic:function(){
    var n=[523,659,784,1046,1318];
    for(var i=0;i<5;i++) this.tone(n[i],0.42,'triangle',0.17,null,i*0.07);
    this.tone(196,0.80,'sawtooth',0.11,98,0.02);
    this.tone(1568,0.60,'sine',0.09,null,0.30);
  },""")])


# ------------------------------------------------------------------ p3  (draw)
patch('src/p3.txt', [(
"""function openLevelUp(){
  var avail = [];
  for(var i=0;i<UPGRADES.length;i++){
    var u = UPGRADES[i];
    var taken = G.taken && G.taken[u.id] || 0;
    if(taken < u.max) avail.push(u);
  }
  if(!avail.length) return;
  var picked = [];
  for(var k=0;k<3 && avail.length;k++){
    var idx = Math.floor(Math.random()*avail.length);
    picked.push(avail[idx]);
    avail.splice(idx,1);
  }
  G.cards = picked;
  G.mode = 'levelup';
  G.cardT = 0;
  A.sLevel();
  G.flash = 0.35;
}""",
"""/* Weighted draw without replacement: each slot is rolled against the weights
   of whatever is still in the pool, so a hand can hold at most one of a given
   upgrade and epics stay scarce even when few cards remain unmaxed. */
function openLevelUp(){
  var pool = [], i;
  for(i=0;i<UPGRADES.length;i++){
    var u = UPGRADES[i];
    if(((G.taken && G.taken[u.id]) || 0) < u.max) pool.push(u);
  }
  if(!pool.length) return;

  var picked = [], best = 0;
  while(picked.length < 3 && pool.length){
    var total = 0, j;
    for(j=0;j<pool.length;j++) total += RARITY[pool[j].r].w;
    var roll = Math.random()*total, chosen = pool.length-1;
    for(j=0;j<pool.length;j++){
      roll -= RARITY[pool[j].r].w;
      if(roll <= 0){ chosen = j; break; }
    }
    if(pool[chosen].r > best) best = pool[chosen].r;
    picked.push(pool[chosen]);
    pool.splice(chosen,1);
  }

  G.cards = picked;
  G.bestRarity = best;
  G.mode = 'levelup';
  G.cardT = 0;
  if(best >= EPIC) A.sEpic(); else A.sLevel();
  G.flash = 0.35 + best*0.12;
}"""),
(
"""  ring(P.x,P.y,150,'rgba(255,215,106,0.7)',0.55,4);
  popText(P.x, P.y-40, u.name, C.scrap, 24);""",
"""  var rc = RARITY[u.r].col;
  ring(P.x,P.y,150,hexA(rc,0.7),0.55,4);
  popText(P.x, P.y-40, u.name, rc, 24);"""),
(
"""        damageEnemy(best, 1, 0, 0);""",
"""        damageEnemy(best, P.stat+1, 0, 0);   // epic: scales with stacks""")])


# ------------------------------------------------------------------ p5  (cards)
patch('src/p5.txt', [(
"""    ctx.fillStyle = hov?'rgba(124,243,255,0.13)':'rgba(255,255,255,0.045)';
    roundRect(r.x, r.y-lift, r.w, r.h, 16); ctx.fill();
    ctx.strokeStyle = hov?'rgba(124,243,255,0.9)':'rgba(234,242,255,0.20)';
    ctx.lineWidth = hov?3:1.5;
    roundRect(r.x, r.y-lift, r.w, r.h, 16); ctx.stroke();

    // icon
    var cx = r.x+r.w/2, cy = r.y-lift+112;
    ctx.globalCompositeOperation='lighter';
    blob(cx,cy,74,'rgba(124,243,255,0.16)');
    ctx.globalCompositeOperation='source-over';
    ctx.strokeStyle = C.player; ctx.lineWidth=3;
    poly(cx,cy,30, 3+(i%4), G.uiT*(0.8+i*0.3)); ctx.stroke();
    ctx.fillStyle = C.player; ctx.globalAlpha = ca*0.9;
    ctx.beginPath(); ctx.arc(cx,cy,8,0,TAU); ctx.fill();
    ctx.globalAlpha = ca;

    var taken = (G.taken&&G.taken[u.id])||0;
    text(u.name, cx, r.y-lift+206, 21, C.text, 'center', 900, ca, 1.5);
    wrapText(u.desc, cx, r.y-lift+244, 15, C.dim, 246, 20);

    // stack pips
    for(var p=0;p<u.max;p++){
      var px = cx - (u.max-1)*7 + p*14;
      ctx.fillStyle = p<taken ? C.scrap : 'rgba(234,242,255,0.20)';
      ctx.beginPath(); ctx.arc(px, r.y-lift+r.h-40, 4, 0, TAU); ctx.fill();
    }
    text(String(i+1), r.x+22, r.y-lift+26, 14, C.dim, 'left', 700, ca*0.8, 1);
    ctx.globalAlpha = 1;""",
"""    var rar = RARITY[u.r];

    // Epics carry a soft outer bloom so the good card reads across the room.
    if(u.r >= EPIC){
      var puls = 0.5 + 0.5*Math.sin(G.uiT*2.6 + i);
      ctx.globalAlpha = ca*(0.10 + 0.12*puls);
      ctx.strokeStyle = rar.col; ctx.lineWidth = 11;
      roundRect(r.x-3, r.y-lift-3, r.w+6, r.h+6, 19); ctx.stroke();
      ctx.globalAlpha = ca;
    }

    ctx.fillStyle = hov ? hexA(rar.col,0.16) : 'rgba(255,255,255,0.045)';
    roundRect(r.x, r.y-lift, r.w, r.h, 16); ctx.fill();
    ctx.strokeStyle = hov ? rar.col : hexA(rar.col, u.r?0.55:0.32);
    ctx.lineWidth = hov?3:(u.r?2:1.5);
    roundRect(r.x, r.y-lift, r.w, r.h, 16); ctx.stroke();

    // icon
    var cx = r.x+r.w/2, cy = r.y-lift+112;
    ctx.globalCompositeOperation='lighter';
    blob(cx,cy,74, hexA(rar.col, rar.glow));
    ctx.globalCompositeOperation='source-over';
    ctx.strokeStyle = rar.col; ctx.lineWidth=3;
    poly(cx,cy,30, u.sides, G.uiT*(0.8+i*0.3)); ctx.stroke();
    ctx.fillStyle = rar.col; ctx.globalAlpha = ca*0.9;
    ctx.beginPath(); ctx.arc(cx,cy,8,0,TAU); ctx.fill();
    ctx.globalAlpha = ca;

    var taken = (G.taken&&G.taken[u.id])||0;
    text(u.name, cx, r.y-lift+206, 21, C.text, 'center', 900, ca, 1.5);
    wrapText(u.desc, cx, r.y-lift+244, 15, C.dim, 246, 20);

    // stack pips
    for(var p=0;p<u.max;p++){
      var px = cx - (u.max-1)*7 + p*14;
      ctx.fillStyle = p<taken ? rar.col : 'rgba(234,242,255,0.20)';
      ctx.beginPath(); ctx.arc(px, r.y-lift+r.h-40, 4, 0, TAU); ctx.fill();
    }
    text(String(i+1), r.x+22, r.y-lift+26, 14, C.dim, 'left', 700, ca*0.8, 1);
    text(rar.name, r.x+r.w-22, r.y-lift+26, 10, rar.col, 'right', 800, ca*0.95, 3);
    ctx.globalAlpha = 1;"""),
(
"""  text('LEVEL '+G.level, VW/2, 106, 18, C.scrap, 'center', 800, a, 5);""",
"""  var hi = RARITY[G.bestRarity||0];
  text('LEVEL '+G.level, VW/2, 106, 18, (G.bestRarity>=EPIC)?hi.col:C.scrap, 'center', 800, a, 5);""")])

print('rarity system wired')
