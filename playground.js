/* A loaded frame is not a ready graph. Keep external content hidden until
 * both the readable HTTP probe and the explorer readiness protocol succeed. */
(async function () {
  const section = document.querySelector('#try');
  const frame = section.querySelector('iframe');
  const links = [...document.querySelectorAll('[data-playground-link]')];
  const url = new URL(frame.dataset.src);
  const controller = new AbortController();
  let finished = false, httpOK = false, ready = false;
  function remove() {
    if (finished) return;
    finished = true;
    clearTimeout(timer);
    controller.abort();
    window.removeEventListener('message', message);
    section.remove();
    links.forEach(link => link.remove());
  }
  function reveal() {
    if (finished || !httpOK || !ready) return;
    clearTimeout(timer);
    section.hidden = false;
    links.forEach(link => { link.hidden = false; });
  }
  function message(event) {
    if (event.origin !== url.origin || event.source !== frame.contentWindow) return;
    const data = event.data;
    if (data?.type === 'quipu:state') {
      if (data.state === 'error') remove();
      else if (data.state === 'ready') { ready = true; reveal(); }
    } else if (data?.type === 'quipu:resize') {
      const height = data.height;
      if (Number.isInteger(height) && height > 0 && height < 20000) frame.style.height = height + 'px';
    }
  }
  const timer = setTimeout(remove, 8000);
  window.addEventListener('message', message);
  frame.addEventListener('error', remove, { once: true });
  // Attach the listener before navigation, including a warm cached explorer.
  frame.src = url.href;
  try {
    const response = await fetch(url, { signal: controller.signal, mode: 'cors' });
    if (!response.ok || new URL(response.url).origin !== url.origin) return remove();
    httpOK = true;
    reveal();
    await response.body?.cancel();
  } catch { remove(); }
})();
