// Keep saved lesson/video anchors usable inside progressively disclosed content.
export function revealLinkedContent() {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  if (!id) return;
  const target = document.getElementById(id);
  if (!target) return;
  let opened = false;
  for (let element = target; element; element = element.parentElement) {
    if (element instanceof HTMLDetailsElement && !element.open) {
      element.open = true;
      opened = true;
    }
  }
  if (opened) requestAnimationFrame(() => target.scrollIntoView({ block: 'start' }));
}

export function enableLinkedDisclosures() {
  revealLinkedContent();
  window.addEventListener('hashchange', revealLinkedContent);
}
