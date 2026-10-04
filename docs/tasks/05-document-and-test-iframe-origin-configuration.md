---
depends-on: []
---

# 05. Document and test iframe origin configuration

This proposal helps integrators configure embedded catalogues and understand the iframe loader's origin selection.

- Priority: Medium.
- Proposed owner: Frontend maintainer.

## Proposed work

1. Document the default origin and the data-site-url override.
2. Provide examples with separate embedding, asset, and catalogue origins.
3. Add focused checks for the default and explicitly configured iframe destinations.
4. Document the upgrade requirement for existing embeds before releasing the changed loader.

## Review evidence

The prepared [iframe loader](../../kasvimuseo/static/js/kasvimuseo/planted-species-iframe.js) selects `data-site-url` or the embedding page's origin.
The review reproduced both destinations. Existing cross-site embeds need an explicit catalogue origin.
The prepared [README](../../README.rst) introduces the attribute.

## Completion checks

- [ ] The default example resolves to the embedding origin.
- [ ] The configured example resolves to the catalogue origin even when the script uses a separate asset origin.
- [ ] Public examples use fictional domains and contain no installation-specific addresses.

## Related work

Complete this contract before maintainers update external embedding pages.
