const search = document.querySelector<HTMLInputElement>('[data-explore-search]');
const place = document.querySelector<HTMLSelectElement>('[data-explore-place]');
const chips = [...document.querySelectorAll<HTMLButtonElement>('[data-mood]')];
const cards = [...document.querySelectorAll<HTMLElement>('.card-grid .experience-card')];
const status = document.querySelector<HTMLElement>('[data-result-status]');
const noResults = document.querySelector<HTMLElement>('[data-no-results]');
const params = new URLSearchParams(location.search);

function normalized(value: string): string {
  return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase().trim();
}

const indexed = cards.map((card) => ({
  card,
  search: normalized(card.dataset.search ?? ''),
  moods: (card.dataset.moods ?? '').split(' '),
  place: card.dataset.place ?? '',
}));

if (search) search.value = params.get('q') ?? '';
if (place) place.value = params.get('place') ?? '';
let mood = params.get('mood') ?? '';
if (!chips.some((chip) => chip.dataset.mood === mood)) mood = '';

function applyFilters(): void {
  const query = normalized(search?.value ?? '');
  const selectedPlace = place?.value ?? '';
  let count = 0;
  for (const item of indexed) {
    const visible = (!query || item.search.includes(query))
      && (!mood || item.moods.includes(mood))
      && (!selectedPlace || item.place === selectedPlace);
    item.card.hidden = !visible;
    if (visible) count++;
  }
  chips.forEach((chip) => chip.setAttribute('aria-pressed', String(chip.dataset.mood === mood)));
  if (status) status.textContent = `${count} ${count === 1 ? 'idea' : 'ideas'} to explore`;
  if (noResults) noResults.hidden = count !== 0;
  const next = new URLSearchParams();
  if (query) next.set('q', search?.value.trim() ?? '');
  if (mood) next.set('mood', mood);
  if (selectedPlace) next.set('place', selectedPlace);
  history.replaceState(null, '', `${location.pathname}${next.size ? `?${next}` : ''}`);
}

search?.addEventListener('input', applyFilters);
place?.addEventListener('change', applyFilters);
chips.forEach((chip) => chip.addEventListener('click', () => {
  mood = mood === chip.dataset.mood ? '' : (chip.dataset.mood ?? '');
  applyFilters();
}));
applyFilters();
