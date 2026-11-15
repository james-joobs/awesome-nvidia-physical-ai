import MarkdownIt from 'markdown-it';
import { cubeScene } from './assets.mjs';
import { copy, modelGuide, pageUrl, readme, repositoryFile, workflows } from './catalog.mjs';

const guides = import.meta.glob([
  '../../../docs/{en,ko}/workflows/*.md',
  '../../../docs/{en,ko}/robot-foundation-models.md',
], { query: '?raw', import: 'default', eager: true });

const readmes = import.meta.glob('../../../README{,.ko}.md', {
  query: '?raw', import: 'default', eager: true,
});

const markdown = new MarkdownIt({ linkify: true });
const renderToken = (tokens, index, options, _env, renderer) =>
  renderer.renderToken(tokens, index, options);

function resolveLink(link, sourcePath) {
  if (/^(?:[a-z][a-z\d+.-]*:|\/\/|#)/i.test(link)) return link;

  const target = new URL(link, `https://repository.invalid/${sourcePath}`);
  const file = decodeURIComponent(target.pathname.slice(1));
  const guide = file.match(/^docs\/(en|ko)\/workflows\/(.+)\.md$/);
  if (guide && workflows.some(({ slug }) => slug === guide[2])) {
    return pageUrl(guide[1], `workflows/${guide[2]}`);
  }

  const model = file.match(/^docs\/(en|ko)\/robot-foundation-models\.md$/);
  if (model) return pageUrl(model[1], modelGuide.route);
  if (file === 'assets/lessons/isaac-sim-first-cube/cube-drop.usda') return cubeScene;

  return repositoryFile(file) + target.search + target.hash;
}

markdown.renderer.rules.link_open = (tokens, index, options, env, renderer) => {
  const token = tokens[index];
  const href = resolveLink(token.attrGet('href'), env.sourcePath);
  token.attrSet('href', href);
  if (href === cubeScene) token.attrSet('download', 'cube-drop.usda');
  return renderToken(tokens, index, options, env, renderer);
};

markdown.renderer.rules.table_open = (tokens, index, options, env, renderer) => {
  const label = markdown.utils.escapeHtml(env.tableLabel);
  return `<div class="table-scroll" tabindex="0" role="region" aria-label="${label}">`
    + renderToken(tokens, index, options, env, renderer);
};

markdown.renderer.rules.table_close = (tokens, index, options, env, renderer) =>
  renderToken(tokens, index, options, env, renderer) + '</div>\n';

export function renderGuide(locale, sourcePath, sectionIds) {
  const source = guides[`../../../${sourcePath}`];
  if (!source) throw new Error(`Missing guide: ${sourcePath}`);

  const env = { sourcePath, tableLabel: copy[locale].referenceTable };
  const tokens = markdown.parse(source, env);

  // The site layout supplies the title, language switch, and navigation.
  if (tokens[0]?.type === 'heading_open' && tokens[0].tag === 'h1') tokens.splice(0, 3);
  if (tokens[0]?.type === 'paragraph_open' && /\]\(\.\.\/(?:\.\.\/)?(?:en|ko)\//.test(tokens[1]?.content)) {
    tokens.splice(0, 3);
  }

  const headings = [];
  for (const [index, token] of tokens.entries()) {
    if (token.type !== 'heading_open' || token.tag !== 'h2') continue;

    const id = sectionIds[headings.length];
    const label = tokens[index + 1].content;
    token.attrSet('id', id ?? `section-${headings.length + 1}`);
    headings.push({ id: token.attrGet('id'), label });
  }
  if (headings.length !== sectionIds.length) {
    throw new Error(`Update the paired section links for ${sourcePath}`);
  }

  return { headings, html: markdown.renderer.render(tokens, markdown.options, env) };
}

export function renderModelList(locale) {
  const { file, modelHeading } = readme[locale];
  const env = { sourcePath: file, tableLabel: copy[locale].modelTable };
  const tokens = markdown.parse(readmes[`../../../${file}`], env);
  const isSection = (token) => token.type === 'heading_open' && token.tag === 'h2';
  const start = tokens.findIndex((token, index) => isSection(token) && tokens[index + 1].content === modelHeading);
  if (start < 0) throw new Error(`Missing model catalog section in ${file}`);
  const end = tokens.findIndex((token, index) => index > start && isSection(token));
  const section = tokens.slice(start + 3, end < 0 ? undefined : end);
  return markdown.renderer.render(section, markdown.options, env);
}
