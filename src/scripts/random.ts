document.querySelectorAll<HTMLElement>('[data-random-destination]').forEach((trigger) => {
  trigger.addEventListener('click', (event) => {
    if (event instanceof MouseEvent && (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey)) return;
    const ids = JSON.parse(trigger.dataset.randomDestination ?? '[]') as string[];
    if (!ids.length) return;
    event.preventDefault();
    const id = ids[Math.floor(Math.random() * ids.length)];
    location.assign(`${trigger.dataset.base ?? '/'}experiences/${id}/`);
  });
});
