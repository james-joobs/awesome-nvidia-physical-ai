import { pageUrl } from './catalog.mjs';

export function showcaseMedia(file) {
  return `${pageUrl('en')}showcase/${file}`;
}

export const showcaseCopy = {
  en: {
    nav: 'Videos',
    homeAlt: 'Sixteen scenes recorded in Isaac Sim, with GR00T putting a cube in a bowl in the first tile',
    homeAction: 'Watch 16 Isaac Sim scenes',
    title: 'Physical AI in motion',
    intro: 'Explore robot policy trials, motion planning, deformable materials, generated video, and driving-model outputs on one RTX 5090. Each recording links to code and checks.',
    overview: '16 scenes',
    featured: '16 scenes from the Isaac Sim GUI',
    featuredDetail: 'Watch the top-left tile for the successful GR00T placement. The next tile shows the earlier attempt that lost the cube.',
    scenes: 'All 16 scenes in screen order',
    grids: 'Compare by topic',
    clips: 'Watch one result',
    play: 'Play',
    open: 'Open MP4',
    guide: 'Read the guide',
    source: 'Scene and tool credits',
    editNote: 'Silent footage. Some shots are sped up or slowed down. Replay, motion planning, and live simulation are labeled below.',
  },
  ko: {
    nav: '영상',
    homeAlt: 'Isaac Sim에서 녹화한 16개 장면. 첫 칸에서 GR00T가 큐브를 그릇에 놓습니다.',
    homeAction: 'Isaac Sim 16개 장면 보기',
    title: '영상으로 보는 피지컬 AI',
    intro: 'RTX 5090 한 대에서 로봇 정책, 경로 계획, 천과 케이블, 영상 생성과 주행 모델을 실행했습니다. 영상마다 코드와 결과 검사 방법을 함께 볼 수 있습니다.',
    overview: '16개 장면',
    featured: 'Isaac Sim GUI로 찍은 16개 장면',
    featuredDetail: '첫 칸에서 GR00T가 큐브를 그릇에 놓습니다. 바로 옆에서는 앞선 시도의 그리퍼가 큐브를 놓칩니다.',
    scenes: '화면 순서대로 16개 장면 보기',
    grids: '주제별로 비교하기',
    clips: '실험 하나씩 보기',
    play: '재생',
    open: 'MP4 열기',
    guide: '가이드 보기',
    source: '씬과 도구 출처',
    editNote: '소리 없이 재생됩니다. 일부 장면은 배속을 조정했습니다. 기록 재생, 경로 계획, 실시간 시뮬레이션을 아래에 표시했습니다.',
  },
};

export const featured = { id: 'isaac-sim-grid', duration: '0:09', width: 1200, height: 676 };

export const grids = [
  {
    id: 'robot-motion', duration: '0:09', width: 768, height: 432, route: 'models/selection',
    en: { title: 'Robot motion', description: 'GR00T places the cube, cuRobo plans around an obstacle, AutoData replays generated demonstrations, and a trained Microduck policy walks in Newton.' },
    ko: { title: '로봇은 어떻게 움직일까', description: 'GR00T 집기 성공, cuRobo 장애물 우회 경로, AutoData 시연 재생, Newton에서 Microduck 보행 정책을 비교합니다.' },
  },
  {
    id: 'physics', duration: '0:09', width: 768, height: 432, route: 'workflows/isaac-sim-first-cube',
    en: { title: 'Physics you can see', description: 'Colliders change where objects stop. Friction changes how far they slide, and restitution changes how high they bounce.' },
    ko: { title: '눈으로 확인하는 물리', description: '충돌체를 바꾸면 물체가 멈추는 높이가 달라집니다. 마찰은 미끄러지는 거리, 반발계수는 튀어 오르는 높이를 바꿉니다.' },
  },
  {
    id: 'scene-to-data', duration: '0:09', width: 768, height: 432, route: 'workflows/workbench-cad-to-isaac-sim',
    en: { title: 'From a scene to sensor data', description: 'Open a CAD workbench, vary the camera scene in Replicator, and inspect RGB, depth, labels, and a reconstructed point cloud.' },
    ko: { title: '작업대에서 센서 데이터까지', description: 'CAD 작업대를 열고 Replicator에서 카메라 장면을 바꿉니다. RGB·깊이·라벨과 복원한 점군을 확인할 수 있습니다.' },
  },
  {
    id: 'everyday-robots', duration: '0:09', width: 768, height: 432, route: 'workflows/workbench-cad-to-isaac-sim',
    en: { title: 'Experiments around a desk', description: 'An alarm rolls away, a snack drawer responds to a card, a cleanup rule puts a mouse in the bin, and a cart tests aisle widths.' },
    ko: { title: '책상 주변에서 해 본 실험', description: '도망가는 알람, 카드를 인식하는 과자 서랍, 마우스까지 치우는 정리 규칙, 통로 폭을 비교하는 카트를 담았습니다.' },
  },
];

