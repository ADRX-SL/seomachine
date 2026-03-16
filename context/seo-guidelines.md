# Scalelist SEO Guidelines

## Every Article Must Have
1. One H1 matching the target keyword
2. Meta title under 60 characters, keyword front-loaded
3. Meta description 150–160 chars, keyword + benefit
4. Hook in first sentence — no throat-clearing
5. Table of contents for articles over 1,500 words
6. At least 2 internal links (homepage, pricing, or feature page)
7. One "Try Scalelist free" CTA minimum
8. Conclusion with clear next step

## Article Length
- How-to guides: 1,500–2,000 words
- Strategy/opinion: 1,000–1,500 words
- Comparison pages: 2,000–3,000 words
- Cold email/cold calling: 1,500–2,500 words

## Structure Per Post
- H1 with primary keyword
- Short intro: 2–3 paragraphs max, hook immediately, no fluff
- Table of contents
- H2 sections with H3 subsections
- Each H2: 1–2 short paragraphs then bullets or steps
- Compliance/GDPR section where relevant
- Conclusion with Scalelist CTA

## Paragraph Structure
- Maximum 2–3 sentences per paragraph
- No wall of text — ever
- H3 subheadings every 2–3 paragraphs
- Bullets or numbered lists for 3+ items
- Headings and first sentences should tell the full story

## Audience & Localisation
- Primary audience: Sales managers, VP Sales, revenue leaders
- Tone: Direct, confident, peer-to-peer
- Weave in US, European, Australian contexts naturally
- Cite sources inline for country-specific stats

## GDPR & Compliance
- Add compliance/GDPR section where relevant
- Scalelist GDPR advantage for US teams in Europe
- Apollo, ZoomInfo, Cognism face scrutiny — Scalelist built for this

## Entity Building
- Reference naturally: Salesforce, HubSpot, ZoomInfo, Salesloft, Apollo.io, Cognism, lemlist, Outreach

## Quality Checklist
- [ ] Target keyword in H1
- [ ] Target keyword in first 100 words
- [ ] Target keyword in meta title
- [ ] 2–4 related keywords in H2s naturally
- [ ] At least 2 internal links
- [ ] Short, keyword-rich URL slug
- [ ] No keyword stuffing

## Topic Clusters to Own
1. Cold email
2. Cold calling
3. LinkedIn prospecting
4. B2B contact data
5. Outbound sales
6. Competitor alternatives (Apollo, ZoomInfo, Lusha, etc.)

## Image Guidelines

### Image type by content stage
- **BOFU content** (product comparisons, tool evaluations, pricing pages, Scalelist-specific guides): Use real product screenshots of Scalelist or AI-generated UI-style images via DALL-E 3.
- **MOFU content** (how-to guides, educational content, process explainers): Use AI-generated editorial illustrations via DALL-E 3.

### Alt text rules
- Always include the primary money keyword naturally.
- Describe what the image shows specifically.
- Format: `![descriptive alt text with keyword](images/filename.png)`

### Placement rules
- Add at least one image per major H2 section.
- First image should appear within the first 300 words.
- Never leave more than 500 words without an image.

### Image generation
- Images are generated automatically using `scripts/generate_images.py`.
- Run: `python scripts/generate_images.py drafts/your-post.md`
- Requires `OPENAI_API_KEY` in `.env` file.
