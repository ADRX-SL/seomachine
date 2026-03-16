#!/usr/bin/env python3
"""
Read topics/cold-calling-topics.csv; for each post:
1. Write a draft to drafts/ (using context from context/) via Anthropic API
2. Convert to docx (scripts/md_to_docx.py).
Skips posts whose slug already exists in output/ as .md or .docx.
Uses ANTHROPIC_API_KEY for draft writing. No image generation.
"""
import csv
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Load .env from repo root
REPO_ROOT = Path(__file__).resolve().parent.parent


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
    """Derive URL-safe slug from post title."""
    if not title or not title.strip():
        return ""
    s = re.sub(r"[^a-z0-9\s-]", "", title.lower().strip())
    s = re.sub(r"[-\s]+", "-", s).strip("-")
    return s[:80] if s else ""


def load_context() -> str:
    """Load all context/*.md files into one string."""
    context_dir = REPO_ROOT / "context"
    if not context_dir.exists():
        return ""
    parts = []
    for p in sorted(context_dir.glob("*.md")):
        try:
            parts.append(f"## {p.name}\n{p.read_text(encoding='utf-8')}")
        except Exception as e:
            print(f"Warning: could not read {p}: {e}", file=sys.stderr)
    return "\n\n---\n\n".join(parts)


def write_draft_with_llm(post_title: str, money_keywords: str, other_keywords: str, context_text: str) -> str:
    """Generate draft markdown using Anthropic API. Returns full markdown string."""
    try:
        from anthropic import Anthropic
    except ImportError:
        print("ERROR: anthropic not installed. Run: pip install anthropic", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set in .env", file=sys.stderr)
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    primary_keyword = (money_keywords or other_keywords or "").strip().split("/")[0].strip() or post_title

    user_content = f"""Write a complete SEO-optimized blog post in markdown.

Post title (use as H1): {post_title}
Primary money keyword (use in H1, first 100 words, one H2, conclusion): {primary_keyword}
Other keywords to weave in naturally: {other_keywords or 'none'}

Requirements:
- Start with meta block: Meta title:, Meta description:, Target keyword:, Slug: (slug from title).
- One H1 = post title. Then intro (hook in first sentence), then ## Table of contents, then 4–7 ## sections.
- Use **bold** for emphasis. Include 2+ internal link placeholders (e.g. scalelist.com, scalelist.com/pricing).
- End with a "Try Scalelist free" CTA and clear next step. Length 1500–2200 words.
- Follow the voice and rules in the context below. Use locations: US, Australia, Singapore only. No HR as persona.
- Do not include image tags; images will be added later."""

    full_prompt = f"{context_text}\n\n---\n\n{user_content}" if context_text else user_content

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        messages=[{"role": "user", "content": full_prompt}],
    )

    text_parts = []
    for block in message.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(getattr(block, "text", "") or "")
        elif hasattr(block, "text"):
            text_parts.append(block.text)
    text = "".join(text_parts).strip()
    if not text:
        raise RuntimeError("No text in Anthropic response")
    return text


def main():
    load_env()
    os.chdir(REPO_ROOT)

    csv_path = REPO_ROOT / "topics" / "cold-calling-topics.csv"
    if not csv_path.exists():
        print(f"ERROR: {csv_path} not found")
        sys.exit(1)

    drafts_dir = REPO_ROOT / "drafts"
    output_dir = REPO_ROOT / "output"
    drafts_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    context_text = load_context()
    print("Context loaded: {} chars from context/".format(len(context_text)))

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
            rows.append({
                "Post Title": title,
                "Money keywords": (row.get("Money keywords") or "").strip(),
                "Other Keywords": (row.get("Other Keywords") or "").strip(),
                "Slug": slug,
            })

    today = datetime.now().strftime("%Y-%m-%d")
    for r in rows:
        slug = r["Slug"]
        title = r["Post Title"]
        if (output_dir / f"{slug}.md").exists() or (output_dir / f"{slug}.docx").exists():
            print(f"Skip (exists in output/): {slug}")
            continue

        draft_name = f"{slug}-{today}.md"
        draft_path = drafts_dir / draft_name
        print(f"Writing draft: {draft_path}")
        try:
            body = write_draft_with_llm(
                title,
                r["Money keywords"],
                r["Other Keywords"],
                context_text,
            )
            draft_path.write_text(body, encoding="utf-8")
        except Exception as e:
            print(f"ERROR writing draft for '{title}': {e}", file=sys.stderr)
            continue

        docx_path = output_dir / f"{slug}.docx"
        print(f"Converting to docx: {docx_path}")
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "md_to_docx.py"),
                str(draft_path.resolve()),
                str(docx_path.resolve()),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"ERROR: md_to_docx failed with code {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            if result.stdout:
                print(result.stdout, file=sys.stderr)
        else:
            print(f"Saved: {docx_path}")

    print("Done.")


if __name__ == "__main__":
    main()
