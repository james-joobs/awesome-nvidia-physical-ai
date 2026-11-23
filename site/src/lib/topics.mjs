import workbenchImage from '../../../assets/lessons/workbench/workbench-viewport.webp?url&no-inline';
import alpasimImage from '../../../assets/project-marks/alpasim-hdmap.webp?url&no-inline';
import cosmosImage from '../../../assets/project-marks/cosmos.png?url&no-inline';
import switchyardImage from '../../../assets/project-marks/switchyard-logo.webp?url&no-inline';
import { modelGuide, workflows } from './catalog.mjs';
import { courseRoute, workbenchProject } from './learning.mjs';
import { clips, grids, showcaseMedia } from './showcase.mjs';
import { toolGuides } from './tool-guides.mjs';

const workbench = {
  ...workbenchProject,
  image: workbenchImage,
  tools: ['OpenUSD', 'Isaac Sim 6.2', 'Replicator'],
  kind: 'screenshot',
  en: { ...workbenchProject.en, alt: 'CAD workbench open in the Isaac Sim viewport' },
  ko: { ...workbenchProject.ko, alt: 'Isaac Sim 뷰포트에 열린 CAD 작업대' },
};
const drivingGuide = workflows.find(({ slug }) => slug === 'alpasim-closed-loop');
const driving = {
  ...drivingGuide,
  page: `workflows/${drivingGuide.slug}`,
  image: alpasimImage,
  kind: 'official',
  credit: { label: 'AlpaSim', url: 'https://github.com/NVlabs/alpasim/blob/affc2eab209fa43bdfa2f26c0f8d437922d78a68/docs/VIDEO_MODEL.md#how-it-works' },
  en: { ...drivingGuide.en, alt: 'Official AlpaSim frame with a high-definition map overlaid on a road scene' },
  ko: { ...drivingGuide.ko, alt: '도로 카메라 영상에 정밀지도를 겹친 AlpaSim 공식 예시' },
};

export const topicGuides = [
  {
    page: 'tools/cosmos', source: 'cosmos', image: cosmosImage, kind: 'official', fit: 'contain',
    sections: ['architecture', 'example', 'access', 'related-tools'], tools: ['Cosmos', 'Cosmos Data Factory'],
    credit: { label: 'NVIDIA Cosmos', url: 'https://github.com/NVIDIA/cosmos-framework/blob/5950e7b4ea3677b99a2de279a7ed7058b5446e42/tools/docs/images/cosmos-logo.png' },
    en: { title: 'Cosmos world models', description: 'See how video and scene conditions become inputs for generation or reasoning.', alt: 'NVIDIA Cosmos logo' },
    ko: { title: 'Cosmos 월드 모델', description: '영상과 장면 조건을 어떻게 입력하고, 영상 생성이나 추론에 어떻게 쓰는지 살펴봅니다.', alt: 'NVIDIA Cosmos 로고' },
  },
  {
    page: 'tools/nemo-switchyard', source: 'nemo-switchyard', image: switchyardImage, kind: 'official', fit: 'contain',
    sections: ['architecture', 'example', 'verification', 'license', 'official-sources', 'related-tools'], tools: ['NeMo Switchyard', 'NIM'],
    credit: { label: 'NVIDIA NeMo', url: 'https://github.com/NVIDIA-NeMo/Switchyard' },
    en: { title: 'Route model requests with NeMo Switchyard', description: 'Follow a request from a video analysis app to a model endpoint and see what to check before serving it.', alt: 'NeMo Switchyard project artwork' },
    ko: { title: 'NeMo Switchyard로 모델 요청 보내기', description: '영상 분석 앱의 요청이 모델 서버에 전달되는 과정을 살펴보고, 서비스를 연결할 때 확인할 항목을 알아봅니다.', alt: 'NeMo Switchyard 공식 프로젝트 이미지' },
  },
];

function recording(id, tools, kind = 'recording') {
  const clip = [...clips, ...grids].find((item) => item.id === id);
  return { ...clip, page: `labs/${id}`, clip, image: showcaseMedia(`${id}.jpg`), tools, kind };
}

