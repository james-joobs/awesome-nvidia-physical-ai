export const catalogFields = [
  ['simulation', 'code', 'Physics, 3D, and simulation', '물리, 3D 및 시뮬레이션'],
  ['robotics', 'code', 'Robot learning, capture, and control', '로봇 학습, 수집 및 제어'],
  ['data-tooling', 'code', 'Data generation, processing, and orchestration', '데이터 생성·처리 및 실행'],
  ['nemo', 'code', 'NeMo and Physical AI tooling', 'NeMo와 물리 AI 도구'],
  ['driving', 'code', 'Autonomous driving', '자율주행'],
  ['discovery', 'resource', 'Discovery platforms and tools', '검색 플랫폼과 도구'],
  ['3d-assets', 'dataset', '3D assets and environments', '3D 자산과 환경'],
  ['robot-data', 'dataset', 'Robot demonstrations and motion', '로봇 시연과 동작'],
  ['perception', 'dataset', 'Robot perception', '로봇 인지'],
  ['driving-data', 'dataset', 'Driving, video, and world-model data', '자율주행·영상·월드 모델 데이터'],
  ['v2d-cosmos-data', 'dataset', 'V2D and Cosmos datasets', 'V2D 및 Cosmos 데이터셋'],
  ['models', 'model', 'Robot foundation models and VLAs', '로봇 파운데이션 모델과 VLA'],
  ['platforms', 'platform', 'Platforms, models, products, standards, and restricted code', '플랫폼·모델·제품·표준 및 제한적 공개 항목'],
  ['external', 'external', 'External models and tools', '대화에서 함께 언급된 외부 모델·도구'],
].map(([id, kind, en, ko]) => ({ id, kind, en, ko }));

const licenseRules = [
  ['Apache-2.0', /\bApache[- ]2\.0\b/i],
  ['BSD-3-Clause', /\bBSD[- ]3[- ]Clause\b/i],
  ['MIT', /\bMIT\b/],
  ['TOST 1.0', /\bTOST 1\.0\b/i],
  ['CC BY 4.0', /\bCC[- ]BY[- ]4\.0\b/i],
  ['CC BY-NC 4.0', /\bCC[- ]BY[- ]NC[- ]4\.0\b/i],
  ['CC BY-NC-SA 4.0', /\bCC[- ]BY[- ]NC[- ]SA[- ]4\.0\b/i],
  ['OpenMDW-1.1', /\bOpenMDW[- ]1\.1\b/i],
  ['NVIDIA Open Model License', /\bNVIDIA Open Model License\b/i],
  ['NVIDIA One-Way Noncommercial', /\bNVIDIA One[- ]Way Noncommercial\b/i],
  ['NVIDIA Community License', /\bNVIDIA Community License\b/i],
  ['NVIDIA Isaac ROS Software License', /\bNVIDIA Isaac ROS Software License\b/i],
  ['NVIDIA Source Code License', /\bNVIDIA Source Code License\b/i],
  ['NVIDIA Software License Agreement', /\bNVIDIA Software License Agreement\b/i],
  ['FLUX Kommunity License', /\bFLUX Kommunity License\b/i],
];

export function licenseLabel(terms, kind) {
  // A checkpoint entry can also mention the license of its source repository.
  const scopedTerms = kind === 'model' ? terms.split(/· openpi code is /i)[0] : terms;
  if (/^Apache-2\.0 with a modified trademark clause/i.test(scopedTerms)) return 'review';
  if (/\bTOST 1\.0\b/i.test(scopedTerms)) return 'TOST 1.0';
  if (/\bLlama 2 Community License\b/i.test(scopedTerms)) return 'review';
  const labels = licenseRules.filter(([, pattern]) => pattern.test(scopedTerms)).map(([label]) => label);
  return labels.length === 1 ? labels[0] : 'review';
}

export function availability(terms, commit, kind) {
  if (/\bArchived\b/.test(commit)) return 'archived';
  if (kind === 'code') return 'public';
  if (/partner rollout|access (?:gated|required|acceptance required)/i.test(terms)) return 'restricted';
  if (/\bAnnounced\b|^Research reports\b|\bPre-release\b|^Beta platform\b/i.test(terms)) return 'announced';
  if (/^Downloadable\b|\bpublic (?:repository|browsing|spaces?|model repositories)\b|\bsource (?:is public|available)\b|; public\s*$/i.test(terms)) {
    return 'public';
  }
  if (/public documentation|^Hardware product|^Product\b|^Platform\b|^Blueprint\b/i.test(terms)) return 'documented';
  return 'unverified';
}

export const catalogCopy = {
  en: {
    title: 'Physical AI catalog',
    description: 'Search projects, model checkpoints, datasets, and platforms. Each entry links to its source and available guides.',
    search: 'Search the catalog',
    placeholder: 'Try Isaac Sim, GR00T, or 3DGS',
    field: 'Field',
    allFields: 'All fields',
    license: 'License',
    allLicenses: 'All licenses',
    access: 'Availability',
    allAccess: 'All statuses',
    clear: 'Clear filters',
    broader: 'No match for that version. Showing matching project names.',
    none: 'No matches. Try a different search or clear a filter.',
    more: 'Show more results',
    showing: 'Showing {visible} of {matches} matching entries',
    termsNote: 'Filters use the catalog’s recorded terms. Check each entry for the scope of the license and the access requirements.',
    commit: 'Latest commit',
    review: 'Mixed, custom, or unverified terms',
    statuses: {
      public: 'Public or downloadable',
      restricted: 'Access required',
      announced: 'Announced or preview',
      archived: 'Archived repository',
      documented: 'Product or documentation',
      unverified: 'Availability unverified',
    },
  },
  ko: {
    title: 'Physical AI 카탈로그',
    description: '프로젝트, 모델 체크포인트, 데이터셋과 플랫폼을 검색하세요. 각 항목에서 공식 출처와 상세 가이드를 열 수 있습니다.',
    search: '카탈로그 검색',
    placeholder: 'Isaac Sim, GR00T, 3DGS 등',
    field: '분야',
    allFields: '모든 분야',
    license: '라이선스',
    allLicenses: '모든 라이선스',
    access: '공개 상태',
    allAccess: '모든 상태',
    clear: '필터 초기화',
    broader: '해당 버전과 일치하는 항목이 없어, 이름이 맞는 프로젝트를 표시합니다.',
    none: '검색 결과가 없습니다. 검색어를 바꾸거나 필터를 해제해 보세요.',
    more: '결과 더 보기',
    showing: '검색 결과 {matches}개 중 {visible}개 표시',
    termsNote: '필터는 카탈로그에 기록된 정보를 사용합니다. 라이선스 적용 범위와 접근 조건은 각 항목의 원문을 확인하세요.',
    commit: '최근 커밋',
    review: '혼합·별도 약관 또는 미확인',
    statuses: {
      public: '공개 또는 다운로드 가능',
      restricted: '접근 절차 필요',
      announced: '발표 또는 프리뷰',
      archived: '보관된 저장소',
      documented: '제품 또는 공식 문서',
      unverified: '공개 상태 미확인',
    },
  },
};
