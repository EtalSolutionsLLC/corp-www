# Et al Solutions LLC Corporate Site

Static corporate website for Et al Solutions LLC.

This site is rendered through Portmason. Source HTML, structural partials, collection manifests, collection data, collection styles, and environment values are combined during `pm-setup` to produce the working static site.

## Quick start

From the site root:

```bash
pm-setup
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
  api/**/*.json
  edge/capability-api/

Rendered SPA targets
  index.html
  index.html#lab
  index.html#brands
  index.html#promotions
  index.html#blog
```

Collection data and configuration belong only under `collections/`. The Systems Lab publishes static JSON contracts under `www/api/` and includes an optional Cloudflare Worker adapter under `edge/capability-api/`.

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

## Portmason Platform™ Systems Lab

The SPA target `/#lab` is the first public Portmason Platform™ product surface and a working part of the site. It is implemented as the `workspace` profile of Portmason Collections™.

The platform model is explicit:

```text
Portmason Platform™
├── Portmason Foundations™     # what systems are built from
│   └── Portmason Collections™ # one named Foundation
├── Portmason Operations™      # how systems are provisioned, deployed, and run
└── Portmason Tooling™         # the cross-cutting pm-* control surface
```

Foundations define the system. Tooling creates, validates, and controls it. Operations provisions, deploys, and runs it. Collections is not a fourth peer layer; it is a named Foundation.

The Lab tools demonstrate combinations of those capabilities rather than mapping one tool to one product family:

- consumption of GitHub's public status API;
- publication and browser consumption of versioned JSON/OpenAPI contracts;
- browser-local sentence-embedding inference using Transformers.js; and
- the existing PageSpeed/page-weight comparison.

The default Pages deployment requires no separate service. Static public
contracts live under `www/api/`. The optional `edge/capability-api/` adapter
publishes extensionless dynamic endpoints and normalizes the external status
response. All local development and deployment commands for the adapter run in
containers.

The language model is loaded only after the visitor selects **Run the local
model**. The visitor's text is processed on that device and is not submitted to
Et al.

## Portmason Collections™

Brands, Promotions, The Transformation Thread, and the Systems Lab use one reusable Portmason Collections™ runtime. Catalog, publication, and workspace are behavior profiles of the same foundation, not separate storage models.

```text
collections/
├── _system/
│   ├── collection.js                 # shared registry and initCollection(root)
│   ├── collection.css
│   ├── collection.schema.json
│   ├── item-base.schema.json
│   ├── catalog-item.schema.json
│   ├── publication-item.schema.json
│   ├── workspace-item.schema.json
│   ├── profiles/
│   │   ├── catalog.js
│   │   ├── publication.js
│   │   └── workspace.js
│   └── render-collection
├── brands/                            # catalog instance
├── promotions/                        # catalog instance
├── transformation-thread/             # publication instance
└── systems-lab/                       # workspace instance
    ├── collection.json
    ├── items.json
    ├── styles.css
    ├── workspace.js
    └── tools/*.html
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

The shared browser runtime is `collections/_system/collection.js`. Every rendered collection root enters through `initCollection(root)`, which resolves a registered profile and supplies a common runtime context. Profile modules contain behavior only:

- catalog: paging, hash state, details, keyboard handling, and responsive controls;
- publication: manifest-driven item loading and safe Markdown article rendering;
- workspace: tile activation, modal lifecycle, focus management, deep-link state, and lazy instance activation.

Collection-specific executable behavior remains with the instance. The Systems Lab registers its adapter from `collections/systems-lab/workspace.js`; the neutral workspace profile does not know about GitHub, OpenAPI, local models, or PageSpeed.

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
PM:COLLECTION-SYSTEMS-LAB
PM:COLLECTION-SCRIPTS
```

After changing a collection manifest, item registry, Markdown item, or collection style, run:

```bash
pm-setup
```


### Workspace profile

The Systems Lab uses `mode: workspace` and `layout: tile-gallery`. The page first renders the Portmason platform relationship, then lightweight visual launch tiles. Each tile declares the platform layers it demonstrates; it does not impersonate or define a product family. Selecting a tile opens one shared modal workspace with a 70/30 tool-to-guidance layout. Tool panels are loaded from the instance's `tools/*.html` files and initialized only when first opened.

The runtime lifecycle is:

```text
discover → open → initialize → interact → preserve/reset → close
```

The `lab` query parameter supports direct links to a specific tool without creating a separate page.

### Portmason and mark notices

Et al Solutions LLC is the company and Portmason Platform™ is the named technology platform. Portmason Foundations™ and Portmason Operations™ are the build and run planes. Portmason Tooling™ is the cross-cutting `pm-*` control surface. Portmason Collections™ is a named Foundation. A.I. Fusion℠ and SIMPLIFAI℠ are California-registered service marks of Et al Solutions LLC. The working evidence ledger is `docs/ip/PORTMASON_FIRST_USE_LEDGER.md`.

Do not use ® without a federal registration. Do not use “Patent Pending” unless a qualifying patent application has actually been filed and remains pending.

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
pm-setup
```

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
