#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
from typing import Dict, List

import requests
from volcenginesdkarkruntime import Ark

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "content" / "blog"
IMG_DIR = BLOG_DIR / "images"
MANIFEST_PATH = BLOG_DIR / "visual_manifest.json"
MODEL = "doubao-seedream-4-5-251128"
SIZE = "2K"
COVER_RATIO = (21, 9)
COVER_SIZE = (2100, 900)
API_KEY = os.getenv("ARK_API_KEY") or "72620536-bd74-4b1a-8460-4ad165b1ddb3"
NEGATIVE_RULES = [
    "no watermark",
    "no text",
    "no letters",
    "no logo",
    "no ai caption",
    "no fake interface",
    "no extra fingers",
    "no low quality mobile screenshot",
]


def load_manifest() -> Dict[str, Dict[str, object]]:
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def build_visual_job(post: Dict[str, object], manifest: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    slug = str(post["slug"])
    entry = manifest.get(slug, {})
    mode = str(entry.get("mode", "generated_editorial"))

    job = {
        "slug": slug,
        "title": post.get("title", slug),
        "mode": mode,
        "notes": entry.get("notes", ""),
        "negative_rules": NEGATIVE_RULES,
        "prompt": entry.get("prompt", ""),
    }

    if mode == "character_reference":
        job["reference_image"] = entry.get("reference_image", "")
    elif mode == "product_screenshot":
        job["screenshot_targets"] = entry.get("screenshot_targets", [])
    else:
        job["prompt_guard"] = "Editorial illustration only. Never include watermark, text, AI letters, or fake product chrome."

    return job


def build_prompt(job: Dict[str, object]) -> str:
    base = str(job.get("prompt") or f"Editorial illustration for {job['title']}")
    negatives = ", ".join(NEGATIVE_RULES)
    return f"{base} Strict exclusions: {negatives}."


def build_generate_request(job: Dict[str, object]) -> Dict[str, object]:
    return {
        "model": MODEL,
        "prompt": build_prompt(job),
        "size": SIZE,
        "watermark": False,
    }


def build_cover_output_path(slug: str) -> Path:
    return Path("content/blog/images") / f"{slug}-cover.jpg"


def collect_posts() -> List[Dict[str, object]]:
    posts = []
    for md_path in sorted(BLOG_DIR.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        title = md_path.stem
        for line in text.splitlines():
            if line.startswith("title:"):
                title = line.split(":", 1)[1].strip().strip('"').strip("'")
                break
        posts.append({"slug": md_path.stem, "title": title})
    return posts


def render_generated_editorial(job: Dict[str, object]) -> Path:
    client = Ark(api_key=API_KEY)
    response = client.images.generate(**build_generate_request(job))
    image_url = response.data[0].url
    result = requests.get(image_url, timeout=120)
    result.raise_for_status()

    out_path = IMG_DIR / f"{job['slug']}.jpg"
    out_path.write_bytes(result.content)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", default="", help="Only inspect or render one blog slug")
    parser.add_argument("--dry-run", action="store_true", help="Print the selected visual job without generating assets")
    args = parser.parse_args()

    manifest = load_manifest()
    posts = collect_posts()
    if args.slug:
        posts = [post for post in posts if post["slug"] == args.slug]

    jobs = [build_visual_job(post, manifest) for post in posts]

    if args.dry_run:
        for job in jobs:
            print(json.dumps(job, ensure_ascii=False, indent=2))
        return

    for job in jobs:
        if job["mode"] != "generated_editorial":
            print(f"skip {job['slug']} mode={job['mode']}")
            continue
        out_path = render_generated_editorial(job)
        print(f"rendered {job['slug']} -> {out_path}")


if __name__ == "__main__":
    main()
