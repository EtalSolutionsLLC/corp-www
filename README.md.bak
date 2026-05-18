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
