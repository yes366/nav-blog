#!/usr/bin/env python3
import json
import re
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "content" / "blog"
VISUAL_MANIFEST_PATH = BLOG_DIR / "visual_manifest.json"
INLINE_IMAGE_RE = re.compile(r"!\[[^\]]*\]\((\./images/[^)]+)\)")


def find_inline_image_refs(text: str) -> List[str]:
    return INLINE_IMAGE_RE.findall(text)


def is_generated_cover_policy(entry: Dict[str, object]) -> bool:
    return str(entry.get("mode", "generated_editorial")) == "generated_editorial"


def load_manifest() -> Dict[str, Dict[str, object]]:
    if not VISUAL_MANIFEST_PATH.exists():
        return {}
    return json.loads(VISUAL_MANIFEST_PATH.read_text(encoding="utf-8"))


def validate() -> List[str]:
    issues: List[str] = []
    manifest = load_manifest()

    for path in sorted(BLOG_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        refs = find_inline_image_refs(text)
        if refs:
            issues.append(f"{path.name}: inline_images={len(refs)}")

        cover_match = re.search(r'^cover:\s*"?(.*?)"?$', text, re.M)
        cover_value = cover_match.group(1) if cover_match else ''
        if not cover_value.endswith('-cover.jpg'):
            issues.append(f"{path.name}: cover_path={cover_value}")

        slug = path.stem
        entry = manifest.get(slug, {"mode": "generated_editorial"})
        if not is_generated_cover_policy(entry):
            issues.append(f"{path.name}: cover_mode={entry.get('mode')}")

    return issues


def main() -> None:
    issues = validate()
    if issues:
        for issue in issues:
            print(issue)
        raise SystemExit(1)
    print("OK: blog quality checks passed")


if __name__ == "__main__":
    main()
