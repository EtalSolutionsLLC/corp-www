# Et al Solutions LLC Corporate Site

Static corporate website for Et al Solutions LLC.

This site is rendered through Portmason. Source HTML, structural partials, collection manifests, collection data, collection styles, and environment values are combined during `pm-setup` to produce the working static site.

## Quick start

From the site root:

```bash
./portmason/pm-setup
```

Then serve locally:

```bash
serve
```

or, for a specific page:

```bash
serve index.html#promotions
```

## Rendering model

Portmason owns repeatable static rendering.

```text
.env
  -> portmason/pm-setup
  -> portmason/pm-deploy-static
  -> rendered HTML pages
```

The site separates shared structure, registered collections, non-collection content, and rendered SPA targets:

```text
Structural HTML
  partials/*.html
  partials/hooks/*

Registered collections
  collections/<collection-id>/collection.json
  collections/<collection-id>/items.json
  collections/<collection-id>/styles.css
  collections/<collection-id>/items/         # optional long-form item content
  collections/<collection-id>/generated/     # optional generated collection state

Non-collection content
  content/*.json

Rendered SPA targets
  index.html
  index.html#brands
  index.html#promotions
  index.html#blog
```

Collection data and configuration belong only under `collections/`. The `content/` directory is reserved for data that is not a reusable collection, such as the Explore decision tree.

## Environment values

Common values are managed through `.env` and rendered by Portmason where needed.

Important values include:

```text
APP_SLUG
DEPLOY_ENV
RUNTIME_ADAPTER_CODE
APP_HOST
SITE_URL
SITE_CONTACT_EMAIL
GTM_CONTAINER_ID
GA4_MEASUREMENT_ID
```

Tracking markup is structural HTML and is rendered through tracking partials. The GTM container ID is data supplied from `.env`.

GA4 should be configured inside the GTM container unless there is a deliberate reason to load it separately. This avoids duplicate page-view events.

## Tracking and consent partials

Tracking and consent markup is rendered into pages through PM regions.

Current tracking partials:

```text
partials/tracking-consent-part1.html
partials/tracking-consent-part2.html
```

The cookie banner behavior lives in:

```text
assets/js/cookie-consent.js
```

Do not duplicate GTM loading in browser-side runtime scripts.

## Shared partials

Shared site structure lives in:

```text
partials/header.html
partials/footer.html
```

Pages preserve PM marker pairs so `pm-setup` can be re-run safely.

Example:

```html
<!-- PM:FOOTER -->
...
<!-- /PM:FOOTER -->
```

Do not remove PM marker pairs unless the page is being intentionally detached from Portmason rendering.

## Served build marker

The site exposes the static artifact version in three ways:

```text
Footer copyright → About this build dialog
View Source      → ETAL_SITE_BUILD comment and meta tag
Automation       → /build-info.json
```

The authoritative build number lives in the repository-root `VERSION` file. The
`SITE-BUILD-META` executable partial hook writes deterministic HTML metadata and
a runtime `www/build-info.json` containing the source commit, UTC materialization
time, deployment target, and builder. The JSON file is included in the served
artifact but intentionally ignored by Git because its timestamp changes on every
materialization.

The footer copyright remains visually unchanged; selecting it opens the build
information dialog.

## Collection System

Brands, Promotions, and The Transformation Thread use one reusable Collection System. Catalog and publication are behavior profiles of the same foundation, not separate storage models.

```text
collections/
├── _system/
│   ├── collection.js
│   ├── collection.css
│   ├── collection.schema.json
│   └── render-collection
├── brands/
│   ├── collection.json
│   ├── items.json
│   └── styles.css
├── promotions/
│   ├── collection.json
│   ├── items.json
│   └── styles.css
└── transformation-thread/
    ├── collection.json
    ├── items.json
    ├── styles.css
    ├── items/<permanent-id>/*.md
    └── generated/selection.json
```

Every manifest declares a stable collection id, behavior mode, layout, data file, style file, presentation, labels, and Portmason render regions. Catalog manifests own their entire SPA section heading and wrapper; the entry page contains only collection render markers.

```json
{
  "id": "brands",
  "mode": "catalog",
  "layout": "carousel",
  "dataFile": "items.json",
  "styleFile": "styles.css"
}
```

```json
{
  "id": "transformation-thread",
  "mode": "publication",
  "layout": "featured-grid",
  "dataFile": "items.json",
  "styleFile": "styles.css"
}
```

The shared browser controller is `collections/_system/collection.js`. Catalog profile behavior includes paging, hash state, details, keyboard handling, and responsive controls. Publication profile behavior includes manifest-driven item loading and safe Markdown article rendering inside the SPA.

The shared catalog carousel chrome is `collections/_system/collection.css`. Each collection keeps its visual identity in its own `styles.css`. The `COLLECTION-STYLES` render hook discovers registered manifests and materializes the stylesheet links, so collection style configuration is not duplicated in `index.html`.

