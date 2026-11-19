import { pageUrl } from './catalog.mjs';

export const firstExerciseRoute = 'labs/gr00t-placement#first-exercise';
export const workbenchRoute = 'labs/workbench-capstone';
export const workbenchRecordingRoute = `${workbenchRoute}#check-recording`;

export const onboardingGuides = [
  {
    page: 'onboarding/nvidia-linux',
    sections: ['machine-and-driver', 'install-layers', 'ssh', 'container', 'troubleshooting'],
    en: {
      title: 'Set up an NVIDIA Linux machine',
      description: 'Check the driver and CUDA layers, then connect over SSH or test a GPU container.',
    },
    ko: {
      title: 'NVIDIA Linux 머신 준비하기',
      description: 'GPU·드라이버·CUDA를 확인하고, SSH로 접속하거나 컨테이너에 GPU를 연결합니다.',
    },
  },
  {
    page: 'onboarding/isaac-sim-tools',
    sections: ['install', 'gui', 'cli', 'tool-selection'],
    en: {
      title: 'Get started with Isaac Sim',
      description: 'Install the simulator, open a USD scene, and learn when to switch from the GUI to the CLI.',
    },
    ko: {
      title: 'Isaac Sim 설치와 첫 실행',
      description: '시뮬레이터를 설치하고 USD 장면을 열어 본 뒤, GUI와 CLI로 이어서 실습합니다.',
    },
  },
];

export const workbenchProject = {
  page: workbenchRoute,
  sections: ['implementation', 'check-recording', 'build-cad', 'capture', 'verify'],
  en: {
    title: 'Build and verify a workbench camera dataset',
    description: 'Turn CAD into an Isaac Sim scene, capture RGB, depth and masks, then check the result on a CPU.',
  },
  ko: {
    title: 'CAD 작업대부터 카메라 데이터셋까지',
    description: '작업대를 Isaac Sim 장면으로 만들어 Replicator로 촬영하고, CPU에서 결과를 검사합니다.',
  },
};

