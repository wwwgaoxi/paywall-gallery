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
CATEGORIES_DIR = GALLERY_DIR / 'categories'
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


def slugify_text(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-') or 'category'


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


def render_card(record: dict, *, image_prefix: str = '..', detail_prefix: str = '') -> str:
    image_path = f"{image_prefix}/{record['featured_image']}"
    detail_href = f"{detail_prefix}apps/{slugified_app_filename(record)}"
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


def render_section_heading(title: str, description: str = '', action_href: str = '', action_label: str = '') -> str:
    action_markup = (
        f'<a class="section-link" href="{escape(action_href, quote=True)}">{escape(action_label)}</a>'
        if action_href and action_label
        else ''
    )
    description_markup = f'<p>{escape(description)}</p>' if description else ''
    return f"""
      <div class=\"section-heading\">
        <div>
          <h2>{escape(title)}</h2>
          {description_markup}
        </div>
        {action_markup}
      </div>
    """


def render_category_card(category: dict, *, image_prefix: str = '..', href_prefix: str = 'categories/') -> str:
    preview_markup = ''.join(
        f'<img src="{image_prefix}/{image}" alt="{escape(category["name"])} preview {index + 1}" loading="lazy">'
        for index, image in enumerate(category['preview_images'][:3])
    )
    return f"""
      <article class=\"category-card\">
        <a class=\"category-card__link\" href=\"{href_prefix}{escape(category['slug'], quote=True)}.html\">
          <div class=\"category-card__preview\">{preview_markup}</div>
          <div class=\"category-card__body\">
            <div class=\"category-card__meta\">
              <span>{category['app_count']} apps</span>
              <span>{category['image_count']} images</span>
            </div>
            <h3>{escape(category['name'])}</h3>
            <p>Browse {escape(category['name'])} paywalls with screenshots shown directly in the page.</p>
          </div>
        </a>
      </article>
    """


def render_category_section(category: dict) -> str:
    cards_markup = ''.join(render_card(app) for app in category['apps'][:4])
    return f"""
      <section class=\"content-section\" id=\"category-{escape(category['slug'], quote=True)}\">
        {render_section_heading(category['name'], f"{category['app_count']} apps · {category['image_count']} preview images", f"categories/{category['slug']}.html", 'View category')}
        <div class=\"card-grid card-grid--compact\">{cards_markup}</div>
      </section>
    """


def render_categories_index(categories: list[dict]) -> str:
    cards_markup = ''.join(render_category_card(category, image_prefix='../..', href_prefix='') for category in categories)
    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Categories · Paywall Gallery</title>
    <link rel=\"stylesheet\" href=\"../{BASE_CSS}\">
  </head>
  <body>
    <div class=\"shell\">
      <header class=\"topbar\">
        <nav class=\"topbar__nav\">
          <a class=\"back-link\" href=\"../index.html\">Home</a>
          <a class=\"back-link\" href=\"../index.html#all-apps\">All apps</a>
        </nav>
      </header>

      <section class=\"page-hero page-hero--compact\">
        <div>
          <p class=\"eyebrow\">Category directory</p>
          <h1>Browse screenshots by content group.</h1>
          <p class=\"hero-copy\">Each category page keeps the screenshots visible while splitting the gallery into easier-to-scan sections.</p>
        </div>
        <div class=\"hero-metrics\">
          <div><span>Categories</span><strong>{len(categories)}</strong></div>
          <div><span>Total apps</span><strong>{sum(category['app_count'] for category in categories)}</strong></div>
          <div><span>Total images</span><strong>{sum(category['image_count'] for category in categories)}</strong></div>
        </div>
      </section>

      <section class=\"category-grid\">{cards_markup}</section>
    </div>
  </body>
</html>
"""


def render_category_page(category: dict) -> str:
    apps = category['apps']
    cards_markup = ''.join(render_card(app, image_prefix='../..', detail_prefix='../') for app in apps)
    preview_markup = ''.join(
        f'<img src="../../{image}" alt="{escape(category["name"])} preview {index + 1}" loading="lazy">'
        for index, image in enumerate(category['preview_images'][:4])
    )
    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>{escape(category['name'])} · Paywall Gallery</title>
    <link rel=\"stylesheet\" href=\"../{BASE_CSS}\">
  </head>
  <body>
    <div class=\"shell\">
      <header class=\"topbar\">
        <nav class=\"topbar__nav\">
          <a class=\"back-link\" href=\"../index.html\">Home</a>
          <a class=\"back-link\" href=\"index.html\">All categories</a>
          <a class=\"back-link\" href=\"../index.html#all-apps\">All apps</a>
        </nav>
        <a class=\"cta-link\" href=\"../index.html#category-{escape(category['slug'], quote=True)}\">Jump to section</a>
      </header>

      <section class=\"page-hero page-hero--compact\">
        <div>
          <p class=\"eyebrow\">Category page</p>
          <h1>{escape(category['name'])}</h1>
          <p class=\"hero-copy\">This page groups related paywalls together so screenshots stay visible without mixing every app into one long stream.</p>
        </div>
        <div class=\"hero-metrics\">
          <div><span>Apps</span><strong>{category['app_count']}</strong></div>
          <div><span>Images</span><strong>{category['image_count']}</strong></div>
          <div><span>Paywall types</span><strong>{category['type_count']}</strong></div>
        </div>
      </section>

      <section class=\"image-strip\">{preview_markup}</section>
      <section class=\"content-section\">
        {render_section_heading('Apps in this category', 'Screenshots are shown directly in every card below.')}
        <div class=\"card-grid\">{cards_markup}</div>
      </section>
    </div>
  </body>
</html>
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
        <nav class=\"topbar__nav\">
          <a class=\"back-link\" href=\"../index.html\">Home</a>
          <a class=\"back-link\" href=\"../categories/{slugify_text(record['category'])}.html\">{escape(record['category'])}</a>
          <a class=\"back-link\" href=\"../categories/index.html\">All categories</a>
        </nav>
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


def render_index(apps: list[dict], categories: list[dict]) -> str:
    category_count = len(categories)
    total_images = sum(app.get('image_count', 0) for app in apps)
    cards_markup = ''.join(render_card(app) for app in apps)
    featured_cards = ''.join(render_card(app) for app in apps[:6])
    category_cards = ''.join(render_category_card(category) for category in categories[:8])
    category_sections = ''.join(render_category_section(category) for category in categories[:6])
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
      <header class=\"topbar\">
        <nav class=\"topbar__nav\">
          <a class=\"back-link\" href=\"index.html\">Home</a>
          <a class=\"back-link\" href=\"#featured-apps\">Featured</a>
          <a class=\"back-link\" href=\"categories/index.html\">Categories</a>
          <a class=\"back-link\" href=\"#all-apps\">All apps</a>
        </nav>
        <a class=\"cta-link\" href=\"categories/index.html\">Browse by category</a>
      </header>

      <header class=\"page-hero\">
        <div>
          <p class=\"eyebrow\">Visual gallery layer</p>
          <h1>Browse paywall screenshots like a product gallery.</h1>
          <p class=\"hero-copy\">This static gallery keeps the existing Markdown and JSON dataset intact while making screenshots, pricing context, and patterns easier to scan.</p>
        </div>
        <div class=\"hero-metrics\">
          <div><span>Apps</span><strong>{len(apps)}</strong></div>
          <div><span>Categories</span><strong>{category_count}</strong></div>
          <div><span>Preview images</span><strong>{total_images}</strong></div>
        </div>
      </header>

      <section class=\"content-section\" id=\"featured-apps\">
        {render_section_heading('Featured apps', 'A visual entry point with screenshots shown directly on the homepage.', '#all-apps', 'See all apps')}
        <div class=\"card-grid card-grid--featured\">{featured_cards}</div>
      </section>

      <section class=\"content-section\" id=\"browse-categories\">
        {render_section_heading('Browse by category', 'Split the dataset into separate content pages while keeping image previews visible.', 'categories/index.html', 'All categories')}
        <div class=\"category-grid\">{category_cards}</div>
      </section>

      {category_sections}

      <section class=\"content-section\" id=\"all-apps\">
        {render_section_heading('All apps', 'Search, filter, and sort the full gallery from one page.')}
      </section>

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


def build_category_groups(apps: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for app in apps:
        grouped.setdefault(app['category'], []).append(app)

    categories: list[dict] = []
    for name, category_apps in grouped.items():
        categories.append({
            'name': name,
            'slug': slugify_text(name),
            'apps': category_apps,
            'app_count': len(category_apps),
            'image_count': sum(app.get('image_count', 0) for app in category_apps),
            'preview_images': [app['featured_image'] for app in category_apps[:4]],
            'type_count': len({app['paywall_type'] for app in category_apps}),
        })

    categories.sort(key=lambda category: (-category['app_count'], category['name']))
    return categories


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
    categories = build_category_groups(apps)

    if APPS_DIR.exists():
        for old_file in APPS_DIR.glob('*.html'):
            old_file.unlink()
    if CATEGORIES_DIR.exists():
        for old_file in CATEGORIES_DIR.glob('*.html'):
            old_file.unlink()

    copy_assets()
    write_text(GALLERY_DIR / 'index.html', render_index(apps, categories))
    write_text(CATEGORIES_DIR / 'index.html', render_categories_index(categories))

    for app in apps:
        detail = parse_sections(ROOT / app['markdown_path'])
        detail.record = app
        write_text(APPS_DIR / slugified_app_filename(app), render_detail_page(detail))
    for category in categories:
        write_text(CATEGORIES_DIR / f"{category['slug']}.html", render_category_page(category))


if __name__ == '__main__':
    main()