export const clips = [
  {
    id: 'world-driving', duration: '0:14', width: 960, height: 540, guide: 'cosmos',
    en: { title: 'World generation and driving-model outputs', description: 'A real Cosmos camera-conditioned generation, then an Alpamayo prediction replay in Isaac Sim. Separate model experiments on our own scenes.' },
    ko: { title: '월드 모델 생성과 주행 모델의 출력', description: 'Cosmos의 카메라 조건 영상 생성에 이어 Alpamayo 예측 경로를 Isaac Sim에서 재생합니다. 직접 만든 장면으로 각각 실행한 모델 실험입니다.' },
  },
  {
    id: 'newton-materials', duration: '0:24', width: 960, height: 540, guide: 'newton',
    en: { title: 'Cloth and cables in Newton', description: 'Newton computes XPBD cloth, VBD cloth, and twisting cables. Isaac Sim displays the saved solver states.' },
    ko: { title: 'Newton으로 천과 케이블 움직여 보기', description: 'XPBD·VBD 천과 케이블 비틀림을 Newton에서 계산하고, 저장된 상태를 Isaac Sim에서 재생합니다.' },
  },
  {
    id: 'gr00t-placement', duration: '0:21', width: 768, height: 432, guide: 'groot-model',
    en: { title: 'GR00T puts the cube in the bowl', description: 'Watch the gripper hold, carry, open, and leave the cube resting in the bowl.' },
    ko: { title: 'GR00T가 큐브를 그릇에 놓기까지', description: '그리퍼가 큐브를 들고 옮긴 뒤 그릇 위에서 열리는 동작을 볼 수 있습니다.' },
  },
  {
    id: 'replicator-outputs', duration: '0:07', width: 768, height: 198, guide: 'replicator',
    en: { title: 'Three outputs from one camera', description: 'Inspect RGB, camera-plane depth, and semantic masks from 12 captured frames.' },
    ko: { title: '카메라 한 대에서 나온 세 가지 데이터', description: '12프레임의 RGB, 카메라 평면 기준 깊이, 의미 분할 마스크를 비교합니다.' },
  },
  {
    id: 'microduck', duration: '0:11', width: 768, height: 432, guide: 'microduck',
    en: { title: 'Microduck walks in Newton', description: 'A walking policy trained in Isaac Lab drives the simulated robot.' },
    ko: { title: 'Newton에서 걷는 Microduck', description: 'Isaac Lab에서 학습한 보행 정책으로 가상 로봇을 움직입니다.' },
  },
  {
    id: 'warp-particles', duration: '0:17', width: 768, height: 432, guide: 'nvidia-warp',
    en: { title: 'Particles collide in Warp', description: 'Warp computes 65,536 interacting particles on the GPU. The viewer draws one in four.' },
    ko: { title: 'Warp로 입자 충돌 계산하기', description: 'GPU에서 입자 65,536개의 상호작용을 계산하고, 영상에는 네 개 중 하나를 표시합니다.' },
  },
];

