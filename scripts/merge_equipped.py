import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        assert s.count(old) == 1, '%s: ambiguous -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


patch('src/p2.txt', [(
"""  var core = cloud['mgn.core'];
  if(!core || owned.indexOf(core) < 0) core = local['mgn.core'];
  if(!core || owned.indexOf(core) < 0) core = 'prospector';

  var sids = {}, shop = [];""",
"""  /* Prefer the cloud's selection, but only where it is an actual selection.
     Every default is permanently "owned", so a device that never picked
     anything still reports one - and letting that win silently undoes a choice
     made somewhere else. Ranking a real choice above a default in both
     directions means a merge can only ever add information. */
  function pickEquipped(cloudV, localV, ok, dflt){
    if(ok(cloudV) && cloudV !== dflt) return cloudV;
    if(ok(localV) && localV !== dflt) return localV;
    if(ok(cloudV)) return cloudV;
    if(ok(localV)) return localV;
    return dflt;
  }
  function ownsCore(v){ return !!v && owned.indexOf(v) >= 0; }
  var core = pickEquipped(cloud['mgn.core'], local['mgn.core'], ownsCore, 'prospector');

  var sids = {}, shop = [];"""),
(
"""  var trail = cloud['mgn.trail'];
  if(!eqOk(trail,'trail')) trail = local['mgn.trail'];
  if(!eqOk(trail,'trail')) trail = 'trail.std';
  var arena = cloud['mgn.arena'];
  if(!eqOk(arena,'arena')) arena = local['mgn.arena'];
  if(!eqOk(arena,'arena')) arena = 'arena.deep';""",
"""  function okTrail(v){ return eqOk(v,'trail'); }
  function okArena(v){ return eqOk(v,'arena'); }
  var trail = pickEquipped(cloud['mgn.trail'], local['mgn.trail'], okTrail, 'trail.std');
  var arena = pickEquipped(cloud['mgn.arena'], local['mgn.arena'], okArena, 'arena.deep');""")])

print('merge now ranks a real selection above a default, for cores too')
