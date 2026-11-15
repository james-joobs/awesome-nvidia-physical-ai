export const languages = ['en', 'ko'];
export const repository = 'https://github.com/james-joobs/awesome-nvidia-physical-ai';

export function pageUrl(locale, page = '') {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const language = locale === 'ko' ? 'ko/' : '';
  return `${base}/${language}${page ? `${page}/` : ''}`;
}

export function repositoryFile(file) {
  return `${repository}/blob/main/${file}`;
}

export const catalogs = {
  en: { file: 'CATALOG.md', modelHeading: 'Robot foundation models and VLAs' },
  ko: { file: 'CATALOG.ko.md', modelHeading: '로봇 파운데이션 모델과 VLA' },
};

export const workflows = [
  {
    slug: 'isaac-sim-first-cube',
    theme: 'lime',
    icon: 'cube',
    tools: ['Isaac Sim', 'PhysX'],
    sections: ['open-the-scene', 'build-the-scene', 'execution-environment'],
    en: {
      goal: 'Learn simulation basics',
      title: 'Drop your first cube',
      description: 'Run the same scene twice to see how a rigid body and a collider change what happens.',
      result: 'A cube that settles on the floor.',
      action: 'Open cube lesson',
    },
    ko: {
      goal: '시뮬레이션 기초 익히기',
      title: 'Isaac Sim 큐브 낙하',
      description: '같은 큐브를 두 번 떨어뜨려 강체와 충돌체가 각각 어떤 역할을 하는지 확인합니다.',
      result: '큐브가 바닥을 통과하지 않고 멈춥니다.',
      action: '큐브 낙하 실습',
    },
  },
  {
    slug: 'workbench-cad-to-isaac-sim',
    theme: 'mint',
    icon: 'workbench',
    tools: ['AIF Pipeline Samples', 'OpenUSD', 'Isaac Sim'],
    sections: ['requirements', 'convert-to-usd', 'compose-the-scene', 'camera-data', 'pick-and-place', 'verification'],
    en: {
      goal: 'Build a simulation scene',
      title: 'Workbench CAD to Isaac Sim',
      description: 'Convert a STEP file to OpenUSD and check the tabletop’s dimensions and collision geometry.',
      result: 'A reusable workbench scene with working collisions.',
      action: 'Open CAD guide',
    },
    ko: {
      goal: '시뮬레이션 장면 만들기',
      title: '작업대 CAD → Isaac Sim',
      description: 'STEP 파일을 OpenUSD로 변환하고 작업대의 치수와 충돌 형상을 검증합니다.',
      result: '치수와 충돌을 확인한 재사용 가능한 장면을 만듭니다.',
      action: 'CAD 변환 가이드',
    },
  },
  {
    slug: 'alpasim-closed-loop',
    theme: 'blue',
    icon: 'car',
    tools: ['AlpaSim', 'NuRec'],
    sections: ['requirements', 'run-the-scene', 'inspect-the-results', 'use-your-own-logs', 'verification'],
    en: {
      goal: 'Evaluate a driving policy',
      title: 'AlpaSim closed-loop evaluation',
      description: 'Run the baseline policy on one reconstructed driving scene with the NuRec renderer.',
      result: 'A completed rollout with collision and off-road metrics.',
      action: 'Open AlpaSim guide',
    },
    ko: {
      goal: '자율주행 정책 평가하기',
      title: 'AlpaSim 폐루프 평가',
      description: 'NuRec으로 재구성한 주행 장면 하나에서 기준 정책을 실행합니다.',
      result: '롤아웃을 완료하고 충돌·도로 이탈 지표를 확인합니다.',
      action: 'AlpaSim 평가 가이드',
    },
  },
];

export const modelGuide = {
  route: 'models/selection',
  sections: ['evaluate-actions', 'cosmos-policy', 'other-vlas', 'world-action-models'],
  en: {
    title: 'Choose and evaluate a robot foundation model',
    description: 'Match the checkpoint to your robot or benchmark, then verify one rollout.',
  },
  ko: {
    title: '로봇 파운데이션 모델 선택과 평가',
    description: '대상 로봇이나 벤치마크에 맞는 체크포인트를 골라 롤아웃 하나를 검증합니다.',
  },
};

export const copy = {
  en: {
    skip: 'Skip to content',
    navigation: 'Main navigation',
    language: 'Language',
    workflows: 'Workflows',
    ecosystem: 'Ecosystem map',
    models: 'Models',
    catalog: 'Full catalog on GitHub',
    community: 'Independent community guide',
    heroTitle: 'Build your first',
    heroAccent: 'Physical AI workflow.',
    heroDescription: 'Pick a goal, find the tools you need, and follow a hands-on guide to your first result.',
    heroAction: 'Choose a workflow',
    workflowHeading: 'What do you want to build?',
    toolLabel: 'Tools',
    resultLabel: 'First result',
    ecosystemHeading: 'How the ecosystem fits together',
    ecosystemDescription: 'Start with the input you have. The map traces how 3D assets, driving logs, and robot demonstrations each lead to a result you can evaluate.',
    mapAlt: 'Three Physical AI paths from inputs to results. CAD becomes an OpenUSD simulation scene, driving logs become a scene for AlpaSim, and demonstrations become robot training data.',
    openMap: 'Open full-size map',
    modelsHeading: 'Robot foundation models and VLAs',
    modelAction: 'Read the model selection guide',
    modelTable: 'Model comparison',
    referenceTable: 'Reference table',
    source: 'Read the Markdown on GitHub',
    download: 'Download cube-drop.usda',
    isaacSimGuide: 'Isaac Sim tool guide',
    onThisPage: 'On this page',
    otherWorkflows: 'More workflows',
    license: 'License and credits',
  },
  ko: {
    skip: '본문으로 건너뛰기',
    navigation: '주 메뉴',
    language: '언어',
    workflows: '실습 경로',
    ecosystem: '생태계 지도',
    models: '모델 목록',
    catalog: 'GitHub에서 전체 목록 보기',
    community: '독립 커뮤니티 가이드',
    heroTitle: '만들고 싶은 것부터',
    heroAccent: 'Physical AI를 시작하세요.',
    heroDescription: '목표를 고르면 필요한 도구와 첫 실습에서 확인할 결과를 바로 볼 수 있습니다.',
    heroAction: '실습 경로 고르기',
    workflowHeading: '무엇을 만들고 싶나요?',
    toolLabel: '필요한 도구',
    resultLabel: '첫 실습 결과',
    ecosystemHeading: '도구들이 어떻게 연결되는지 한눈에 보기',
    ecosystemDescription: '가지고 있는 입력부터 출발하세요. 3D 자산, 주행 로그, 로봇 시연 데이터가 각각 어떤 검증 결과로 이어지는지 보여줍니다.',
    mapAlt: 'Physical AI의 세 경로. CAD는 OpenUSD 시뮬레이션 장면으로, 주행 로그는 AlpaSim 평가 장면으로, 로봇 시연은 정책 학습 데이터로 이어집니다.',
    openMap: '지도 원본 크기로 열기',
    modelsHeading: '로봇 파운데이션 모델과 VLA',
    modelAction: '모델 선택·평가 가이드 보기',
    modelTable: '모델 비교표',
    referenceTable: '참고 표',
    source: 'GitHub에서 Markdown 원문 보기',
    download: 'cube-drop.usda 다운로드',
    isaacSimGuide: 'Isaac Sim 도구 가이드',
    onThisPage: '이 문서에서',
    otherWorkflows: '다른 실습 경로',
    license: '라이선스와 출처',
  },
};
