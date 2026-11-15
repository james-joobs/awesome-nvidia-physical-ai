# Astro Pages Preview

Use Node.js 24 LTS from a checkout of this repository.

```sh
cd site
npm ci
npm run build
npm run preview
```

Open the local URL printed by Astro and append `/awesome-nvidia-physical-ai/` for the English home or `/awesome-nvidia-physical-ai/ko/` for Korean. Use `npm run dev` for live edits.

- Follow each workflow card from both homes. The language selector opens the matching guide and keeps the section when you follow an in-page link.
- Open the ecosystem map at full size, check the model table and selection guide, and download `cube-drop.usda` from the cube lesson.
- At a narrow viewport, check the stacked workflow cards and scroll the model table horizontally to reach the license and source columns.

The site reads the workflow and model Markdown from the repository and bundles the existing diagrams and lesson asset. Update paired section IDs in `src/lib/catalog.mjs` if the top-level sections of a guide change. The static output in `site/dist/` is configured for a GitHub Pages project site. GitHub Pages publishing will be configured after review.
