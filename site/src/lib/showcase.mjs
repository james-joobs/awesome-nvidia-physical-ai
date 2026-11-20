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
    intro: 'Explore robot policies, physics, 3D Gaussian worlds, generated indoor scenes and ego-camera driving. Our GPU workstation runs use NVIDIA GPU tools, CARLA and Blender; each recording links to code and checks.',
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
    intro: '로봇 정책·물리부터 3DGS 공간·실내 장면 생성·운전자 시점 주행까지 살펴보세요. GPU 머신에서 NVIDIA GPU 도구와 CARLA·Blender를 직접 실행했으며, 영상마다 코드와 검사 방법을 연결했습니다.',
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
    id: 'worldgen-scenes', duration: '0:20', width: 960, height: 540,
    en: { title: 'Generate and explore a world from text or an image', description: 'WorldGen creates a robotics lab, a forest trail and an expanded living room. Watch translated 3D camera views, then load the generated scene in your browser.' },
    ko: { title: '글과 이미지로 만든 3D 공간 둘러보기', description: 'WorldGen으로 로봇 실험실·숲길·확장된 거실을 생성했습니다. 3D 공간에서 카메라를 움직인 영상을 보고, 브라우저에서도 직접 둘러보세요.' },
  },
  {
    id: 'worldgen-dynamic-navigation', duration: '0:36', width: 960, height: 540,
    media: { ko: 'worldgen-dynamic-navigation-ko' },
    en: { title: 'When an obstacle moves, the map must change too', description: 'A gate closes during driving and reopens. The old permanent map still blocks the robot; fresh range observations let the new controller wait, clear the map and continue. Actual Isaac Sim GUI recordings at 1×.' },
    ko: { title: '움직이는 장애물에 멈추고 다시 출발하기', description: '주행 중 차단벽이 닫혔다 열립니다. 이전 지도에는 관측이 남아 막히지만, 새 제어는 거리 관측으로 지도를 갱신하고 다시 출발합니다. 실제 Isaac Sim GUI를 1배속으로 녹화했습니다.' },
  },
  {
    id: 'worldgen-navigation', duration: '0:26', width: 960, height: 540,
    media: { ko: 'worldgen-navigation-ko' },
    en: { title: 'Fixed waypoints or a route from sensor scans?', description: 'A new box blocks the old route. An actual Physics Raycast Sensor feeds an occupancy grid and A* planner, and the same robot chooses the other side. Native Isaac Sim GUI footage at 1× speed.' },
    ko: { title: '정해 둔 경유점과 센서로 찾은 경로 비교', description: '추가 상자가 기존 경로를 막습니다. 실제 물리 거리 센서의 측정값으로 점유 격자와 A* 경로를 만들자, 같은 로봇이 반대편으로 우회합니다. Isaac Sim GUI를 1배속으로 녹화했습니다.' },
  },
  {
    id: 'worldgen-isaac', duration: '0:25', width: 960, height: 540,
    en: { title: 'Drive inside the generated WorldGen laboratory', description: 'A generated laboratory becomes an Isaac Sim 6.2 scene. Watch an articulated AMR meet a crate, reverse and follow waypoints around it. The recovery is scripted; contacts and motion are live PhysX.' },
    ko: { title: 'WorldGen 실험실에서 로봇 움직이기', description: '생성한 실험실에서 이동 로봇이 상자에 막힌 뒤 후진해 우회합니다. 회복 순서는 미리 정했고, 접촉과 움직임은 Isaac Sim 6.2의 PhysX가 실제 계산합니다.' },
  },
  {
    id: 'spatial-reconstruction', duration: '0:16', width: 640, height: 360,
    en: { title: 'Explore a plaza reconstructed with 3DGS', description: 'CARLA camera views become an fVDB radiance field. Move the viewpoint in the browser, or watch the full model rendered along a new camera path.' },
    ko: { title: '3DGS로 복원한 광장 둘러보기', description: 'CARLA 촬영을 fVDB로 복원했습니다. 브라우저에서 직접 시점을 움직이거나 전체 모델의 카메라 이동 영상을 볼 수 있습니다.' },
  },
  {
    id: 'carla-ego', duration: '0:16', width: 1280, height: 720,
    en: { title: 'Four environments from the driver’s seat', description: 'Actual CARLA ego cameras: clear city, heavy rain, wet sunset, and fog. Traffic Manager is a rule-based driver; these are sensor captures, not AI policy results.' },
    ko: { title: '운전자 시점으로 보는 네 도로 환경', description: 'CARLA에서 도심·폭우·젖은 주택가·안개를 직접 촬영했습니다. 규칙 기반 Traffic Manager의 주행이며 AI 정책 성능을 평가한 영상은 아닙니다.' },
  },
  {
    id: 'scene-generation', duration: '0:06', width: 640, height: 360,
    en: { title: 'Walk through a procedurally generated house', description: 'Infinigen generates a furnished house and plans a camera tour. Blender Cycles renders the geometry; this is procedural generation, not neural world-model inference.' },
    ko: { title: '새로 생성한 집 안 둘러보기', description: 'Infinigen이 방·가구를 생성하고 카메라 경로를 정합니다. Blender Cycles로 렌더링한 절차적 생성 예제이며 신경망 월드 모델은 아닙니다.' },
  },
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
    id: 'worldgen-dynamic-navigation-gate', lab: 'worldgen-dynamic-navigation', duration: '0:23', width: 960, height: 540,
    en: { title: 'Stop for a closing gate, then continue', description: 'A moving physical collider blocks the passage. The robot waits with zero wheel commands and resumes from new observations when a path opens.' },
    ko: { title: '닫히는 차단벽 앞에서 기다렸다 다시 출발', description: '움직이는 실제 충돌체가 통로를 막습니다. 바퀴 명령을 0으로 두고 대기하다가 새 관측으로 통과할 경로를 찾으면 다시 움직입니다.' },
  },
  {
    id: 'worldgen-dynamic-navigation-cart', lab: 'worldgen-dynamic-navigation', duration: '0:28', width: 960, height: 540,
    en: { title: 'A moving box enters the first detour', description: 'The initial sensor-generated route goes below the static crate. A box enters this passage, the robot brakes, and a later plan takes it around the other side.' },
    ko: { title: '주행하던 우회로에 상자가 들어오면', description: '처음 센서로 계산한 경로는 고정 상자 아래쪽을 향합니다. 그 통로에 다른 상자가 들어오자 제동하고, 이후 계산한 경로로 반대편을 돌아 도착합니다.' },
  },
  {
    id: 'worldgen-dynamic-navigation-static', lab: 'worldgen-dynamic-navigation', duration: '0:19', width: 960, height: 540,
    en: { title: 'Previous controller: the physical gate opens, but map memory remains', description: 'The same range sensor and moving gate, using the unchanged previous permanent-map Navigator. The robot stops and still has no route after the gate withdraws.' },
    ko: { title: '이전 방식: 벽이 물러나도 지도에는 관측이 남습니다', description: '같은 거리 센서와 움직이는 차단벽에 이전 제어기를 그대로 사용했습니다. 차단벽이 빠져나간 뒤에도 통과할 경로를 찾지 못해 정지해 있습니다.' },
  },

  {
    id: 'worldgen-navigation-lower', lab: 'worldgen-navigation', duration: '0:16', width: 960, height: 540,
    en: { title: 'Lower passage blocked: the robot chooses the upper side', description: 'The controller receives only ranges, ego pose and a goal. The cyan line is recomputed online; it is not a supplied waypoint list.' },
    ko: { title: '아래쪽 통로가 막히면 위쪽으로', description: '제어기에는 거리·현재 위치·목적지만 전달합니다. 청록색 경로는 실행 중 다시 계산하며, 미리 입력한 경유점 목록이 아닙니다.' },
  },
  {
    id: 'worldgen-navigation-upper', lab: 'worldgen-navigation', duration: '0:16', width: 960, height: 540,
    en: { title: 'Upper passage blocked: the choice changes', description: 'Move the added box to the opposite side without changing the planner. The measured route changes with the scan.' },
    ko: { title: '위쪽을 막으면 선택이 바뀝니다', description: '계획기는 그대로 두고 추가 상자만 반대편으로 옮겼습니다. 센서 관측에 따라 실제 이동 경로가 달라집니다.' },
  },
  {
    id: 'worldgen-navigation-center', lab: 'worldgen-navigation', duration: '0:16', width: 960, height: 540,
    en: { title: 'One box, no supplied detour', description: 'The original central obstacle is detected from range hits. The planner builds its first route from an empty obstacle map.' },
    ko: { title: '상자 하나부터 경유점 없이', description: '원래의 중앙 상자를 거리 측정으로 감지합니다. 비어 있는 장애물 지도에서 첫 우회 경로를 계산합니다.' },
  },
  {
    id: 'worldgen-navigation-fixed', lab: 'worldgen-navigation', duration: '0:21', width: 960, height: 540,
    en: { title: 'The fixed-route baseline in the changed layout', description: 'The previous waypoint list is unchanged and ignores range data. Live contacts stop the robot at the added box; the goal is not reached.' },
    ko: { title: '바뀐 배치에서 기존 경유점을 그대로 실행', description: '앞선 경유점 목록을 수정하지 않고 거리 데이터도 제어에 쓰지 않습니다. 추가 상자에 실제로 막혀 목적지에 도착하지 못합니다.' },
  },

  {
    id: 'worldgen-isaac-blocked', lab: 'worldgen-isaac', duration: '0:11', width: 960, height: 540,
    tags: ['Isaac Sim 6.2', 'PhysX', 'WorldGen'],
    en: { title: 'A forward command does not pass through a collider', description: 'The same physical robot receives equal wheel-speed targets and stops against the crate. Contact events and measured poses are saved.' },
    ko: { title: '전진 명령을 줘도 충돌체는 통과하지 않습니다', description: '같은 로봇의 두 바퀴에 같은 속도를 줍니다. 상자 앞에서 멈추는 실제 접촉과 몸체 위치를 기록했습니다.' },
  },
  {
    id: 'worldgen-isaac-detour', lab: 'worldgen-isaac', duration: '0:21', width: 960, height: 540,
    tags: ['Isaac Sim 6.2', 'PhysX', 'Waypoint feedback'],
    en: { title: 'A closer view of waypoint control', description: 'An independent run follows the detour directly. The camera is closer and the generated-room emission is lower than in the main overview. No crate contact was reported.' },
    ko: { title: '경유점 제어를 가까이서 보기', description: '우회 경로를 바로 따라가는 별도 실행입니다. 대표 영상보다 가까운 시점이며 배경 발광값도 낮습니다. 상자 접촉은 보고되지 않았습니다.' },
  },
  {
    id: 'worldgen-isaac-probes', lab: 'worldgen-isaac', duration: '0:03', width: 960, height: 540,
    tags: ['Isaac Sim 6.2', 'PhysX', 'Collision check'],
    en: { title: 'Check contact before you drive', description: 'Four 10 cm cubes drop onto the explicit floor. Compare their saved heights with the no-collider and generated-mesh tests in the lab.' },
    ko: { title: '주행 전에 바닥 접촉 확인하기', description: '10cm 큐브 네 개를 바닥 충돌체에 떨어뜨립니다. 실습 기록에서 충돌체가 없는 경우와 추정 메시를 쓴 경우의 높이도 비교합니다.' },
  },
  ...[
    ['livingroom', 'Expand one image into a 360° living room', '이미지 한 장에서 360° 거실로 확장하기'],
    ['forest-trail', 'Generate a forest trail from text', '글로 생성한 숲길 둘러보기'],
  ].map(([id, en, ko]) => ({
    id: `worldgen-${id}`, lab: 'worldgen-scenes', duration: '0:20', width: 960, height: 540,
    tags: ['WorldGen', 'FLUX.1', 'DA-2', 'fVDB renderer'],
    en: { title: en, description: 'Actual GPU workstation model inference, followed by a translated camera path rendered from the Gaussian PLY. Distance is inferred and not metric ground truth.' },
    ko: { title: ko, description: 'GPU 머신에서 모델을 직접 실행한 뒤 Gaussian PLY에서 카메라를 움직여 렌더링했습니다. 깊이는 추정값이며 실제 거리의 정답은 아닙니다.' },
  })),
  ...[
    ['city-clear', 'Clear city', '맑은 도심'],
    ['junction-rain', 'Heavy-rain junction', '폭우가 내리는 교차로'],
    ['suburb-sunset', 'Wet suburb at sunset', '해 질 무렵의 젖은 주택가'],
    ['highway-fog', 'Foggy highway', '안개 낀 고속도로'],
  ].map(([id, en, ko]) => ({
    id: `carla-${id}`, lab: 'carla-ego', duration: '0:16', width: 768, height: 432,
    tags: ['CARLA 0.9.16', 'Ego RGB', 'Traffic Manager'],
    en: { title: en, description: 'Original-speed, on-board RGB sensor capture in CARLA. Open the lab for setup, camera placement, and per-frame records.' },
    ko: { title: ko, description: 'CARLA 차량에 단 RGB 센서를 원래 속도로 재생합니다. 실습에서 설치·카메라 위치·프레임별 기록을 확인할 수 있습니다.' },
  })),
  ...[
    ['city', 'City from one image', '사진 한 장에서 복원한 도심'],
    ['suburb', 'Suburb from one image', '사진 한 장에서 복원한 주택가'],
  ].map(([id, en, ko]) => ({
    id: `sharp-${id}`, lab: 'spatial-reconstruction', duration: '0:08', width: 640, height: 360,
    tags: ['Apple SHARP', 'fVDB renderer', 'Single-view reconstruction'],
    en: { title: en, description: 'SHARP predicts 3D Gaussians from our CARLA image. fVDB renders nearby views. Research-only model weights; no complete 360° scene.' },
    ko: { title: ko, description: 'CARLA 사진을 SHARP에 넣고 fVDB로 주변 시점을 렌더링했습니다. 연구용 가중치를 사용한 단일 시점 복원이며 완전한 360° 공간은 아닙니다.' },
  })),
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
