import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// Disciplines used for filtering on the Projects page.
// Keep this list in sync with the `categories` options in public/admin/config.yml.
export const CATEGORIES = [
  'Master Planning',
  'Architecture',
  'Landscape',
  'Interiors',
  'Hospitality',
  'Visualization',
] as const;

// Each project lives in its own folder: src/content/projects/<slug>/index.md
// with its images next to it. The folder name becomes the URL: /projects/<slug>/
const projects = defineCollection({
  loader: glob({
    pattern: '*/index.md',
    base: './src/content/projects',
    generateId: ({ entry }) => entry.replace(/\/index\.md$/, ''),
  }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      summary: z.string(),
      location: z.string(),
      year: z.number().int().optional(),
      categories: z.array(z.enum(CATEGORIES)).min(1),
      services: z.string().optional(),
      cover: image(),
      coverAlt: z.string(),
      facts: z
        .array(z.object({ label: z.string(), value: z.string() }))
        .default([]),
      gallery: z
        .array(
          z.object({
            image: image(),
            alt: z.string(),
            caption: z.string().optional(),
          }),
        )
        .default([]),
      featured: z.boolean().default(false),
      order: z.number().default(100),
      draft: z.boolean().default(false),
    }),
});

export const collections = { projects };
