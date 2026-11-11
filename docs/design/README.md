# Arch-I-Tech website design

Snapshot of the design canvas, saved 2026-11-11.

Live canvas (editable, the source of truth): https://claude.ai/artifact/12xKffHTSR7tSTXQmDFctX

## What's here

- `canvas/` — the canvas source exactly as published: `canvas.json` (board layout) and one `.dc.html` per page.
  These files need the canvas runtime to render; open the live link to view them. Image `src` values like
  `/_blob/<id>` refer to the files in `assets/` with the same id.
- `assets/` — every image the design uses, named by its id.

| Board | File |
|---|---|
| Home | `canvas/Main.dc.html` |
| Projects (with working filters) | `canvas/Projects.dc.html` |
| Project page — Ocean Lake Resort | `canvas/Project.dc.html` |
| About & Services (team, Upwork/LinkedIn) | `canvas/About.dc.html` |
| Header options A–D (A was chosen) | `canvas/HeaderOptions.dc.html` |

## Design decisions

- **Purpose:** portfolio only. No contact form, email or phone; visitors reach the studio through Upwork
  (studio agency page and personal profiles), with LinkedIn as secondary. Upwork buttons always come before LinkedIn.
- **Menu:** Projects · About. Both behave the same: ink text, accent on hover, accent underline on the current page. (Until 2026-11-11 "About" was always accent-coloured, and a separate "Services" item jumped to the Services section of the About page; both dropped.)
- **Upwork / LinkedIn icons:** the official marks from [Simple Icons](https://simpleicons.org) (CC0), stored once as files and referenced everywhere — on the site `src/assets/icons/upwork.svg` and `linkedin.svg` (they take the text colour), in the canvas the two SVG assets below.
- **Header:** option A — the logo at 64px tall (`width: 19.5rem; max-width: 100%`), menu on the right.
- **Footer (all pages):** dark band with the ARCH-I-TECH wordmark and copyright only.
- **Missing links are left out**, not shown as placeholders.

## Tokens

| Token | Value |
|---|---|
| Background | `#F4F2EE` (alt band `#ECE9E3`, image placeholder `#E2DED7`) |
| Text | `#161616`; secondary `#4A4744`, `#5E5B57`, labels `#6A6560` |
| Accent | `#8B1818` (logo ink is `#7D0000`) |
| Rules | `#D6D1C9`; button outlines `#C9C3BA` |
| Footer | `#161616` background, `#EDEBE7` text, `#A9A49D` muted |
| Fonts | Inter Tight (headings, 300–600), Inter (body, 400–600) — Google Fonts |
| Layout | max width 1360px, 2.5rem side padding |

## Assets

| File | What it is |
|---|---|
| `6196cfe3….png` | Logo, red, transparent, 240px tall — **use this one** |
| `2a0530a5….png` | Logo, white, transparent, 240px tall (for dark backgrounds) |
| `7036884c….png` | Logo, red, 144px tall (older, smaller copy) |
| `6d58aae4….jpg` | Dan Markov portrait, 4:5 |
| `1d7635e8….jpg` | AL-Brayeh City, Kuwait — home hero |
| `db6fbaad….jpg` | Ocean Lake Resort — hero |
| `bb524280….png` | Ocean Lake Resort — site plan |
| `14a5489b….jpg` | Ocean Lake — lagoon toward the Atlantic |
| `a6b25d71….jpg` | Ocean Lake — townhome upper balcony |
| `66510387….jpg` | Ocean Lake — townhome terrace |
| `e9c42bd9….jpg` | Ocean Lake — beachfront recreation lawn |
| `cab06a6a….jpg` | Silverlight Gardens, New York |
| `b6f954dc….jpg` | Quebrada de Bicho Prieto, Lima |
| `184a1052….jpg` | Via De La Paz, Los Angeles |
| `83c768eb….jpg` | Gallya Grove, New Jersey |
| `fcb0e2d3….jpg` | Museum, Sports & Amusement Park, Kelowna |
| `d5caed61….jpg` | Residence on a Slope, California |
| `9ceffc20….jpg` | Glamping Eco Village, Durmitor |
| `1df1e71c….svg` | Upwork icon (Simple Icons, CC0) |
| `279f687c….svg` | LinkedIn icon (Simple Icons, CC0) |

The logo files were made from `arch-i-tech logo/Arch-I-Tech LOGO_RED.png` in the parent project folder
(URL line removed, white made transparent).

## Still open

- Photos for Irina Rizova and Borislav Stoynev (cards show initials for now).
- Upwork profile links for Irina and Dan: two IDs were given (`~0165804fef172522a1`, `~01942d02deedf3b3de`)
  but not yet matched to a person; both buttons point to upwork.com for now.
- The project page is a template filled with Ocean Lake Resort; other projects need their own content.
- More portfolio images are available in `03_PORTFOLIO_WEB/BEST_MISC` and `03_PORTFOLIO_WEB/2019` in the parent folder.
