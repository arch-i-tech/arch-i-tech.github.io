"""One-off importer: arch-i-tech.blogspot.com posts -> src/content/projects/<slug>/.

Usage:
  python scripts/import-blogger.py <feed.json> <pages.json> [--download]

- Reads the Blogger JSON feeds (posts + static pages).
- Saves every original image to ../OriginalBloggerImages/<slug>/ (untouched bytes).
- Writes a site copy of each image, downscaled to max 2560px, next to index.md.
- Copies post text verbatim (HTML -> Markdown), YouTube videos into `videos`.
- Writes docs/import/blogger-import.json and docs/import/blogger-import-log.md.

Without --download it only plans (no network, no files except the log).
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import html
import io
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, Comment
from markdownify import markdownify
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
PROJECTS = REPO / "src" / "content" / "projects"
ORIGINALS = REPO.parent / "OriginalBloggerImages"
LOGDIR = REPO / "docs" / "import"
MAX_EDGE = 2560

# The six 2026 case studies, featured on the home page in this order.
FEATURED = [
    "al-brayeh-city",
    "quebrada-de-bicho-prieto",
    "ocean-lake-resort",
    "via-de-la-paz",
    "gallya-grove",
    "silverlight-gardens-wellness-recreational-campus",
]
# Projects that already exist in the repo (built from the design canvas) and must not be overwritten.
KEEP_EXISTING = {"ocean-lake-resort"}

# Untitled posts on the blog: titles assigned here from their "Project:" line and labels.
UNTITLED = {
    "/2026/04/blog-post_66.html": ("Kitchen Interior", "USA"),
    "/2026/04/blog-post_16.html": ("Hi-Tech Data Center", ""),
    "/2026/04/blog-post_41.html": ("Planning and architecture for Eco-Adventure resort", ""),
    "/2026/04/blog-post_56.html": ("School and Public Building", "CA, USA"),
    "/2026/04/blog-post_0.html": ("Residential Tower", "USA"),
    "/2026/04/blog-post_9.html": ("Tropical Fruit Farm", "USA"),
    "/2026/04/blog-post_25.html": ("Vegetable Farm", "USA"),
    "/2026/04/blog-post_93.html": ("Residence with Pool House", ""),
    "/2026/04/blog-post_12.html": ("Farm Warehouse", "USA"),
    "/2026/04/blog-post_8.html": ("Grain House", "USA"),
    "/2026/04/blog-post_3.html": ("Residence", "CA, USA"),
}

CATS = ["Master Planning", "Architecture", "Landscape Architecture", "Interior Design", "3D Animation"]

# Blogger static pages that list posts per discipline -> our category.
PAGE_CATS = {
    "MASTER PLANNING": "Master Planning",
    "ARCHITECTURE": "Architecture",
    "INTERIOR DESIGN": "Interior Design",
    "LANDSCAPE ARCHITECTURE": "Landscape Architecture",
    "3D ANIMATION": "3D Animation",
    "PROJECTION MAPPING": "3D Animation",
}

# Post labels -> category (lower-case substring match, checked in order).
LABEL_RULES = [
    ("Master Planning", ["master plan", "master paln", "urban plan", "urban design", "planning", "planing",
                         "zoning", "eco village", "градоустройство", "урбанизъм", "пуп"]),
    ("Landscape Architecture", ["landscape", "garden", "pool design", "park", "ландшафт", "градина", "planters"]),
    ("Interior Design", ["interior", "restaurant", "lobby", "hotel room", "furniture", "kitchen", "office interior",
                         "food court", "shop design", "интериор"]),
    ("3D Animation", ["animation", "fly through", "walk through", "vfx", "3d projection", "mapping",
                      "documentary", "анимация", "мапинг"]),
    ("Architecture", ["architecture", "building", "house", "hotel", "villa", "residence", "residential",
                      "facade", "warehouse", "farm", "pavilion", "архитектура", "data center", "museum"]),
]


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return re.sub(r"-{2,}", "-", text)


def norm_post_path(url: str) -> str:
    """Blogger post URL -> '/2018/03/foo.html' (ignores domain .com/.bg and query)."""
    p = urllib.parse.urlparse(url)
    return p.path


def original_url(src: str) -> str:
    """Blogger image URL -> URL of the original upload."""
    if "/img/a/" in src:
        base = re.sub(r"=[^/]*$", "", src)
        return base + "=s0"
    # .../s1600/name.jpg, .../w640-h480/name.jpg, .../s320-rw/name.jpg
    return re.sub(r"/(s\d+|w\d+-h\d+|s\d+-[a-z-]+|w\d+-h\d+-[a-z-]+)/(?=[^/]+$)", "/s0/", src)


def image_key(url: str) -> str:
    u = original_url(url)
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^(\d+\.)?bp\.blogspot\.com", "bp", u)
    return u


def image_name(url: str) -> str:
    if "/img/a/" in url:
        return ""
    name = urllib.parse.unquote(url.rsplit("/", 1)[-1])
    name = re.sub(r"\.[a-zA-Z0-9]+$", "", name)
    return slugify(name)[:40]


def is_blogger_image(url: str) -> bool:
    return bool(re.search(r"(blogger\.googleusercontent\.com/img|bp\.blogspot\.com|ggpht\.com)", url))


def youtube_id(src: str) -> str | None:
    m = re.search(r"(?:youtube(?:-nocookie)?\.com/(?:embed|v)/|youtu\.be/|ytimg\.com/vi/)([A-Za-z0-9_-]{11})", src)
    return m.group(1) if m else None


def parse_post(entry: dict) -> dict:
    raw = entry["content"]["$t"]
    soup = BeautifulSoup(raw, "html.parser")
    for t in soup(["style", "script"]):
        t.decompose()
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()

    # Case-study posts (2026): stat boxes / metrics / fact items -> facts.
    facts: list[dict] = []
    for box in soup.select(".stat-box, .ait-fact-item"):
        strong = box.find("strong")
        if strong:
            label = strong.get_text(" ", strip=True).rstrip(":")
            strong.extract()
            value = box.get_text(" ", strip=True)
            if label and value:
                facts.append({"label": label, "value": value})
        box.decompose()
    for wrap in soup.select(".ait-metrics-bar > div"):
        v, l = wrap.select_one(".ait-metric-value"), wrap.select_one(".ait-metric-label")
        if v and l:
            facts.append({"label": l.get_text(" ", strip=True), "value": v.get_text(" ", strip=True)})
    sub = soup.select_one(".ait-subtitle")
    subtitle = sub.get_text(" ", strip=True) if sub else ""
    for t in soup.select(".ait-metrics-bar, .ait-project-stats, .ait-project-facts, .ait-title"):
        t.decompose()

    # Alt text and captions written on the blog, keyed by image.
    alts: dict[str, str] = {}
    captions: dict[str, str] = {}
    for img in soup.find_all("img"):
        a = img.find_parent("a")
        u = a.get("href") if a is not None and is_blogger_image(a.get("href", "")) else img.get("src", "")
        k = image_key(u)
        alt = (img.get("alt") or "").strip()
        if alt and alt.lower() not in {"hero image", "image"}:
            alts[k] = alt
        node = img
        for _ in range(4):
            node = node.parent
            if node is None:
                break
            cap = node.find(class_=re.compile("caption"))
            if cap:
                captions[k] = cap.get_text(" ", strip=True)
                cap.decompose()
                break

    images: list[str] = []
    seen: set[str] = set()

    def add_img(u: str):
        if not u or not is_blogger_image(u):
            return
        k = image_key(u)
        if k not in seen:
            seen.add(k)
            images.append(u)

    for a in soup.find_all("a"):
        href = a.get("href", "")
        if a.find("img") and is_blogger_image(href):
            add_img(href)
    for img in soup.find_all("img"):
        add_img(img.get("src", ""))

    videos: list[str] = []
    blogger_videos: list[str] = []
    for tag in soup.find_all(["iframe", "embed", "object", "param"]):
        for attr in ("src", "data", "value", "data-thumbnail-src"):
            v = tag.get(attr, "")
            if not v:
                continue
            yid = youtube_id(v)
            if yid and yid not in videos:
                videos.append(yid)
            elif "blogger.com/video" in v and v not in blogger_videos:
                blogger_videos.append(v)
    # Plain links to YouTube in the text count too.
    for a in soup.find_all("a"):
        yid = youtube_id(a.get("href", ""))
        if yid and yid not in videos:
            videos.append(yid)

    # Body: remove media (moved to gallery / videos), keep text verbatim.
    for tag in soup.find_all(["img", "iframe", "embed", "object", "video"]):
        tag.decompose()
    for a in soup.find_all("a"):
        if not a.get_text(strip=True):
            a.decompose()
        elif is_blogger_image(a.get("href", "")):
            a.unwrap()
    for blk in soup.find_all(["div", "li"]):
        blk.insert_after(soup.new_tag("br"))
    md = markdownify(str(soup), heading_style="ATX", bullets="-", strip=["span", "font", "div"])
    md = html.unescape(md).replace("\xa0", " ")
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = md.replace("****", "**\n\n**")
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    # Lines that are only formatting leftovers.
    md = "\n".join(l for l in md.splitlines() if l.strip() not in {"**", "****", "*", "__", "\\", "."})
    md = re.sub(r"\n{3,}", "\n\n", md).strip()

    text = re.sub(r"\s+", " ", BeautifulSoup(md, "html.parser").get_text()).strip()

    link = next((l["href"] for l in entry["link"] if l["rel"] == "alternate"), "")
    return {
        "title": entry["title"]["$t"].strip(),
        "published": entry["published"]["$t"][:10],
        "updated": entry["updated"]["$t"][:10],
        "url": link,
        "path": norm_post_path(link),
        "labels": [c["term"] for c in entry.get("category", [])],
        "images": images,
        "alts": {image_key(u): alts.get(image_key(u), "") for u in images},
        "captions": {image_key(u): captions.get(image_key(u), "") for u in images},
        "facts": facts,
        "videos": videos,
        "bloggerVideos": blogger_videos,
        "body": md,
        "text": text,
        "subtitle": subtitle,
    }


def page_categories(pages: dict) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for e in pages["feed"].get("entry", []):
        cat = PAGE_CATS.get(e["title"]["$t"].strip().upper())
        if not cat:
            continue
        for href in re.findall(r'href="([^"]+)"', e["content"]["$t"]):
            if "blogspot." in href and href.endswith(".html") or ".html?" in href:
                out.setdefault(norm_post_path(href), set()).add(cat)
    return out


def label_categories(labels: list[str], title: str) -> list[str]:
    hay = " | ".join(labels + [title]).lower()
    found = [cat for cat, keys in LABEL_RULES if any(k in hay for k in keys)]
    return found


def derive_title(p: dict) -> tuple[str, bool]:
    """Untitled posts: take the 'Project:' line, else the first text line. Returns (title, needs_review)."""
    if p["title"]:
        return p["title"], False
    if p["path"] in UNTITLED:
        return UNTITLED[p["path"]][0], True
    m = re.search(r"Project\s*:\s*([^\n*]+)", p["body"])
    if m:
        t = re.sub(r"[*_#]", "", m.group(1)).strip(" ;,.")
        if t:
            return t[:90], True
    for line in p["body"].splitlines():
        t = re.sub(r"[*_#>\[\]]", "", line).strip()
        if len(t) > 3:
            return t[:90], True
    return ", ".join(p["labels"][:3]) or "Untitled project", True


def derive_year(p: dict, title: str) -> int | None:
    for src in (title, p["body"][:600]):
        ys = [int(y) for y in re.findall(r"\b(19[89]\d|20[0-2]\d)\b", src)]
        if ys:
            return max(ys)
    return None


NOT_PLACES = {"patio", "main entry", "lobby", "room", "sports & amusement park complex"}


def derive_location(p: dict, title: str, facts: list[dict]) -> str:
    for f in facts:
        if f["label"].lower() == "location":
            return f["value"]
    if p["path"] in UNTITLED:
        return UNTITLED[p["path"]][1]
    if p["published"] >= "2026-07":
        m = re.search(r"(?:—|,|\bin)\s+([A-Z][^—:|]+)$", title)
        return m.group(1).strip() if m else ""
    first, *rest = [s.strip() for s in title.split(",")]
    m = re.search(r"\bin\s+([A-Z].*)$", first)
    parts = ([m.group(1)] if m else []) + rest
    clean = []
    for s in parts:
        if re.search(r"[\u0400-\u04FF]", s) or s.lower() in NOT_PLACES:
            continue
        s = re.sub(r"\s*\b(19|20)\d\d\b.*$", "", s)
        s = re.sub(r"\s*-\s*STAGE\s*\d+", "", s, flags=re.I).strip(" .")
        if s and not s.isdigit():
            clean.append(s)
    return ", ".join(clean)[:80]


LABEL_LINE = re.compile(r"^\W*(category|категория|project|проект|location|client|клиент)\s*:", re.I)


def clean_inline(t: str) -> str:
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)|\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[*_#>\\]", "", t)
    return re.sub(r"\s+", " ", t).strip(" ;,")


def first_sentence(t: str) -> str:
    m = re.match(r"(.{40,260}?[.!?])(?=\s+[A-Z„\"]|$)", t)
    return (m.group(1) if m else t[:260]).strip()


def summary_from(p: dict, title: str) -> str:
    if p.get("subtitle"):
        return p["subtitle"]
    for line in p["body"].splitlines():
        t = clean_inline(line)
        if len(t) < 25 or LABEL_LINE.match(t) or re.search(r"https?://", t):
            continue
        if len(re.findall(r"[\u0400-\u04FF]", t)) > len(t) / 4:
            continue
        return first_sentence(t)
    flat = clean_inline(p["body"])
    m = re.search(r"Project\s*:\s*(.+?)(?=\s*(?:Проект|Категория|Category|Location)\s*:|$)", flat)
    if m and len(m.group(1)) > 3:
        return m.group(1).strip(" ;,")[:260]
    return title


def yaml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def fetch(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (site migration script)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get("Content-Type", "")


EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp"}


def save_image(url: str, orig_dir: Path, site_dir: Path, stem: str) -> dict:
    """Download the original, keep it untouched, write a <=2560px site copy. Returns metadata."""
    orig_dir.mkdir(parents=True, exist_ok=True)
    existing = list(orig_dir.glob(stem + ".*"))
    if existing:
        data = existing[0].read_bytes()
        ext = existing[0].suffix
        src_used = "cache"
    else:
        tried = [original_url(url), url]
        data, ctype, src_used = b"", "", ""
        for u in tried:
            try:
                data, ctype = fetch(u)
                src_used = u
                if data:
                    break
            except Exception as e:  # noqa: BLE001
                src_used = f"ERROR {e}"
        if not data:
            return {"url": url, "error": src_used}
        ext = EXT.get(ctype.split(";")[0].strip(), "")
        if not ext:
            fmt = Image.open(io.BytesIO(data)).format or "JPEG"
            ext = {"JPEG": ".jpg", "PNG": ".png", "GIF": ".gif", "WEBP": ".webp"}.get(fmt, ".jpg")
        (orig_dir / (stem + ext)).write_bytes(data)

    im = Image.open(io.BytesIO(data))
    w, h = im.size
    site_dir.mkdir(parents=True, exist_ok=True)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    out_ext = ".png" if (ext == ".png" and has_alpha) else ".jpg"
    out = site_dir / (stem + out_ext)
    if max(w, h) <= MAX_EDGE and ext == out_ext:
        out.write_bytes(data)
        resized = False
    else:
        im.seek(0)
        im = im.convert("RGBA" if out_ext == ".png" else "RGB")
        if max(w, h) > MAX_EDGE:
            im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
        if out_ext == ".png":
            im.save(out, optimize=True)
        else:
            im.save(out, quality=85, optimize=True, progressive=True)
        resized = True
    return {
        "url": url,
        "downloadedFrom": src_used,
        "original": str((orig_dir / (stem + ext)).relative_to(ORIGINALS.parent)).replace("\\", "/"),
        "originalSize": [w, h],
        "originalBytes": len(data),
        "site": out.name,
        "siteSize": list(Image.open(out).size),
        "converted": resized,
        "sha1": hashlib.sha1(data).hexdigest()[:12],
    }


def main() -> None:
    feed_path, pages_path = Path(sys.argv[1]), Path(sys.argv[2])
    download = "--download" in sys.argv
    feed = json.loads(feed_path.read_text(encoding="utf-8"))
    pages = json.loads(pages_path.read_text(encoding="utf-8"))
    page_cats = page_categories(pages)

    posts = [parse_post(e) for e in feed["feed"]["entry"]]
    posts.sort(key=lambda p: p["published"], reverse=True)

    used_slugs: set[str] = set()
    records = []
    for i, p in enumerate(posts):
        title, title_review = derive_title(p)
        base = slugify(title.split(" — ")[0].split(":")[0] if p["published"] >= "2026-07" else title) or "project"
        # 2026 case studies have long subtitles; keep the project name only for the slug.
        if p["published"] >= "2026-07":
            base = slugify(re.split(r"\s[—|:-]\s|:\s", title)[0])
            if base == "silverlight-gardens":
                base = "silverlight-gardens-wellness-recreational-campus"
        slug = base[:60].strip("-")
        n = 2
        while slug in used_slugs:
            slug = f"{base[:57]}-{n}"
            n += 1
        used_slugs.add(slug)

        cats_page = sorted(page_cats.get(p["path"], set()), key=CATS.index)
        cats_label = label_categories(p["labels"], title)
        cats = cats_page or cats_label
        cat_source = "blog category page" if cats_page else ("post labels" if cats_label else "default")
        if not cats:
            cats = ["Architecture"]
        if (p["videos"] or p["bloggerVideos"]) and not p["images"] and "3D Animation" not in cats:
            cats = cats + ["3D Animation"]
        cats = sorted(set(cats), key=CATS.index)

        year = derive_year(p, title)
        records.append({
            "slug": slug,
            "title": title,
            "titleNeedsReview": title_review,
            "originalTitle": p["title"],
            "url": p["url"],
            "published": p["published"],
            "labels": p["labels"],
            "categories": cats,
            "categorySource": cat_source,
            "year": year,
            "yearSource": "title/text" if year else "none",
            "location": derive_location(p, title, p["facts"]),
            "facts": [f for f in p["facts"] if f["label"].lower() != "location"],
            "alts": p["alts"],
            "captions": p["captions"],
            "summary": summary_from(p, title),
            "videos": p["videos"],
            "bloggerVideos": p["bloggerVideos"],
            "imageUrls": p["images"],
            "body": p["body"],
            "featured": slug in FEATURED,
            "order": (FEATURED.index(slug) + 1) if slug in FEATURED else 100 + i,
            "keptExisting": slug in KEEP_EXISTING,
        })

    if download:
        jobs = {}
        with cf.ThreadPoolExecutor(max_workers=8) as ex:
            for r in records:
                site_dir = PROJECTS / r["slug"]
                orig_dir = ORIGINALS / r["slug"]
                for n, u in enumerate(r["imageUrls"], 1):
                    stem = f"{n:02d}" + (f"-{image_name(u)}" if image_name(u) else "")
                    # Existing hand-made projects: originals only, never touch their folder.
                    target = (REPO.parent / "OriginalBloggerImages" / "_unused") if r["keptExisting"] else site_dir
                    jobs[ex.submit(save_image, u, orig_dir, target, stem)] = (r["slug"], n)
                # Video-only posts: YouTube thumbnail as cover.
                if not r["imageUrls"] and r["videos"]:
                    for q in ("maxresdefault", "hqdefault"):
                        u = f"https://i.ytimg.com/vi/{r['videos'][0]}/{q}.jpg"
                        jobs[ex.submit(save_image, u, orig_dir, site_dir, f"00-youtube-{q}")] = (r["slug"], 0)
            results: dict[str, list] = {}
            for f in cf.as_completed(jobs):
                slug, n = jobs[f]
                try:
                    res = f.result()
                except Exception as e:  # noqa: BLE001
                    res = {"error": repr(e)}
                res["n"] = n
                results.setdefault(slug, []).append(res)
                print(f"{slug} #{n}: {'ERR ' + res['error'] if 'error' in res else res['site']}", flush=True)
        for r in records:
            imgs = sorted(results.get(r["slug"], []), key=lambda x: (x["n"], x.get("site", "")))
            # Keep only the best YouTube thumbnail.
            yt = [x for x in imgs if x["n"] == 0 and "error" not in x]
            yt = [x for x in yt if "maxres" in x["site"] and x["originalSize"][0] > 120] or [x for x in yt if "hqdefault" in x["site"]]
            for x in imgs:
                if x["n"] == 0 and x not in yt[:1] and "site" in x:
                    (PROJECTS / r["slug"] / x["site"]).unlink(missing_ok=True)
            r["images"] = [x for x in imgs if x["n"] > 0] + yt[:1]
            write_project(r)

    LOGDIR.mkdir(parents=True, exist_ok=True)
    (LOGDIR / "blogger-import.json").write_text(
        json.dumps([{k: v for k, v in r.items() if k != "body"} for r in records], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_log(records, download)
    print(f"{len(records)} posts planned; download={download}")


def write_project(r: dict) -> None:
    if r["keptExisting"]:
        return
    imgs = [x for x in r.get("images", []) if "site" in x]
    folder = PROJECTS / r["slug"]
    if not imgs:
        r["skipped"] = "no images could be downloaded"
        return
    cover, gallery = imgs[0], imgs[1:]
    lines = ["---", f"title: {yaml_str(r['title'])}", f"summary: {yaml_str(r['summary'])}"]
    if r["location"]:
        lines.append(f"location: {yaml_str(r['location'])}")
    if r["year"]:
        lines.append(f"year: {r['year']}")
    lines.append("categories:")
    lines += [f"  - {c}" for c in r["categories"]]
    lines.append(f"cover: ./{cover['site']}")
    def alt_of(x):
        k = image_key(x["url"])
        return r["alts"].get(k) or r["captions"].get(k) or r["title"]

    lines.append(f"coverAlt: {yaml_str(alt_of(cover))}")
    if r["facts"]:
        lines.append("facts:")
        for f in r["facts"]:
            lines.append(f"  - label: {yaml_str(f['label'])}")
            lines.append(f"    value: {yaml_str(f['value'])}")
    if gallery:
        lines.append("gallery:")
        for g in gallery:
            lines.append(f"  - image: ./{g['site']}")
            lines.append(f"    alt: {yaml_str(alt_of(g))}")
            cap = r["captions"].get(image_key(g["url"]))
            if cap:
                lines.append(f"    caption: {yaml_str(cap)}")
    if r["videos"]:
        lines.append("videos:")
        lines += [f"  - youtube: {v}" for v in r["videos"]]
    lines.append(f"source: {r['url']}")
    if r["featured"]:
        lines.append("featured: true")
    lines.append(f"order: {r['order']}")
    lines.append("---")
    lines.append("")
    lines.append(r["body"])
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_log(records: list[dict], downloaded: bool) -> None:
    L = ["# Blogger import log", "",
         "Source: https://arch-i-tech.blogspot.com/ (Blogger JSON feed, all posts + static pages).",
         "Generated by `scripts/import-blogger.py`. Original images: `../OriginalBloggerImages/<slug>/`;",
         f"site copies (max {MAX_EDGE}px) next to each project's `index.md`.", "",
         "Text is copied verbatim from the posts (images and video embeds moved to gallery/videos).",
         "Titles, years, locations and categories are derived automatically. Rows marked ⚠ need a look.", "",
         "| # | Project | Blog post | Published | Year | Categories (source) | Images | Videos | Notes |",
         "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(records, 1):
        notes = []
        if r["titleNeedsReview"]:
            notes.append("⚠ untitled on blog — title assigned during import")
        if r["keptExisting"]:
            notes.append("kept existing design version; originals downloaded only")
        if r["bloggerVideos"]:
            notes.append(f"⚠ {len(r['bloggerVideos'])} Blogger-hosted video(s) not migrated")
        if not r["imageUrls"] and r["videos"]:
            notes.append("cover = YouTube thumbnail")
        if r.get("skipped"):
            notes.append("⚠ SKIPPED: " + r["skipped"])
        errs = [x for x in r.get("images", []) if "error" in x]
        if errs:
            notes.append(f"⚠ {len(errs)} image(s) failed")
        if not r["year"]:
            notes.append("no year found")
        if r["featured"]:
            notes.append("featured")
        title = r["title"].replace("|", "\\|")
        n_imgs = len([x for x in r.get("images", []) if "site" in x]) if downloaded else len(r["imageUrls"])
        L.append(f"| {i} | `{r['slug']}` — {title} | [post]({r['url']}) | {r['published']} | {r['year'] or ''} | "
                 f"{', '.join(r['categories'])} ({r['categorySource']}) | {n_imgs} | {len(r['videos'])} | {'; '.join(notes)} |")
    dupes = {}
    for r in records:
        key = slugify(re.split(r"[:,—\-]", r["title"])[0])[:20]
        dupes.setdefault(key, []).append(r["slug"])
    d = [v for v in dupes.values() if len(v) > 1]
    if d:
        L += ["", "## Possible duplicates", ""] + [f"- {', '.join(f'`{s}`' for s in v)}" for v in d]
    (LOGDIR / "blogger-import-log.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
