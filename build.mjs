// Concatenates src/p*.txt into:
//   game-body.html  -> Artifact-shaped fragment (no <html>/<head>/<body>)
//   dist/index.html -> standalone build for CrazyGames submission
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(fileURLToPath(import.meta.url));
const parts = ['p1', 'p2', 'p3', 'p4', 'p5']
  .map(n => readFileSync(join(root, 'src', n + '.txt'), 'utf8'));

const body = parts.join('\n');

// The Artifact host's CSP blocks external scripts, so the SDK could never
// load there; leaving it enabled would only log a violation on every open.
// The standalone CrazyGames build below keeps it on.
const artifactBody = body.replace(
  'var ENABLE_CG_SDK = true;',
  'var ENABLE_CG_SDK = false;   // disabled for the Artifact build (CSP blocks the SDK)'
);
if (artifactBody === body) throw new Error('build: could not find the SDK flag to disable');
writeFileSync(join(root, 'game-body.html'), artifactBody, 'utf8');

const standalone = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<meta name="description" content="Magnetar - hold to pull, release to blast. A one-button neon arena roguelite.">
<meta name="theme-color" content="#04050c">
${body}
</body>
</html>
`;
mkdirSync(join(root, 'dist'), { recursive: true });
writeFileSync(join(root, 'dist', 'index.html'), standalone, 'utf8');

// syntax check the inlined script
const m = body.match(/<script>([\s\S]*)<\/script>/);
writeFileSync(join(root, 'dist', '.check.js'), m[1], 'utf8');

// --- test build: timer-driven loop + globals exposed, for automated QA only ---
const openRe = /\(function\(\)\{\s*'use strict';/;
const closeRe = /\}\)\(\);\s*<\/script>/;
if (!openRe.test(body)) throw new Error('test build: IIFE opening not found');
if (!closeRe.test(body)) throw new Error('test build: IIFE closing not found');
const t = body
  .replace(openRe, '/* test build: IIFE unwrapped */')
  .replace(closeRe, '</script>');
const shim = `<script>
(function(){
  var q = [], id = 0;
  window.requestAnimationFrame = function(fn){ var i=++id; setTimeout(function(){ fn(performance.now()); }, 16); return i; };
  window.__errors = [];
  window.addEventListener('error', function(e){ window.__errors.push(String(e.message)+' @'+e.lineno); });
})();
</script>
`;
writeFileSync(join(root, 'dist', 'test.html'), standalone.replace(body, shim + t), 'utf8');

console.log('game-body.html', body.length, 'bytes');
console.log('dist/index.html', standalone.length, 'bytes');
