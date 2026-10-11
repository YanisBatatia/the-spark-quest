import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const experiences = defineCollection({
  loader: glob({ pattern: '**/*.json', base: './src/data/experiences' }),
  schema: z.object({
    id: z.string().regex(/^\d{3}$/),
    title: z.string().min(1),
    location: z.object({
      label: z.string().min(1),
      placeGroup: z.string().min(1),
    }),
    description: z.string().min(1),
    teaser: z.string().min(1),
    moods: z.array(z.enum(['wonder', 'make', 'listen', 'taste', 'nature', 'rest'])).min(1),
    goodToKnow: z.string().min(1),
    whyItMightDelightYou: z.string().min(1),
    provider: z.object({ name: z.string().min(1), url: z.string().url() }).optional(),
    source: z.object({
      pdfId: z.string().regex(/^\d{3}$/),
      pdfPage: z.number().int().min(5).max(35),
    }),
    editorialStatus: z.literal('needs-review'),
  }),
});

export const collections = { experiences };