// Extra runs share an existing lab and its reading order.
export const additionalRecordings = [
  {
    id: 'four-domain-grid', lab: 'world-driving', route: 'topics', labRoute: 'topics', duration: '0:20', width: 1280, height: 720,
    tags: ['cuRobo', 'Newton', 'Cosmos3-Edge', 'Alpamayo2-Edge', 'Isaac Sim'],
    en: { title: 'Four fields on one GPU', description: 'Clockwise from the top left: cuRobo paths, Newton solver replay, Alpamayo trajectory replay, and Cosmos generated RGB. Short takes loop; the Newton tile changes examples.' },
    ko: { title: 'GPU 한 대에서 네 분야 실험하기', description: '왼쪽 위부터 시계 방향으로 cuRobo 경로, Newton 계산 재생, Alpamayo 예측 경로 재생, Cosmos 생성 영상입니다. 짧은 영상은 반복하고 Newton은 예제가 바뀝니다.' },
  },
  {
    id: 'gr00t-transfer-check', lab: 'gr00t-placement', duration: '0:20', width: 960, height: 540, guide: 'groot-model',
    en: { title: 'A lift is not yet a placement', description: 'November 19 live GR00T run, shown at 2× speed. Both new trials lifted the cube but neither placed it in the bowl.' },
    ko: { title: '들었다고 그릇에 놓은 것은 아닙니다', description: '11월 19일 GR00T 정책 실행을 2배속으로 담았습니다. 새 시도 두 번 모두 큐브를 들었지만 그릇 배치에는 실패했습니다.' },
  },
  {
    id: 'curobo-replan', lab: 'robot-motion', duration: '0:11', width: 960, height: 540, guide: 'curobo',
    en: { title: 'Same goal, a new obstacle', description: 'November 19 GPU replan. Isaac Sim replays the calculated arm collision geometry; sampled sphere clearance is about 2.17 mm.' },
    ko: { title: '같은 목적지, 새로 생긴 장애물', description: '11월 19일 GPU에서 다시 계산한 경로입니다. 팔의 충돌 형상을 Isaac Sim에서 재생하며, 저장된 구체의 최소 간격은 약 2.17mm입니다.' },
  },
];

export const sceneLabels = {
  en: [
    'GR00T places the cube · live policy', 'GR00T loses the cube · live policy',
    'cuRobo avoids a barrier · planned paths', 'AutoData stacks cubes · demonstration replay',
    'SimReady collider comparison · live PhysX', 'Collider shifted 12 cm · live PhysX',
    'Three friction settings · live PhysX', 'Three bounce heights · live PhysX',
    'Cube drop on a CAD workbench · live PhysX', 'Replicator camera and lighting changes · live capture',
    'Reconstructed RGB-D point cloud · replay', 'PhysX and Newton · solver replay',
    'Three aisle widths · planned routes', 'Runaway alarm · PhysX trajectory replay',
    'Snack drawer · replay', 'Two cleanup rules · PhysX trajectory replay',
  ],
  ko: [
    'GR00T 큐브 놓기 성공 · 정책 실행', 'GR00T 집기 실패 · 정책 실행',
    'cuRobo 장애물 우회 · 경로 계획', 'AutoData 큐브 쌓기 · 시연 재생',
    'SimReady 충돌체 비교 · PhysX 실행', '12cm 어긋난 충돌체 · PhysX 실행',
    '마찰계수 세 가지 · PhysX 실행', '반발계수 세 가지 · PhysX 실행',
    'CAD 작업대 위 큐브 낙하 · PhysX 실행', 'Replicator 시점과 조명 변경 · 데이터 생성',
    'RGB-D 점군 복원 · 기록 재생', 'PhysX와 Newton · 계산 결과 재생',
    '세 가지 통로 폭 · 경로 계획', '도망가는 알람 · PhysX 기록 재생',
    '과자 서랍 · 기록 재생', '책상 정리 규칙 두 가지 · PhysX 기록 재생',
  ],
};
