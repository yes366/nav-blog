#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "content" / "blog"

REPLACEMENTS = {
    "https://naviya.chat/characters": "https://www.naviya.chat/create",
    "https://www.naviya.chat/characters": "https://www.naviya.chat/create",
    "https://naviya.chat/characters/inspector": "https://www.naviya.chat/create",
    "https://www.naviya.chat/characters/inspector": "https://www.naviya.chat/create",
    "https://naviya.chat/features/advanced-roleplay": "https://www.naviya.chat/",
    "https://www.naviya.chat/features/advanced-roleplay": "https://www.naviya.chat/",
    "https://naviya.chat/features/voice": "https://www.naviya.chat/",
    "https://www.naviya.chat/features/voice": "https://www.naviya.chat/",
    "https://naviya.chat/features": "https://www.naviya.chat/",
    "https://www.naviya.chat/features": "https://www.naviya.chat/",
    "https://naviya.chat/download": "https://www.naviya.chat/",
    "https://www.naviya.chat/download": "https://www.naviya.chat/",
    "https://naviya.chat/privacy": "https://www.naviya.chat/policy",
    "https://www.naviya.chat/privacy": "https://www.naviya.chat/policy",
    "https://naviya.chat/studio": "https://www.naviya.chat/create",
    "https://www.naviya.chat/studio": "https://www.naviya.chat/create",
}


def repair_url(url: str) -> str:
    if url in REPLACEMENTS:
        return REPLACEMENTS[url]
    return url.replace("https://naviya.chat", "https://www.naviya.chat")


def repair_text(text: str) -> str:
    fixed = text.replace("https://naviya.chat/characters](https://naviya.chat/characters", "https://www.naviya.chat/create")
    for old, new in sorted(REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        fixed = fixed.replace(old, new)
    fixed = fixed.replace("https://naviya.chat", "https://www.naviya.chat")
    return fixed


def main() -> None:
    for md_path in sorted(BLOG_DIR.glob("*.md")):
        original = md_path.read_text(encoding="utf-8")
        updated = repair_text(original)
        if updated != original:
            md_path.write_text(updated, encoding="utf-8")
            print(f"updated {md_path.name}")


if __name__ == "__main__":
    main()
