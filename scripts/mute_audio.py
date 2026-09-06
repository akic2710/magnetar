import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


# ------------------------------------------------------------------ p1
patch('src/p1.txt', [(
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
  },""",
"""  ducked:false, forced:false,
  setMute:function(m){
    this.muted = m; store('mgn.mute', m?'1':'0');
    this.applyGain();
  },
  /* CrazyGames requires the game to be silent for the duration of a video ad.
     Ducking is separate from mute so restoring audio afterwards cannot
     clobber what the player actually chose. */
  duck:function(on){ this.ducked = !!on; this.applyGain(); },
  /* The portal can mute the game itself via SDK.game.settings.muteAudio. The
     docs require that to take priority over in-game audio settings, so it is a
     third independent flag: the player's own mute button cannot lift it. */
  setForcedMute:function(on){ this.forced = !!on; this.applyGain(); },
  silent:function(){ return this.muted || this.ducked || this.forced; },
  applyGain:function(){
    if(!this.master || !this.ctx) return;
    this.master.gain.setTargetAtTime(this.silent()?0:0.5, this.ctx.currentTime, 0.03);
  },"""),
# stop scheduling nodes at all while forced silent
("""  tone:function(f,dur,type,vol,f2,delay,bus){
    if(!this.ctx||this.muted) return;""",
 """  tone:function(f,dur,type,vol,f2,delay,bus){
    if(!this.ctx||this.muted||this.forced) return;"""),
("""  hit:function(dur,vol,freq,q,delay){
    if(!this.ctx||this.muted) return;""",
 """  hit:function(dur,vol,freq,q,delay){
    if(!this.ctx||this.muted||this.forced) return;"""),
("""    this.humGain.gain.setTargetAtTime(this.muted?0:v*0.15, t, 0.06);""",
 """    this.humGain.gain.setTargetAtTime(this.silent()?0:v*0.15, t, 0.06);"""),
("""    if(!this.ctx || this.muted || this.ducked){ this.musT = 0; return; }""",
 """    if(!this.ctx || this.silent()){ this.musT = 0; return; }""")])


# ------------------------------------------------------------------ p5
patch('src/p5.txt', [
# adopt the portal's mute setting, and follow it when it changes
("""    // A revive button that can never fire is a rejection cause, so find out
    // up front whether ads can actually run for this player.""",
 """    /* The portal can mute us at any time. Read it once, then follow changes -
       the player's own mute button deliberately cannot lift this. */
    try{
      if(SDK.game && SDK.game.settings) A.setForcedMute(!!SDK.game.settings.muteAudio);
      if(SDK.game && SDK.game.addSettingsChangeListener){
        SDK.game.addSettingsChangeListener(function(st){
          A.setForcedMute(!!(st && st.muteAudio));
        });
      }
    }catch(e){}

    // A revive button that can never fire is a rejection cause, so find out
    // up front whether ads can actually run for this player."""),
# the HUD icon should tell the truth about why it is silent
("""  drawBtn(BTN_MUTE, A.muted?'muted':'sound');
  drawBtn(BTN_PAUSE, G.paused?'play':'pause');""",
 """  drawBtn(BTN_MUTE, (A.muted||A.forced)?'muted':'sound');
  drawBtn(BTN_PAUSE, G.paused?'play':'pause');"""),
("""  drawBtn(BTN_MUTE, A.muted?'muted':'sound');
  ctx.globalAlpha = 1;
}""",
 """  drawBtn(BTN_MUTE, (A.muted||A.forced)?'muted':'sound');
  ctx.globalAlpha = 1;
}""")])

print('portal muteAudio support wired')
