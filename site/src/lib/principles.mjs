import { modelGuide, workflows } from './catalog.mjs';
import { firstExerciseRoute, onboardingGuides, workbenchProject, workbenchRecordingRoute } from './learning.mjs';
import { clips, grids } from './showcase.mjs';
import { topicGuides, topics } from './topics.mjs';
import { toolGuides } from './tool-guides.mjs';

export const principlesRoute = 'learn/principles';

const sources = [
  ...onboardingGuides,
  workbenchProject,
  ...workflows.map((guide) => ({ ...guide, page: `workflows/${guide.slug}` })),
  { ...modelGuide, page: modelGuide.route },
  ...topicGuides,
  ...toolGuides,
  ...[...grids, ...clips].map((clip) => ({ ...clip, page: `labs/${clip.id}`, sections: ['implementation'] })),
];
const guideByPage = new Map(sources.map((guide) => [guide.page, guide]));
export const principleGuideCount = guideByPage.size;

const lab = (route, en, ko) => ({ route, en, ko });

const tracks = [
  {
    id: 'setup', icon: 'terminal', theme: 'lime',
    en: { title: 'Set up your environment', description: 'Check the GPU and driver first, then learn how to open a stage in the GUI and run a capture from the terminal.' },
    ko: { title: '환경 설정', description: 'GPU와 드라이버를 확인한 뒤 GUI에서 장면을 열고 터미널에서 캡처를 실행하는 흐름을 익힙니다.' },
    read: ['onboarding/nvidia-linux', 'onboarding/isaac-sim-tools'],
    practice: [
      lab('workflows/isaac-sim-first-cube#open-the-scene', 'Open and play a USD scene', 'USD 장면을 열고 재생하기'),
    ],
  },
  {
    id: 'simulation',
    en: { description: 'Start with a stage and a falling cube. Then compare contact, solver behavior, and GPU particle simulation.' },
    ko: { description: '장면을 열고 큐브를 떨어뜨리는 원리부터 읽으세요. 접촉, 물리 엔진의 계산 결과, GPU 입자 시뮬레이션으로 이어집니다.' },
    read: [
      'tools/isaac-sim', 'workflows/isaac-sim-first-cube', 'tools/nvidia-physx', 'tools/simready',
      'labs/physics', 'tools/newton', 'labs/newton-materials', 'tools/nvidia-warp', 'labs/warp-particles',
    ],
    practice: [
      lab('workflows/isaac-sim-first-cube#open-the-scene', 'Drop a cube with and without a collider', '충돌체를 켜고 끄며 큐브 떨어뜨리기'),
      lab('labs/physics#run', 'Compare colliders, friction, and bounce', '충돌체·마찰·반발 비교하기'),
      lab('labs/newton-materials#run', 'Simulate cloth and cables in Newton', 'Newton으로 천과 케이블 계산하기'),
    ],
  },
  {
    id: 'synthetic-data',
    en: { description: 'Build and capture a CAD scene first. Follow with RGB-D reconstruction, then explore advanced capture or reconstruction from photos.' },
    ko: { description: 'CAD를 장면으로 바꿔 촬영하는 흐름부터 읽으세요. 깊이로 점군을 만들고, 심화 촬영이나 사진 기반 복원으로 확장합니다.' },
    read: [
      'tools/openusd', 'workflows/workbench-cad-to-isaac-sim', 'tools/replicator', 'labs/workbench-capstone',
      'labs/scene-to-data', 'labs/replicator-outputs', 'tools/fvdb-reality-capture',
    ],
    practice: [
      lab(workbenchRecordingRoute, 'Check the saved workbench data without a GPU', 'GPU 없이 저장된 작업대 데이터 검사하기'),
      lab('labs/workbench-capstone#build-cad', 'Build a workbench scene and capture new frames', '작업대 장면을 만들어 새 프레임 촬영하기'),
    ],
  },
  {
    id: 'robotics',
    en: { description: 'Read how environments and evaluation work, then follow a policy run, motion planning, demonstration capture, and locomotion training.' },
    ko: { description: '로봇 환경과 성공 판정부터 익힌 뒤 정책 실행, 경로 계획, 시연 수집·생성, 보행 학습 순으로 살펴봅니다.' },
    read: [
      'tools/isaac-lab', 'labs/everyday-robots', 'tools/isaac-lab-arena', 'models/selection', 'labs/gr00t-placement',
      'tools/curobo', 'labs/robot-motion', 'tools/isaac-capture', 'tools/video-to-data', 'tools/autodata', 'labs/microduck',
    ],
    practice: [
      lab(firstExerciseRoute, 'Score a GR00T trial in your browser', '브라우저에서 GR00T 집기·놓기 판정하기'),
      lab('labs/robot-motion#run', 'Replan around an obstacle', '장애물을 우회하는 로봇 팔 경로 계산하기'),
    ],
  },
  {
    id: 'autonomous-driving',
    en: { description: 'Reconstruct the scene and read the policy output first. Evaluate a closed-loop drive before exploring rewards and policy updates.' },
    ko: { description: '주행 장면 복원과 정책의 궤적 출력부터 읽으세요. 폐루프 주행을 평가한 뒤 보상 계산과 정책 갱신을 살펴봅니다.' },
    read: ['tools/nurec', 'tools/alpamayo', 'workflows/alpasim-closed-loop', 'tools/alpagym', 'tools/cosmos-rl'],
    practice: [
      lab('workflows/alpasim-closed-loop#requirements', 'Run the official AlpaSim example with a GPU and scene access', 'GPU와 장면 접근 권한을 준비해 AlpaSim 공식 예제 실행하기'),
    ],
  },
  {
    id: 'world-models',
    en: { description: 'Curate source video, see what world models generate or infer, then follow evidence from video search into a model request.' },
    ko: { description: '원본 영상 선별부터 월드 모델의 추론·생성을 살펴보고, 영상에서 찾은 근거가 모델 요청으로 어떻게 이어지는지 읽습니다.' },
    read: ['tools/cosmos-curator', 'tools/cosmos', 'labs/world-driving', 'tools/cosmos-data-factory', 'tools/metropolis-vss', 'tools/nemo-switchyard'],
    practice: [
      lab('labs/world-driving#run', 'Generate a video and inspect driving-model outputs', '영상을 생성하고 주행 모델의 출력 확인하기'),
      lab('tools/metropolis-vss#example', 'Follow the VSS walkthrough to find timestamped evidence', 'VSS 사용 순서를 따라 시간 정보가 있는 영상 근거 찾기'),
    ],
  },
];

