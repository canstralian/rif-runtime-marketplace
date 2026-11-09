# Forge Exchange static frontend

GitHub Pages port of the [Forge Exchange Floot prototype](https://forge-exchange.floot.app/).

This is a **demo catalog** containing six expressly fictional plugin concepts. It is not an installer, an executable security tool, a payment service, or a verified plugin directory. The real, installable RIF Runtime Claude Code plugin in this repository is maintained separately under `plugins/rif-runtime/`; do not confuse it with the six demo cards.

## Local development

Prerequisites: Node.js 22+ and npm.

```bash
cd web
npm install
npm run dev
npm run build
```

Vite outputs to `web/dist/`, which is intentionally gitignored. The production site uses `/rif-runtime-marketplace/` as its asset base path. The UI supports search, category filtering, keyboard-accessible details, and browser-local bookmark storage. Bookmarks do **not** sync across browsers or devices.

## GitHub Pages

`.github/workflows/pages.yml` builds on PRs and deploys on a push to `master`. In repository **Settings → Pages → Build and deployment**, set **Source** to **GitHub Actions**, then merge the PR.

Expected URL: https://canstralian.github.io/rif-runtime-marketplace/

No Floot runtime, backend, repository secrets, plugin installation, or payment service is required. The existing marketplace validation workflow remains unchanged.

## Provenance

The UI structure and the fictional catalog were adapted from the owner's Forge Exchange Floot prototype (read on 20 October 2026). Its original React components depended on Floot-provided UI primitives. This port replaces those primitives with portable React controls and Radix Dialog. The editorial purple/black design and original disclosures are preserved.
