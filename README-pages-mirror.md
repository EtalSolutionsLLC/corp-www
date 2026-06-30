# Corp WWW Pages Mirror — Build 028

This build adds the reusable GitHub Pages mirror publisher without changing
website content, the featured promotion, or any ReviewNudge URL.

## Changed files

- `.github/workflows/publish-pages-mirror.yml`
- `tests/test_pages_mirror_workflow.py`

## Required GitHub setup

Create the public mirror repository:

```text
EtalSolutionsLLC/corp-www-test-pages
```

Initialize it with a `main` branch and enable GitHub Pages from `main` at `/`.

Create a fine-grained GitHub token that can write repository contents only to
the approved mirror repositories. Store it in the private authoritative
`corp-www` repository as:

```text
PAGES_MIRROR_TOKEN
```

## First test publication

Run **Publish GitHub Pages mirror** manually with:

```text
target_repository: EtalSolutionsLLC/corp-www-test-pages
source_path: deploy/prd/www
custom_domain:
```

Leaving `custom_domain` blank uses the default GitHub Pages hostname and avoids
touching production DNS.

## Cutover order

1. Publish and verify the test mirror.
2. Confirm the mirror contains only static publication artifacts.
3. Convert the existing production repository into the production mirror.
4. Remove direct `actions/upload-pages-artifact` and `actions/deploy-pages`
   steps from `gen-site-html.yml`.
5. Verify both mirrors.
6. Change `EtalSolutionsLLC/corp-www` visibility to private.

Do not make `corp-www` private until the mirror token and private-repository
workflow execution have been verified.