### Structural rendering

Collection manifests and data are authoritative. Static HTML for the SPA is materialized by executable Portmason hooks in `partials/hooks/`, which delegate to `collections/_system/render-collection`. Do not keep hand-maintained collection HTML partials beside the data.

Current render markers are:

```text
PM:COLLECTION-STYLES
PM:COLLECTION-BRANDS
PM:COLLECTION-PROMOTIONS-HERO-TEASER
PM:COLLECTION-PROMOTIONS
PM:COLLECTION-TRANSFORMATION-THREAD
```

After changing a collection manifest, item registry, Markdown item, or collection style, run:

```bash
pm-setup
```

### Catalog profile

Brands and Promotions use `mode: catalog`. Their `items.json` files share a common item contract with optional fields such as logo, price, tags, attributes, and primary action. The renderer adapts to the fields present; domain-specific configuration is not scattered through JavaScript or partials.

Catalog sections land directly on the configured default item. A separate overview is optional and must not become the default landing experience.

### Publication profile

The Transformation Thread uses `mode: publication` and remains inside the main SPA at `/#blog`. It has no standalone page, header, footer, or redirect shell.

Its manifest owns presentation and selection policy. Its `items.json` registry owns permanent ids, editorial slots, categories, status, and Markdown references. Long-form files live under the same collection:

```text
collections/transformation-thread/items/008/title.md
collections/transformation-thread/items/008/excerpt.md
collections/transformation-thread/items/008/full-article.md
```

Daily rotation writes only the generated selection state:

```text
collections/transformation-thread/generated/selection.json
```

The collection renderer reads that selection when `pm-setup` materializes the SPA. The rotation command no longer edits an HTML partial.

Manual local rotation:

```bash
bin/rotate-transformation-thread \
  --force \
  --collection www/collections/transformation-thread/collection.json
pm-setup
```

Manual GitHub rotation remains available under **Actions → Generate site HTML → Run workflow**. Leave **Rotation date** blank to use the current date in the configured timezone, or enter an ISO date such as `2026-06-19`. Scheduled runs retain the local-midnight guard.

### Ownership rule

Do not create or restore `www/catalogs/`, `www/content/transformation-thread*`, collection-specific JavaScript under `assets/js/`, collection-specific CSS under `assets/css/`, or hand-maintained collection HTML partials. Those are legacy locations and are removed by `bin/cleanup-root`.

## Repository cleanup

The repository root is the authoritative working source. Each `deploy/<env>/`
directory is a preserved snapshot of the root from the time that deployment was
built and must not be selectively cleaned or deduplicated.

Use the repeatable root cleanup command to remove verified obsolete source files
and generated workspace residue without changing any deployment snapshot:

```bash
bin/cleanup-root --dry-run
bin/cleanup-root
```

The command protects `.project_timestamp`, `.env`, `.env.generated`,
`config.generated.json`, `www/`, and every `deploy/*` tree.

## Common checks

Check for forbidden legacy collection locations:

```bash
grep -RIn --exclude-dir=.git --exclude-dir=deploy --exclude-dir=capture \
  -e 'www/catalogs/' \
  -e 'content/transformation-thread' \
  -e 'PM:CATALOG-' \
  -e 'PM:TRANSFORMATION-THREAD' \
  .
```

Run Portmason:

```bash
./portmason/pm-setup
```

## Explore decision tree

The corp-site Explore panel is a first-class SPA section at:

```text
/#explore
```

Its Portmason-managed structural source is:

```text
partials/explore.html
```

The main SPA owns the render region:

```html
<!-- PM:EXPLORE -->
...
<!-- /PM:EXPLORE -->
```

The two-level conditional tree data lives in:

```text
content/explore-decision-tree.json
```

The native browser controller lives in:

```text
assets/js/explore-decision-tree.js
```

The shared action-anchor design system and Explore-specific presentation live in:

```text
assets/css/action-system.css
assets/css/explore.css
```

Do not hand-edit the rendered `PM:EXPLORE` block in `index.html`. Update the partial or JSON source, then run:

```bash
pm-setup
```

The performance counter is intentionally browser-observed and lives inside Explore. It does not claim a Lighthouse or Core Web Vitals score.

## Homepage 60-second summary

The homepage keeps a compact `In a hurry? Read the 60-second version.` trigger. The substantive summary opens in a standard top-layer dialog so it does not consume hero viewport space.

The isolated component assets are:

```text
assets/css/home-quick-summary.css
assets/js/home-quick-summary.js
```

The dialog uses the shared circular `×` modal-close standard and supports its close button, Escape, clicking outside the dialog, and modal action navigation.

### Viewport composition practice

When composing a screen between the shared header and footer, preserve approximately half an inch of visible breathing room at the top and bottom whenever practical. Treat this as a design-review judgment, not as a global CSS rule.
