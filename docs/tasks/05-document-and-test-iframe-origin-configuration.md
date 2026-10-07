---
depends-on: []
---

# 05. Deduce the catalogue origin in the iframe loader

This task makes the iframe loader find the catalogue without any attribute on the embedding page.

- Priority: High. The deployment of the upgraded runtime waits for it.
- Proposed owner: Frontend maintainer.

## Decision of 2026-10-07

The maintainer decided that external pages must not carry `data-site-url`.
The loader must deduce the catalogue address from the deployment configuration or from its own runtime properties.
This replaces the plan of 2026-10-04, which documented the attribute and asked every embedding page to add it.

## Proposed work

1. Remove the `data-site-url` attribute from the loader and from `README.rst`, "Embedding the species list".
2. Make the loader deduce the catalogue origin. The preferred source is the loader's own address, `document.currentScript.src`:
    - When the asset origin is the catalogue origin, as in development, use that origin.
    - When the asset origin is a `static.` label in front of the catalogue origin, as in the deployments, remove the label.
    - If a deployment needs another rule, give it through the deployment configuration, not through the embedding page.
3. Add checks for the three cases: same origin, a `static.` asset origin, and the embedding page on a third origin.
4. Document the rule in `README.rst` with fictional domains.

## Review evidence

The loader on `master` builds the frame address from `data-site-url`, or from the embedding page's origin without it.
The embedding page is on a third origin, so the loader without the attribute requests the catalogue from the wrong origin.
The private deployment repository records the check of 2026-10-07 and the inventory of embedding pages.
The deployments serve the loader from `static.<catalogue host>` and the catalogue from `<catalogue host>`.

## Completion checks

- [ ] The loader needs no attribute on the embedding page.
- [ ] A page on a third origin that loads the script from the `static.` asset origin requests the catalogue origin.
- [ ] A page that loads the script from the catalogue origin requests the same origin.
- [ ] Public examples use fictional domains and contain no installation-specific addresses.

## Related work

The private deployment repository deploys a revision with this loader only after this task lands on `master`.
Its task 5 checks the live embed afterwards.
