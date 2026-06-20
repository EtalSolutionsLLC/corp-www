# Et al Capability API

A no-database edge adapter for the Systems Lab. It publishes the same public
capability contract served statically by GitHub Pages, plus a live normalized
GitHub dependency-status endpoint.

## Test

```bash
edge/capability-api/bin/test
```

## Deploy

Set `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`, then run:

```bash
edge/capability-api/bin/deploy
```

After deployment, set `CAPABILITY_API_BASE_URL` in the appropriate Portmason
environment configuration and run `pm-setup`. The Lab automatically uses the
edge API; without it, the public Pages JSON contracts remain functional.
