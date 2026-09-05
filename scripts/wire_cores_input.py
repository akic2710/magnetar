import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = 'src/p5.txt'
s = io.open(p, encoding='utf-8').read()

old = """  if(G.mode==='over'){
    if((G.overT||0) > 0.55){ restart(); IN.swallow=true; }
    return;
  }"""
new = """  if(G.mode==='over'){
    var ob = overBtns();
    if(inRect(x,y,ob.cores)){ openCores(); IN.swallow=true; return; }
    if((G.overT||0) > 0.55){ restart(); IN.swallow=true; }
    return;
  }
  if(G.mode==='cores'){
    if(inRect(x,y,BTN_LAUNCH)){ restart(); IN.swallow=true; return; }
    for(var ci=0; ci<CORES.length; ci++){
      if(!inRect(x,y,coreCardRect(ci))) continue;
      var c = CORES[ci];
      if(owns(c.id)){
        if(c.id!==selectedCore()){ equipCore(c.id); A.sUi(); }
      } else if(buyCore(c.id)){
        equipCore(c.id);
        A.sLevel();
        G.boughtT = G.uiT;
      } else {
        A.tone(150,0.20,'square',0.09,100);   // not enough Flux
      }
      IN.swallow=true;
      return;
    }
    return;
  }"""
assert old in s, 'game-over UI branch not found'
s = s.replace(old, new)

# The cores screen is reachable from the death screen, never before first play,
# so the "gameplay within one click" rule still holds.
old2 = "function drawCores(){"
new2 = """function openCores(){
  G.mode = 'cores';
  G.coreT = 0;
  A.sUi();
}

function drawCores(){"""
assert old2 in s
s = s.replace(old2, new2, 1)

io.open(p, 'w', encoding='utf-8').write(s)
print('p5: cores input wired')

# ---- keyboard: C opens cores from the death screen, Enter launches ----
p = 'src/p2.txt'
s = io.open(p, encoding='utf-8').read()
old3 = "  if(e.code==='Enter' && G.mode==='over') restart();"
new3 = """  if(e.code==='Enter' && (G.mode==='over' || G.mode==='cores')) restart();
  if(e.code==='KeyC' && G.mode==='over') openCores();"""
assert old3 in s
s = s.replace(old3, new3)
io.open(p, 'w', encoding='utf-8').write(s)
print('p2: cores keyboard shortcuts wired')
