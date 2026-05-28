# Open Paywall Gallery

Languages: [English](README.md) | [简体中文](README.zh-CN.md)

A public dataset of 500 top iOS subscription app paywalls and onboarding flows, published by <a href="https://www.paywallpro.app/?utm_source=github&utm_medium=open_dataset&utm_campaign=paywall_gallery" target="_blank" rel="noopener noreferrer">PaywallPro</a>.

Explore screenshots, pricing models, paywall patterns, onboarding previews, and monetization signals from real subscription apps.

Star this repo if you want weekly updates with 50 new apps.

Open an Issue if you want us to add a specific app: [request an app](https://github.com/paywallpro/paywall-gallery/issues/new?template=app-request.yml).

---

## Visual gallery

This repository now includes a static gallery layer in `/tmp/workspace/wwwgaoxi/paywall-gallery/gallery` so you can browse screenshots in a card grid instead of raw Markdown tables.

The gallery home now includes featured apps, category-based sections, and dedicated category pages with screenshots shown directly in the page.

To regenerate the gallery from the existing JSON + Markdown dataset:

```bash
npm run build:gallery
```

To preview it locally:

```bash
npm run preview:gallery
```

Then open:

```txt
http://127.0.0.1:8123/gallery/index.html
```

Category directory:

```txt
http://127.0.0.1:8123/gallery/categories/index.html
```

---

![500+ iOS Paywalls & Onboarding Flows](assets/readme-hero.jpg)

---

## What is PaywallPro?

PaywallPro is a subscription intelligence platform for app developers, product managers, growth teams, and designers.

It helps teams study real iOS paywalls, onboarding flows, pricing models, historical changes, and monetization signals from leading subscription apps.

PaywallPro tracks:

- 46,000+ iOS paywall screenshots
- 2,000+ onboarding flows
- Historical paywall versions
- Pricing and trial changes
- Revenue signals such as MRR, RPD, ARPU, and subscription benchmarks

Built for professionals who want real subscription insights, not just visual inspiration:

- Explore competitor paywalls and learn what drives conversions
- Track how pricing, trials, and design evolve over time
- Analyze revenue with RPD, ARPU, and subscription benchmarks
- Discover monetization strategies from top-performing apps

This open dataset is published by the PaywallPro team to give the developer and product community free access to curated paywall intelligence.

---

## Why this exists

Subscription apps are growing fast, but most teams still make paywall and pricing decisions based on guesswork, personal taste, or isolated A/B tests.

Open Paywall Gallery helps builders study real paywall examples before deciding what to design, build, or test.

Use it to understand:

- How top apps present subscription value
- How pricing options are structured
- How free trials are positioned
- How onboarding flows prepare users for purchase
- How monthly and annual plans are framed
- How paywall patterns differ by category
- What monetization signals can be learned from real apps

---

## About this repository

`paywall-gallery` is an open dataset of iOS app paywall and onboarding previews, published as machine-readable Markdown files.

It is a curated subset of the PaywallPro database, designed to be:

- Freely accessible, no signup required
- Machine-readable, with structured frontmatter for programmatic access
- Easy to browse, with human-readable summaries and preview screenshots
- Useful for product research, pricing research, UX reference, and growth analysis

Current public release: 500 apps. We will keep adding 50 new apps every week.

The complete app index lives in [apps/index.md](apps/index.md). [Browse all 500 apps](apps/index.md).

---

## What's included

This public repository includes:

- Representative paywall screenshots
- Onboarding flow previews where available
- Compact app case pages
- Pricing model summaries
- Paywall pattern classification
- Selected public-facing monetization signals
- Category-level indexes
- Links to explore more on PaywallPro

---

## What's kept on PaywallPro

This repository offers a curated public preview of each app.

The full PaywallPro product includes:

- Full paywall screenshot sets
- Complete onboarding flows
- All historical paywall versions
- Version-by-version changes
- Before and after paywall comparisons
- Historical pricing experiments
- A/B comparison references
- Revenue, MRR, RPD, ARPU, and ranking signals
- Advanced filters by category, region, pricing model, and app type

Explore the full database:

<a href="https://www.paywallpro.app/?utm_source=github&utm_medium=open_dataset&utm_campaign=paywall_gallery" target="_blank" rel="noopener noreferrer">https://www.paywallpro.app</a>

---

## Data format

Each app entry lives in:

```txt
apps/{app-name}-{app_id}.md
```

Example:

```yaml
---
app_name: "YouTube"
app_id: 544007664
developer: "Google"
category: "Photo & Video"
paywall_type: "Free Trial - Soft Paywall"
pricing_model: "2 offer sets across month"
mrr: "$55.84M"
rating: 4.68
versions_count: 1
offers:
  - period: "month"
    prices: ["$18.99", "$18.99/$29.99"]
screenshots_count: 2
onboarding_flows_count: 1
app_detail_url: "https://www.paywallpro.app/apps/YouTube-us?id=PAYWALLPRO_INFO_ID"
---
```

See [Data Dictionary](docs/data-dictionary.md) for field definitions.

---

## Top 20 featured apps

| App | Category | Estimated MRR | Pattern | Page |
|---|---|---:|---|---|
| Life360: Stay Connected & Safe | Social Networking | $4.50M | Free Trial - Soft Paywall | [Open](apps/life360-stay-connected-and-safe-384830320.md) |
| Grindr - Gay Dating & Chat | Social Networking | $3.10M | No Free Trial - Soft Paywall | [Open](apps/grindr-gay-dating-and-chat-319881193.md) |
| YouTube | Photo & Video | $3.07M | No Free Trial - Soft Paywall | [Open](apps/youtube-544007664.md) |
| Google Photos: Backup & Edit | Photo & Video | $2.77M | No Free Trial - Soft Paywall | [Open](apps/google-photos-backup-and-edit-962194608.md) |
| Amazon Music: Songs & Podcasts | Music | $2.58M | Free Trial - Soft Paywall | [Open](apps/amazon-music-songs-and-podcasts-510855668.md) |
| Bumble Dating App: Meet & Date | Lifestyle | $2.57M | Credit Paywall | [Open](apps/bumble-dating-app-meet-and-date-930441707.md) |
| GameChanger | Sports | $2.54M | Free Trial - Soft Paywall | [Open](apps/gamechanger-1308415878.md) |
| X | News | $2.48M | No Free Trial - Soft Paywall | [Open](apps/x-333903271.md) |
| Telegram Messenger | Social Networking | $2.13M | No Free Trial - Soft Paywall | [Open](apps/telegram-messenger-686449807.md) |
| Dropbox: Cloud Storage Backup | Productivity | $2.09M | Free Trial - Soft Paywall | [Open](apps/dropbox-cloud-storage-backup-327630330.md) |
| NFL | Sports | $2.04M | No Free Trial - Soft Paywall | [Open](apps/nfl-389781154.md) |
| SoundCloud: The Music You Love | Music | $1.71M | No Free Trial - Soft Paywall | [Open](apps/soundcloud-the-music-you-love-336353151.md) |
| BIGO LIVE-Live Stream, Go Live | Social Networking | $1.65M | No Free Trial - Soft Paywall | [Open](apps/bigo-live-live-stream-go-live-1077137248.md) |
| NYTimes: US and Global News | News | $1.48M | No Free Trial - Soft Paywall | [Open](apps/nytimes-us-and-global-news-284862083.md) |
| FaceApp: Perfect Face Editor | Photo & Video | $1.45M | Free Trial - Soft Paywall | [Open](apps/faceapp-perfect-face-editor-1180884341.md) |
| Wyze - Never Wonder | Lifestyle | $1.45M | Free Trial - Soft Paywall | [Open](apps/wyze-never-wonder-1288415553.md) |
| MileIQ: Mileage Tracker & Log | Finance | $1.26M | Free Trial - Soft Paywall | [Open](apps/mileiq-mileage-tracker-and-log-578830929.md) |
| Lingokids: Games & Shows | Education | $1.16M | No Free Trial - Soft Paywall | [Open](apps/lingokids-games-and-shows-1002043426.md) |
| Quizlet: More than Flashcards | Education | $1.16M | Free Trial - Soft Paywall | [Open](apps/quizlet-more-than-flashcards-546473125.md) |
| TIDAL Music: HiFi Sound | Music | $1.03M | Free Trial - Soft Paywall | [Open](apps/tidal-music-hifi-sound-913943275.md) |

The complete app index lives in [apps/index.md](apps/index.md). [Browse all 500 apps](apps/index.md).

---

## Browse by category

- [Social Networking](categories/social-networking.md)
- [Photo & Video](categories/photo-video.md)
- [Music](categories/music.md)
- [Lifestyle](categories/lifestyle.md)
- [Sports](categories/sports.md)
- [News](categories/news.md)
- [Productivity](categories/productivity.md)
- [Finance](categories/finance.md)
- [Education](categories/education.md)
- [Health & Fitness](categories/health-and-fitness.md)
- [Business](categories/business.md)
- [Medical](categories/medical.md)
- [Utilities](categories/utilities.md)
- [Entertainment](categories/entertainment.md)
- [Travel](categories/travel.md)
- [Reference](categories/reference.md)
- [Food & Drink](categories/food-and-drink.md)
- [Shopping](categories/shopping.md)
- [Books](categories/books.md)
- [Navigation](categories/navigation.md)
- [Weather](categories/weather.md)
- [Graphics & Design](categories/graphics-and-design.md)
- [Games](categories/games.md)

---

## Browse by paywall pattern

- [Free Trial Paywalls](docs/free-trial-paywalls.md)
- [Monthly vs Annual Pricing](docs/monthly-vs-annual-pricing.md)
- [Paywall Pattern Taxonomy](docs/paywall-pattern-taxonomy.md)

---

## Coming soon

We are exploring a Skills version of this dataset so developers, product managers, and growth teams can reference real paywall examples directly in their workflows.

Imagine asking:

- Show me 10 free trial paywalls from top fitness apps
- Compare monthly vs annual pricing across productivity apps
- Find onboarding flows that transition into a soft paywall

---

## Suggested use cases

For indie developers:

- Find pricing references before launching a subscription app
- Study how top apps explain subscription value
- Compare free trial and non-trial paywall structures

For product managers:

- Benchmark paywall patterns across categories
- Prepare paywall redesign references
- Understand how competitors package plans and benefits

For growth teams:

- Analyze pricing anchors
- Study trial positioning
- Find ideas for paywall A/B tests

For designers:

- Study layout, visual hierarchy, offer cards, CTA design, and benefit presentation
- Build a reference library for subscription UX

---

## Roadmap

- v0.1.0 - Top 500 Public Review Release
- Weekly Drop #1 - 50 new apps
- Weekly Drop #2 - 50 new apps
- Category index pages
- Paywall pattern index pages
- Continuous weekly expansion
- Automated update pipeline with GitHub Actions

---

## Contributing

Found a paywall worth documenting? Spotted a data error?

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

See [REQUESTS.md](REQUESTS.md) for the current app request list.

---

## License and usage

Structured metadata in this repository is available for learning, research, commentary, and internal product reference with attribution.

You may not bulk copy, repackage, resell, or use this dataset to build a competing commercial paywall intelligence product.

Screenshots are copyrighted by their respective app developers.

See [LICENSE](LICENSE) for details.

---

## Powered by PaywallPro

Open Paywall Gallery is published by PaywallPro.

PaywallPro helps subscription app teams research paywalls, onboarding flows, pricing models, historical changes, and monetization signals from top iOS apps.
