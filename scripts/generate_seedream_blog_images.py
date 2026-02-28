#!/usr/bin/env python3
import os
import re
import time
import requests
from pathlib import Path
from typing import Dict, Tuple
from volcenginesdkarkruntime import Ark

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "content" / "blog"
IMG_DIR = BLOG_DIR / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "doubao-seedream-4-5-251128"
SIZE = "2048x2048"
# 兼容本地环境：优先环境变量，其次回退到已有可用 key（来自现有脚本）
API_KEY = os.getenv("ARK_API_KEY") or "72620536-bd74-4b1a-8460-4ad165b1ddb3"

PLACEHOLDER_RE = re.compile(r"PLACEHOLDER:[^)\s]+")


def parse_frontmatter(md_text: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not md_text.startswith("---\n"):
        return out
    end = md_text.find("\n---\n", 4)
    if end < 0:
        return out
    front = md_text[4:end]
    for line in front.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def make_prompt(title: str, description: str, slug: str) -> str:
    base = (
        "Professional editorial illustration for a tech blog article. "
        "Modern digital art, cinematic lighting, high detail, clean composition, "
        "vibrant but balanced colors, no text, no logo, no watermark. "
    )
    return f"{base} Topic: {title}. Context: {description}. Keyword: {slug}."


def generate_image(client: Ark, prompt: str, out_path: Path) -> Tuple[bool, str]:
    try:
        resp = client.images.generate(
            model=MODEL,
            prompt=prompt,
            size=SIZE,
        )
        image_url = resp.data[0].url
        r = requests.get(image_url, timeout=120)
        r.raise_for_status()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(r.content)
        return True, image_url
    except Exception as e:
        return False, str(e)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="仅处理前N个文件，0=全部")
    parser.add_argument("--file", type=str, default="", help="仅处理指定文件名，如 a.md")
    args = parser.parse_args()

    client = Ark(api_key=API_KEY)
    files = sorted(BLOG_DIR.glob("*.md"))
    if args.file:
        target = (BLOG_DIR / args.file).resolve()
        files = [target] if target.exists() else []
    elif args.limit and args.limit > 0:
        files = files[:args.limit]
    total = 0
    updated = 0
    generated = 0

    for md_file in files:
        total += 1
        text = md_file.read_text(encoding="utf-8")
        placeholders = set(PLACEHOLDER_RE.findall(text))
        if not placeholders:
            continue

        fm = parse_frontmatter(text)
        slug = fm.get("slug") or md_file.stem
        title = fm.get("title") or slug.replace("-", " ").title()
        description = fm.get("description") or title

        rel_img = f"./images/{slug}.jpg"
        abs_img = IMG_DIR / f"{slug}.jpg"

        if not abs_img.exists():
            prompt = make_prompt(title, description, slug)
            print(f"[GEN] {md_file.name} -> {abs_img.name}")
            ok, info = generate_image(client, prompt, abs_img)
            if ok:
                generated += 1
                print(f"[OK] generated: {abs_img.name}")
            else:
                print(f"[ERR] {md_file.name}: {info}")
                continue
            time.sleep(1.5)

        new_text = PLACEHOLDER_RE.sub(rel_img, text)
        if new_text != text:
            md_file.write_text(new_text, encoding="utf-8")
            updated += 1
            print(f"[OK] patched placeholders: {md_file.name}")

    print("\nDone")
    print(f"files scanned: {total}")
    print(f"files updated: {updated}")
    print(f"images generated: {generated}")


if __name__ == "__main__":
    main()
