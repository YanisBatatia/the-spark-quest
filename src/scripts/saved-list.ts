const STORAGE_KEY = 'spark-quest:saved:v1';
const VALID_ID = /^\d{3}$/;
let saved: string[] = [];
let storageAvailable = true;

function readSaved(): string[] {
  try {
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]');
    if (!Array.isArray(value)) return [];
    return [...new Set(value.filter((id): id is string => typeof id === 'string' && VALID_ID.test(id)))];
  } catch {
    storageAvailable = false;
    return [];
  }
}

function save(next: string[]): boolean {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    saved = next;
    return true;
  } catch {
    storageAvailable = false;
    showStorageMessage();
    return false;
  }
}

function showStorageMessage(): void {
  let message = document.querySelector<HTMLElement>('[data-storage-message]');
  if (!message) {
    const target = document.querySelector('[data-save-id]') ?? document.querySelector('.list-actions');
    if (!target) return;
    message = document.createElement('p');
    message.className = 'storage-message';
    message.setAttribute('role', 'status');
    message.setAttribute('data-storage-message', '');
    target.insertAdjacentElement('afterend', message);
  }
  message.textContent = 'This browser is not allowing the list to be saved. You can still browse every idea.';
}

function render(): void {
  const selected = new Set(saved);
  document.querySelectorAll<HTMLButtonElement>('[data-save-id]').forEach((button) => {
    const id = button.dataset.saveId ?? '';
    const isSaved = selected.has(id);
    const title = button.dataset.saveTitle ?? 'this idea';
    button.setAttribute('aria-pressed', String(isSaved));
    button.setAttribute('aria-label', `${isSaved ? 'Remove' : 'Save'} ${title} ${isSaved ? 'from' : 'to'} my list`);
    const label = button.querySelector<HTMLElement>('.save-label');
    if (label) label.textContent = isSaved ? 'Saved to my list' : 'Save to my list';
  });

  const list = document.querySelector<HTMLElement>('[data-saved-list]');
  if (list) {
    const cards = new Map([...list.querySelectorAll<HTMLElement>('[data-saved-item]')]
      .map((card) => [card.dataset.experienceId ?? '', card]));
    for (const card of cards.values()) card.hidden = true;
    for (const id of saved) {
      const card = cards.get(id);
      if (!card) continue;
      card.hidden = false;
      list.append(card);
    }
    const empty = document.querySelector<HTMLElement>('[data-empty-list]');
    if (empty) empty.hidden = saved.length > 0;
    document.querySelectorAll<HTMLElement>('[data-list-actions]').forEach((actions) => {
      actions.hidden = saved.length === 0;
    });
  }
}

document.addEventListener('click', (event) => {
  const target = event.target;
  if (!(target instanceof Element)) return;
  const saveButton = target.closest<HTMLButtonElement>('[data-save-id]');
  if (saveButton) {
    if (!storageAvailable) return showStorageMessage();
    const id = saveButton.dataset.saveId ?? '';
    const next = saved.includes(id) ? saved.filter((item) => item !== id) : [...saved, id];
    if (save(next)) render();
    return;
  }
  const removeButton = target.closest<HTMLButtonElement>('[data-remove-id]');
  if (removeButton) {
    const next = saved.filter((id) => id !== removeButton.dataset.removeId);
    if (save(next)) render();
  }
  if (target.closest('[data-print-list]')) window.print();
  if (target.closest('[data-export-list]')) exportList();
});

function exportList(): void {
  const list = document.querySelector<HTMLElement>('[data-saved-list]');
  if (!list) return;
  const cards = new Map([...list.querySelectorAll<HTMLElement>('[data-saved-item]')]
    .map((card) => [card.dataset.experienceId ?? '', card]));
  const quote = (value: string) => `"${value.replaceAll('"', '""')}"`;
  const rows = [['ID', 'Title', 'Location', 'URL'].map(quote).join(',')];
  for (const id of saved) {
    const card = cards.get(id);
    if (!card) continue;
    rows.push([
      id, card.dataset.title ?? '', card.dataset.location ?? '',
      new URL(card.dataset.href ?? '', location.origin).href,
    ].map(quote).join(','));
  }
  const blob = new Blob(['\uFEFF', rows.join('\r\n'), '\r\n'], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'the-spark-quest-my-list.csv';
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

saved = readSaved();
render();
if (!storageAvailable) showStorageMessage();
window.addEventListener('storage', (event) => {
  if (event.key === STORAGE_KEY) {
    saved = readSaved();
    render();
  }
});
