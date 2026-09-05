import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


# ------------------------------------------------------------------ p2
# The rotate overlay is drawn in CSS pixels so it can cover the letterbox bars,
# not just the playfield, so hit-testing it needs the raw pointer position too.
patch('src/p2.txt', [(
"""var IN = {
  x:VW/2, y:VH/2, down:false, justDown:false, justUp:false, has:false,
  keys:{}, kx:0, ky:0, kMag:false, anyKey:false, clickX:0, clickY:0, clicked:false
};""",
"""var IN = {
  x:VW/2, y:VH/2, down:false, justDown:false, justUp:false, has:false,
  keys:{}, kx:0, ky:0, kMag:false, anyKey:false, clickX:0, clickY:0, clicked:false,
  cssX:0, cssY:0, clickCssX:0, clickCssY:0
};

/* Only prompt on something that can actually be rotated. A desktop window that
   happens to be taller than it is wide should never be told to turn itself. */
var TOUCH_CAPABLE = ('ontouchstart' in window) || ((navigator.maxTouchPoints|0) > 0);
var rotateDismissed = false;"""),
(
"""function onDown(cx,cy){
  var p = toWorld(cx,cy);
  IN.x=p.x; IN.y=p.y; IN.has=true;
  if(!IN.down){ IN.down=true; IN.justDown=true; }
  IN.clickX=p.x; IN.clickY=p.y; IN.clicked=true;
  boot();
}""",
"""function onDown(cx,cy){
  var p = toWorld(cx,cy);
  IN.x=p.x; IN.y=p.y; IN.has=true;
  IN.cssX=cx; IN.cssY=cy; IN.clickCssX=cx; IN.clickCssY=cy;
  if(!IN.down){ IN.down=true; IN.justDown=true; }
  IN.clickX=p.x; IN.clickY=p.y; IN.clicked=true;
  boot();
}"""),
(
"""function onMove(cx,cy){
  var p=toWorld(cx,cy); IN.x=p.x; IN.y=p.y;""",
"""function onMove(cx,cy){
  var p=toWorld(cx,cy); IN.x=p.x; IN.y=p.y;
  IN.cssX=cx; IN.cssY=cy;""")])


