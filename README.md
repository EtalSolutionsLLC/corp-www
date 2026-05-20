# Et al Solutions LLC Corporate Site

Static corporate website for Et al Solutions LLC.

## Portmason configuration

This site follows the Portmason static-site configuration pattern:

```text
.env
  -> portmason/pm-setup
  -> .env.generated
  -> config.generated.json
  -> assets/js/site-config.js
```

The browser never reads `.env` directly. Portmason reads `.env`, renders a browser-safe `config.generated.json`, and `assets/js/site-config.js` loads that generated file.

To regenerate config after changing `.env`:

```bash
./portmason/pm-setup
```

Primary config values:

- `APP_SLUG`
- `CM_ENV`
- `RUNTIME_ADAPTER_CODE`
- `APP_HOST`
- `SITE_URL`
- `SITE_CONTACT_EMAIL`
- `GTM_CONTAINER_ID`
- `GA4_MEASUREMENT_ID`

## Brand pages

The homepage includes a brand directory section. Individual brand pages live under `brands/`:

- `brands/simplifai.html`
- `brands/solutions-et-al.html`
- `brands/transformation-thread.html`
- `brands/25th-hour.html`

The brand directory data lives in `content/brands.json`.

## The Transformation Thread blog interface

The Transformation Thread brand page includes a native static blog interface at:

```text
brands/transformation-thread.html#blog
```

The interface is intentionally static and low-conflict. It uses the existing site CSS and does not embed a third-party blog widget.

Supporting content data lives in:

```text
content/transformation-thread-posts.json
```

For now, article cards link to email requests or future article URLs. When a real article is published, update both the card link in `brands/transformation-thread.html` and the matching `url` value in `content/transformation-thread-posts.json`.

## Transformation Thread blog title treatment

The Transformation Thread blog interface uses `.thread-blog-intro` as a title/intro panel and `.thread-featured-post` / `.thread-post-card` as article surfaces. Keep the title panel visually distinct so it does not read as another article card.

## Offer pages

Featured offers now live under `offers/`, similar to brand pages.

Current offer pages:

- `offers/index.html` — offer archive
- `offers/what-can-ai-do-for-you.html` — featured consumer A.I. offer
- `offers/ai-optimized-sdlc-assessment.html` — archived/professional SDLC offer

Offer metadata is stored in:

```text
content/offers.json
```

To swap the featured offer, update the homepage featured card/section and point it to the appropriate `offers/*.html` page. Keep previous offers in the archive so campaign history is not lost.
