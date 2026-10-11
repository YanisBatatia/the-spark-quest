const search = document.querySelector<HTMLInputElement>('[data-explore-search]');
const place = document.querySelector<HTMLSelectElement>('[data-explore-place]');
const chips = [...document.querySelectorAll<HTMLButtonElement>('[data-mood]')];
const recommendationChip = document.querySelector<HTMLButtonElement>('[data-recommendations]');
const grid = document.querySelector<HTMLElement>('.card-grid');
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
  recommendationRank: Number(card.dataset.recommendationRank) || 0,
}));
const defaultOrder = new Map(cards.map((card, index) => [card, index]));

if (search) search.value = params.get('q') ?? '';
if (place) place.value = params.get('place') ?? '';
let mood = params.get('mood') ?? '';
if (!chips.some((chip) => chip.dataset.mood === mood)) mood = '';
let recommended = params.get('recommended') === '1';

function applyFilters(): void {
  const query = normalized(search?.value ?? '');
  const selectedPlace = place?.value ?? '';
  let count = 0;
  for (const item of indexed) {
    const visible = (!query || item.search.includes(query))
      && (!mood || item.moods.includes(mood))
      && (!selectedPlace || item.place === selectedPlace)
      && (!recommended || item.recommendationRank > 0);
    item.card.hidden = !visible;
    const why = item.card.querySelector<HTMLElement>('.card-recommendation');
    if (why) why.hidden = !recommended;
    if (visible) count++;
  }
  chips.forEach((chip) => chip.setAttribute('aria-pressed', String(chip.dataset.mood === mood)));
  recommendationChip?.setAttribute('aria-pressed', String(recommended));
  grid?.classList.toggle('show-recommendations', recommended);
  if (grid) indexed.sort((a, b) => recommended
    ? (a.recommendationRank || 999) - (b.recommendationRank || 999) || (defaultOrder.get(a.card) ?? 0) - (defaultOrder.get(b.card) ?? 0)
    : (defaultOrder.get(a.card) ?? 0) - (defaultOrder.get(b.card) ?? 0)).forEach((item) => grid.append(item.card));
  if (status) status.textContent = `${count} ${count === 1 ? 'idea' : 'ideas'} ${recommended ? 'in my recommendations' : 'to explore'}`;
  if (noResults) noResults.hidden = count !== 0;
  const next = new URLSearchParams();
  if (query) next.set('q', search?.value.trim() ?? '');
  if (mood) next.set('mood', mood);
  if (selectedPlace) next.set('place', selectedPlace);
  if (recommended) next.set('recommended', '1');
  history.replaceState(null, '', `${location.pathname}${next.size ? `?${next}` : ''}`);
}

search?.addEventListener('input', applyFilters);
place?.addEventListener('change', applyFilters);
chips.forEach((chip) => chip.addEventListener('click', () => {
  mood = mood === chip.dataset.mood ? '' : (chip.dataset.mood ?? '');
  applyFilters();
}));
recommendationChip?.addEventListener('click', () => {
  recommended = !recommended;
  applyFilters();
});
applyFilters();
