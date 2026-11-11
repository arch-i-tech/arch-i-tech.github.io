# Arch-I-Tech website — build plan

Three phases, done in order. Each one is usable and checked before the next starts.

| Phase | Goal | Live at |
| --- | --- | --- |
| 1. Static site | A complete site the team can review | `https://arch-i-tech.github.io` |
| 2. CMS | Architects edit content without touching code | `https://arch-i-tech.github.io/admin/` |
| 3. Domain | The new site replaces the old one | Custom domain |

The old site is not affected until phase 3, so phases 1 and 2 can take as long as they need.

---

## Phase 1 — Static site (no CMS)

Most of the pages, layout and styles already exist. This phase makes them build, deploy and look finished.

### Build and repo

- [ ] `npm install`, `npm run build`, `npm run check`; fix anything that breaks
- [ ] Commit `package-lock.json`
- [ ] Commit the pending LinkedIn / Upwork / role-title changes
- [ ] Remove the leftover `claude/design-review-b8ba2a` worktree and branch (if no longer needed)

### Site basics

- [ ] Favicon and app icons in `public/`
- [ ] Sitemap (`@astrojs/sitemap`) and `robots.txt`
- [ ] Keep the category list in one place (currently duplicated in `src/content.config.ts` and `public/admin/config.yml`)
- [ ] Move remaining hard-coded colours into the tokens in `src/styles/global.css`
- [ ] Check layout on phone, tablet and desktop; check keyboard navigation

### Content

- [ ] Contact details in `src/data/site.json` (email, phone, studio location, social links)
- [ ] More projects in `src/content/projects/<slug>/` (cover, gallery, facts, description)
- [ ] Team portraits (replace the initials placeholders)
- [ ] Final copy review: home, projects, studio pages

About page team and services stay hard-coded in this phase; they move to the CMS in phase 2.

### Deploy

- [ ] Repo **Settings → Pages → Source: GitHub Actions**
- [ ] Push to `main`, confirm the workflow deploys
- [ ] Team reviews the preview at `https://arch-i-tech.github.io`

**Done when:** the site builds cleanly, deploys from `main`, and the team signs off on the preview.

---

## Phase 2 — CMS

### Decisions first

- [ ] **Branching.** The CMS commits straight to `main`; development happens on `develop`. Pick one:
  - CMS → `main`, merge `main` into `develop` regularly
  - CMS → `develop`, promote `develop` → `main` to publish
  - Drop `develop`, use short feature branches off `main`
- [ ] **Sign-in.** GitHub personal access tokens (no setup, awkward for non-developers) or deploy
      [sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth) on a free Cloudflare Worker (GitHub login button)
- [ ] **What is editable.** Projects and site settings already are. Decide on team, services,
      "What we do" and home intro text

### Build

- [ ] Pin the Sveltia CMS version in `public/admin/index.html`
- [ ] Set up the chosen sign-in method; give each architect GitHub access to the repo
- [ ] Move the chosen sections into CMS-editable data files and add them to `config.yml`
- [ ] Contact form: pick Formspree or Web3Forms, set `formEndpoint`, add a thank-you page and spam protection
- [ ] Add a build check (`astro check` + `astro build`) on pull requests so a bad edit can't break the live site

### Test and hand over

- [ ] Create, edit and delete a test project from the CMS; confirm it deploys
- [ ] Upload a large image; confirm it is resized to WebP
- [ ] Short how-to for the team: adding a project, editing contact details, drafts

**Done when:** an architect can add a project end to end without help.

---

## Phase 3 — Domain (retires the old site)

### Before touching DNS

- [ ] List the old site's URLs (main pages, project pages, anything linked or indexed)
- [ ] Map each old URL to its new page and add redirects
- [ ] Record the current DNS records at GoDaddy, especially **MX (email)**, which must not change
- [ ] Back up the old site

### Switch

- [ ] Add the custom domain in repo **Settings → Pages**
- [ ] GoDaddy DNS: A records `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` for `@`;
      CNAME `www` → `arch-i-tech.github.io`. Leave MX and other records alone
- [ ] Enable **Enforce HTTPS** once the certificate is issued
- [ ] Update `site` in `astro.config.mjs` and `site_url` / `display_url` in `public/admin/config.yml`

### After

- [ ] Test the old URLs redirect correctly; test email still arrives
- [ ] Submit the sitemap to Google Search Console
- [ ] Update the domain on LinkedIn, Upwork, Facebook and email signatures
- [ ] Shut down old hosting once traffic has moved

**Done when:** the domain serves the new site over HTTPS, old links redirect, and email works.

---

## Open questions

- Custom domain name?
- English only, or also Bulgarian / Spanish?
- Analytics: wanted? Which one?
- Self-host fonts instead of Google Fonts (GDPR, if EU visitors matter)?
- How many projects at launch, and are the photos ready?
