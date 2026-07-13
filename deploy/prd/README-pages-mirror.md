# Corp WWW Finalized Test Artifact — Build 035

The test mirror no longer publishes the raw `www/` working tree.

The workflow now:

1. Checks out the authoritative source.
2. Checks out the exact Portmason revision pinned by `.portmason-tooling-ref`.
3. Copies `www/` into a clean staging artifact.
4. Finalizes the artifact with source, build, deployment, timestamp, and SHA metadata.
5. Verifies the finalized deployment contract.
6. Publishes only that verified artifact to the public mirror.
7. Writes the deterministic custom domain `www-test.etal.solutions`.

Automatic test publication remains tied to `main`; manual dispatch remains
available for recovery. Production remains separate and manual.
