# Content import logs

Everything pulled into the site from outside the repo is logged here for review.

| File | What |
|---|---|
| [blogger-import-log.md](blogger-import-log.md) | Every post imported from https://arch-i-tech.blogspot.com/ — slug, source post, categories and where they came from, image/video counts, and ⚠ items to check |
| [blogger-import.json](blogger-import.json) | The same, machine-readable, including every image URL |
| [local-files-log.md](local-files-log.md) | Files used from the local project folder `D:\Projects\Arch-I-Tech_Web_Site_09.01.12` |

## How the blog import works

`scripts/import-blogger.py` (one-off, Python 3 + `beautifulsoup4`, `markdownify`, `Pillow`):

1. Reads the Blogger JSON feeds for posts and static pages.
2. Downloads each image's original upload (Blogger `s0` size) to
   `D:\Projects\Arch-I-Tech_Web_Site_09.01.12\GITHUB\OriginalBloggerImages\<slug>\` — untouched bytes, outside the repo.
3. Writes a site copy next to the project's `index.md`: unchanged if already ≤ 2560 px, otherwise downscaled to
   2560 px on the long edge (JPEG q85).
4. Copies the post text verbatim (HTML → Markdown). Images become the cover + gallery; YouTube embeds become
   `videos`; the 2026 case studies' stat boxes become `facts`, and their image alt texts / captions are kept.
5. Categories come from the blog's own category pages (Architecture, Interior Design, Landscape Architecture,
   3D Animation, Projection Mapping → 3D Animation, Master Planning) and otherwise from the post's labels.

Re-running it overwrites the imported `index.md` files (not `ocean-lake-resort`, which was hand-made from the
design canvas). Originals already downloaded are reused, so a re-run doesn't hit the network for images.

Feeds used: `https://arch-i-tech.blogspot.com/feeds/posts/default?alt=json&max-results=500` and
`https://arch-i-tech.blogspot.com/feeds/pages/default?alt=json`.