export const topics = [
  {
    slug: 'simulation', theme: 'lime', icon: 'cube',
    stacks: ['Isaac Sim', 'PhysX', 'Newton', 'Warp', 'SimReady'],
    resources: [[`workflows/${workflows[0].slug}`, workflows[0].en.action, workflows[0].ko.action]],
    en: { title: 'Physics & simulation', description: 'See what changes when you swap a collider, adjust friction, or calculate forces on the GPU.' },
    ko: { title: '물리·시뮬레이션', description: '충돌체나 마찰을 바꾸면 물체가 어떻게 움직이는지 보고, GPU로 입자 충돌도 계산해 보세요.' },
    focus: {
      en: { title: 'Physics engines', outcome: 'Compare collision shapes, friction, and bouncing in Isaac Sim; inspect Newton and Warp simulation results.', availability: 'Recorded runs · scripts and USD scenes' },
      ko: { title: '물리 엔진·시뮬레이션', outcome: 'Isaac Sim에서 충돌체·마찰·반발력에 따른 차이를 보고, Newton과 Warp의 계산 결과도 확인합니다.', availability: '실행 영상 · 코드와 USD 장면' },
    },
    entries: [recording('newton-materials', ['Newton', 'Warp', 'Isaac Sim']), recording('physics', ['Isaac Sim', 'PhysX', 'SimReady', 'Newton']), recording('warp-particles', ['Warp', 'CUDA'])],
  },
  {
    slug: 'synthetic-data', theme: 'mint', icon: 'workbench', course: 'simulation-data',
    stacks: ['OpenUSD', 'Replicator', 'AIF Pipeline Samples', 'SimReady', 'fVDB Reality Capture'],
    en: { title: '3D assets & synthetic data', description: 'Build a scene from CAD, capture color and depth, and check that the labels line up.' },
    ko: { title: '3D 에셋·합성 데이터', description: 'CAD를 시뮬레이션 장면으로 만들고 RGB·깊이·마스크를 뽑아 같은 시점의 데이터인지 확인합니다.' },
    entries: [workbench, recording('scene-to-data', ['OpenUSD', 'Isaac Sim', 'Replicator']), recording('replicator-outputs', ['Replicator', 'Isaac Lab'], 'advanced')],
  },
  {
    slug: 'robotics', theme: 'lime', icon: 'robot', course: 'robot-policies',
    stacks: ['Isaac Lab', 'GR00T', 'cuRobo', 'Isaac Capture', 'AutoData'],
    resources: [[modelGuide.route, 'Compare robot foundation models', '로봇 파운데이션 모델 비교하기']],
    en: { title: 'Robotics & control', description: 'Check a pick-and-place policy, plan around obstacles, and replay a learned walk.' },
    ko: { title: '로봇 학습·제어', description: '로봇 팔이 큐브를 집어 옮기는지 판정하고, 장애물을 우회하는 경로와 학습한 보행을 확인합니다.' },
    focus: {
      en: { title: 'Robotics', outcome: 'Judge a GR00T pick-and-place trial, explore obstacle avoidance, and follow a Microduck walking policy.', availability: 'Browser lab · recorded runs and code' },
      ko: { title: '로봇 학습·제어', outcome: 'GR00T의 집기 성공 여부를 판정하고, 장애물 회피 경로와 Microduck의 보행 정책을 살펴봅니다.', availability: '브라우저 실습 · 실행 영상과 코드' },
    },
    entries: [recording('gr00t-placement', ['GR00T', 'Isaac Lab-Arena']), recording('robot-motion', ['cuRobo', 'AutoData', 'GR00T', 'Newton']), recording('microduck', ['Isaac Lab', 'Newton']), recording('everyday-robots', ['Isaac Sim', 'PhysX'])],
  },
  {
    slug: 'autonomous-driving', theme: 'blue', icon: 'car', course: 'driving-evaluation',
    stacks: ['NVIDIA 3DGRUT', 'COLMAP', 'Spark', 'CARLA', 'AlpaSim', 'NuRec', 'Harmonizer', 'Alpamayo', 'AlpaGym', 'DRIVE Sim'],
    en: { title: 'Autonomous driving', description: 'Reconstruct a real road from RGB alone, orbit around a Volvo in 3D, then explore CARLA sensors, model predictions and closed-loop evaluation.' },
    ko: { title: '자율주행', description: 'RGB 사진만으로 실사 도로를 복원하고 Volvo 주변을 3D로 둘러보세요. CARLA 센서, 주행 모델의 예측, 폐루프 평가로 이어집니다.' },
    focus: {
      en: { title: 'Autonomous driving', outcome: 'RGB → COLMAP → NuRec and Harmonizer, with Alpamayo predictions and source-RGB perception. Inspect each stage from one RTX 5090 run.', availability: 'RGB only · interactive 3D · code and checks' },
      ko: { title: '자율주행', outcome: 'RGB → COLMAP → NuRec·Harmonizer에 Alpamayo 예측과 원본 RGB 인식을 연결했습니다. RTX 5090 한 장에서 실행한 각 단계를 직접 확인합니다.', availability: 'RGB 전용 · 3D 직접 조작 · 코드와 결과 검사' },
    },
    entries: [recording('nurec-rgb-reality', ['RGB only', 'NuRec', 'Harmonizer', 'Alpamayo 2 Edge']), recording('rgb-reality-view', ['RGB only', 'COLMAP', 'NVIDIA 3DGUT', 'Spark']), recording('pandaset-nurec', ['PandaSet', 'NuRec', 'Harmonizer', 'Blender']), recording('carla-ego', ['CARLA', 'Unreal Engine', 'Ego RGB']), recording('reality-view', ['NuRec', 'Harmonizer', 'Alpamayo 2 Edge', 'Isaac Sim']), driving, recording('world-driving', ['Isaac Sim', 'Alpamayo2-Edge', 'Cosmos3-Edge'])],
  },
  {
    slug: 'world-models', theme: 'blue', icon: 'layers',
    stacks: ['WorldGen', 'Lyra', 'fVDB', 'Spark / World Labs', 'Infinigen', 'Cosmos', 'Cosmos Curator', 'Cosmos Data Factory', 'Video-to-Data', 'NeMo Switchyard'],
    en: { title: '3D worlds & rendering', description: 'Explore 3D Gaussian scenes, generate indoor geometry, and compare these with neural 3D world generation and video world models.' },
    ko: { title: '3D 세계 생성·렌더링', description: '3DGS 공간을 직접 둘러보고 실내 기하 구조를 생성합니다. 생성형 3D 세계·사진 복원·영상 월드 모델의 차이도 살펴보세요.' },
    focus: {
      en: { title: '3D worlds & world models', outcome: 'Generate a 3D world with WorldGen, explore fVDB reconstruction and procedural houses, then compare Marble, Lyra and video models.', availability: 'Interactive 3DGS · Recorded experiments · generation and reconstruction separated' },
      ko: { title: '3D 세계·월드 모델', outcome: 'WorldGen으로 만든 공간과 fVDB 복원 장면을 직접 둘러보세요. 절차적 생성, Marble·Lyra, 영상 모델의 입출력도 비교합니다.', availability: '탐색 가능한 3DGS · GPU 실행 · 생성과 복원 구분' },
    },
    entries: [recording('worldgen-scenes', ['WorldGen', 'FLUX.1', 'DA-2']), recording('worldgen-isaac', ['WorldGen', 'Isaac Sim 6.2', 'PhysX']), recording('worldgen-navigation', ['WorldGen', 'Isaac Sim 6.2', 'Physics Raycast Sensor']), recording('worldgen-dynamic-navigation', ['WorldGen', 'Isaac Sim 6.2', 'Physics Raycast Sensor']), recording('spatial-reconstruction', ['fVDB', 'CARLA', 'Spark / World Labs']), recording('scene-generation', ['Infinigen', 'Blender']), recording('world-driving', ['Cosmos3-Edge', 'Alpamayo2-Edge', 'Isaac Sim']), ...topicGuides],
  },
].sort((left, right) => {
  const order = ['robotics', 'simulation', 'world-models', 'autonomous-driving', 'synthetic-data'];
  return order.indexOf(left.slug) - order.indexOf(right.slug);
}).map((topic) => ({
  ...topic,
  guides: toolGuides.filter((guide) => guide.topic === topic.slug || topic.stacks.includes(guide.en.title)),
}));

