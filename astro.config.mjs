// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://docs.astro.build/en/reference/configuration-reference/
export default defineConfig({
  // Change to the custom domain (e.g. https://www.example.com) once DNS is set up.
  site: 'https://arch-i-tech.github.io',
  // Org site repo (<org>.github.io) is served from the domain root, so no `base` is needed.
  trailingSlash: 'ignore',
  build: {
    format: 'directory',
  },
  // Update robots.txt's Sitemap line too when `site` changes.
  integrations: [sitemap({ filter: (page) => !page.includes('/admin/') })],
});
