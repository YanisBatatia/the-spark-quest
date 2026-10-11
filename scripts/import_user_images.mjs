import { readdir, readFile, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import sharp from 'sharp';

const root = fileURLToPath(new URL('../', import.meta.url));
const incoming = join(root, '../exp-image');
const destination = join(root, 'src/assets/experiences');
const creditsPath = join(root, 'src/data/image-credits.json');
const credits = JSON.parse(await readFile(creditsPath, 'utf8'));
const names = (await readdir(incoming)).filter((name) => /^\d{3}\.(?:jpe?g|png|webp|avif)$/i.test(name)).sort();
const seen = new Set();

// Short, scene-specific descriptions for the owner-selected photographs.
const descriptions = {
  '001': 'Northern Lights above a small cabin in the snow',
  '002': 'Small aircraft flying beside snow-covered Denali peaks',
  '003': 'Alaska train traveling through a snowy forest',
  '004': 'Huskies pulling a sled through a snowy forest',
  '005': 'Warm spring pool surrounded by snow in Alaska',
  '006': 'Visitor among illuminated ice sculptures at night',
  '007': 'Musk ox standing in its enclosure',
  '008': 'Visitors near an animal in an Alaskan wildlife park',
  '009': 'Crowd and reindeer at a winter festival in Anchorage',
  '011': 'Gray wolf walking through snow',
  '012': 'Warm lodge interior overlooking snowy Yellowstone',
  '013': 'Elk grazing across a snowy mountain landscape',
  '014': 'Candlelit dining room at a winter ranch',
  '015': 'Towering snow sculptures beneath a blue sky',
  '016': 'Horse and rider at a winter street festival',
  '017': 'Steam train rounding a snowy mountain bend',
  '018': 'Train winding through the Rocky Mountains',
  '019': 'Aerial view of the LIGO observatory',
  '020': 'Aquatic circus performance above a dark stage',
  '022': 'Large flock of cranes and geese taking flight above water',
  '025': 'Submarine beneath bright blue ocean water',
  '026': 'Giraffe beside a safari lodge',
  '027': 'Alligator beside a path in the Everglades',
  '028': 'Cypress trees reflected in a blackwater swamp',
  '030': 'Historic inn beneath live oaks on a quiet island',
  '031': 'Blue bioluminescence glowing along a nighttime shore',
  '032': 'Visitors watching lava glow at Kilauea',
  '033': 'Aerial view of Kauai’s Napali Coast',
  '034': 'Sunrise over the Grand Canyon',
  '035': 'Snow among the red hoodoos of Bryce Canyon',
  '036': 'White gypsum dunes stretching toward the horizon',
  '037': 'Sunlit cavern interior with visitors below',
  '038': 'Sunrise over the rock formations of Monument Valley',
  '039': 'Visitor on the rim of a vast impact crater',
  '040': 'Artfully plated multi-course dinner',
  '041': 'Crowd watching Mardi Gras floats in New Orleans',
  '042': 'Costumed riders at a rural Cajun Mardi Gras',
  '043': 'Hoop dancers performing outdoors',
  '044': 'Sundance Film Festival marquee in Boulder',
  '045': 'Displays and visitors at a gem and fossil show',
  '048': 'Rodeo rider in an arena',
  '049': 'Pirate-themed festivities by the water in Tampa',
  '050': 'Crowded street festival in Puerto Rico',
  '052': 'Second-line parade with musicians in New Orleans',
  '053': 'Ornate Broadway theater interior',
  '055': 'Sun Studio exterior in Memphis',
  '056': 'Historic blues venue on a Mississippi street',
  '057': 'Colorful interior of a historic recording studio',
  '058': 'Large opera audience inside the Met',
  '059': 'Ballet dancers performing on stage',
  '060': 'Musicians and visitors at a lively Cajun music venue',
  '062': 'Glassmaker working with molten glass',
  '068': 'Hands making a flower lei',
  '075': 'Historic bathhouse exterior',
  '076': 'Snow beside a Japanese-style garden bath',
  '078': 'Paddlewheel steamboat on the Mississippi River',
  '079': 'Elegant dining room at an inn',
  '080': 'Festival tents and guests beside Miami Beach',
  '081': 'Space shuttle and launch displays at Kennedy Space Center',
  '082': 'Spectators watching a rocket launch',
  '083': 'Observatory buildings in a mountain landscape',
  '084': 'Radio telescopes beneath a cloudy sky',
  '085': 'Masked performers in theatrical costumes',
  '086': 'Colorful immersive art installation',
  '087': 'Dinosaur fossils embedded in rock',
  '089': 'Large audiovisual spectacle against a desert landscape',
  '090': 'Visitors exploring musical instruments in a museum',
  '091': 'Indoor orchid garden beneath a glass ceiling',
  '092': 'Sunlit conservatory with lush plants',
  '094': 'Keeper introducing a sloth to a visitor',
  '095': 'Keeper meeting a penguin',
  '097': 'Grand reading room of the Library of Congress',
  '098': 'Exhibits inside the National Comedy Center',
  '099': 'Illuminated exterior of the International Spy Museum',
  '102': 'Niagara Falls surrounded by winter ice',
  '110': 'Poet speaking at a literary event',
};

function sourceUrl(path) {
  try {
    const metadata = execFileSync('xattr', ['-p', 'com.apple.metadata:kMDItemWhereFroms', path]);
    const matches = metadata.toString('utf8').match(/https?:\/\/[^\x00-\x20]+/g);
    return matches?.[0]?.replace(/_$/, '') ?? null;
  } catch { return null; }
}

for (const name of names) {
  const id = name.slice(0, 3);
  if (seen.has(id)) throw new Error(`More than one replacement for ${id}`);
  seen.add(id);
  if (!descriptions[id]) throw new Error(`Unexpected replacement ID: ${id}`);
  const input = join(incoming, name);
  const { width = 0, height = 0 } = await sharp(input).metadata();
  if (width < 550 || height < 350) throw new Error(`Replacement ${name} is too small (${width}×${height})`);
  const source = sourceUrl(input);
  if (!source) throw new Error(`Missing download source for ${name}`);
  await sharp(input).rotate().resize({ width: 1400, withoutEnlargement: true }).flatten({ background: '#f7f3ea' }).jpeg({ quality: 84, progressive: true }).toFile(join(destination, `${id}.jpg`));
  credits[id] = {
    file: `${id}.jpg`, alt: descriptions[id], title: descriptions[id],
    author: 'Photographer not identified', license: 'Used with permission', sourceUrl: source,
    note: 'Owner-selected photograph.',
  };
  console.log(`${id}: ${name} → ${id}.jpg (${width}×${height})`);
}

await writeFile(creditsPath, JSON.stringify(Object.fromEntries(Object.entries(credits).sort(([a], [b]) => a.localeCompare(b))), null, 2) + '\n');
console.log(`Imported ${seen.size} owner-selected images.`);