export const focusTopics = ['robotics', 'simulation', 'world-models', 'autonomous-driving']
  .map((slug) => topics.find((topic) => topic.slug === slug));

export function topicForPage(page) {
  return topics.find(({ entries, guides, resources, course }) => (course && courseRoute(course) === page) ||
    entries.some((entry) => entry.page === page) || guides.some((guide) => guide.page === page) ||
    resources?.some(([route]) => route === page));
}

export const topicsCopy = {
  en: {
    nav: 'Lab topics', browse: 'Explore lab topics', all: 'All topics', topicNav: 'Browse by topic',
    intro: 'See what each stack can do, then open the lab for the commands, scene files, and checks.',
    examples: 'Labs and examples', tools: 'Tools in this topic', principles: 'How these tools work', openLab: 'Open lab', openGuide: 'Read the guide',
    recording: 'Recorded run', screenshot: 'Lab capture', advanced: 'Advanced lab', official: 'Reference guide',
    officialMedia: 'Official visual', capturedMedia: 'Captured in Isaac Sim',
  },
  ko: {
    nav: '실습 분야', browse: '분야별 실습 둘러보기', all: '전체 분야', topicNav: '분야 선택',
    intro: '도구별로 어떤 결과를 만들 수 있는지 먼저 살펴보세요. 실습 페이지에서 실행 명령과 장면 파일, 결과 검사 방법을 확인할 수 있습니다.',
    examples: '실습과 예제', tools: '이 분야의 도구', principles: '도구별 동작 원리', openLab: '실습 보기', openGuide: '가이드 보기',
    recording: '실행 영상', screenshot: '실습 화면', advanced: '심화 실습', official: '참고 가이드',
    officialMedia: '공식 이미지', capturedMedia: 'Isaac Sim 실습 화면',
  },
};
