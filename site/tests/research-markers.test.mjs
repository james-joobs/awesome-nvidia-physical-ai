import assert from 'node:assert/strict';
import test from 'node:test';
import MarkdownIt from 'markdown-it';
import { hideResearchMarkers } from '../src/lib/research-markers.mjs';

const marker = '<!-- research-events:41e30500a422c7d4deb10a09,fa4daa163823614eae7ca287 -->';
const markdown = () => new MarkdownIt({ linkify: true }).use(hideResearchMarkers);

test('bilingual research tables retain their sources without exposing review IDs', () => {
  for (const label of ['Project page', '프로젝트 페이지']) {
    const source = `| Research | Sources |\n|---|---|\n| **BirdDreams** | [${label}](https://research.nvidia.com/labs/sil/projects/birddreams/) · [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) ${marker} |`;
    const html = markdown().render(source);
    assert.match(html, /<strong>BirdDreams<\/strong>/);
    assert.ok(html.includes(`>${label}</a>`));
    assert.ok(html.includes('href="https://research.nvidia.com/labs/sil/projects/birddreams/"'));
    assert.ok(html.includes('href="https://creativecommons.org/licenses/by/4.0/"'));
    assert.doesNotMatch(html, /research-events|41e30500a422c7d4deb10a09/);
    assert.ok(source.includes(marker), 'source metadata remains available to the review queue');
  }
});

test('inline and fenced code examples preserve literal comment syntax', () => {
  const html = markdown().render('`' + marker + '`\n\n```html\n' + marker + '\n```');
  assert.equal(html.match(/research-events:/g)?.length, 2);
  assert.ok(html.includes('&lt;!--'));
});

test('hiding tracking metadata does not enable raw HTML or strip ordinary prose', () => {
  const html = markdown().render('<script>alert("sample")</script>\n\n<!-- teaching note -->');
  assert.doesNotMatch(html, /<script>/);
  assert.ok(html.includes('&lt;script&gt;'));
  assert.ok(html.includes('teaching note'));
});
