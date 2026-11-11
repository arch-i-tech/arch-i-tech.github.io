# Phase 1 review — left to do

Written 2026-11-11 after the phase 1 review. The code issues found in that review are fixed; what is
left are content decisions and the open items from [plan.md](plan.md). Tick items off as they are done.

Each project is edited in `src/content/projects/<slug>/index.md` (or in the CMS once phase 2 is set up).
Re-running `scripts/import-blogger.py` overwrites the imported files, so hand edits would be lost.

## Open plan items

- [ ] Team portraits for Irina Rizova and Borislav Stoynev (About page shows initials)
- [ ] Final copy review: home, projects, about pages
- [ ] Repo **Settings → Pages → Source: GitHub Actions**
- [ ] Push to `main` and confirm the workflow deploys (the new image cache in `deploy.yml` is untested until then)
- [ ] Team reviews the preview at https://arch-i-tech.github.io

## Project content

### Summary is the same as the title (5)

The page hides the repeated line, but the summary is still used in search results and link previews.
Write a one- or two-sentence summary.

- [ ] `5-star-hotel-in-myanmar`
- [ ] `hi-tech-data-center`
- [ ] `mixed-use-building-in-revere-ma-usa`
- [ ] `nimasa-burutu-2015`
- [ ] `promo-arch-i-tech-2009`

### Summary is only a place or year (2)

- [ ] `kitchen-interior` — "USA, 2026"
- [ ] `tropical-villa-design` — "LUXURY VILLA, 2014"

### Possible duplicates

Decide whether to merge, or mark one as `draft: true`.

- [ ] `silverlight-gardens-wellness-recreational-campus` (featured, 10 gallery images) and
      `silverlight-gardens-therapeutic-recreational-campus-bronx-ri` (57 gallery images)
- [ ] `mixed-use-building-in-revere-ma-usa` and `mixed-use-residential-building-in-revere-ma-usa`

### Blog boilerplate in the text (109 projects)

Text was copied verbatim from the blog. These bodies contain "Category: … / Project: …" lines that repeat
the facts already shown above the text; 54 of them also carry the Bulgarian version of each line.
Decide once whether to strip these lines (it can be scripted) and whether to keep the Bulgarian text.

- [ ] Decision: strip "Category / Project" lines?
- [ ] Decision: keep or remove Bulgarian text? (ties in with the language question in plan.md)

### Image descriptions (87 projects)

Every gallery image in these projects uses the project title as its description. Fine as a fallback;
real descriptions ("Lobby", "Site plan", …) are better for screen readers and search. Low priority —
start with the featured projects.

### Cover is a YouTube thumbnail, no gallery (14)

Some thumbnails are low resolution. Replace with a proper still where one exists
(the `03_PORTFOLIO_WEB` folder in the parent project folder has higher-resolution renders).

- [ ] `3d-animation-2012`
- [ ] `3d-mapping-hilton-sofia-2011`
- [ ] `aquarius-system-2010-2012`
- [ ] `australian-new-south-wales-3d-historical-reconstruction`
- [ ] `beckside-park-bradford`
- [ ] `dolphins-bay-2008`
- [ ] `fountains-of-benguela-2009`
- [ ] `nimasa-burutu-2015`
- [ ] `promo-arch-i-tech-2009`
- [ ] `rise-of-the-quantum-traveller-cg-animation`
- [ ] `sports-hall-2010`
- [ ] `taste-of-bulgaria-2011`
- [ ] `tsupod-device-to-save-people-during-tsunami`
- [ ] `urban-rejuvenation-2011`

### Single image, no video (6)

Thin pages — add images, or mark as `draft: true`.

- [ ] `main-mufti-2007`
- [ ] `master-plan-eco-village`
- [ ] `mobile-homes-elevado-estates`
- [ ] `office-interior-home-life`
- [ ] `renovation-chateau-2012`
- [ ] `soccer-ball-trash-bin-2010`

### No year (24)

