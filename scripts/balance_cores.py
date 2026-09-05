import io, os, re
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = 'src/p2.txt'
s = io.open(p, encoding='utf-8').read()

start = s.index('var CORES = [')
end = s.index('function coreById(id){')

# Cores are SIDEGRADES, not a power ladder. Bot testing had Warden reaching
# wave 44 against Prospector's 17, which meant the cheapest unlock ended the
# meta - you would buy it once and never choose anything else again. Every
# core now pays for its strength somewhere, and cost reflects how far it
# departs from the default rather than how strong it is.
new = '''var CORES = [
  { id:'prospector', name:'PROSPECTOR', cost:0, col:'#7cf3ff', sides:3,
    tag:'The standard core. Balanced, forgiving, nothing to unlearn.',
    stats:['3 lives, 6 slots','Standard pull','Standard blast'],
    ap:function(p){} },

  { id:'warden', name:'WARDEN', cost:150, col:'#6effc0', sides:6,
    tag:'Heavy shell, short reach. Wear your orbit into the swarm like a saw.',
    stats:['4 lives, 4 slots','Orbit grinds x2','Slower, shorter reach'],
    ap:function(p){ p.hp=4; p.maxHp=4; p.orbDmg=2; p.orbR+=8;
                    p.cap=4; p.magR-=35; p.spd*=0.85; p.blastSpd*=0.85; } },

  { id:'maw', name:'MAW', cost:450, col:'#5ab9ff', sides:8,
    tag:'A hungry ring. Swallow half the field before you let go of it.',
    stats:['11 orbit slots','Pull +25%','2 lives, slower'],
    ap:function(p){ p.cap=11; p.pullMul=1.25; p.hp=2; p.maxHp=2;
                    p.spd*=0.88; p.blastSpd*=0.90; } },

  { id:'needle', name:'NEEDLE', cost:900, col:'#b6f0ff', sides:3,
    tag:'Glass and spite. Four slugs that go straight through everything.',
    stats:['2 lives, 4 slots','+1 damage, +1 pierce','Blast +25% speed'],
    ap:function(p){ p.hp=2; p.maxHp=2; p.cap=4; p.dmg+=1; p.pierce+=1;
                    p.blastSpd*=1.25; } },

  { id:'pulsar', name:'PULSAR', cost:1500, col:'#eaf4ff', sides:5,
    tag:'Built to detonate, not to collect. Every release is a shockwave.',
    stats:['Repulse wave','Static charge','2 lives, 5 slots'],
    ap:function(p){ p.repulse=1; p.stat=1; p.cap=5; p.hp=2; p.maxHp=2;
                    p.magR-=20; } },

  { id:'drifter', name:'DRIFTER', cost:1800, col:'#8affe0', sides:4,
    tag:'No drag while pulling. You never have to stop moving again.',
    stats:['Full speed while held','Move speed +25%','2 lives, 5 slots'],
    ap:function(p){ p.holdMul=1.0; p.spd*=1.25; p.hp=2; p.maxHp=2; p.cap=5; } }
];

'''
s = s[:start] + new + s[end:]

assert s.count('var CORES = [') == 1
assert len(re.findall(r"\bid:'", s[start:s.index('function coreById(id){')])) == 6
io.open(p, 'w', encoding='utf-8').write(s)
print('cores rebalanced as sidegrades')
