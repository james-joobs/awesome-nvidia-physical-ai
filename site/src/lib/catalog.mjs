export const languages = ['en', 'ko'];
export const repository = 'https://github.com/james-joobs/awesome-nvidia-physical-ai';

export function pageUrl(locale, page = '') {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const language = locale === 'ko' ? 'ko/' : '';
  return `${base}/${language}${page ? `${page}/` : ''}`;
}

export function catalogSearchUrl(locale, query) {
  return `${pageUrl(locale, 'catalog')}?q=${encodeURIComponent(query)}`;
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
    sections: ['implementation', 'execution-environment', 'open-the-scene', 'build-the-scene', 'verify'],
    en: {
      goal: 'Learn simulation basics',
      title: 'Drop your first cube',
      description: 'Run the same scene twice to see how a rigid body and a collider change what happens.',
      result: 'A cube that settles on the floor.',
      action: 'Open cube lesson',
    },
    ko: {
      goal: '시뮬레이션 기초 익히기',
      title: 'Isaac Sim에서 큐브 떨어뜨리기',
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
    sections: ['implementation', 'requirements', 'convert-to-usd', 'compose-the-scene', 'camera-data', 'pick-and-place', 'verification'],
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
      description: 'STEP 파일을 OpenUSD로 변환한 뒤 작업대 치수와 충돌체를 확인합니다.',
      result: '카메라 데이터 생성이나 로봇 실습에 쓸 작업대 장면을 만듭니다.',
      action: 'CAD 변환 가이드',
    },
  },
  {
    slug: 'alpasim-closed-loop',
    theme: 'blue',
    icon: 'car',
    tools: ['AlpaSim', 'NuRec'],
    sections: ['implementation', 'requirements', 'run-the-scene', 'inspect-the-results', 'use-your-own-logs', 'verification'],
    en: {
      goal: 'Evaluate a driving policy',
      title: 'AlpaSim closed-loop evaluation',
      description: 'Run the baseline policy on one reconstructed driving scene with the NuRec renderer.',
      result: 'A completed rollout with collision and off-road metrics.',
      action: 'Open AlpaSim guide',
    },
    ko: {
      goal: '자율주행 정책 평가하기',
      title: 'AlpaSim으로 자율주행 정책 평가하기',
      description: 'NuRec으로 복원한 주행 장면에서 기준 정책을 실행합니다.',
      result: '주행을 마친 뒤 충돌·도로 이탈 지표를 확인합니다.',
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
    title: '로봇 파운데이션 모델 고르고 평가하기',
    description: '로봇이나 벤치마크에 맞는 체크포인트를 고르고, 정책을 한 번 실행해 결과를 확인합니다.',
  },
};

export const copy = {
  en: {
    skip: 'Skip to content',
    navigation: 'Main navigation',
    language: 'Language',
    workflows: 'Learning paths',
    ecosystem: 'Ecosystem map',
    models: 'Models',
    browseCatalog: 'Catalog',
    catalog: 'Full catalog on GitHub',
    community: 'Independent community guide',
    heroTitle: 'Learn NVIDIA',
    heroAccent: 'Physical AI by doing.',
    ecosystemHeading: 'How the ecosystem fits together',
    ecosystemDescription: 'Start with the input you have. The map traces how 3D assets, driving logs, and robot demonstrations each lead to a result you can evaluate.',
    mapAlt: 'Three workflows. Build an OpenUSD scene from CAD and generate labeled data in Isaac Sim. Reconstruct driving logs with NuRec and evaluate a policy in AlpaSim. Turn demonstrations into training data for Isaac Lab or GR00T, then evaluate and deploy the policy.',
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
    navigation: '메인 메뉴',
    language: '언어',
    workflows: '학습 경로',
    ecosystem: '생태계 지도',
    models: '로봇 모델',
    browseCatalog: '카탈로그',
    catalog: 'GitHub에서 전체 목록 보기',
    community: '독립 커뮤니티 가이드',
    heroTitle: 'NVIDIA 피지컬 AI,',
    heroAccent: '실습으로 배우기',
    ecosystemHeading: '도구를 어떻게 연결해 쓰나요?',
    ecosystemDescription: 'CAD, 주행 로그, 로봇 시연 데이터가 있다면 어떤 도구를 거쳐 시뮬레이션, 주행 평가, 정책 학습에 쓸 수 있는지 살펴보세요.',
    mapAlt: '세 가지 작업 흐름. CAD를 OpenUSD 장면으로 변환해 Isaac Sim에서 라벨이 붙은 데이터를 만듭니다. NuRec으로 주행 장면을 복원해 AlpaSim에서 정책을 평가합니다. 로봇 시연을 데이터셋으로 만들어 Isaac Lab이나 GR00T로 학습한 뒤 정책을 평가하고 배포합니다.',
    openMap: '지도 크게 보기',
    modelsHeading: '로봇 파운데이션 모델과 VLA',
    modelAction: '모델 선택·평가 가이드 보기',
    modelTable: '모델 비교표',
    referenceTable: '참고 자료',
    source: 'GitHub에서 Markdown 원문 보기',
    download: 'cube-drop.usda 다운로드',
    isaacSimGuide: 'Isaac Sim 가이드',
    onThisPage: '목차',
    otherWorkflows: '다른 실습',
    license: '라이선스와 출처',
  },
};