# ------------------------------------------------------------------ p5
patch('src/p5.txt', [

# ---- state + geometry, in CSS pixels ----
("""/* ------------------------------- banner -------------------------------- */""",
 """/* ---------------------------- rotate prompt ---------------------------- */
/* The arena is a fixed 16:9 field scaled to fit, so a portrait phone gets a
   letterboxed strip about a third of the screen tall. Ask for landscape - but
   never trap anyone: orientation can be locked at the OS level, so the prompt
   is always dismissable and the run continues underneath. */
function needsRotate(){
  if(!TOUCH_CAPABLE || rotateDismissed || G.adBusy) return false;
  return cssH > cssW * 1.05;          // margin stops it flapping near square
}

function rotateBtn(){
  var u = Math.min(cssW, cssH) / 100;
  var w = Math.min(cssW * 0.62, 60*u), h = Math.max(38, 13*u);
  return { x:(cssW-w)/2, y:cssH/2 + 30*u, w:w, h:h };
}

function drawRotate(){
  var w = cssW, h = cssH, u = Math.min(w, h) / 100;
  ctx.fillStyle = 'rgba(3,5,14,0.94)';
  ctx.fillRect(0, 0, w, h);

  var cx = w/2, cy = h/2 - 14*u;

  // phone turning from portrait to landscape, on a loop
  var t = (G.uiT * 0.5) % 1;
  var e = t < 0.45 ? 0 : (t < 0.7 ? (t-0.45)/0.25 : 1);
  e = e*e*(3-2*e);                                   // smoothstep
  var ang = -Math.PI/2 * e;
  var pw = 15*u, ph = 26*u;

  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(ang);
  ctx.fillStyle = hexA(C.player, 0.10);
  roundRect(-pw, -ph, pw*2, ph*2, 3.2*u); ctx.fill();
  ctx.strokeStyle = C.player; ctx.lineWidth = Math.max(2, 0.7*u);
  roundRect(-pw, -ph, pw*2, ph*2, 3.2*u); ctx.stroke();
  ctx.strokeStyle = hexA(C.player, 0.30); ctx.lineWidth = Math.max(1, 0.35*u);
  roundRect(-pw*0.74, -ph*0.80, pw*1.48, ph*1.60, 1.4*u); ctx.stroke();
  ctx.restore();

  // arc arrow sweeping the same quarter turn
  var r = ph * 1.5;
  ctx.strokeStyle = hexA(C.scrap, 0.85);
  ctx.lineWidth = Math.max(2, 0.6*u);
  ctx.beginPath(); ctx.arc(cx, cy, r, -Math.PI*0.92, -Math.PI*0.30); ctx.stroke();
  var ah = -Math.PI*0.30, ax = cx + Math.cos(ah)*r, ay = cy + Math.sin(ah)*r;
  ctx.fillStyle = C.scrap;
  ctx.save(); ctx.translate(ax, ay); ctx.rotate(ah + Math.PI/2);
  ctx.beginPath();
  ctx.moveTo(0, 2.2*u); ctx.lineTo(-1.9*u, -1.6*u); ctx.lineTo(1.9*u, -1.6*u);
  ctx.closePath(); ctx.fill();
  ctx.restore();

  text('ROTATE YOUR DEVICE', cx, cy + 46*u, Math.max(15, 5.2*u), C.text, 'center', 900, 1, 0.22*u);
  text('Magnetar is built for landscape', cx, cy + 56*u, Math.max(11, 2.9*u), C.dim, 'center', 600, 0.8, 0.05*u);

  var b = rotateBtn();
  ctx.fillStyle = 'rgba(255,255,255,0.05)';
  roundRect(b.x, b.y, b.w, b.h, b.h*0.28); ctx.fill();
  ctx.strokeStyle = 'rgba(234,242,255,0.30)'; ctx.lineWidth = 2;
  roundRect(b.x, b.y, b.w, b.h, b.h*0.28); ctx.stroke();
  text('Play anyway', b.x + b.w/2, b.y + b.h/2, Math.max(12, 3.4*u), C.dim, 'center', 700, 0.85, 0.5);
}

/* ------------------------------- banner -------------------------------- */"""),

# ---- draw it in CSS space, outside the letterboxed clip ----
("""  if(G.dmgFlash>0.001){
    // Kept off the centre of the screen: the moment you take a hit is the
    // moment you most need to see what is coming next.
    var gr = ctx.createRadialGradient(VW/2,VH/2,VH*0.42, VW/2,VH/2,VH*0.88);
    gr.addColorStop(0,'rgba(255,40,70,0)');
    gr.addColorStop(1,'rgba(255,40,70,'+(G.dmgFlash*0.48)+')');
    ctx.fillStyle=gr; ctx.fillRect(0,0,VW,VH);
  }
  ctx.restore();
}""",
"""  if(G.dmgFlash>0.001){
    // Kept off the centre of the screen: the moment you take a hit is the
    // moment you most need to see what is coming next.
    var gr = ctx.createRadialGradient(VW/2,VH/2,VH*0.42, VW/2,VH/2,VH*0.88);
    gr.addColorStop(0,'rgba(255,40,70,0)');
    gr.addColorStop(1,'rgba(255,40,70,'+(G.dmgFlash*0.48)+')');
    ctx.fillStyle=gr; ctx.fillRect(0,0,VW,VH);
  }
  ctx.restore();

  /* Drawn last and in CSS pixels rather than virtual ones, so it covers the
     letterbox bars too - in portrait the playfield is only a third of the
     screen, and a prompt confined to it would be the size of the problem. */
  if(needsRotate()){
    ctx.setTransform(dpr,0,0,dpr,0,0);
    drawRotate();
  }
}"""),

# ---- gate the sim, and tell the SDK gameplay paused ----
("""  var sim = (G.mode==='play' || G.mode==='intro' || G.mode==='levelup' || G.mode==='dying');
  if(G.paused || G.adBusy) sim = false;""",
 """  // Rotating back to landscape offers the prompt again on a later flip.
  if(cssW >= cssH) rotateDismissed = false;
  var rot = needsRotate();
  if(rot !== window.__rotWas){
    window.__rotWas = rot;
    if(window.CG){
      if(rot) window.CG.gameplayStop();
      else if(G.mode==='play' || G.mode==='intro') window.CG.gameplayStart();
    }
  }

  var sim = (G.mode==='play' || G.mode==='intro' || G.mode==='levelup' || G.mode==='dying');
  if(G.paused || G.adBusy || rot) sim = false;"""),

# ---- input: only the dismiss button responds while it is up ----
("""  var x = IN.clickX, y = IN.clickY;
  IN.clicked = false;
  if(G.adBusy){ IN.swallow = true; return; }   // the overlay blocks everything
""",
 """  var x = IN.clickX, y = IN.clickY;
  IN.clicked = false;
  if(G.adBusy){ IN.swallow = true; return; }   // the overlay blocks everything

  if(needsRotate()){
    // Hit-tested in CSS pixels, because that is the space it was drawn in.
    var rb = rotateBtn();
    if(IN.clickCssX >= rb.x && IN.clickCssX <= rb.x+rb.w &&
       IN.clickCssY >= rb.y && IN.clickCssY <= rb.y+rb.h){
      rotateDismissed = true;
    }
    IN.swallow = true;   // never let a tap fall through to the game underneath
    return;
  }
""")])

print('rotate prompt wired')
