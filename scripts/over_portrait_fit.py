import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def patch(path, pairs):
    s = io.open(path, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
    for old, new in pairs:
        assert old in s, '%s: not found -> %r' % (path, old[:70])
        assert s.count(old) == 1, '%s: ambiguous -> %r' % (path, old[:70])
        s = s.replace(old, new, 1)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(s)


patch('src/p5.txt', [(
"""  var titleSize = fit(cssW * 0.075, 22, 38);
  var scoreSize = fit(cssW * 0.160, 44, 72);
  var statSize  = fit(cssW * 0.065, 18, 28);
  var fluxSize  = fit(cssW * 0.070, 20, 30);
  var small     = fit(cssW * 0.029, 10, 13);

  var top = m + Math.round(cssH * 0.02);
  var bot = row1Y - Math.round(cssH * 0.02);
  var block = titleSize + scoreSize + statSize + fluxSize + 4*small + 108;
  var y = top + Math.max(0, (bot - top - block) / 2);

  var titleY = y + titleSize*0.5;   y += titleSize + 8;
  var rankY  = y + small*0.5;       y += small + 20;
  var scoreY = y + scoreSize*0.5;   y += scoreSize + 6;
  var scoreLabelY = y + small*0.5;  y += small + 16;
  var hr1Y = y;                     y += 16;
  var statY = y + statSize*0.5;     y += statSize + 4;
  var statLabelY = y + small*0.5;   y += small + 16;
  var hr2Y = y;                     y += 16;
  var fluxY = y + fluxSize*0.5;     y += fluxSize + 6;
  var bankY = y + small*0.5;""",
"""  var small = fit(cssW * 0.029, 10, 13);
  var T0 = fit(cssW * 0.075, 22, 38);
  var S0 = fit(cssW * 0.160, 44, 72);
  var C0 = fit(cssW * 0.065, 18, 28);
  var F0 = fit(cssW * 0.070, 20, 30);

  var top = m + Math.round(cssH * 0.02);
  var bot = row1Y - Math.round(cssH * 0.02);
  var span = bot - top;

  /* Sized from the width, but stacked down the screen - so on a short viewport
     the column has to come down or it runs into the buttons. A 360x400 frame
     overflowed by 31px. Shrink the display type and the gaps together, keeping
     the small labels at their floor, until the block fits; real phones are
     nowhere near this and land on s = 1 unchanged. */
  var GAPS = [8, 20, 6, 16, 16, 4, 16, 16, 6];
  var s = 1, titleSize, scoreSize, statSize, fluxSize, gaps, block, i;
  for(i = 0; i < 14; i++){
    var gs = Math.max(0.55, s);
    titleSize = Math.max(18, Math.round(T0*s));
    scoreSize = Math.max(32, Math.round(S0*s));
    statSize  = Math.max(15, Math.round(C0*s));
    fluxSize  = Math.max(16, Math.round(F0*s));
    gaps = [];
    block = titleSize + scoreSize + statSize + fluxSize + 4*small;
    for(var k=0;k<GAPS.length;k++){ gaps[k] = Math.round(GAPS[k]*gs); block += gaps[k]; }
    if(block <= span || s <= 0.55) break;
    s -= 0.04;
  }

  var y = top + Math.max(0, (span - block) / 2);
  var titleY = y + titleSize*0.5;   y += titleSize + gaps[0];
  var rankY  = y + small*0.5;       y += small + gaps[1];
  var scoreY = y + scoreSize*0.5;   y += scoreSize + gaps[2];
  var scoreLabelY = y + small*0.5;  y += small + gaps[3];
  var hr1Y = y;                     y += gaps[4];
  var statY = y + statSize*0.5;     y += statSize + gaps[5];
  var statLabelY = y + small*0.5;   y += small + gaps[6];
  var hr2Y = y;                     y += gaps[7];
  var fluxY = y + fluxSize*0.5;     y += fluxSize + gaps[8];
  var bankY = y + small*0.5;""")])

print('portrait game over: block shrinks to fit short viewports')
