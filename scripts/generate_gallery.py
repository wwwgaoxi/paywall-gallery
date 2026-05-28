from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Iterable

ROOT = Path('/tmp/workspace/wwwgaoxi/paywall-gallery')
DATA_FILE = ROOT / 'data' / 'apps.json'
GALLERY_DIR = ROOT / 'gallery'
APPS_DIR = GALLERY_DIR / 'apps'
ASSETS_DIR = GALLERY_DIR / 'assets'

SECTION_RE = re.compile(r'^##\s+(.*)$')
BOLD_RE = re.compile(r'\*\*(.+?)\*\*')
LINK_RE = re.compile(r'\[(.+?)\]\((.+?)\)')


@dataclass
class AppDetail:
    record: dict
    title: str
    snapshot: list[str]
    why_it_matters: list[str]
    key_takeaways: list[str]
    builders_can_learn: list[str]
    questions: list[str]
    pricing_rows: list[list[str]]
    monetization_rows: list[list[str]]


BASE_CSS = 'assets/gallery.css'
BASE_JS = 'assets/gallery.js'


def format_money(value: int | float | None) -> str:
    if not value:
        return 'Not available'
    value = float(value)
    if value >= 1_000_000:
        return f'${value / 1_000_000:.2f}M'
    if value >= 1_000:
        return f'${value / 1_000:.2f}K'
    return f'${value:,.0f}'


def slugified_app_filename(record: dict) -> str:
    return f"{record['slug']}-{record['app_id']}.html"


def split_frontmatter(text: str) -> str:
    if not text.startswith('---\n'):
        return text
    parts = text.split('\n---\n', 1)
    if len(parts) == 2:
        return parts[1]
    return text


def parse_sections(markdown_path: Path) -> AppDetail:
    text = markdown_path.read_text(encoding='utf-8')
    body = split_frontmatter(text)
    lines = body.splitlines()

    title = ''
    sections: dict[str, list[str]] = {}
    current_heading: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if current_heading is not None:
            sections[current_heading] = [line.rstrip() for line in buffer]
        buffer = []

    for line in lines:
        if line.startswith('# ') and not title:
            title = line[2:].strip()
            continue
        match = SECTION_RE.match(line)
        if match:
            flush()
            current_heading = match.group(1).strip()
            continue
        if current_heading is not None:
            buffer.append(line)
    flush()

    def extract_paragraphs(name: str) -> list[str]:
        section_lines = sections.get(name, [])
        paragraphs: list[str] = []
        chunk: list[str] = []
        for line in section_lines:
            stripped = line.strip()
            if not stripped:
                if chunk:
                    paragraphs.append(' '.join(chunk))
                    chunk = []
                continue
            if stripped.startswith('- ') or stripped.startswith('|') or stripped.startswith('<'):
                continue
            chunk.append(stripped)
        if chunk:
            paragraphs.append(' '.join(chunk))
        return paragraphs

    def extract_bullets(name: str) -> list[str]:
        return [line.strip()[2:].strip() for line in sections.get(name, []) if line.strip().startswith('- ')]

    def extract_table(name: str) -> list[list[str]]:
        rows = [line.strip() for line in sections.get(name, []) if line.strip().startswith('|')]
        if len(rows) < 3:
            return []
        parsed: list[list[str]] = []
        for row in rows[2:]:
            columns = [column.strip() for column in row.strip('|').split('|')]
            parsed.append(columns)
        return parsed

    return AppDetail(
        record={},
        title=title or markdown_path.stem,
        snapshot=extract_paragraphs('Snapshot'),
        why_it_matters=extract_paragraphs('Why This Paywall Matters'),
        key_takeaways=extract_bullets('Key Takeaways'),
        builders_can_learn=extract_bullets('What Builders Can Learn'),
        questions=extract_bullets('Questions to Explore'),
        pricing_rows=extract_table('Pricing Structure'),
        monetization_rows=extract_table('Monetization Signals'),
    )


def inline_markdown(text: str) -> str:
    def replace_link(match: re.Match[str]) -> str:
        label, href = match.groups()
        return f'<a href="{escape(href, quote=True)}">{escape(label)}</a>'

    safe = escape(text)
    safe = BOLD_RE.sub(r'<strong>\1</strong>', safe)
    safe = LINK_RE.sub(replace_link, safe)
    return safe


def render_badge(text: str) -> str:
    return f'<span class="badge">{escape(text)}</span>'


