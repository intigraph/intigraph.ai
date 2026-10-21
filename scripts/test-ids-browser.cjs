const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
module.exports = async function testIdsBrowser(browser, root) {
  const catalog = JSON.parse(fs.readFileSync(path.join(root,'ids/catalog.json')));
  const server = http.createServer((req,res) => {
    const pathname = new URL(req.url,'http://localhost').pathname;
    const requested = pathname === '/ids-resolver.js' ? 'ids-resolver.js' : pathname === '/ids/' ? 'ids/index.html' : catalog.some(c=>pathname==='/ids/'+c.path+'/') ? pathname.slice(1)+'index.html' : '404.html';
    res.writeHead(requested==='404.html'?404:200,{'Content-Type':requested.endsWith('.js')?'text/javascript':'text/html'});
    res.end(fs.readFileSync(path.join(root,requested)));
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const context = await browser.newContext();
  try {
    await context.route('https://**/*', route=>route.request().url().startsWith('https://scbrown.github.io/quipu/explore/') ? route.fulfill({contentType:'text/html',body:'<title>Controlled explorer destination</title>'}) : route.abort());
    const page = await context.newPage();
    for (const width of [1280,390]) {
      await page.setViewportSize({width,height:900});
      await page.goto(origin+'/ids/');
      assert.equal(await page.locator('main li').count(),11);
      for (const item of catalog) {
        await page.goto(origin+'/ids/'+item.path+'/');
        assert.equal(await page.locator('article').count(),item.terms);
        assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),item.path+' overflow');
      }
    }
    await page.goto(origin+'/ids/seeds/id/aegis-test');
    await page.waitForURL('https://scbrown.github.io/quipu/explore/**');
    assert.equal(new URL(page.url()).searchParams.get('entity'),'https://w3id.org/intigraph/seeds/id/aegis-test');
    for (const bad of ['/unrelated','/ids/unknown/id/a','/ids/seeds/id/a.ttl','/ids/seeds/id/%2e%2e%2fb']) {
      const response = await page.goto(origin+bad);
      assert.equal(response.status(),404);
      assert.equal(new URL(page.url()).origin,origin);
    }
    console.log('IDs: 11 namespaces desktop/mobile; entity redirect positive; four browser refusal controls PASS');
  } finally {await context.close();await new Promise(resolve=>server.close(resolve));}
};
