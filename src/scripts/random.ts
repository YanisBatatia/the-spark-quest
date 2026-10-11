const button = document.querySelector<HTMLButtonElement>('[data-random-destination]');
button?.addEventListener('click', () => {
  const ids = JSON.parse(button.dataset.randomDestination ?? '[]') as string[];
  if (!ids.length) return;
  const id = ids[Math.floor(Math.random() * ids.length)];
  location.assign(`${button.dataset.base ?? '/'}experiences/${id}/`);
});
