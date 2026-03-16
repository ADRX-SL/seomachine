import os
import sys
import re
import requests
from pathlib import Path
from openai import OpenAI

def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

load_env()

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY not found")
    sys.exit(1)

client = OpenAI(api_key=api_key)

post_path = Path(sys.argv[1])
content = post_path.read_text()
images_dir = post_path.parent / "images"
images_dir.mkdir(exist_ok=True)

headings = re.findall(r'^## (.+)$', content, re.MULTILINE)
print(f"Found {len(headings)} sections")

heading_to_filename = {}

for heading in headings:
    filename = re.sub(r'[^a-z0-9]+', '-', heading.lower()).strip('-')[:50] + ".png"
    heading_to_filename[heading] = filename
    print(f"Generating: {filename}")

    prompt = f"Professional B2B SaaS illustration for: {heading[:100]}. Clean, minimal, blue and white."
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1792x1024",
        n=1,
    )

    url = response.data[0].url
    img_data = requests.get(url, timeout=60).content
    (images_dir / filename).write_bytes(img_data)
    print(f"Saved: {filename}")

# Insert image tags into the markdown after each matching H2
updated_content = content
for heading, filename in heading_to_filename.items():
    image_tag = f"![{heading}](images/{filename})"
    heading_line = f"## {heading}"

    # Skip if the image tag is already present right after the heading
    pattern = rf"{re.escape(heading_line)}\n{re.escape(image_tag)}"
    if re.search(pattern, updated_content):
        continue

    updated_content = updated_content.replace(
        heading_line + "\n",
        heading_line + "\n" + image_tag + "\n",
    )

post_path.write_text(updated_content, encoding="utf-8")

print("Done!")
