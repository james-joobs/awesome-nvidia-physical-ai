import { createHighlighter } from 'shiki';

const languages = {
  bash: { label: 'Shell', syntax: 'bash' },
  sh: { label: 'Shell', syntax: 'bash' },
  json: { label: 'JSON', syntax: 'json' },
  python: { label: 'Python', syntax: 'python' },
  py: { label: 'Python', syntax: 'python' },
  yaml: { label: 'YAML', syntax: 'yaml' },
  yml: { label: 'YAML', syntax: 'yaml' },
  usda: { label: 'OpenUSD', syntax: 'text' },
  mermaid: { label: 'Mermaid', syntax: 'text' },
};

const highlighter = await createHighlighter({
  langs: ['bash', 'json', 'python', 'yaml'],
  themes: ['github-light', 'github-dark'],
});

const labels = {
  en: { plain: 'Text', copy: 'Copy', copied: 'Copied', failed: 'Select the code to copy it' },
  ko: { plain: '텍스트', copy: '복사', copied: '복사됨', failed: '코드를 선택해서 복사하세요' },
};

export function renderCodeBlock(code, format, locale) {
  const text = labels[locale];
  const language = Object.hasOwn(languages, format) ? languages[format] : { label: text.plain, syntax: 'text' };
  const highlighted = highlighter.codeToHtml(code, {
    lang: language.syntax,
    themes: { light: 'github-light', dark: 'github-dark' },
    defaultColor: 'light-dark()',
    transformers: [{
      pre(node) {
        delete node.properties.style;
        node.properties.tabindex = 0;
        node.properties['aria-label'] = language.label;
      },
    }],
  });
  return `<div class="code-block">
    <div class="code-toolbar"><span>${language.label}</span>
      <button type="button" class="code-copy" data-copy-code data-copied="${text.copied}" data-copy-failed="${text.failed}" hidden>
        <span aria-live="polite">${text.copy}</span>
      </button>
    </div>
    ${highlighted}
  </div>`;
}
