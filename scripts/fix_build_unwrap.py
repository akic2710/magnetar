import io, os, glob
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Normalise every source part to LF. Python's text-mode write turns '\n' into
# '\r\n' on Windows, which is how the build's newline-sensitive match broke.
changed = []
for path in sorted(glob.glob('src/*.txt')):
    raw = io.open(path, 'rb').read()
    if b'\r\n' in raw:
        io.open(path, 'wb').write(raw.replace(b'\r\n', b'\n'))
        changed.append(os.path.basename(path))
print('normalised to LF:', ', '.join(changed) if changed else 'nothing to do')

# Make the unwrap newline-agnostic AND check each replacement separately, so a
# half-unwrapped test build fails the build instead of silently shipping.
p = 'build.mjs'
s = io.open(p, encoding='utf-8').read()
old = """let t = body
  .replace("(function(){\\n'use strict';", '/* test build: IIFE unwrapped */')
  .replace(/\\}\\)\\(\\);\\s*<\\/script>/, '</script>');
if (t === body) throw new Error('test build: IIFE unwrap failed');"""
new = """const openRe = /\\(function\\(\\)\\{\\s*'use strict';/;
const closeRe = /\\}\\)\\(\\);\\s*<\\/script>/;
if (!openRe.test(body)) throw new Error('test build: IIFE opening not found');
if (!closeRe.test(body)) throw new Error('test build: IIFE closing not found');
const t = body
  .replace(openRe, '/* test build: IIFE unwrapped */')
  .replace(closeRe, '</script>');"""
assert old in s, 'build.mjs unwrap block not found'
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('build.mjs: unwrap is newline-agnostic and checked per-step')