export const courses = [
  {
    slug: 'simulation-data',
    icon: 'workbench',
    theme: 'lime',
    en: {
      title: 'From CAD to camera data',
      description: 'Build a workbench scene and generate aligned RGB, depth, and segmentation data.',
      setup: 'Browser first, then Python. Use an RTX GPU and Isaac Sim 6.2 for new captures.',
      result: 'A USD scene, a reconstructed point cloud, and verified camera data.',
    },
    ko: {
      title: 'CAD에서 카메라 데이터까지',
      description: '작업대 장면을 만들고 같은 시점에서 RGB·깊이·분할 데이터를 생성합니다.',
      setup: '브라우저에서 시작해 Python으로 검사합니다. 새 촬영에는 RTX GPU와 Isaac Sim 6.2가 필요합니다.',
      result: 'USD 작업대, 복원한 점군, 검사를 마친 카메라 데이터',
    },
    lessons: [
      {
        route: firstExerciseRoute,
        mode: 'browser',
        en: ['Decide whether a robot run succeeded', 'Read a few recorded trials and practice checking a result before you run any code.'],
        ko: ['브라우저에서 로봇의 성공 여부 판정하기', '코드를 실행하기 전에 기록을 보고 실험 결과를 판정하는 법을 익힙니다.'],
      },
      {
        route: workbenchRecordingRoute,
        mode: 'cpu',
        en: ['Check saved camera data without a GPU', 'Open the bundled RGB, depth, and masks and calculate how far the cube moved.'],
        ko: ['GPU 없이 작업대 데이터 검사하기', '동봉한 사진·깊이·마스크를 읽고 큐브가 얼마나 이동했는지 계산합니다.'],
      },
      {
        route: `${workbenchRoute}#build-cad`,
        mode: 'gpu',
        en: ['Generate your own data in Isaac Sim 6.2', 'Build the workbench from STEP, capture four new frames, and run the same checker on your files.'],
        ko: ['Isaac Sim 6.2에서 새 데이터 만들기', 'STEP으로 작업대를 만들고 네 프레임을 촬영한 뒤, 같은 검사 코드로 내 결과를 확인합니다.'],
      },
    ],
    advanced: {
      route: 'labs/replicator-outputs',
      en: ['Capture 12 frames with a separate Replicator scene', 'Uses Isaac Sim 6.1 and Isaac Lab, with its own USD and checker. Compare masks as the camera, light, and occlusion change.'],
      ko: ['별도 장면으로 Replicator 12프레임 촬영하기', 'Isaac Sim 6.1과 Isaac Lab에서 별도 USD와 검사 코드를 사용합니다. 카메라·조명·가림에 따라 마스크가 어떻게 달라지는지 봅니다.'],
    },
  },
  {
    slug: 'robot-policies',
    icon: 'cube',
    theme: 'mint',
    en: {
      title: 'Robot policies and motion',
      description: 'Score a GR00T run, check an obstacle-aware path, and train a walking policy.',
      setup: 'A browser to start. The GPU labs list their own Isaac Sim or Isaac Lab setup.',
      result: 'Episode outcomes, planned paths, and a training checkpoint.',
    },
    ko: {
      title: '로봇 정책과 동작',
      description: 'GR00T의 집기 결과를 판정하고, 장애물을 우회하는 경로와 보행 정책을 만들어 봅니다.',
      setup: '브라우저로 시작. GPU 실습별로 Isaac Sim 또는 Isaac Lab 환경이 필요합니다.',
      result: '회차별 판정 로그, 장애물 우회 경로, 보행 정책 체크포인트',
    },
    lessons: [
      {
        route: firstExerciseRoute,
        mode: 'browser',
        en: ['Tell a lift from a placement', 'Read the Arena event log and check which trials complete the full task.'],
        ko: ['들기와 놓기 구분하기', 'Arena 이벤트 기록을 읽고 어디까지 성공했는지 직접 판정합니다.'],
      },
      {
        route: 'labs/gr00t-placement#run',
        mode: 'gpu',
        en: ['Run GR00T in Isaac Lab-Arena', 'Run the pick-and-place task and check your own episode JSONL.'],
        ko: ['Isaac Lab-Arena에서 GR00T 실행하기', '집기·놓기 과제를 실행하고 새로 생긴 JSONL을 검사합니다.'],
      },
      {
        route: 'labs/robot-motion',
        mode: 'gpu',
        en: ['Replan around an obstacle', 'Use cuRobo to compare two paths to the same target with and without a barrier.'],
        ko: ['장애물이 생겼을 때 경로 다시 계산하기', '같은 목표에 장애물을 추가하기 전후의 cuRobo 경로를 비교합니다.'],
      },
      {
        route: 'labs/microduck',
        mode: 'gpu',
        en: ['Train Microduck to walk', 'Train with Isaac Lab and Newton, then inspect the learning curve and replay the checkpoint.'],
        ko: ['Microduck 보행 정책 학습하기', 'Isaac Lab과 Newton으로 학습하고, 보상 추이를 확인한 뒤 체크포인트를 재생합니다.'],
      },
    ],
  },
  {
    slug: 'driving-evaluation',
    icon: 'car',
    theme: 'blue',
    en: {
      title: 'Ego cameras to driving evaluation',
      description: 'Start with real CARLA camera recordings, inspect Alpamayo outputs, then follow AlpaSim policy evaluation.',
      setup: 'View saved videos without a GPU. CARLA requires Linux, NVIDIA GPU and Docker; AlpaSim needs separate NuRec scene access.',
      result: 'Camera frames and trajectories first; policy rollout metrics in the AlpaSim extension.',
      scope: 'CARLA recordings and Alpamayo inference are provided. The AlpaSim steps remain an official-example guide.',
    },
    ko: {
      title: '운전자 카메라부터 주행 평가까지',
      description: '실제 CARLA 카메라 촬영부터 시작해 Alpamayo의 출력을 읽고 AlpaSim 정책 평가로 확장합니다.',
      setup: '저장된 영상은 GPU 없이 확인. CARLA는 Linux·NVIDIA GPU·Docker, AlpaSim은 별도 NuRec 장면 접근 권한 필요.',
      result: '카메라 프레임·경로를 확인한 뒤 AlpaSim의 주행 평가 지표로 확장',
      scope: 'CARLA 촬영과 Alpamayo 추론 결과를 제공합니다. AlpaSim 단계는 공식 예제를 대조한 가이드입니다.',
    },
    lessons: [
      {
        route: 'labs/carla-ego#implementation', mode: 'gpu',
        en: ['See through the ego camera', 'Watch four recorded CARLA environments, then follow setup and record your own sensors.'],
        ko: ['운전자 시점에서 보기', '네 CARLA 환경의 촬영을 보고 설치 순서를 따라 내 센서 영상을 만듭니다.'],
      },
      {
        route: 'labs/world-driving#implementation', mode: 'gpu',
        en: ['Read a learned model’s output', 'Inspect six-camera inputs and Alpamayo’s future poses; distinguish inference from a driving rollout.'],
        ko: ['학습 모델의 출력 읽기', '여섯 카메라 입력과 Alpamayo의 미래 자세를 보고 추론과 실제 주행을 구분합니다.'],
      },
      {
        route: 'workflows/alpasim-closed-loop#requirements',
        mode: 'guide',
        en: ['Prepare a NuRec scene', 'Check access, the example scene ID, and the pinned AlpaSim revision.'],
        ko: ['NuRec 예제 장면 준비하기', '데이터 접근 권한, 예제 장면 ID, 가이드가 지정한 AlpaSim 버전을 확인합니다.'],
      },
      {
        route: 'workflows/alpasim-closed-loop#run-the-scene',
        mode: 'guide',
        en: ['Run one baseline rollout', 'Follow the official setup and launch the baseline on a single scene.'],
        ko: ['기준 정책으로 한 장면 주행하기', '공식 예제 환경을 구성하고 기준 정책으로 장면 하나를 실행합니다.'],
      },
      {
        route: 'workflows/alpasim-closed-loop#inspect-the-results',
        mode: 'guide',
        en: ['Inspect the result and set up a comparison', 'Find the metrics and hold the scene and renderer fixed before changing the policy.'],
        ko: ['주행 결과 확인하고 비교 조건 정하기', '평가 지표를 확인하고 정책을 바꾸기 전에 장면과 렌더러를 고정합니다.'],
      },
    ],
  },
];

