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

## Promotion pages and featured-promotion partials

Promotions use the same structural/data split as brands:

```text
partials/promotions/*.html  = structural HTML fragments used by the homepage render
content/promotions.json     = data/catalog metadata used for archive/list behavior
promotions/*.html           = standalone promotion landing pages
promotions/index.html       = promotion archive page
```

Current promotion pages:

- `promotions/index.html` — promotion archive
- `promotions/what-can-ai-do-for-you.html` — current consumer A.I. promotion
- `promotions/ai-optimized-sdlc-assessment.html` — past/professional SDLC promotion

Current promotion partials:

- `partials/promotions/current-featured.html` — the homepage promotion slot rendered by `pm-setup`
- `partials/promotions/what-can-ai-do-for-you.html` — reusable source partial for the current consumer promotion
- `partials/promotions/ai-optimized-sdlc-assessment.html` — reusable source partial for the SDLC promotion

The homepage owns the stable anchor and wrapper:

```html
<section class="section-light panel" id="promotions" aria-labelledby="featured-promotion-title">
<!-- PM:PROMOTIONS-CURRENT-FEATURED -->
  ...rendered promotion partial...
<!-- /PM:PROMOTIONS-CURRENT-FEATURED -->
</section>
```

To swap the featured promotion:

```bash
cp partials/promotions/current-featured.html    partials/promotions/<old-promotion-slug>.html

cp partials/promotions/<new-promotion-slug>.html    partials/promotions/current-featured.html

pm-setup
```

Each promotion partial should include a link to the archive:

```html
<a class="hero-cta secondary" href="/promotions/">Past Promotions</a>
```

Keep naming clear:

```text
Structural HTML: partials/promotions/current-featured.html
Catalog data:    content/promotions.json
Landing pages:   promotions/<promotion-slug>.html
```
