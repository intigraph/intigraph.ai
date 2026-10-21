// Fixed destination only: a path cannot select a redirect host.
(function (root) {
  function resolve(pathname) {
    if (typeof pathname !== 'string' || /[%\\\x00-\x20]/.test(pathname)) return null;
    const match = pathname.match(/^\/ids\/((?:[a-z][a-z0-9-]*\/)+id\/[A-Za-z0-9_~.-]+(?:\/[A-Za-z0-9_~.-]+)*)\/?$/);
    if (!match || /(?:^|\/)\.{1,2}(?:\/|$)/.test(match[1]) || /\.(?:ttl|jsonld)$/i.test(match[1])) return null;
    const namespace = match[1].split('/id/')[0];
    if (!['quechua','quipu','seeds','camayoc/core','camayoc/delivery','camayoc/code-entities','camayoc/session-transcript','camayoc/usage-breakdown','camayoc/homelab-infra','camayoc/personal-media','camayoc/software-factory'].includes(namespace)) return null;
    const target = new URL('https://scbrown.github.io/quipu/explore/');
    target.searchParams.set('entity', 'https://w3id.org/intigraph/' + match[1]);
    return target.href;
  }
  if (typeof module !== 'undefined') module.exports = resolve;
  else {
    const destination = resolve(root.location.pathname);
    if (destination) {
      const link = root.document.getElementById('entity-link');
      link.href = destination; link.hidden = false;
      root.location.replace(destination);
    }
  }
})(typeof window !== 'undefined' ? window : globalThis);
