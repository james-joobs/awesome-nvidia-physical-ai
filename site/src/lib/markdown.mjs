import MarkdownIt from 'markdown-it';
import { cubeScene } from './assets.mjs';
import { copy, modelGuide, pageUrl, catalogs, repositoryFile, workflows } from './catalog.mjs';

import { availability, catalogFields, licenseLabel } from './catalog-filters.mjs';

const guides = import.meta.glob([
  '../../../docs/{en,ko}/workflows/*.md',
  '../../../docs/{en,ko}/labs/*.md',
  '../../../docs/{en,ko}/robot-foundation-models.md',
], { query: '?raw', import: 'default', eager: true });

const catalogSources = import.meta.glob('../../../CATALOG{,.ko}.md', {
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
  const lab = file.match(/^docs\/(en|ko)\/labs\/([\w-]+)\.md$/);
  if (lab) return pageUrl(lab[1], `labs/${lab[2]}`) + target.hash;
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

function parseCatalog(locale) {
  const { file } = catalogs[locale];
  const env = { sourcePath: file, tableLabel: copy[locale].modelTable };
  return { env, tokens: markdown.parse(catalogSources[`../../../${file}`], env) };
}

export function renderModelList(locale) {
  const { file, modelHeading } = catalogs[locale];
  const { env, tokens } = parseCatalog(locale);
  const isSection = (token) => token.type === 'heading_open' && token.tag === 'h2';
  const start = tokens.findIndex((token, index) => isSection(token) && tokens[index + 1].content === modelHeading);
  if (start < 0) throw new Error(`Missing model catalog section in ${file}`);
  const end = tokens.findIndex((token, index) => index > start && isSection(token));
  const section = tokens.slice(start + 3, end < 0 ? undefined : end);
  return markdown.renderer.render(section, markdown.options, env);
}


function extractRows(locale) {
  const { env, tokens } = parseCatalog(locale);
  const rows = [];
  let field;
  let inCatalog = false;
  let heading = '';
  for (const [index, token] of tokens.entries()) {
    if (token.type === 'heading_open') {
      const label = tokens[index + 1].content;
      if (token.tag === 'h2' && /^1\. /.test(label)) inCatalog = true;
      if (token.tag === 'h2' && /^4\. /.test(label)) inCatalog = false;
      heading = label.replace(/^\d+\. /, '');
      field = catalogFields.find((option) => option[locale] === heading);
    }
    if (!inCatalog || token.type !== 'tbody_open') continue;
    if (!field) throw new Error(`Unmapped catalog table in ${env.sourcePath}: ${heading}`);

    let cells = [];
    for (let next = index + 1; tokens[next].type !== 'tbody_close'; next++) {
      const cell = tokens[next];
      if (cell.type === 'inline') cells.push(cell.children);
      if (cell.type !== 'tr_close') continue;

      const [name, role, terms] = cells;
      const commit = field.kind === 'code' ? cells[3] : [];
      const links = field.kind === 'external' ? terms : cells.slice(commit.length ? 4 : 3).flat();
      const sources = [...name, ...links].filter((child) => child.type === 'link_open');
      const urls = sources.map((child) => child.attrGet('href'));
      if (!urls.length) throw new Error(`Missing catalog source in ${env.sourcePath} (${field.id})`);
      const identity = urls.map((url) => url.replace(/^docs\/(en|ko)\//, 'docs/').split('#')[0]).join(' ');
      const plain = (children) => markdown.renderer.renderInlineAsText(children, markdown.options, env);
      const html = (children) => markdown.renderer.renderInline(children, markdown.options, env);
      rows.push({
        key: field.id + ':' + identity,
        field: field.id,
        kind: field.kind,
        title: plain(name),
        name: html(name),
        role: html(role),
        terms: html(terms),
        commit: html(commit),
        termsText: plain(terms),
        commitText: plain(commit),
        links: field.kind === 'external' ? html(cells[3]) : cells.slice(commit.length ? 4 : 3).map(html).filter((item) => item !== '—').join(' · '),
        search: [plain(name), plain(role), plain(terms), field.en, field.ko, ...urls].join(' '),
      });
      cells = [];
    }
  }
  return rows;
}

export function catalogEntries(locale) {
  const english = extractRows('en');
  const korean = extractRows('ko');
  if (korean.length !== english.length || korean.some((entry, index) => entry.key !== english[index].key)) {
    throw new Error('English and Korean catalog tables must list the same entries in the same order.');
  }

  return (locale === 'en' ? english : korean).map((entry, index) => {
    const reference = english[index];
    return {
      ...entry,
      license: licenseLabel(reference.termsText, reference.kind),
      access: availability(reference.termsText, reference.commitText, reference.kind),
      search: english[index].search + ' ' + korean[index].search,
    };
  });
}
