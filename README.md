# Et al Solutions LLC Corporate Site

Static corporate website for Et al Solutions LLC.

This site is rendered through Portmason. Source HTML, structural partials, catalog JSON, catalog CSS, and environment values are combined during `pm-setup` to produce the working static site.

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

The site separates structure, catalog data, catalog styling, and rendered routes:

```text
Structural HTML
  partials/*.html
  public page shells and PM render regions

Catalog data
  catalogs/*.json

Catalog styling
  catalogs/*.css

Rendered routes
  index.html
  brands/*.html
  index.html#promotions
```

Keep the distinction clear:

```text
Partials define shared structure.
Catalog JSON files define catalog data/content.
Catalog CSS files define reusable catalog presentation.
HTML pages define public routes, page-specific copy, and stable anchors.
```

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
partials/brand-header.html
partials/promotion-header.html
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

## Catalog collection model

Catalogs are reusable data-driven collections.

Each catalog lives in:

```text
catalogs/<catalog-name>/catalog.json
catalogs/<catalog-name>/items.json
catalogs/<catalog-name>/<catalog-name>.css
```

Current catalog:

```text
catalogs/promotions/catalog.json
catalogs/promotions/items.json
catalogs/promotions/promotions.css
```

The catalog name is declared by each catalog manifest. For example:

```text
catalogs/promotions/catalog.json + items.json + promotions.css = self-registering promotions catalog
catalogs/blog/catalog.json + items.json + blog.css = blog catalog
catalogs/services/catalog.json + items.json + services.css = services catalog
```

The catalog renderer should stay domain-agnostic. A promotion is not a special renderer type; it is a catalog item displayed on the promotions route.

Use generic catalog fields such as:

```text
id
slug
status
label
title
shortTitle
subtitle
audience
summary
description
price
priceNote
primaryAction
secondaryAction
tags
attributes
sections
sortOrder
```

Avoid data keys that over-couple the renderer to a specific domain, such as:

```text
promotionTitle
promotionSummary
promotionCta
promotionStatus
```

Route-specific page copy may still say “Promotions,” “Services,” or “Blog.” The data model and renderer should remain catalog-oriented.

## Catalog CSS

Catalog styling is intentionally isolated from the main stylesheet.

The promotions catalog stylesheet is:

```text
catalogs/promotions/promotions.css
```

It styles both:

```text
homepage featured catalog teaser/summary
index.html#promotions full catalog page
```

This makes the catalog component easier to reuse or resell. A future customer-specific implementation can replace or customize the catalog stylesheet without digging through the global site CSS.

## Homepage featured catalog item

The homepage keeps a featured catalog summary section at:

```html
<section class="section-light panel" id="promotions" aria-labelledby="featured-promotion-title">
  <!-- PM:CATALOG-PROMOTIONS-FEATURED -->
  ...
  <!-- /PM:CATALOG-PROMOTIONS-FEATURED -->
</section>
```

Portmason renders this region from the featured item in:

```text
catalogs/promotions/items.json
```

The homepage hero also has a smaller teaser region:

```html
<!-- PM:CATALOG-PROMOTIONS-HERO-TEASER -->
...
<!-- /PM:CATALOG-PROMOTIONS-HERO-TEASER -->
```

That teaser is also rendered from the same featured catalog item.

## Promotions page

The promotions page is:

```text
index.html#promotions
```

Public URL:

```text
/#promotions
```

This is the full promotions destination. It renders the featured/current item first and then renders the remaining catalog items below it.

Each item receives a stable section anchor based on its slug:

```text
/#<slug>
```

The full-list render region is:

```html
<!-- PM:CATALOG-PROMOTIONS-FULL-LIST -->
...
<!-- /PM:CATALOG-PROMOTIONS-FULL-LIST -->
```

Do not create one-off standalone promotion pages for normal catalog items. The full detail view lives as a section on `/#promotions`.

## Launching a new featured catalog item

Use this process when promoting a new offer to the homepage.

### 1. Edit the catalog data

Update:

```text
catalogs/promotions/items.json
```

Add or update the catalog item record.

### 2. Set item state

Set the new item as:

```json
"status": "featured"
```

Set the outgoing item to an appropriate non-featured status, such as:

```json
"status": "past"
```

There should normally be exactly one featured item.

### 3. Confirm generic fields

Confirm the item has appropriate values for:

```text
id
slug
title
subtitle
summary
description
price
priceNote
primaryAction
tags
attributes
sortOrder
```

### 4. Render the site

```bash
./portmason/pm-setup
```

### 5. Verify

Check:

```text
Homepage hero teaser renders the featured catalog item.
Homepage /#promotions renders the featured catalog summary.
The mobile swipe hint appears on the featured catalog summary.
The featured item links to /#<slug> for details.
/#promotions renders the featured item first.
/#promotions renders all other catalog items below it.
No per-item standalone promotion page is required.
```

## Mobile swipe behavior

Some mobile sections use horizontal swipe panels instead of long stacked content.

Current mobile swipe areas include:

```text
Services
Homepage featured catalog summary
```

Swipe hints should be visible on mobile only and should remain consumer-facing.

Example:

```html
<p class="mobile-swipe-hint catalog-swipe-hint" aria-hidden="true" data-swipe-hint data-forward-text="Swipe sideways for details" data-back-text="Swipe left for summary">Swipe sideways for details <span>→</span></p>
```

The behavior is handled by:

```text
```

Do not remove the hints unless the section no longer uses a horizontal swipe layout.

## Brand pages

Brand pages live under:

```text
brands/
```

The brand directory data lives in:

```text
content/brands.json
```

The homepage brand section uses this data for the brand cards.

Individual brand pages are static HTML pages and use shared brand header/footer partials.

## The Transformation Thread blog interface

The Transformation Thread brand page includes a native static blog interface at:

```text
brands/transformation-thread.html#blog
```

Supporting card data lives in:

```text
content/transformation-thread-posts.json
```

The interface is intentionally static and low-conflict. It uses the existing site CSS and does not embed a third-party blog widget.

## Data vs structural naming

Use names that make ownership clear.

Good examples:

```text
catalogs/promotions/catalog.json
catalogs/promotions/items.json
catalogs/promotions/promotions.css
PM:CATALOG-PROMOTIONS-HERO-TEASER
PM:CATALOG-PROMOTIONS-FEATURED
PM:CATALOG-PROMOTIONS-FULL-LIST
```

Avoid names that imply JSON owns structure, such as:

```text
PM:PROMOTIONS-JSON
```

The render region is structural. The JSON file is only the data source.

## Common checks

Search for catalog references:

```bash
grep -RIn --exclude-dir=.git --exclude-dir=capture \
  -e 'catalogs/promotions/items.json' \
  -e 'PM:CATALOG-PROMOTIONS' \
  -e 'catalog-featured' \
  .
```

Check for stale promotion-specific render references:

```bash
grep -RIn --exclude-dir=.git --exclude-dir=capture \
  -e 'PM:PROMOTIONS-CURRENT-FEATURED' \
  -e 'PM:PROMOTIONS-ARCHIVE' \
  -e 'catalogs/promotions/items.json' \
  -e 'PM:CATALOG' \
  .
```

Run Portmason:

```bash
./portmason/pm-setup
```