def render_card(record: dict) -> str:
    image_path = f"../{record['featured_image']}"
    detail_href = f"apps/{slugified_app_filename(record)}"
    return f"""
        <article class=\"app-card\">
          <a class=\"app-card__image\" href=\"{detail_href}\">
            <img src=\"{image_path}\" alt=\"{escape(record['app_name'])} cover\" loading=\"lazy\">
          </a>
          <div class=\"app-card__body\">
            <div class=\"app-card__eyebrow\">{render_badge(record['category'])}{render_badge(record['paywall_type'])}</div>
            <h2><a href=\"{detail_href}\">{escape(record['app_name'])}</a></h2>
            <p class=\"app-card__meta\">{escape(record['developer'])}</p>
            <p class=\"app-card__pricing\">{escape(record['pricing'])}</p>
            <dl class=\"metric-grid\">
              <div><dt>MRR</dt><dd>{format_money(record.get('mrr_usd'))}</dd></div>
              <div><dt>Images</dt><dd>{record.get('image_count', 0)}</dd></div>
              <div><dt>Onboarding</dt><dd>{record.get('onboarding_flows_count', 0)}</dd></div>
            </dl>
          </div>
        </article>
    """


def render_table(rows: list[list[str]], columns: Iterable[str]) -> str:
    rows_markup = ''.join(
        '<tr>' + ''.join(f'<td>{inline_markdown(cell)}</td>' for cell in row) + '</tr>'
        for row in rows
    )
    head_markup = ''.join(f'<th>{escape(column)}</th>' for column in columns)
    return f"""
      <div class=\"table-shell\">
        <table>
          <thead><tr>{head_markup}</tr></thead>
          <tbody>{rows_markup}</tbody>
        </table>
      </div>
    """


def render_list(items: list[str]) -> str:
    if not items:
        return '<p class="empty-copy">No public notes available for this section.</p>'
    return '<ul class="content-list">' + ''.join(f'<li>{inline_markdown(item)}</li>' for item in items) + '</ul>'


def render_paragraphs(items: list[str]) -> str:
    if not items:
        return '<p class="empty-copy">No public notes available for this section.</p>'
    return ''.join(f'<p>{inline_markdown(item)}</p>' for item in items)


def render_detail_page(detail: AppDetail) -> str:
    record = detail.record
    screenshots = [record['featured_image'], *record.get('screenshot_images', [])]
    hero_image = f"../../{screenshots[0]}"
    thumbnails = ''.join(
        f'''<button class="thumb-button" type="button" data-full-src="../../{image}" data-alt="{escape(record['app_name'])} screenshot {index + 1}">
              <img src="../../{image}" alt="{escape(record['app_name'])} screenshot {index + 1}" loading="lazy">
            </button>'''
        for index, image in enumerate(screenshots)
    )

    info_items = [
        ('Category', record['category']),
        ('Paywall type', record['paywall_type']),
        ('Pricing model', record['pricing']),
        ('Version', record.get('current_version', 'Not available')),
        ('Release date', record.get('version_release_date', 'Not available')),
        ('Images', str(record.get('image_count', 0))),
        ('Onboarding previews', str(record.get('onboarding_flows_count', 0))),
        ('Estimated MRR', format_money(record.get('mrr_usd'))),
    ]
    info_markup = ''.join(
        f'<div class="info-card"><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>'
        for label, value in info_items
    )

    pricing_markup = render_table(detail.pricing_rows, ['Offer', 'Details']) if detail.pricing_rows else '<p class="empty-copy">Pricing table is not available in the public markdown record.</p>'
    monetization_markup = render_table(detail.monetization_rows, ['Metric', 'Value']) if detail.monetization_rows else '<p class="empty-copy">Monetization table is not available in the public markdown record.</p>'

    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>{escape(detail.title)} · Paywall Gallery</title>
    <link rel=\"stylesheet\" href=\"../{BASE_CSS}\">
  </head>
  <body class=\"detail-page\">
    <div class=\"shell\">
      <header class=\"topbar\">
        <a class=\"back-link\" href=\"../index.html\">← Back to gallery</a>
        <a class=\"cta-link\" href=\"{escape(record['paywallpro_url'])}\" target=\"_blank\" rel=\"noopener noreferrer\">Open on PaywallPro</a>
      </header>

      <main class=\"detail-layout\">
        <section class=\"hero-panel\">
          <div class=\"hero-copy\">
            <div class=\"badge-row\">{render_badge(record['category'])}{render_badge(record['paywall_type'])}</div>
            <h1>{escape(record['app_name'])}</h1>
            <p class=\"hero-subtitle\">{escape(record['developer'])} · {format_money(record.get('mrr_usd'))} estimated MRR · {escape(record.get('pricing', 'Not available'))}</p>
            <div class=\"hero-summary\">{render_paragraphs(detail.snapshot or detail.why_it_matters[:1])}</div>
          </div>
          <div class=\"hero-preview\">
            <button class=\"hero-image-button\" type=\"button\" data-full-src=\"{hero_image}\" data-alt=\"{escape(record['app_name'])} featured screenshot\">
              <img class=\"hero-image\" src=\"{hero_image}\" alt=\"{escape(record['app_name'])} featured screenshot\">
            </button>
            <div class=\"thumbnail-grid\">{thumbnails}</div>
          </div>
        </section>

        <section class=\"info-grid\">
          {info_markup}
        </section>

        <section class=\"content-grid\">
          <article class=\"content-card\">
            <h2>Key takeaways</h2>
            {render_list(detail.key_takeaways)}
          </article>
          <article class=\"content-card\">
            <h2>Why this paywall matters</h2>
            {render_paragraphs(detail.why_it_matters)}
          </article>
          <article class=\"content-card\">
            <h2>Pricing structure</h2>
            {pricing_markup}
          </article>
          <article class=\"content-card\">
            <h2>Monetization signals</h2>
            {monetization_markup}
          </article>
          <article class=\"content-card\">
            <h2>What builders can learn</h2>
            {render_list(detail.builders_can_learn)}
          </article>
          <article class=\"content-card\">
            <h2>Questions to explore</h2>
            {render_list(detail.questions)}
          </article>
        </section>
      </main>
    </div>

    <div class=\"lightbox\" hidden>
      <button class=\"lightbox__close\" type=\"button\" aria-label=\"Close screenshot preview\">×</button>
      <img class=\"lightbox__image\" src=\"\" alt=\"\">
    </div>

    <script src=\"../{BASE_JS}\"></script>
  </body>
