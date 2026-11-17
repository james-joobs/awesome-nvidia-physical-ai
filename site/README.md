# GitHub Pages site

Use Node.js 24 LTS from a checkout of this repository.

```sh
cd site
npm ci
npm run build
npm run preview
```

Open the local URL printed by Astro and append `/awesome-nvidia-physical-ai/` for the English home or `/awesome-nvidia-physical-ai/ko/` for Korean. Use `npm run dev` for live edits.

- Follow each learning path and its lesson links from both homes. The language selector opens the matching page and keeps the section when you follow an in-page link.
- Open the browser exercise from both homes. Submit an incorrect answer and a correct answer, then follow the link to the Python result check.
- Open the catalog on both homes. Try search and all three filters together, clear the search, and switch languages with filters active.
- Open the ecosystem map at full size, check the model table and selection guide, and download `cube-drop.usda` from the cube lesson.
- At a narrow viewport, check the stacked learning paths and scroll the model table horizontally to reach the license and source columns.

The site reads workflow guides from `docs/` and the model table from `CATALOG.md` and `CATALOG.ko.md` and bundles the existing diagrams and lesson asset. Update paired section IDs in `src/lib/catalog.mjs` if the top-level sections of a guide change. The static output in `site/dist/` is configured for a GitHub Pages project site. The catalog search reads the same Markdown tables. Keep the English and Korean rows in matching order and update the field labels in `src/lib/catalog-filters.mjs` when renaming a section. The deploy workflow publishes from `main` and runs again after the weekly commit-date refresh succeeds.
