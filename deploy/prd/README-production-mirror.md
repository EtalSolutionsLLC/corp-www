# Corp WWW Production Mirror — Build 039

This build adds a manual-only production promotion workflow targeting:

```text
EtalSolutionsLLC/www.etal.solutions
```

The published custom domain is:

```text
www.etal.solutions
```

## Promotion contract

```text
deploy/prd/www
→ clean staging copy
→ Portmason production finalization
→ deployment verification
→ public production mirror
```

The workflow requires a dedicated fine-grained token named:

```text
PRODUCTION_PAGES_MIRROR_TOKEN
```

Scope that token only to `EtalSolutionsLLC/www.etal.solutions` with:

- Contents: Read and write
- Metadata: Read

`OPS_AND_SOPS_READ_TOKEN` remains required for the pinned private Portmason
tooling checkout.

The existing direct GitHub Pages production deployment is intentionally left
unchanged for the first mirror validation. Retire it only after the mirror
repository, custom domain, and build-information panel have been verified.
