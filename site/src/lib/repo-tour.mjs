export const tourCopy = {
  en: {
    title: 'Follow a workflow through the repo',
    description: 'Choose a goal and trace it through the datasets, catalog, guides, and result checks.',
    shortcut: 'See the repo in action',
    goals: 'Choose a goal',
    stages: ['Data and assets', 'Catalog', 'Hands-on guide', 'Result check'],
    play: 'Play walkthrough',
    pause: 'Pause',
    replay: 'Replay',
    next: 'Next step',
    reset: 'Back to start',
  },
  ko: {
    title: '이 레포로 어떻게 시작하나요?',
    description: '목표를 고르면 필요한 데이터와 도구를 찾아 실습하고, 결과를 확인하기까지의 흐름을 볼 수 있습니다.',
    shortcut: '레포 활용 흐름 보기',
    goals: '목표 고르기',
    stages: ['데이터·에셋', '카탈로그', '실습 가이드', '결과 확인'],
    play: '흐름 재생',
    pause: '일시 정지',
    replay: '다시 재생',
    next: '다음 단계',
    reset: '처음으로',
  },
};

export const tourPaths = [
  {
    id: 'workbench',
    theme: 'mint',
    icon: 'workbench',
    destinations: [
      ['catalog', { field: '3d-assets' }],
      ['catalog', { field: 'simulation', q: 'AIF Pipeline Samples' }],
      ['workflows/workbench-cad-to-isaac-sim'],
      ['workflows/workbench-cad-to-isaac-sim', '#compose-the-scene'],
    ],
    en: {
      goal: 'Build a scene',
      steps: [
        ['Workbench CAD', 'Start with a STEP file and the real tabletop dimensions.', 'Browse 3D assets'],
        ['AIF Pipeline Samples', 'Convert the STEP file to an OpenUSD asset.', 'Find AIF in the catalog'],
        ['OpenUSD → Isaac Sim', 'Bring in the workbench and add a collider to the tabletop.', 'Follow the CAD guide'],
        ['A cube rests on the table', 'Check the tabletop dimensions and watch the cube settle on it.', 'Run the collision check'],
      ],
    },
    ko: {
      goal: '시뮬레이션 장면',
      steps: [
        ['작업대 CAD', 'STEP 파일과 실제 상판 치수를 준비합니다.', '3D 에셋 목록'],
        ['AIF Pipeline Samples', 'STEP 파일을 OpenUSD 에셋으로 변환합니다.', '카탈로그에서 AIF 찾기'],
        ['OpenUSD → Isaac Sim', '작업대를 불러오고 상판에 충돌체를 추가합니다.', 'CAD 실습 따라 하기'],
        ['상판에 멈추는 큐브', '상판 치수가 맞는지, 큐브가 바닥으로 빠지지 않는지 확인합니다.', '충돌 확인 단계 보기'],
      ],
    },
  },
  {
    id: 'driving',
    theme: 'blue',
    icon: 'car',
    destinations: [
      ['catalog', { field: 'driving-data', q: 'NuRec' }],
      ['catalog', { q: 'NuRec' }],
      ['workflows/alpasim-closed-loop'],
      ['workflows/alpasim-closed-loop', '#inspect-the-results'],
    ],
    en: {
      goal: 'Evaluate driving',
      steps: [
        ['Driving data', 'Start with a sample scene from the NuRec driving dataset.', 'Find the driving dataset'],
        ['NuRec', 'Reconstruct the driving scene so it can be rendered from new viewpoints.', 'Find NuRec in the catalog'],
        ['AlpaSim', 'Run a baseline driving policy in the reconstructed scene.', 'Follow the AlpaSim guide'],
        ['Collision and off-road metrics', 'Review the driving video and metrics before comparing policies.', 'Find the recorded metrics'],
      ],
    },
    ko: {
      goal: '자율주행 정책 평가',
      steps: [
        ['주행 데이터', 'NuRec 주행 데이터셋에서 예제 장면을 고릅니다.', '주행 데이터셋 찾기'],
        ['NuRec', '새로운 카메라 시점에서도 렌더링할 수 있게 장면을 복원합니다.', '카탈로그에서 NuRec 찾기'],
        ['AlpaSim', '복원한 장면에서 기준 주행 정책을 실행합니다.', 'AlpaSim 실습 따라 하기'],
        ['충돌·도로 이탈 지표', '주행 영상과 평가 지표를 함께 살펴봅니다.', '평가 결과 파일 찾기'],
      ],
    },
  },
  {
    id: 'robotics',
    theme: 'lime',
    icon: 'cube',
    destinations: [
      ['catalog', { field: 'robot-data' }],
      ['catalog', { field: 'models', q: 'GR00T' }],
      ['models/selection'],
      ['models/selection', '#evaluate-actions'],
    ],
    en: {
      goal: 'Test a robot policy',
      steps: [
        ['Robot demonstrations', 'Check what the recorded cameras, observations, and actions contain.', 'Browse demonstration datasets'],
        ['GR00T checkpoint', 'Check whether the checkpoint supports your robot or benchmark.', 'Compare GR00T checkpoints'],
        ['Robot model guide', 'Use the official example to check input and action formats before running the policy.', 'Follow the model guide'],
        ['A baseline run', 'Record the success criteria and initial conditions to compare later runs.', 'Open the evaluation checklist'],
      ],
    },
    ko: {
      goal: '로봇 정책 테스트',
      steps: [
        ['로봇 시연 데이터', '카메라 영상, 관측값, 로봇의 행동이 어떻게 기록됐는지 확인합니다.', '시연 데이터셋 보기'],
        ['GR00T 체크포인트', '사용할 로봇이나 벤치마크를 지원하는 체크포인트를 고릅니다.', 'GR00T 체크포인트 비교'],
        ['로봇 모델 가이드', '공식 예제에서 입력과 행동 형식을 확인한 뒤 정책을 실행합니다.', '모델 가이드 따라 하기'],
        ['비교 기준이 될 실행 기록', '다음 평가와 비교할 수 있도록 성공 기준과 초기 조건을 기록합니다.', '평가 체크리스트 보기'],
      ],
    },
  },
];
