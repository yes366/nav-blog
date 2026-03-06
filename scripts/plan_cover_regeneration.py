#!/usr/bin/env python3
import json
import re
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "content" / "blog"
MANIFEST_PATH = BLOG_DIR / "visual_manifest.json"

STYLE_SUFFIX = (
    "Create a premium 21:9 editorial hero image for a blog cover. "
    "Appeal to anime and AI roleplay users while staying polished and high-quality. "
    "Use cinematic composition, clean focal subject, rich atmosphere, and tasteful lighting. "
    "No text, no letters, no logos, no watermark, no UI chrome, no panels, no collage."
)


def infer_prompt(title: str, slug: str) -> str:
    lower = f"{title} {slug}".lower()

    if "voice" in lower:
        return (
            "A stylish close-up of a character speaking into a glowing phone call interface, "
            "soft neon ambience, intimate conversational mood, polished anime-inspired realism. "
            + STYLE_SUFFIX
        )
    if "language learning" in lower or "conversation practice" in lower:
        return (
            "A confident young person practicing conversation with an AI companion in a modern cafe, "
            "subtle phone glow, calm focused expression, contemporary lifestyle editorial scene. "
            + STYLE_SUFFIX
        )
    if "tabletop" in lower or "dungeon" in lower or "storytelling" in lower:
        return (
            "A game master desk with maps, dice, notebooks, and a luminous character apparition emerging from the story world, "
            "cinematic fantasy-tech atmosphere. "
            + STYLE_SUFFIX
        )
    if "character builder" in lower or "create" in lower:
        return (
            "A creator shaping an AI character concept with floating mood fragments, character silhouettes, and polished worldbuilding details, "
            "premium editorial key art. "
            + STYLE_SUFFIX
        )
    if "girlfriend" in lower or "boyfriend" in lower or "companion" in lower or "romance" in lower:
        return (
            "A tender anime-inspired companion scene with warm lighting, intimate eye contact, and emotionally rich atmosphere, "
            "tasteful and premium, not explicit. "
            + STYLE_SUFFIX
        )
    if "anime" in lower:
        return (
            "A vivid anime-inspired cast portrait with distinct personalities and elegant color harmony, "
            "high-end key visual styling for a feature article. "
            + STYLE_SUFFIX
        )
    if "image generation" in lower:
        return (
            "A polished creator scene with beautifully rendered character art drafts, cinematic glow, and premium creative studio energy, "
            "focused on visual imagination not software UI. "
            + STYLE_SUFFIX
        )
    if "writer" in lower or "creative writing" in lower:
        return (
            "A writer at a desk with floating story fragments, notebooks, and moody light, "
            "editorial fantasy-tech aesthetic with anime fan appeal. "
            + STYLE_SUFFIX
        )
    if "no filter" in lower:
        return (
            "A dramatic late-night chat atmosphere with moody light and mysterious emotional tension, "
            "clean editorial composition for an article about creative freedom. "
            + STYLE_SUFFIX
        )
    return (
        f"A high-quality editorial anime-inspired hero image for the article titled '{title}', "
        "with one clear focal subject, cinematic atmosphere, and premium visual storytelling. "
        + STYLE_SUFFIX
    )


def load_manifest() -> Dict[str, Dict[str, object]]:
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def parse_meta(md_path: Path) -> Dict[str, str]:
    text = md_path.read_text(encoding="utf-8")
    title = re.search(r'^title:\s*"?(.*?)"?$', text, re.M)
    cover = re.search(r'^cover:\s*"?(.*?)"?$', text, re.M)
    return {
        "slug": md_path.stem,
        "title": title.group(1) if title else md_path.stem,
        "cover": cover.group(1) if cover else "",
    }


def main() -> None:
    manifest = load_manifest()
    changed = 0
    for md_path in sorted(BLOG_DIR.glob("*.md")):
        meta = parse_meta(md_path)
        slug = meta["slug"]
        entry = manifest.setdefault(slug, {})
        entry["mode"] = "generated_editorial"
        entry["prompt"] = infer_prompt(meta["title"], slug)
        entry["notes"] = (
            "21:9 cover image only. No text, no letters, no logos, no watermark, "
            "no website UI, no collage."
        )
        changed += 1
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"updated_manifest_entries {changed}")


if __name__ == "__main__":
    main()
