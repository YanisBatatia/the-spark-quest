import downloadedCredits from '../data/image-credits.json';

export type ImageCredit = {
  file: string;
  alt: string;
  title: string;
  author: string;
  license: string;
  licenseUrl?: string;
  sourceUrl?: string;
  note: string;
};

const generatedCredits: Record<string, ImageCredit> = {
  '021': { file: '021.png', alt: 'Illustration of a manatee seen from a Florida boardwalk', title: 'Florida manatee', author: 'The Spark Quest', license: 'Original generated illustration', note: 'Illustrative artwork.' },
  '051': { file: '051.png', alt: 'Illustration of musicians playing jazz in an intimate room', title: 'Jazz performance', author: 'The Spark Quest', license: 'Original generated illustration', note: 'Illustrative artwork.' },
  '067': { file: '067.png', alt: 'Illustration of hands shaping clay on a pottery wheel', title: 'Pottery workshop', author: 'The Spark Quest', license: 'Original generated illustration', note: 'Illustrative artwork.' },
};

export const imageCredits: Record<string, ImageCredit> = { ...downloadedCredits, ...generatedCredits };

const modules = import.meta.glob<ImageMetadata>('../assets/experiences/*.{jpg,png}', { eager: true, import: 'default' });
export const featuredImages: Record<string, ImageMetadata> = {};
for (const [path, image] of Object.entries(modules)) {
  const id = path.match(/\/([0-9]{3})\.(?:jpg|png)$/)?.[1];
  if (id) featuredImages[id] = image;
}
