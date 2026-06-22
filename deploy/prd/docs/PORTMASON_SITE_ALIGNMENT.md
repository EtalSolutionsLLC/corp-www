# Legacy Static Site Alignment Contract

Both the corporate and David sites use the same Portmason legacy static-site implementation.

## Common contract

- Shell `pm-setup` remains the orchestrator.
- `RUNTIME_ADAPTER_CODE=static-local` is used for development.
- `RUNTIME_ADAPTER_CODE=static-github` is used for production.
- `www/` is the authoritative site source.
- `deploy/prd/` is a synchronized deployment workspace.
- `pm-sync-deploy-from-root` owns production snapshot refresh and drift detection.
- Static PM regions are rendered through `pm-deploy-static` and executable hooks.
- Portmason Collections uses the shared `_system` runtime, schemas, profiles, and renderer.
- Development uses shared Traefik ingress; production publishes `deploy/prd/www` to GitHub Pages.
- Compose bind mounts use long syntax so container targets never retain literal quote characters.
- Production entrypoints are resolved from `REPO_ROOT`; relative executable assumptions are prohibited.
- The `solutions.etal.*` EPC label namespace is authoritative.

Site-specific content, collection instances, CSS, domains, analytics identifiers, and scheduled content behavior are intentional extension points.