</html>
"""


def render_index(apps: list[dict]) -> str:
    categories = len({app['category'] for app in apps})
    total_images = sum(app.get('image_count', 0) for app in apps)
    cards_markup = ''.join(render_card(app) for app in apps)
    payload = json.dumps(apps, separators=(',', ':'))

    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Paywall Gallery</title>
    <link rel=\"stylesheet\" href=\"{BASE_CSS}\">
  </head>
  <body>
    <div class=\"shell\">
      <header class=\"page-hero\">
        <div>
          <p class=\"eyebrow\">Visual gallery layer</p>
          <h1>Browse paywall screenshots like a product gallery.</h1>
          <p class=\"hero-copy\">This static gallery keeps the existing Markdown and JSON dataset intact while making screenshots, pricing context, and patterns easier to scan.</p>
        </div>
        <div class=\"hero-metrics\">
          <div><span>Apps</span><strong>{len(apps)}</strong></div>
          <div><span>Categories</span><strong>{categories}</strong></div>
          <div><span>Preview images</span><strong>{total_images}</strong></div>
        </div>
      </header>

      <section class=\"toolbar\">
        <label>
          <span>Search</span>
          <input id=\"search-input\" type=\"search\" placeholder=\"Search app, developer, category...\">
        </label>
        <label>
          <span>Category</span>
          <select id=\"category-filter\"><option value=\"all\">All categories</option></select>
        </label>
        <label>
          <span>Paywall type</span>
          <select id=\"type-filter\"><option value=\"all\">All patterns</option></select>
        </label>
        <label>
          <span>Pricing model</span>
          <select id=\"pricing-filter\"><option value=\"all\">All pricing models</option></select>
        </label>
        <label>
          <span>Sort by</span>
          <select id=\"sort-select\">
            <option value=\"mrr-desc\">MRR ↓</option>
            <option value=\"mrr-asc\">MRR ↑</option>
            <option value=\"images-desc\">Images ↓</option>
            <option value=\"onboarding-desc\">Onboarding ↓</option>
            <option value=\"name-asc\">Name A–Z</option>
            <option value=\"category-asc\">Category A–Z</option>
          </select>
        </label>
      </section>

      <section class=\"results-header\">
        <p id=\"results-count\">Showing {len(apps)} apps</p>
        <a class=\"cta-link\" href=\"../README.md\">Dataset docs</a>
      </section>

      <section id=\"card-grid\" class=\"card-grid\">{cards_markup}</section>
      <div id=\"empty-state\" class=\"empty-state\" hidden>No matching apps found. Try broadening the filters.</div>
    </div>

    <script id=\"apps-data\" type=\"application/json\">{payload}</script>
    <script src=\"{BASE_JS}\"></script>
  </body>
</html>
"""


def normalize_app(record: dict) -> dict:
    return {
        **record,
        'detail_path': f"apps/{slugified_app_filename(record)}",
        'mrr_display': format_money(record.get('mrr_usd')),
        'search_blob': ' '.join(
            str(record.get(key, ''))
            for key in ('app_name', 'developer', 'category', 'paywall_type', 'pricing')
        ).lower(),
    }


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def copy_assets() -> None:
    src_assets = ROOT / 'gallery-src' / 'assets'
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for asset in src_assets.iterdir():
        shutil.copy2(asset, ASSETS_DIR / asset.name)


def main() -> None:
    with DATA_FILE.open('r', encoding='utf-8') as file:
        raw_apps = json.load(file)

    apps = [normalize_app(app) for app in raw_apps]
    apps.sort(key=lambda app: (app.get('mrr_usd') or 0), reverse=True)

    if APPS_DIR.exists():
        for old_file in APPS_DIR.glob('*.html'):
            old_file.unlink()

    copy_assets()
    write_text(GALLERY_DIR / 'index.html', render_index(apps))

    for app in apps:
        detail = parse_sections(ROOT / app['markdown_path'])
        detail.record = app
        write_text(APPS_DIR / slugified_app_filename(app), render_detail_page(detail))


if __name__ == '__main__':
    main()