const listedPages = tracks.flatMap(({ read }) => read);
if (new Set(listedPages).size !== listedPages.length ||
    listedPages.length !== principleGuideCount || listedPages.some((page) => !guideByPage.has(page))) {
  throw new Error('List every theory guide once in the reading tracks.');
}

export const readingTracks = tracks.map((track) => {
  const topic = topics.find(({ slug }) => slug === track.id);
  return {
    ...track,
    icon: track.icon ?? topic.icon,
    theme: track.theme ?? topic.theme,
    en: { title: topic?.en.title, ...track.en },
    ko: { title: topic?.ko.title, ...track.ko },
    read: track.read.map((page) => {
      const guide = guideByPage.get(page);
      return { ...guide, route: `${page}#${guide.sections[0]}` };
    }),
  };
});

const labByPage = new Map([
  [lab('labs/physics#run', 'Compare colliders, friction, and bounce', '충돌체·마찰·반발 비교하기'),
    'tools/nvidia-physx', 'tools/simready', 'labs/physics'],
  [lab('labs/newton-materials#run', 'Simulate cloth and cables in Newton', 'Newton으로 천과 케이블 계산하기'),
    'tools/newton', 'labs/newton-materials'],
  [lab('labs/warp-particles#run', 'Run the Warp particle experiment', 'Warp 입자 실험 실행하기'),
    'tools/nvidia-warp', 'labs/warp-particles'],
  [lab('workflows/workbench-cad-to-isaac-sim#convert-to-usd', 'Convert the CAD workbench to USD', '작업대 CAD를 USD로 변환하기'),
    'tools/openusd', 'workflows/workbench-cad-to-isaac-sim'],
  [lab('labs/scene-to-data#run', 'Reconstruct a point cloud from saved data', '저장된 데이터로 점군 복원하기'), 'labs/scene-to-data'],
  [lab('labs/replicator-outputs#run', 'Capture the 12-frame Replicator dataset', 'Replicator로 12프레임 촬영하기'), 'labs/replicator-outputs'],
  [lab('https://github.com/openvdb/fvdb-reality-capture/blob/7b3264827e782959f55a6536acb2db1d5e8b2ce1/docs/tutorials/radiance_field_and_mesh_reconstruction.md',
    'Official fVDB reconstruction tutorial', 'fVDB 공식 장면 복원 예제'), 'tools/fvdb-reality-capture'],
  [lab('labs/microduck#run', 'Train Microduck to walk', 'Microduck 보행 정책 학습하기'), 'tools/isaac-lab', 'labs/microduck'],
  [lab('labs/everyday-robots#run', 'Try the camera-controlled drawer', '카메라로 과자 서랍 제어하기'), 'labs/everyday-robots'],
  [lab('labs/robot-motion#run', 'Plan a path around an obstacle', '장애물을 우회하는 로봇 팔 경로 계산하기'), 'tools/curobo', 'labs/robot-motion'],
  [lab('labs/robot-motion#run', 'Generate demonstrations with AutoData', 'AutoData로 로봇 시연 생성하기'), 'tools/autodata'],
  [lab('https://nvidia.github.io/IsaacCapture/main/teleop/quick_start.html',
    'Official Isaac Capture teleoperation quickstart', 'Isaac Capture 공식 원격조작 실습'), 'tools/isaac-capture'],
  [lab('tools/video-to-data#example', 'Follow the Video-to-Data example', 'Video-to-Data 적용 예시 따라가기'), 'tools/video-to-data'],
  [lab('labs/world-driving#run', 'Run Alpamayo on your own synthetic camera views', '직접 만든 카메라 영상으로 Alpamayo 실행하기'), 'tools/alpamayo'],
  [lab('https://github.com/NVlabs/alpagym/blob/972d160eed0e23d388497851504a3a233fec5879/docs/ONBOARDING.md',
    'Official AlpaGym training walkthrough', 'AlpaGym 공식 학습 예제'), 'tools/alpagym', 'tools/cosmos-rl'],
  [lab('tools/cosmos-curator#example', 'Curate a manipulation video archive', '로봇 조작 영상 선별 예시 보기'), 'tools/cosmos-curator'],
  [lab('labs/world-driving#run', 'Generate a video and inspect model outputs', '영상을 생성하고 모델 출력 확인하기'), 'tools/cosmos', 'labs/world-driving'],
  [lab('tools/cosmos-data-factory#example', 'Follow a driving video augmentation recipe', '주행 영상 증강 예시 따라가기'), 'tools/cosmos-data-factory'],
  [lab('tools/nemo-switchyard#example', 'Trace how a video summary request is routed', '영상 요약 요청의 모델 연결 예시 보기'), 'tools/nemo-switchyard'],
].flatMap(([practice, ...pages]) => pages.map((page) => [page, practice])));

export function principleProgress(page) {
  const track = readingTracks.find(({ read }) => read.some((guide) => guide.page === page));
  if (!track) return;
  const index = track.read.findIndex((guide) => guide.page === page);
  return {
    track,
    position: index + 1,
    previous: track.read[index - 1],
    next: track.read[index + 1],
    practice: labByPage.get(page) ?? track.practice[0],
  };
}

export const principlesCopy = {
  en: {
    nav: 'How the tools work', title: 'How Physical AI tools work',
    intro: 'Read the diagrams and data examples in order for the field you want to learn, then follow the linked lab.',
    all: (count) => `All ${count} theory guides`,
    choose: 'Choose a field', count: (count) => `${count} guides`,
    practice: 'Try it next', home: 'Home',
  },
  ko: {
    nav: '동작 원리 가이드', title: '피지컬 AI 도구의 동작 원리',
    intro: '관심 분야를 골라 그림과 데이터 예시를 순서대로 읽고, 해당 실습으로 이어가세요.',
    all: (count) => `동작 원리 ${count}개 모두 보기`,
    choose: '분야 선택', count: (count) => `가이드 ${count}개`,
    practice: '이어서 할 실습', home: '홈',
  },
};
