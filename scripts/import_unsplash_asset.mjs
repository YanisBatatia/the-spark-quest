import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import sharp from 'sharp';

const [id, source] = process.argv.slice(2);
const root = fileURLToPath(new URL('../', import.meta.url));
const selections = JSON.parse(readFileSync(join(root, 'scripts/unsplash-selections.json'), 'utf8'));
const selected = selections[id];
if (!selected || !source || !/^\d{3}$/.test(id)) throw new Error('Use: node scripts/import_unsplash_asset.mjs ID BUNDLED_ASSET_PATH');
const metadata = await sharp(source).metadata();
if ((metadata.width ?? 0) < 500 || (metadata.height ?? 0) < 350) throw new Error(`Image ${id} is too small`);
await sharp(source).resize({ width: 1200, withoutEnlargement: true }).jpeg({ quality: 82, progressive: true }).toFile(join(root, 'src/assets/experiences', `${id}.jpg`));
const manifest = join(root, 'src/data/image-credits.json');
const credits = JSON.parse(readFileSync(manifest, 'utf8'));
credits[id] = {
  file: `${id}.jpg`, alt: selected.alt, title: selected.title,
  author: selected.author, license: 'Unsplash License',
  licenseUrl: 'https://unsplash.com/license', sourceUrl: selected.sourceUrl,
  note: 'Illustrative photo; the pictured scene may differ from the named experience.',
};
writeFileSync(manifest, JSON.stringify(Object.fromEntries(Object.entries(credits).sort(([a], [b]) => a.localeCompare(b))), null, 2) + '\n');
console.log(`Imported ${id}: ${selected.title} (${metadata.width}×${metadata.height})`);
