# Corp WWW Empty Mirror Bootstrap — Build 033

The public mirror may start as a completely empty GitHub repository with no
commit and no default branch.

The workflow now:

1. Initializes a local mirror repository.
2. Checks whether remote `main` exists.
3. Fetches existing `main` when present.
4. Creates an orphan `main` when the mirror is empty.
5. Publishes the sanitized static site.
6. Pushes and establishes `main`.

No README or manual first commit is required in the mirror repository.
