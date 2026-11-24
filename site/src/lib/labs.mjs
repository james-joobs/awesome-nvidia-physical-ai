import manifest from '../../../labs/index.json';

const files = import.meta.glob(['../../../labs/*/*.{py,sh,json,yaml,patch,js,mjs,html,css,txt}', '../../../labs/*/guidance/*.{py,yaml,txt}', '../../../labs/*/temporal/*.{py,mjs,json}'], {
  query: '?raw', import: 'default', eager: true,
});

export const { labs, heroTags, scenes } = manifest;
const labsById = new Map(labs.map((lab) => [lab.id, lab]));

export function findLab(id) {
  const lab = labsById.get(id);
  if (!lab) throw new Error(`No lab for ${id}`);
  return lab;
}

export function labCode({ id, code }) {
  return code.map((name) => {
    const path = `labs/${id}/${name}`;
    const source = files[`../../../${path}`];
    if (source === undefined) throw new Error(`Missing lab source ${path}`);
    return { name, path, source };
  });
}

export const labCopy = {
  en: {
    action: 'Try the lab',
    back: 'Video gallery',
    tools: 'Tools used',
    run: 'Run the lab',
    code: 'Source code',
    github: 'View files on GitHub',
    evidence: 'Open the recorded result',
    index: 'All labs on GitHub',
  },
  ko: {
    action: '실습 따라 하기',
    back: '영상 갤러리',
    tools: '사용한 도구',
    run: '실습 실행하기',
    code: '실습 소스 코드',
    github: 'GitHub에서 파일 보기',
    evidence: '촬영 당시 결과 열기',
    index: 'GitHub에서 전체 실습 보기',
  },
};
