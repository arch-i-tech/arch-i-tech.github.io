// Runs after `astro build` (npm "postbuild"). Astro copies every original image into
// dist/_astro even when pages only use the resized versions; with hundreds of large
// renders that nearly fills GitHub Pages' 1 GB limit. Delete images nothing references.
import { readdir, readFile, stat, unlink } from 'node:fs/promises';
import { join, extname } from 'node:path';

const DIST = 'dist';
const IMAGE = new Set(['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif']);
const TEXT = new Set(['.html', '.css', '.js', '.xml', '.json', '.webmanifest', '.txt']);

async function walk(dir) {
  const out = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) out.push(...(await walk(p)));
    else out.push(p);
  }
  return out;
}

const files = await walk(DIST);
let text = '';
for (const f of files) if (TEXT.has(extname(f).toLowerCase())) text += await readFile(f, 'utf8');

let removed = 0;
let bytes = 0;
for (const name of await readdir(join(DIST, '_astro'))) {
  const f = join(DIST, '_astro', name);
  if (!IMAGE.has(extname(name).toLowerCase())) continue;
  if (text.includes(name)) continue;
  bytes += (await stat(f)).size;
  await unlink(f);
  removed++;
}
console.log(`prune-unused-images: removed ${removed} unreferenced images (${(bytes / 2 ** 20).toFixed(0)} MB)`);
