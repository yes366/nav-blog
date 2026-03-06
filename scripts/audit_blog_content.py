#!/usr/bin/env python3
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "content" / "blog"
REPORTS_DIR = ROOT / "reports"
REPORT_PATH = REPORTS_DIR / "blog_audit.json"
URL_RE = re.compile(r"https://(?:www\.)?naviya\.chat[^)\s\"']*")
WORD_RE = re.compile(r"[a-z0-9]+")


def parse_frontmatter(md_text: str) -> Dict[str, object]:
    if not md_text.startswith("---\n"):
        return {}

    end = md_text.find("\n---\n", 4)
    if end < 0:
        return {}

    frontmatter = md_text[4:end]
    data: Dict[str, object] = {}

    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")

    tags_raw = str(data.get("tags", "[]"))
    if tags_raw.startswith("[") and tags_raw.endswith("]"):
        data["tags"] = [
            item.strip().strip('"').strip("'")
            for item in tags_raw[1:-1].split(",")
            if item.strip()
        ]
    else:
        data["tags"] = []

    return data


def title_similarity(title_a: str, title_b: str) -> float:
    words_a = set(WORD_RE.findall(title_a.lower()))
    words_b = set(WORD_RE.findall(title_b.lower()))
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


def infer_image_mode(post: Dict[str, object]) -> str:
    title = str(post.get("title", "")).lower()
    slug = str(post.get("slug", "")).lower()
    tags = [str(tag).lower() for tag in post.get("tags", [])]

    character_signals = (
        title.startswith("meet ")
        or title.startswith("chat with ")
        or "character spotlight" in tags
        or "villain" in slug
        or "mystery-characters" in slug
        or "fantasy-roleplay-characters" in slug
    )
    if character_signals:
        return "character_generated"

    screenshot_signals = (
        "apps" in title
        or "builder" in title
        or "comparison" in title
        or "guide" in slug
        or "tabletop" in slug
        or "image-generation" in slug
    )
    if screenshot_signals:
        return "product_generated"

    return "generated"


def fetch_status_code(url: str) -> int:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
    try:
        with urlopen(request, timeout=15) as response:
            return getattr(response, "status", 200)
    except HTTPError as exc:
        return exc.code
    except URLError:
        return 0


def classify_issue(slug: str, url: str, status_code: int, similarity_score: float, image_mode: str) -> Dict[str, object]:
    issues: List[str] = []

    if url and status_code == 404:
        issues.append("dead_link")
    if similarity_score >= 0.5:
        issues.append("duplicate_title_family")
    if image_mode == "character_generated":
        issues.append("image_needs_reference")
    if image_mode == "product_generated":
        issues.append("image_needs_screenshot")
    if image_mode == "generated":
        issues.append("image_needs_regeneration")

    return {
        "slug": slug,
        "issues": issues,
    }


def collect_posts() -> List[Dict[str, object]]:
    posts: List[Dict[str, object]] = []
    for md_path in sorted(BLOG_DIR.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        meta = parse_frontmatter(text)
        title = str(meta.get("title", md_path.stem))
        slug = str(meta.get("slug", md_path.stem))
        urls = sorted(set(URL_RE.findall(text)))
        posts.append(
            {
                "file": md_path.name,
                "slug": slug,
                "title": title,
                "tags": meta.get("tags", []),
                "urls": urls,
                "image_mode": infer_image_mode({"title": title, "slug": slug, "tags": meta.get("tags", [])}),
            }
        )
    return posts


def build_report() -> Dict[str, object]:
    posts = collect_posts()
    status_cache: Dict[str, int] = {}
    duplicate_map: Dict[str, List[Dict[str, object]]] = defaultdict(list)

    for post in posts:
        for other in posts:
            if post["slug"] == other["slug"]:
                continue
            score = title_similarity(str(post["title"]), str(other["title"]))
            if score >= 0.5:
                duplicate_map[str(post["slug"])].append(
                    {"slug": other["slug"], "score": round(score, 3)}
                )

    report_posts = []
    for post in posts:
        issues = []
        for url in post["urls"]:
            status_code = status_cache.setdefault(url, fetch_status_code(url))
            issue = classify_issue(
                slug=str(post["slug"]),
                url=url,
                status_code=status_code,
                similarity_score=0.0,
                image_mode="generated",
            )
            if issue["issues"]:
                issues.append({"type": issue["issues"], "url": url, "status_code": status_code})

        duplicate_issue = classify_issue(
            slug=str(post["slug"]),
            url="",
            status_code=200,
            similarity_score=0.5 if duplicate_map.get(str(post["slug"])) else 0.0,
            image_mode=str(post["image_mode"]),
        )
        if duplicate_issue["issues"]:
            issues.append(
                {
                    "type": duplicate_issue["issues"],
                    "matches": duplicate_map.get(str(post["slug"]), []),
                }
            )

        report_posts.append(
            {
                "file": post["file"],
                "slug": post["slug"],
                "title": post["title"],
                "image_mode": post["image_mode"],
                "issues": issues,
            }
        )

    return {
        "total_posts": len(report_posts),
        "posts": report_posts,
    }


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