- [ ] `5-star-hotel-in-myanmar`
- [ ] `al-brayeh-city`
- [ ] `amphibious-space-ship-cinematic-shot`
- [ ] `at-the-base-of-the-rock-gibraltar`
- [ ] `chahna`
- [ ] `container-family-house`
- [ ] `facade-patio-main-entry`
- [ ] `feeding-the-future`
- [ ] `gallya-grove`
- [ ] `hi-tech-data-center`
- [ ] `ibis-hotel`
- [ ] `micro-city`
- [ ] `mixed-use-building-in-revere-ma-usa`
- [ ] `mixed-use-residential-building-in-revere-ma-usa`
- [ ] `ocean-lake-resort`
- [ ] `quebrada-de-bicho-prieto`
- [ ] `residence-with-pool-house`
- [ ] `rise-of-the-quantum-traveller-cg-animation`
- [ ] `silverlight-gardens-therapeutic-recreational-campus-bronx-ri`
- [ ] `silverlight-gardens-wellness-recreational-campus`
- [ ] `sport-facility`
- [ ] `via-de-la-paz`
- [ ] `vistas-apartment-complex`
- [ ] `warehouse-odisha-india`

### No location (70)

The card and the facts row simply leave the location out. Fill in where known.

- [ ] `3d-animation-2012`
- [ ] `adenta-valley`
- [ ] `amphibious-space-ship-cinematic-shot`
- [ ] `aquapak-2007`
- [ ] `aquarius-system-2010-2012`
- [ ] `australian-new-south-wales-3d-historical-reconstruction`
- [ ] `bay-huts-and-marina-2007`
- [ ] `beckside-park-bradford`
- [ ] `belize`
- [ ] `benguela-gardens-2008`
- [ ] `bio-solar-design-concept-2010`
- [ ] `chahna`
- [ ] `clark-avenue-residential`
- [ ] `clearwater`
- [ ] `cliff-restaurant-2007`
- [ ] `container-family-house`
- [ ] `dolphins-bay-2008`
- [ ] `eco-adventure-resort`
- [ ] `eco-lux-garden-center`
- [ ] `estate-landscape-planning`
- [ ] `facade-patio-main-entry`
- [ ] `facade-redesign`
- [ ] `feeding-the-future`
- [ ] `fountains-of-benguela-2009`
- [ ] `front-signage-strand`
- [ ] `glamping-eco-village`
- [ ] `health-clinic-wellness-center`
- [ ] `hi-tech-data-center`
- [ ] `hotel-coral-2008`
- [ ] `hotel-interiors-restaurants-lobby-room`
- [ ] `hours-of-the-heart-2012`
- [ ] `ibis-hotel`
- [ ] `interior-design-2-studios`
- [ ] `interior-design-projects-2007-2009`
- [ ] `interiors-2010`
- [ ] `looking-over-the-fjord`
- [ ] `main-mufti-2007`
- [ ] `master-plan-eco-village`
- [ ] `mexico-playa-la-majahua-resort`
- [ ] `micro-city`
- [ ] `nimasa-burutu-2015`
- [ ] `north-strathfield-railway-station-active-suburban-transit-hu`
- [ ] `office-interior-home-life`
- [ ] `pavilions-strand`
- [ ] `planning-and-architecture-for-eco-adventure-resort`
- [ ] `planters-and-furniture-2012`
- [ ] `promo-arch-i-tech-2009`
- [ ] `renovation-chateau-2012`
- [ ] `residence-on-a-slope`
- [ ] `residence-with-pool-and-landscape-features`
- [ ] `residence-with-pool-house`
- [ ] `residential-interiors`
- [ ] `rise-of-the-quantum-traveller-cg-animation`
- [ ] `roof-top-restaurant`
- [ ] `shtastliveca-2010`
- [ ] `soccer-ball-trash-bin-2010`
- [ ] `sport-facility`
- [ ] `sports-hall-2010`
- [ ] `swiss-villas-2011`
- [ ] `taste-of-bulgaria-2011`
- [ ] `the-assegai-rock-climbing-centre`
- [ ] `the-sushi-79`
- [ ] `ton-bonbon-2010`
- [ ] `trichkova-vodenitza-complex`
- [ ] `tropical-villa-design`
- [ ] `tsupod-community`
- [ ] `tsupod-device-to-save-people-during-tsunami`
- [ ] `ulpia-oescus-2011`
- [ ] `urban-rejuvenation-2011`
- [ ] `vistas-apartment-complex`

### Other

- [ ] Untitled blog posts were given titles during import (rows marked ⚠ in
      [import/blogger-import-log.md](import/blogger-import-log.md)) — confirm the titles
- [ ] Two Blogger-hosted videos were not migrated: `planning-and-architecture-for-eco-adventure-resort`,
      `museum-sports-amusement-park-complex-kelowna-canada`
