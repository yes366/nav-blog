#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "content" / "blog"
MANIFEST_PATH = BLOG_DIR / "visual_manifest.json"
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
    }

    if mode == "character_reference":
        job["reference_image"] = entry.get("reference_image", "")
    elif mode == "product_screenshot":
        job["screenshot_targets"] = entry.get("screenshot_targets", [])
    else:
        job["prompt_guard"] = "Editorial illustration only. Never include watermark, text, AI letters, or fake product chrome."

    return job


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", default="", help="Only inspect one blog slug")
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

    print("This script currently prepares curated visual jobs only. Use --dry-run to inspect them.")


if __name__ == "__main__":
    main()
