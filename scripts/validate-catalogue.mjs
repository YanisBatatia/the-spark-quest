import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const directory = join(root, 'src/data/experiences');
const assets = join(root, 'src/assets/experiences');
const maps = join(root, 'public/maps');
const credits = JSON.parse(readFileSync(join(root, 'src/data/image-credits.json'), 'utf8'));
const coordinates = JSON.parse(readFileSync(join(root, 'src/data/map-coordinates.json'), 'utf8'));
const originals = new Set(['021', '051', '067']);
const files = readdirSync(directory).filter((name) => name.endsWith('.json')).sort();
const expected = new Set([
  ...Array.from({ length: 71 }, (_, i) => String(i + 1).padStart(3, '0')),
  ...Array.from({ length: 28 }, (_, i) => String(i + 73).padStart(3, '0')),
  '102', '110',
]);
const errors = [];

if (files.length !== 101) errors.push(`Expected 101 JSON files; found ${files.length}`);
for (const filename of files) {
  const entry = JSON.parse(readFileSync(join(directory, filename), 'utf8'));
  const id = filename.slice(0, -5);
  if (!expected.has(id)) errors.push(`Unexpected ID: ${id}`);
  if (entry.id !== id || entry.source?.pdfId !== id) errors.push(`Mismatched ID in ${filename}`);
  for (const key of ['title', 'description', 'teaser', 'goodToKnow', 'whyItMightDelightYou']) {
    if (!entry[key]?.trim()) errors.push(`Missing ${key} in ${filename}`);
  }
  if (entry.description?.length < 170) errors.push(`Description too short in ${filename}`);
  if (entry.whyItMightDelightYou?.length < 40) errors.push(`Delight note too short in ${filename}`);
  if (entry.description === entry.whyItMightDelightYou || entry.teaser === entry.whyItMightDelightYou) errors.push(`Repeated editorial copy in ${filename}`);
  if (entry.editorialStatus !== 'researched' || !/^https:\/\//.test(entry.source?.webUrl ?? '')) errors.push(`Missing research source in ${filename}`);
  if (!entry.location?.label?.trim() || !entry.location?.placeGroup?.trim()) errors.push(`Missing location in ${filename}`);
  if (!Array.isArray(entry.moods) || entry.moods.length === 0) errors.push(`Missing moods in ${filename}`);
  if (entry.provider && (!entry.provider.name?.trim() || !/^https:\/\//.test(entry.provider.url))) errors.push(`Invalid provider in ${filename}`);
  if (!existsSync(join(maps, `${id}.svg`))) errors.push(`Missing map for ${id}`);
  const point = coordinates[id];
  if (!point || !Number.isFinite(point.lat) || !Number.isFinite(point.lon) || Math.abs(point.lat) > 90 || Math.abs(point.lon) > 180) errors.push(`Invalid map coordinates for ${id}`);
  if (originals.has(id)) {
    if (!existsSync(join(assets, `${id}.png`))) errors.push(`Missing original illustration for ${id}`);
  } else {
    const credit = credits[id];
    if (!credit) errors.push(`Missing image credit for ${id}`);
    else {
      if (credit.file !== `${id}.jpg` || !existsSync(join(assets, credit.file))) errors.push(`Missing photo for ${id}`);
      if (!credit.alt?.trim() || !credit.title?.trim() || !credit.author?.trim() || !credit.license?.trim()) errors.push(`Incomplete image credit for ${id}`);
      if (!/^https:\/\//.test(credit.sourceUrl ?? '')) errors.push(`Invalid image source for ${id}`);
    }
  }
  expected.delete(id);
}
if (expected.size) errors.push(`Missing IDs: ${[...expected].join(', ')}`);
for (const id of Object.keys(credits)) {
  if (!files.includes(`${id}.json`) || originals.has(id)) errors.push(`Unexpected image credit: ${id}`);
}
for (const id of Object.keys(coordinates)) {
  if (!files.includes(`${id}.json`)) errors.push(`Unexpected map coordinates: ${id}`);
}
for (const filename of readdirSync(assets)) {
  if (!/^[0-9]{3}\.(?:jpg|png)$/.test(filename)) continue;
  const id = filename.slice(0, 3);
  if (!files.includes(`${id}.json`) || (filename.endsWith('.jpg') && !credits[id]) || (filename.endsWith('.png') && !originals.has(id))) {
    errors.push(`Untracked image asset: ${filename}`);
  }
}

if (errors.length) {
  console.error(errors.join('\n'));
  process.exitCode = 1;
} else {
  console.log('Catalogue validated: 101 researched entries, images with credits, and location maps.');
}
