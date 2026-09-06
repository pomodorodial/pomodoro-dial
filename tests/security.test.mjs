import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';

const root = new URL('../', import.meta.url);
const read = path => readFileSync(new URL(path, root), 'utf8');
const html = read('index.html');
const app = html.match(/<script>([\s\S]*?)<\/script>/)[1];

test('app and service worker have valid JavaScript syntax', () => {
  new vm.Script(app);
  new vm.Script(read('sw.js'));
});

for (const path of ['index.html', 'about/index.html', 'changelog/index.html', 'pomodoro-technique/index.html', 'privacy/index.html']) {
  test(path + ': CSP authorizes executable inline scripts and structured data parses', () => {
    const page = read(path);
    const policy = page.match(/<meta http-equiv="Content-Security-Policy" content="([^"]*)">/)?.[1];
    assert.ok(policy, 'CSP meta tag is present');
    assert.ok(page.indexOf('Content-Security-Policy') < page.indexOf('<script'));
    assert.ok(policy.includes("object-src 'none'"));
    for (const [, attrs, source] of page.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)) {
      if (/application\/ld\+json/.test(attrs)) JSON.parse(source);
      else if (!/\bsrc\s*=/.test(attrs) && source.trim()) {
        const hash = createHash('sha256').update(source).digest('base64');
        assert.ok(policy.includes("'sha256-" + hash + "'"), 'inline script hash matches policy');
      }
    }
  });
}

const branchStart = app.indexOf("if (location.hash === '#feedback')");
assert.ok(branchStart >= 0, 'panel startup block exists');
const panelBoot = app.slice(branchStart, app.lastIndexOf('})();'));
for (const [hash, panel] of [['#feedback', 'feedback'], ['#stats', 'stats'], ['#settings', 'settings']]) {
  test(hash + ' opens the panel and clears only the hash, despite local statistics history', () => {
    const opened = [], replacements = [];
    const statistics = { '2026-09-06': { done: 3, seconds: 4500 } };
    vm.runInNewContext(panelBoot, {
      history: statistics,
      window: { history: { replaceState: (...args) => replacements.push(args) } },
      location: { hash, pathname: '/', search: '?focus=50' },
      openFeedback: () => opened.push('feedback'),
      openStats: () => opened.push('stats'),
      openSheet: () => opened.push('settings')
    });
    assert.deepEqual(opened, [panel]);
    assert.deepEqual(replacements, [[null, '', '/?focus=50']]);
    assert.equal(statistics['2026-09-06'].done, 3);
  });
}

test('service worker uses one navigation cache entry per path and finds it offline', async () => {
  const handlers = {}, entries = new Map();
  let offline = false;
  const cache = { async put(key, response) { entries.set(key, response); } };
  vm.runInNewContext(read('sw.js'), {
    URL,
    self: { location: { origin: 'https://pomodorodial.com' }, addEventListener: (name, fn) => { handlers[name] = fn; } },
    caches: { open: async () => cache, match: async key => entries.get(key) },
    fetch: async () => {
      if (offline) throw new Error('offline');
      return { ok: true, clone() { return this; } };
    }
  });
  async function navigate(url) {
    let response;
    handlers.fetch({ request: { url, method: 'GET', mode: 'navigate' }, respondWith(p) { response = p; } });
    const result = await response;
    await new Promise(resolve => setImmediate(resolve));
    return result;
  }
  await navigate('https://pomodorodial.com/?focus=25');
  await navigate('https://pomodorodial.com/?focus=50');
  assert.deepEqual([...entries.keys()], ['https://pomodorodial.com/']);
  offline = true;
  assert.equal(await navigate('https://pomodorodial.com/?focus=90'), entries.get('https://pomodorodial.com/'));
});
