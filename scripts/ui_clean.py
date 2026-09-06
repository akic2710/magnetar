import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        assert s.count(old) == 1, '%s: ambiguous -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


# ------------------------------------------------------------------ p3
# The screen-wide flashes are presentation, not simulation. Decaying them
# inside update() meant they froze the moment the sim stopped.
patch('src/p3.txt', [(
"""  G.shake = Math.max(0, G.shake - G.shake*7*dt - 12*dt);
  G.flash = Math.max(0, G.flash - dt*2.4);
  G.pulse = Math.max(0, G.pulse - dt*2.2);
  G.chroma = Math.max(0, G.chroma - dt*1.4);
  G.dmgFlash = Math.max(0, G.dmgFlash - dt*1.8);
  G.waveBanner = Math.max(0, G.waveBanner - dt);""",
"""  G.shake = Math.max(0, G.shake - G.shake*7*dt - 12*dt);
  G.pulse = Math.max(0, G.pulse - dt*2.2);
  /* flash, dmgFlash and chroma decay in frame() instead - see the note there. */
  G.waveBanner = Math.max(0, G.waveBanner - dt);""")])


# ------------------------------------------------------------------ p4
# A full bar says nothing. Only draw one once it has something to report.
patch('src/p4.txt', [])

patch('src/p5.txt', [

# ---- 1. decay the screen flashes on real time, so they cannot freeze ----
("""  if(!G.adBusy) A.tick();
  G.uiT += rdt;""",
 """  if(!G.adBusy) A.tick();
  G.uiT += rdt;

  /* These three are presentation, not simulation, so they tick on real time.
     Decayed inside update() they froze whenever the sim stopped - and since
     you almost always take a hit in the moments before dying, the red damage
     flash stayed painted at full strength over the death screen and every
     menu reached from it. */
  G.flash    = Math.max(0, G.flash    - rdt*2.4);
  G.dmgFlash = Math.max(0, G.dmgFlash - rdt*1.8);
  G.chroma   = Math.max(0, G.chroma   - rdt*1.4);"""),

# ---- 2. and never paint an arena flash over a menu ----
("""  if(G.flash>0.001){
    ctx.globalCompositeOperation='lighter';
    ctx.fillStyle='rgba(180,220,255,'+(G.flash*0.30)+')';
    ctx.fillRect(0,0,VW,VH);
    ctx.globalCompositeOperation='source-over';
  }
  if(G.dmgFlash>0.001){""",
 """  /* Belt and braces: even mid-fade, these belong to the arena and not to a
     screen you are reading. */
  var arenaFx = (G.mode==='play' || G.mode==='intro' || G.mode==='dying');
  if(arenaFx && G.flash>0.001){
    ctx.globalCompositeOperation='lighter';
    ctx.fillStyle='rgba(180,220,255,'+(G.flash*0.30)+')';
    ctx.fillRect(0,0,VW,VH);
    ctx.globalCompositeOperation='source-over';
  }
  if(arenaFx && G.dmgFlash>0.001){"""),

# ---- 3. the HUD is for playing ----
("""  // Both meta screens are full screens of their own, and the HUD would ghost
  // through the 0.94 backdrop they draw over it.
  if(G.mode!=='cores' && G.mode!=='shop') drawHUD();""",
 """  /* The HUD belongs to the arena. On a decision screen it only repeats in a
     ghost layer what the panel already says - wave, score, level - and offers
     a pause button that does nothing there. The meta screens are full screens
     of their own and would ghost through their backdrop as well. */
  var showHUD = (G.mode==='play' || G.mode==='intro' ||
                 G.mode==='dying' || G.mode==='revive');
  if(showHUD) drawHUD();"""),

# ---- ...so the two screens that lose it keep the one control worth having ----
("""  text(IN.isTouch?'Tap a card':'Click a card, or press 1 / 2 / 3',
       VW/2, 616, 14, C.dim, 'center', 600, a*0.75, 1.5);
}""",
 """  text(IN.isTouch?'Tap a card':'Click a card, or press 1 / 2 / 3',
       VW/2, 616, 14, C.dim, 'center', 600, a*0.75, 1.5);
  // Pause means nothing here, so only the mute button comes along.
  drawBtn(BTN_MUTE, (A.muted||A.forced)?'muted':'sound');
}"""),
("""  text(hint, VW/2, by+bh-26, 12, C.dim, 'center', 600, 0.55*a, 1.5);
  ctx.globalAlpha = 1;
}""",
 """  text(hint, VW/2, by+bh-26, 12, C.dim, 'center', 600, 0.55*a, 1.5);
  drawBtn(BTN_MUTE, (A.muted||A.forced)?'muted':'sound');
  ctx.globalAlpha = 1;
}"""),

# ---- 4. card text should not compete with the field drifting behind it ----
("""  ctx.fillStyle='rgba(3,5,14,'+(0.82*a)+')';
  ctx.fillRect(0,0,VW,VH);

  var hi = RARITY[G.bestRarity||0];""",
 """  // Deep enough that the slowed field reads as texture rather than as
  // something moving across the words you are trying to compare.
  ctx.fillStyle='rgba(3,5,14,'+(0.90*a)+')';
  ctx.fillRect(0,0,VW,VH);

  var hi = RARITY[G.bestRarity||0];"""),

# ---- 5. a full health bar carries no information ----
("""    if(e.maxHp>2 && e.type!=='boss'){""",
 """    // Only once it has something to say: a full bar is six pixels of noise
    // repeated across every tough enemy on screen.
    if(e.maxHp>2 && e.type!=='boss' && e.hp < e.maxHp){""")])

print('UI pass: flash never freezes, HUD off the decision screens, '
      'deeper level-up backdrop, health bars only when damaged')
