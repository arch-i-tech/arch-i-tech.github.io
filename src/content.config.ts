import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
import categoryData from './data/categories.json';

// Disciplines used for filtering on the Projects page and in "What we do".
// The single source is src/data/categories.json (also editable in the CMS).
export const CATEGORY_LIST = categoryData.categories;
export const CATEGORIES = CATEGORY_LIST.map((c) => c.name) as [string, ...string[]];

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
      location: z.string().default(''),
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
      // YouTube video IDs (the 11 characters after "watch?v=").
      videos: z
        .array(z.object({ youtube: z.string().regex(/^[A-Za-z0-9_-]{11}$/), title: z.string().optional() }))
        .default([]),
      // Original post on arch-i-tech.blogspot.com (kept for redirects in phase 3; not shown).
      source: z.string().url().optional(),
      featured: z.boolean().default(false),
      order: z.number().default(100),
      draft: z.boolean().default(false),
    }),
});

export const collections = { projects };
