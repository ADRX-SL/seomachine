#!/usr/bin/env python3
"""
One-off: for each post in the cold-calling CSV (from path in argv or default),
write a draft to drafts/ using the EXACT same structure/voice as
drafts/how-to-find-mobile-numbers-for-cold-calling-2026-03-09.md.
No images, markdown only. Skips "How to find mobile numbers for cold calling".
Uses ANTHROPIC_API_KEY and context/.
"""
import csv
import os
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REFERENCE_DRAFT = REPO_ROOT / "drafts" / "how-to-find-mobile-numbers-for-cold-calling-2026-03-09.md"
SKIP_SLUG = "how-to-find-mobile-numbers-for-cold-calling"


def load_env():
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

def slug_from_title(title: str) -> str:
    if not title or not title.strip():
        return ""
    s = re.sub(r"[^a-z0-9\s-]", "", title.lower().strip())
    s = re.sub(r"[\s-]+", "-", s).strip("-")
    return s[:80] if s else ""

def load_context() -> str:
    context_dir = REPO_ROOT / "context"
    if not context_dir.exists():
        return ""
    parts = []
    for p in sorted(context_dir.glob("*.md")):
        try:
            parts.append(f"## {p.name}\n{p.read_text(encoding='utf-8')}")
        except Exception as e:
            print(f"Warning: {p}: {e}", file=sys.stderr)
    return "\n\n---\n\n".join(parts)

def reference_draft_without_images() -> str:
    """Reference draft with all ![...](images/...) lines removed."""
    text = REFERENCE_DRAFT.read_text(encoding="utf-8")
    return re.sub(r"\n!\[[^\]]*\]\(images/[^)]+\)\s*\n", "\n", text)

def write_draft(post_title: str, money_keywords: str, other_keywords: str, context_text: str, reference_text: str) -> str:
    from anthropic import Anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    client = Anthropic(api_key=api_key)
    primary = (money_keywords or other_keywords or "").strip().split("/")[0].strip() or post_title

    user = f"""You are writing a Scalelist cold-calling blog post. Use the EXACT same structure, voice, and conventions as the REFERENCE post below — but for this new topic. Do NOT include any image tags (no ![...](images/...) ). Do NOT mention "images will be added later". Output only the markdown.

NEW POST:
- Post title (H1): {post_title}
- Primary money keyword (in H1, first 100 words, at least one H2, conclusion): {primary}
- Other keywords to weave in: {other_keywords or 'none'}

Requirements (match reference):
- Start with 4-line meta block: Meta title:, Meta description:, Target keyword:, Slug: (slug from title, lowercase-hyphenated).
- H1 = post title. Hook in first sentence. Then 2–3 sentences, then "In this guide you'll learn:" with 4 bullet points, then "Along the way... Scalelist."
- ## Table of contents with numbered anchor links only (no images).
- 4–7 ## sections with substantive content. Use **bold**, blockquotes for concrete examples. Examples must use only US, Australia, or Singapore; industries: SaaS, financial services, IT services, construction, real estate, insurance, outsourcing. Named tools: HubSpot, Salesforce, Pipedrive, Instantly, lemlist, Skipcall, Flunter, Allo; competitors: Apollo, ZoomInfo, Lusha, RocketReach.
- Where relevant, describe Scalelist's Chrome extension workflow (LinkedIn/Sales Navigator, no export) and CSV upload workflow (existing list from CRM/event) separately; never "export from Sales Navigator and upload as CSV".
- Closing section that leads into Scalelist. End with a paragraph containing [Try Scalelist free](https://scalelist.com) and link to [pricing](https://scalelist.com/pricing). Length 1500–2200 words.

REFERENCE POST (structure to copy, no images in your output):
---
{reference_text[:18000]}
---
CONTEXT (brand voice, SEO, features):
---
{context_text[:14000]}
---"""

    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        messages=[{"role": "user", "content": user}],
    )
    parts = []
    for block in msg.content:
        if getattr(block, "type", None) == "text":
            parts.append(getattr(block, "text", "") or "")
        elif hasattr(block, "text"):
            parts.append(block.text)
    text = "".join(parts).strip()
    if not text:
        raise RuntimeError("Empty response from API")
    return text


def main():
    load_env()
    csv_path = sys.argv[1] if len(sys.argv) > 1 else (REPO_ROOT / "topics" / "cold-calling-topics.csv")
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"ERROR: CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)
    if not REFERENCE_DRAFT.exists():
        print(f"ERROR: Reference draft not found: {REFERENCE_DRAFT}", file=sys.stderr)
        sys.exit(1)

    context_text = load_context()
    reference_text = reference_draft_without_images()
    drafts_dir = REPO_ROOT / "drafts"
    drafts_dir.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get("Post Title") or "").strip()
            if not title:
                continue
            slug = (row.get("Slug") or "").strip() or slug_from_title(title)
            if not slug:
                continue
            if slug == SKIP_SLUG or "how to find mobile numbers for cold calling" in title.lower():
                print(f"Skip: {slug}")
                continue
            rows.append({
                "Post Title": title,
                "Money keywords": (row.get("Money keywords") or "").strip(),
                "Other Keywords": (row.get("Other Keywords") or "").strip(),
                "Slug": slug,
            })

    for i, r in enumerate(rows):
        slug = r["Slug"]
        title = r["Post Title"]
        draft_path = drafts_dir / f"{slug}-{today}.md"
        print(f"[{i+1}/{len(rows)}] Writing: {draft_path}")
        try:
            body = write_draft(title, r["Money keywords"], r["Other Keywords"], context_text, reference_text)
            draft_path.write_text(body, encoding="utf-8")
            print(f"  Saved: {draft_path}")
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)
    print("Done.")


if __name__ == "__main__":
    main()
