const map = document.querySelector<HTMLElement>('[data-map]');
const toggle = document.querySelector<HTMLButtonElement>('[data-map-toggle]');
const live = map?.querySelector<HTMLElement>('[data-map-live]');
const preview = map?.querySelector<HTMLElement>('.map-preview');
const label = map?.querySelector<HTMLElement>('[data-map-label]');

if (map && toggle && live && preview && label) {
  toggle.addEventListener('click', () => {
    const opening = toggle.getAttribute('aria-expanded') !== 'true';
    if (opening && !live.querySelector('iframe')) {
      const frame = document.createElement('iframe');
      frame.src = map.dataset.mapSrc ?? '';
      frame.title = `Interactive map near ${label.textContent?.trim() ?? 'this experience'}`;
      frame.loading = 'lazy';
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.setAttribute('allowfullscreen', '');
      live.append(frame);
    }
    live.hidden = !opening;
    preview.hidden = opening;
    label.hidden = opening;
    toggle.setAttribute('aria-expanded', String(opening));
    toggle.innerHTML = opening ? 'Back to illustrated map <span aria-hidden="true">↶</span>' : 'Explore interactive map <span aria-hidden="true">↗</span>';
  });
}
