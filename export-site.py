from pathlib import Path
from urllib.parse import quote
import re

root = Path(__file__).resolve().parent
target = root / 'dist/index.html'
rendered = target.read_text()
assert 'codex-visualization' in rendered, 'Run the visualization renderer before this export adaptation'
fragment = (root / 'mixer.fragment.html').read_text()
assert 'window.openai' not in fragment
# Run the self-contained mixer directly in the page: an opaque-origin preview
# iframe cannot request MIDI permission. The mixer needs no preview host APIs.
fragment = fragment.replace('blocked by this embedded browser', 'blocked by this browser')
fragment = fragment.replace("field(d,'name').setAttribute('data-tooltip',file.name)", "field(d,'name').setAttribute('title',file.name)")
favicon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#202326"/><circle cx="9" cy="13" r="6" fill="none" stroke="#8bd9e9" stroke-width="2"/><circle cx="23" cy="13" r="6" fill="none" stroke="#8bd9e9" stroke-width="2"/><path d="M7 25h18m-8-3v6" stroke="#f0f3f5" stroke-width="2"/></svg>'
head = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="referrer" content="no-referrer">
<meta name="description" content="A private two-deck browser mixer with local audio, demo loops, EQ, crossfader and MIDI learn.">
<title>DDJ-FLX4 Mixer</title>
'''
head += '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,' + quote(favicon, safe='') + '">\n'
head += '''<style>
:root { color-scheme: light dark; background: #e8ebee; color: #192126; }
html, body { margin: 0; min-height: 100%; }
body { font-family: system-ui, sans-serif; box-sizing: border-box; padding: clamp(8px, 2vw, 24px); }
main { max-width: 1400px; margin: 0 auto; }
#flx4-mixer .topline { padding-right: 0; }
.cursor-interaction { cursor: pointer; }
@media (prefers-color-scheme: dark) { :root { background: #151719; color: #f0f3f5; } }
@supports not (color: light-dark(white, black)) {
  #flx4-mixer { --dj-bg:#e8ebee;--dj-panel:#f5f6f7;--dj-well:#dce1e5;--dj-text:#192126;--dj-dim:#53616a;--dj-edge:#bdc6cd;--dj-active:#166d7e;--dj-on:#e2f4f7;--dj-warn:#88450a; }
  @media (prefers-color-scheme: dark) { #flx4-mixer { --dj-bg:#151719;--dj-panel:#202326;--dj-well:#101214;--dj-text:#f0f3f5;--dj-dim:#b1bcc5;--dj-edge:#3b444a;--dj-active:#8bd9e9;--dj-on:#143e47;--dj-warn:#ffc985; } }
}
</style>
</head>
<body>
<main>
'''
tail = '''
</main>
<noscript>This mixer needs JavaScript enabled to play audio and use its controls.</noscript>
<script>
(() => {
  const context = document.modelContext;
  if (!context?.registerTool) return;
  const lifecycle = new AbortController();
  const root = document.getElementById('flx4-mixer');
  const readState = () => ({
    status: root.querySelector('#dj-status').textContent,
    crossfader: Number(root.querySelector('#dj-cross').value),
    master: Number(root.querySelector('#dj-master').value),
    decks: ['A', 'B'].map(id => {
      const deck = root.querySelector('[data-deck="' + id + '"]');
      return { id, playing: deck.querySelector('[data-action="play"]').getAttribute('aria-pressed') === 'true' };
    })
  });
  const noArguments = input => {
    if (!input || typeof input !== 'object' || Array.isArray(input) || Object.keys(input).length) throw new Error('Expected an empty object');
  };
  const register = tool => {
    try { Promise.resolve(context.registerTool(tool, {signal: lifecycle.signal})).catch(() => {}); } catch (_) {}
  };
  register({name:'read_mixer_state',title:'Read mixer state',description:'Read current playback state and master/crossfader settings.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true,untrustedContentHint:false},execute(input){noArguments(input);return readState();}});
  register({name:'stop_mixer_audio',title:'Stop mixer audio',description:'Stop both decks and reset their playheads, using the visible Stop all action.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:false,untrustedContentHint:false},execute(input){noArguments(input);root.querySelector('#dj-stop').click();return readState();}});
  window.addEventListener('pagehide', () => lifecycle.abort(), {once:true});
})();
</script>
</body>
</html>
'''
# The fragment's scoped CSS must precede standalone overrides.
style = re.search(r'<style>(.*?)</style>', head, re.S).group(0)
head = head.replace(style, '')
target.write_text(head + fragment + style + tail)
print(target)
