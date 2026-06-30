# Corp WWW Deterministic Test Mirror — Build 031

This build supersedes Build 028.

The test deployment contains no runtime choices. The workflow is permanently
bound to:

```text
source repository: EtalSolutionsLLC/corp-www
source artifact:   deploy/dev/www
mirror repository: EtalSolutionsLLC/corp-www-test-pages
custom domain:     none
```

The workflow presents one action only:

```text
Run workflow
```

It does not ask for a repository, source path, environment, or domain.

Production publication is intentionally not included in this build. It will use
its own separately named, parameterless workflow after the test mirror pattern
has been verified.
