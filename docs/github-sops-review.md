# GitHub Actions SOPS support

## Changed files and sections

- `/home/davidomer/code/corp-www/.github/workflows/portmason-setup-and-deploy.yml`: installs pinned SOPS 3.13.3 with a SHA-256 checksum from the official release; the setup step receives `secrets.SOPS_AGE_KEY` and fails clearly if missing.
- `/home/davidomer/code/david/.github/workflows/portmason-setup-and-deploy.yml`: same active workflow changes. Disabled workflows were not changed.
- `/home/davidomer/code/corp-www/docs/github-sops-review.md`: this change record.

Both workflows previously had neither SOPS installation nor age private-key injection. David confirmed that the Actions secret had not yet been created. The failing run log was not supplied, so the exact logged error remains unverified.

## Required GitHub setup

For each repository, Settings → Secrets and variables → Actions → New repository secret. Name: `SOPS_AGE_KEY`. Value: the existing age private key matching the encrypted environment's recipient (`AGE-SECRET-KEY-…`, not `age1…`). A repository-accessible organization secret is also acceptable where supported. The workflow reference is already present under Run Portmason setup → env.

Push the local workflow changes, then start a new workflow run so it uses the updated workflow. Rerunning an old failed run can retain its old workflow revision.

## Verification and limits

Both workflow YAML files parsed; embedded shell scripts passed bash syntax checks; secret references and focused diff formatting passed. SOPS decryption was verified with a disposable encrypted dotenv fixture and a generated temporary age key supplied solely through SOPS_AGE_KEY. The fixture/key were removed without displaying values. No new repository tests were added.

No GitHub secret was read, created or changed by Codex. No workflow was pushed, dispatched or rerun. No deployment files were inspected or edited, and pm-setup was not executed locally. User-generated environment/build files were left alone.
