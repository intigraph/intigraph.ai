const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const resolve = require('./ids-resolver.cjs');
module.exports = function testIds(root) {
  assert.equal(fs.readFileSync(path.join(root,'ids-resolver.js'),'utf8'),fs.readFileSync(path.join(root,'scripts/ids-resolver.cjs'),'utf8'));
  const target = new URL(resolve('/ids/seeds/id/aegis-test'));
  assert.equal(target.origin,'https://scbrown.github.io');
  assert.equal(target.pathname,'/quipu/explore/');
  assert.equal(target.searchParams.get('entity'),'https://w3id.org/intigraph/seeds/id/aegis-test');
  for (const bad of ['/elsewhere','/ids/unknown/id/a','/ids/seeds/id/a.ttl','/ids/seeds/id/a.jsonld','/ids/seeds/id/..','/ids/seeds/id/%2e%2e','/ids/seeds/id/a?url=evil','/ids/seeds/id/a\\x','//evil/id/a']) assert.equal(resolve(bad),null,bad);
  execFileSync('python3',[path.join(root,'scripts/check-public-tree.py')],{stdio:'inherit'});
  const dir = fs.mkdtempSync(path.join(os.tmpdir(),'ids-ci-'));
  try {
    execFileSync('python3',['-m','venv',dir],{stdio:'inherit'});
    const python = path.join(dir,'bin/python');
    execFileSync(python,['-m','pip','install','--disable-pip-version-check','rdflib==7.1.4'],{stdio:'inherit'});
    execFileSync(python,[path.join(root,'scripts/test-ids.py')],{stdio:'inherit'});
  } finally {fs.rmSync(dir,{recursive:true,force:true});}
};
