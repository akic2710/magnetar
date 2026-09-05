import io, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
p = 'src/p2.txt'
s = io.open(p, encoding='utf-8').read()

# A player who dies on wave 8 earned 37 Flux under the old formula, which put
# the first unlock five runs away - too far to teach that the meta exists.
# The flat term and heavier wave weight pull the first unlock to run 2-3.
old = ("/* Depth is worth more than score, so a deep careful run beats farming wave 3. */\n"
       "function fluxFor(score, wave){ return Math.floor(score/150) + wave*3; }")
new = ("/* Depth is worth more than score, so a deep careful run beats farming wave 3.\n"
       "   The flat term keeps a short first run from feeling like it paid nothing. */\n"
       "function fluxFor(score, wave){ return 15 + Math.floor(score/150) + wave*4; }")
assert old in s
s = s.replace(old, new)

for old_cost, new_cost in [("name:'WARDEN', cost:200,", "name:'WARDEN', cost:150,"),
                           ("name:'MAW', cost:500,", "name:'MAW', cost:450,")]:
    assert old_cost in s, old_cost
    s = s.replace(old_cost, new_cost)

io.open(p, 'w', encoding='utf-8').write(s)
print('economy tuned: first unlock now ~2-3 runs')
