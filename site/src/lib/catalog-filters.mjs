export const catalogFields = [
  ['simulation', 'code', 'Physics, 3D, and simulation', '물리·3D·시뮬레이션'],
  ['robotics', 'code', 'Robot learning, capture, and control', '로봇 학습·시연 수집·제어'],
  ['data-tooling', 'code', 'Data generation, processing, and orchestration', '데이터 생성·처리 및 실행'],
  ['nemo', 'code', 'NeMo and Physical AI tooling', 'NeMo와 피지컬 AI 도구'],
  ['driving', 'code', 'Autonomous driving', '자율주행'],
  ['discovery', 'resource', 'Discovery platforms and tools', '검색 플랫폼과 도구'],
  ['3d-assets', 'dataset', '3D assets and environments', '3D 자산과 환경'],
  ['robot-data', 'dataset', 'Robot demonstrations and motion', '로봇 시연과 동작'],
  ['perception', 'dataset', 'Robot perception', '로봇 인지'],
  ['driving-data', 'dataset', 'Driving, video, and world-model data', '자율주행·영상·월드 모델 데이터'],
  ['v2d-cosmos-data', 'dataset', 'V2D and Cosmos datasets', 'V2D 및 Cosmos 데이터셋'],
  ['models', 'model', 'Robot foundation models and VLAs', '로봇 파운데이션 모델과 VLA'],
  ['platforms', 'platform', 'Platforms, models, products, standards, and restricted code', '플랫폼·모델·제품·표준 및 제한적 공개 항목'],
  ['external', 'external', 'External models and tools', '함께 쓰는 외부 모델과 도구'],
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
  ['NVIDIA Internal Scientific Research and Development Model License', /\bNVIDIA Internal Scientific Research and Development Model License\b/i],
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
  if (kind === 'external' && /CC-BY assets/i.test(scopedTerms)) return 'review';
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
    browse: 'Browse by',
    featured: 'Featured',
    allProjects: 'Full catalog',
    featuredTitle: 'Featured tool guides',
    guide: 'Read guide',
    filters: 'Filters',
    sort: 'Sort by',
    sortDefault: 'Default order',
    sortAscending: 'Name A–Z',
    sortDescending: 'Name Z–A',
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
    title: '피지컬 AI 카탈로그',
    description: '프로젝트, 모델 체크포인트, 데이터셋, 플랫폼을 검색할 수 있습니다. 검색 결과에서 공식 자료와 가이드를 확인하세요.',
    browse: '둘러보기',
    featured: '추천',
    allProjects: '전체 카탈로그',
    featuredTitle: '주요 도구 가이드',
    guide: '가이드 보기',
    filters: '필터',
    sort: '정렬',
    sortDefault: '기본 순서',
    sortAscending: '이름 오름차순',
    sortDescending: '이름 내림차순',
    search: '카탈로그 검색',
    placeholder: 'Isaac Sim, GR00T, 3DGS 등',
    field: '분야',
    allFields: '모든 분야',
    license: '라이선스',
    allLicenses: '모든 라이선스',
    access: '공개 상태',
    allAccess: '모든 상태',
    clear: '필터 초기화',
    broader: '입력한 버전의 자료가 없어 프로젝트 이름으로 검색했습니다.',
    none: '검색 결과가 없습니다. 검색어를 바꾸거나 필터를 해제해 보세요.',
    more: '결과 더 보기',
    showing: '검색 결과 {matches}개 중 {visible}개',
    termsNote: '라이선스가 코드·가중치·데이터 중 어디에 적용되는지, 별도 사용 신청이 필요한지는 각 항목의 공식 자료를 확인하세요.',
    commit: '최근 커밋',
    review: '여러 조건·별도 약관·미확인',
    statuses: {
      public: '공개 또는 다운로드 가능',
      restricted: '신청 또는 동의 필요',
      announced: '발표 또는 프리뷰',
      archived: '보관된 저장소',
      documented: '제품 또는 공식 문서',
      unverified: '공개 여부 미확인',
    },
  },
};
