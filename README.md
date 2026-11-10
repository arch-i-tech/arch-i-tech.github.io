# arch-i-tech.github.io

Portfolio website for Arch-I-Tech Ltd, built with [Astro](https://astro.build), hosted on GitHub Pages, and edited by the team through [Sveltia CMS](https://github.com/sveltia/sveltia-cms) at `/admin/`.

## Structure

```
src/
  content/projects/<slug>/index.md   one folder per project, images next to it
  content.config.ts                  project fields (schema) + category list
  data/site.json                     contact & company details (editable in CMS)
  layouts/BaseLayout.astro           <head>, SEO/OG tags, header + footer
  components/                        Header, Footer, ProjectCard
  pages/                             /, /projects/, /projects/<slug>/, /about/, 404
  styles/global.css                  design tokens and shared styles
public/admin/                        CMS (index.html + config.yml)
.github/workflows/deploy.yml         build + deploy to GitHub Pages on push to main
```

## Local development

Requires Node.js 20.3+ (22 LTS recommended).

```bash
npm install
npm run dev        # http://localhost:4321
npm run build      # outputs to dist/
npm run preview    # serve the built site
```

Commit `package-lock.json` after the first `npm install`.

## Deployment

1. Repo **Settings → Pages → Source: GitHub Actions**.
2. Push to `main`; the workflow builds and deploys.
3. Custom domain: add it in Settings → Pages, then point DNS (GoDaddy) at GitHub Pages
   (A records 185.199.108–111.153 for `@`, CNAME `www` → `arch-i-tech.github.io`).
   Update `site` in `astro.config.mjs` and `site_url` in `public/admin/config.yml`.

## Adding a project

Through the CMS (`/admin/` → Projects → New), or by hand: create
`src/content/projects/<slug>/index.md` with the front matter used in
`ocean-lake-resort/index.md` and put the images in the same folder.