export const learningCopy = {
  en: {
    audience: 'Free hands-on learning for developers',
    firstExercise: 'Try a lab in your browser',
    paths: 'Learning paths',
    setup: 'Setup',
    result: 'What you’ll produce',
    openPath: 'View path',
    lessons: 'Lessons',
    advanced: 'Optional advanced lab',
    code: 'Lab code',
    galleryTitle: 'See what the tools do',
    galleryLink: 'Browse the video labs',
    modes: { browser: 'Browser', cpu: 'Python · no GPU', gpu: 'GPU lab', guide: 'Guided example' },
  },
  ko: {
    audience: '개발자를 위한 무료 실습',
    firstExercise: '설치 없이 첫 실습 해보기',
    paths: '학습 경로',
    setup: '준비 환경',
    result: '결과물',
    openPath: '학습 경로 보기',
    lessons: '실습 순서',
    advanced: '별도 심화 실습',
    code: '실습 코드',
    galleryTitle: '실습 결과를 영상으로',
    galleryLink: '영상과 실습 보기',
    modes: { browser: '브라우저', cpu: 'Python · GPU 없이', gpu: 'GPU 실습', guide: '가이드' },
  },
};

export const courseRoute = (slug) => `learn/${slug}`;

export function lessonUrl(locale, route) {
  const [path, fragment] = route.split('#');
  return pageUrl(locale, path) + (fragment ? `#${fragment}` : '');
}
