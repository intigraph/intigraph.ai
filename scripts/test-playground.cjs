const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const assert = require('node:assert/strict');
const root = path.resolve(process.env.SITE_DIR || path.join(__dirname, '..'));
const origin = 'https://scbrown.github.io';
const fixture = '<!doctype html><title>Controlled playground frame</title><p id="control">Ready: cross-origin resize fixture, not the Quipu engine</p><script>window.emit = data => { document.querySelector("#control").textContent = "Sent " + JSON.stringify(data); parent.postMessage(data, "*"); };</script>';
const server = http.createServer((req, res) => {
  const name = new URL(req.url, 'http://localhost').pathname.slice(1) || 'index.html';
  if (!['index.html', 'logo.svg', 'icon.svg', 'steve.jpg', 'steve.webp'].includes(name)) { res.writeHead(404); res.end(); return; }
  res.setHeader('Content-Type', name.endsWith('.html') ? 'text/html' : name.endsWith('.svg') ? 'image/svg+xml' : 'image/' + path.extname(name).slice(1));
  res.end(fs.readFileSync(path.join(root, name)));
});
(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const browser = await chromium.launch({ headless: false, ...(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    await context.route('https://**/*', route => route.request().url().startsWith(origin + '/quipu/explore/')
      ? route.fulfill({ contentType: 'text/html', body: fixture }) : route.abort());
    const page = await context.newPage();
    const errors = []; page.on('pageerror', error => errors.push(error.message));
    await page.goto(`http://127.0.0.1:${server.address().port}/`);
    await page.click('#play-go');
    const iframe = page.locator('#play iframe');
    const child = await (await iframe.elementHandle()).contentFrame();
    await child.waitForSelector('#control');
    const src = new URL(await iframe.getAttribute('src'));
    const height = () => iframe.evaluate(node => node.getBoundingClientRect().height);
    const send = async data => { await child.evaluate(data => window.emit(data), data); await page.waitForTimeout(60); };
    await send({ type: 'quipu:resize', height: 920 }); const grown = await height();
    await send({ type: 'quipu:resize', height: 640 }); const shrunk = await height();
    const results = { childControl: await child.locator('#control').innerText(), embedURL: src.origin === origin && src.pathname === '/quipu/explore/' && src.searchParams.get('embed') === '1' && src.searchParams.get('theme') === 'intigraph', grows: grown === 920, shrinks: shrunk === 640 };
    for (const bad of [0, -1, 20000, 1.25, '900', null, NaN, Infinity]) {
      await send({ type: 'quipu:resize', height: bad }); assert.equal(await height(), shrunk, 'invalid height changed iframe');
    }
    await send({ type: 'unrelated', height: 990 }); assert.equal(await height(), shrunk, 'unrelated message changed iframe');
    await page.evaluate(() => window.postMessage({ type: 'quipu:resize', height: 990 }, '*'));
    await page.waitForTimeout(60); assert.equal(await height(), shrunk, 'wrong origin changed iframe');
    await page.evaluate(() => window.dispatchEvent(new MessageEvent('message', { origin: 'https://scbrown.github.io', source: window, data: { type: 'quipu:resize', height: 990 } })));
    await page.waitForTimeout(60); assert.equal(await height(), shrunk, 'wrong source changed iframe');
    results.rejectsInvalidMessages = true;
    await page.setViewportSize({ width: 390, height: 860 });
    results.mobileFits = await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth);
    results.errors = errors;
    console.log(JSON.stringify(results, null, 2));
    assert.deepEqual(errors, []);
    if (!process.argv.includes('--observe')) for (const name of ['embedURL', 'grows', 'shrinks', 'mobileFits']) assert(results[name], name);
    await context.close();
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; }).finally(() => server.close());
