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
    intro: 'Watch Physical AI demos, then open the code and lab to try them yourself.',
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
    editNote: 'Scene order and tools are listed below.',
  },
  ko: {
    nav: '영상',
    homeAlt: 'Isaac Sim에서 녹화한 16개 장면. 첫 칸에서 GR00T가 큐브를 그릇에 놓습니다.',
    homeAction: 'Isaac Sim 16개 장면 보기',
    title: '영상으로 보는 피지컬 AI',
    intro: '피지컬 AI 데모를 살펴보고, 연결된 코드와 실습으로 직접 따라 해 보세요.',
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
    editNote: '각 장면의 순서와 사용 도구를 아래에서 확인할 수 있습니다.',
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
    id: 'human-4d-gaussian', duration: '0:32', width: 720, height: 960,
    media: { en: 'human-4d-dance/orbit', ko: 'human-4d-dance/orbit' },
    en: { title: 'Human 4D reconstruction: motion, views and Gaussian rendering', description: 'Explore a dance as a rigged 3D avatar, compare 3DGS and 4DGS, and orbit the motion in your browser.' },
    ko: { title: '인체 4D 재구성: 동작·시점·Gaussian 렌더링', description: '춤 동작을 3D 아바타로 복원하고, 3DGS·4DGS 결과를 비교하며 여러 방향에서 살펴봅니다.' },
  },
  {
    id: 'nurec-rgb-reality', duration: '0:30', width: 1920, height: 1080,
    media: { en: 'nurec-adaptive-live.en', ko: 'nurec-adaptive-live.ko' },
    en: { title: 'Responsive Reality View: preview while moving, refine at rest', description: 'Reconstruct a road from RGB with DA3, Aether and NuRec, then explore depth, camera views and Alpamayo paths.' },
    ko: { title: 'Reality View: 이동 중 미리보기, 정지 후 고화질', description: 'DA3·Aether·NuRec으로 RGB 도로를 복원하고 깊이·카메라 시점·Alpamayo 경로를 살펴봅니다.' },
  },
  {
    id: 'rgb-reality-view', duration: '0:25', width: 1280, height: 720,
    media: { en: 'rgb-perception.en', ko: 'rgb-perception.ko' },
    en: { title: 'Standalone 3DGUT comparison: RGB reconstruction and perception', description: 'Turn real camera images into a 3DGUT scene and inspect cars, people and their estimated 3D positions.' },
    ko: { title: '독립 실행형 3DGUT 비교: RGB 복원·객체 인식', description: '실사 카메라 사진을 3DGUT 장면으로 복원하고 차량·사람의 인식 결과와 3D 위치를 확인합니다.' },
  },
  {
    id: 'pandaset-nurec', duration: '0:15', width: 1024, height: 576,
    media: { en: 'pandaset-nurec.en', ko: 'pandaset-nurec.ko' },
    en: { title: 'RGB + LiDAR reference: NuRec and Harmonizer', description: 'Reconstruct a PandaSet road with RGB and LiDAR, then compare NuRec views and Harmonizer enhancement.' },
    ko: { title: 'RGB + LiDAR 비교 실험: NuRec·Harmonizer', description: 'PandaSet의 RGB·LiDAR로 도로를 복원하고 NuRec 시점과 Harmonizer 보정 결과를 비교합니다.' },
  },
  {
    id: 'reality-view', duration: '0:20', width: 1280, height: 720,
    media: { en: 'reality-view.en', ko: 'reality-view.ko' },
    en: { title: 'Synthetic road test: neural views and a predicted route', description: 'Connect NuRec reconstruction, Harmonizer enhancement and an Alpamayo route on a synthetic road.' },
    ko: { title: '합성 도로로 확인하는 NuRec·Alpamayo 연결', description: '합성 도로에서 NuRec 복원·Harmonizer 보정·Alpamayo 예측 경로를 연결합니다.' },
  },
  {
    id: 'worldgen-scenes', duration: '0:20', width: 960, height: 540,
    en: { title: 'Generate and explore a world from text or an image', description: 'Generate a robotics lab, living room and forest trail, then explore them in 3D.' },
    ko: { title: '글과 이미지로 만든 3D 공간 둘러보기', description: '로봇 실험실·거실·숲길을 생성하고 3D 공간을 직접 둘러봅니다.' },
  },
  {
    id: 'worldgen-dynamic-navigation', duration: '0:36', width: 960, height: 540,
    media: { ko: 'worldgen-dynamic-navigation-ko' },
    en: { title: 'When an obstacle moves, the map must change too', description: 'A moving gate blocks the robot; range sensing updates the map so it can stop and continue.' },
    ko: { title: '움직이는 장애물에 멈추고 다시 출발하기', description: '움직이는 차단벽을 센서로 감지하고, 지도를 갱신해 멈췄다가 다시 출발합니다.' },
  },
  {
    id: 'worldgen-navigation', duration: '0:26', width: 960, height: 540,
    media: { ko: 'worldgen-navigation-ko' },
    en: { title: 'Fixed waypoints or a route from sensor scans?', description: 'Compare fixed waypoints with sensor-guided obstacle avoidance in a generated laboratory.' },
    ko: { title: '정해 둔 경유점과 센서로 찾은 경로 비교', description: '생성한 실험실에서 정해 둔 경유점과 센서 기반 장애물 우회를 비교합니다.' },
  },
  {
    id: 'worldgen-isaac', duration: '0:25', width: 960, height: 540,
    en: { title: 'Drive inside the generated WorldGen laboratory', description: 'Bring a generated laboratory into Isaac Sim and move a robot through scripted recovery and waypoint control.' },
    ko: { title: 'WorldGen 실험실에서 로봇 움직이기', description: '생성한 실험실을 Isaac Sim에 가져와 로봇의 경유점 주행과 정해 둔 장애물 회복 동작을 실행합니다.' },
  },
  {
    id: 'spatial-reconstruction', duration: '0:16', width: 640, height: 360,
    en: { title: 'Explore a plaza reconstructed with 3DGS', description: 'CARLA camera views become an fVDB radiance field. Move the viewpoint in the browser, or watch the full model rendered along a new camera path.' },
    ko: { title: '3DGS로 복원한 광장 둘러보기', description: 'CARLA 촬영을 fVDB로 복원했습니다. 브라우저에서 직접 시점을 움직이거나 전체 모델의 카메라 이동 영상을 볼 수 있습니다.' },
  },
  {
    id: 'carla-ego', duration: '0:16', width: 1280, height: 720,
    en: { title: 'Four environments from the driver’s seat', description: 'Explore city streets, rain, sunset and fog through CARLA ego cameras driven by Traffic Manager.' },
    ko: { title: '운전자 시점으로 보는 네 도로 환경', description: 'Traffic Manager로 주행하며 CARLA의 도심·비·노을·안개를 운전자 카메라로 살펴봅니다.' },
  },
  {
    id: 'scene-generation', duration: '0:06', width: 640, height: 360,
    en: { title: 'Walk through a procedurally generated house', description: 'Generate a furnished house with Infinigen and render a camera tour in Blender.' },
    ko: { title: '새로 생성한 집 안 둘러보기', description: 'Infinigen으로 가구가 있는 집을 생성하고 Blender로 실내를 둘러봅니다.' },
  },
  {
    id: 'world-driving', duration: '0:14', width: 960, height: 540, guide: 'cosmos',
    en: { title: 'World generation and driving-model outputs', description: 'Watch Cosmos generate camera-controlled video and Alpamayo paths play back in Isaac Sim.' },
    ko: { title: '월드 모델 생성과 주행 모델의 출력', description: 'Cosmos의 카메라 조건 영상 생성과 Isaac Sim에서 재생하는 Alpamayo 경로를 살펴봅니다.' },
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
export const labMediaFiles = {
  'labs/nurec-rgb-reality/evidence/unified/interaction.en.mp4': 'reality-joint.en.mp4',
  'labs/nurec-rgb-reality/evidence/unified/interaction.ko.mp4': 'reality-joint.ko.mp4',
  'labs/nurec-rgb-reality/evidence/unified/generation.en.mp4': 'reality-aether-generation.en.mp4',
  'labs/nurec-rgb-reality/evidence/unified/generation.ko.mp4': 'reality-aether-generation.ko.mp4',
  'site/public/showcase/human-4d-dance/orbit.mp4': 'human-4d-dance/orbit.mp4',
  'site/public/showcase/human-4d-dance/rigged-3dgs.mp4': 'human-4d-dance/rigged-3dgs.mp4',
  'labs/nurec-rgb-reality/evidence/adaptive/interaction.en.mp4': 'nurec-adaptive-live.en.mp4',
  'labs/nurec-rgb-reality/evidence/adaptive/interaction.ko.mp4': 'nurec-adaptive-live.ko.mp4',
  'labs/nurec-rgb-reality/evidence/adaptive/browser.en.mp4': 'nurec-browser-preview.en.mp4',
  'labs/nurec-rgb-reality/evidence/adaptive/browser.ko.mp4': 'nurec-browser-preview.ko.mp4',
  'labs/nurec-rgb-reality/evidence/adaptive/quality.en.mp4': 'nurec-adaptive-quality.en.mp4',
  'labs/nurec-rgb-reality/evidence/adaptive/quality.ko.mp4': 'nurec-adaptive-quality.ko.mp4',
  'labs/nurec-rgb-reality/evidence/speed/interaction.en.mp4': 'nurec-speed-live.en.mp4',
  'labs/nurec-rgb-reality/evidence/speed/interaction.ko.mp4': 'nurec-speed-live.ko.mp4',
  'labs/nurec-rgb-reality/evidence/speed/quality.en.mp4': 'nurec-speed-quality.en.mp4',
  'labs/nurec-rgb-reality/evidence/speed/quality.ko.mp4': 'nurec-speed-quality.ko.mp4',
  'labs/nurec-rgb-reality/evidence/temporal/comparison.en.mp4': 'nurec-temporal.en.mp4',
  'labs/nurec-rgb-reality/evidence/temporal/comparison.ko.mp4': 'nurec-temporal.ko.mp4',
  'labs/nurec-rgb-reality/evidence/temporal/interaction.en.mp4': 'nurec-temporal-live.en.mp4',
  'labs/nurec-rgb-reality/evidence/temporal/interaction.ko.mp4': 'nurec-temporal-live.ko.mp4',
  'labs/nurec-rgb-reality/evidence/guidance/native-comparison.en.mp4': 'nurec-guidance.en.mp4',
  'labs/nurec-rgb-reality/evidence/guidance/native-comparison.ko.mp4': 'nurec-guidance.ko.mp4',
  'labs/nurec-rgb-reality/evidence/guidance/interaction.en.mp4': 'nurec-guided-interaction.en.mp4',
  'labs/nurec-rgb-reality/evidence/guidance/interaction.ko.mp4': 'nurec-guided-interaction.ko.mp4',
  'labs/nurec-rgb-reality/evidence/nurec-overview.en.mp4': 'nurec-overview.en.mp4',
  'labs/nurec-rgb-reality/evidence/nurec-overview.ko.mp4': 'nurec-overview.ko.mp4',
  'labs/nurec-rgb-reality/evidence/nurec-rgb-reality.en.mp4': 'nurec-rgb-reality.en.mp4',
  'labs/nurec-rgb-reality/evidence/nurec-rgb-reality.ko.mp4': 'nurec-rgb-reality.ko.mp4',
  'labs/nurec-rgb-reality/evidence/nurec-harmonizer.en.mp4': 'nurec-harmonizer.en.mp4',
  'labs/nurec-rgb-reality/evidence/nurec-harmonizer.ko.mp4': 'nurec-harmonizer.ko.mp4',
  'labs/rgb-reality-view/evidence/rgb-perception.en.mp4': 'rgb-perception.en.mp4',
  'labs/rgb-reality-view/evidence/rgb-perception.ko.mp4': 'rgb-perception.ko.mp4',
  'labs/rgb-reality-view/evidence/rgb-reality-view.en.mp4': 'rgb-reality-view.en.mp4',
  'labs/rgb-reality-view/evidence/rgb-reality-view.ko.mp4': 'rgb-reality-view.ko.mp4',
  'labs/pandaset-nurec/evidence/pandaset-nurec.en.mp4': 'pandaset-nurec.en.mp4',
  'labs/pandaset-nurec/evidence/pandaset-nurec.ko.mp4': 'pandaset-nurec.ko.mp4',
  'labs/pandaset-nurec/evidence/comparison.en.mp4': 'pandaset-comparison.en.mp4',
  'labs/pandaset-nurec/evidence/comparison.ko.mp4': 'pandaset-comparison.ko.mp4',
  'labs/pandaset-nurec/evidence/volvo-quarter.mp4': 'pandaset-volvo-quarter.mp4',
  'labs/pandaset-nurec/evidence/nurec-quarter.mp4': 'pandaset-nurec-quarter.mp4',
  'labs/reality-view/evidence/reality-view.en.mp4': 'reality-view.en.mp4',
  'labs/reality-view/evidence/reality-view.ko.mp4': 'reality-view.ko.mp4',
  'labs/reality-view/evidence/nurec-novel.mp4': 'reality-view-nurec.mp4',
  'labs/reality-view/evidence/harmonizer-novel.mp4': 'reality-view-harmonizer.mp4',
  'labs/reality-view/evidence/alpamayo-overlay.mp4': 'reality-view-alpamayo.mp4',
};

export const additionalRecordings = [
  {
    id: 'reality-joint-geometry', lab: 'nurec-rgb-reality', duration: '0:21', width: 1440, height: 1080,
    media: { en: 'reality-joint.en', ko: 'reality-joint.ko' },
    en: { title: 'RGB, depth and cameras: actual 3D comparison', description: 'Switch DA3, Aether and NuRec views, scrub time, and locate an RGB pixel in 3D.' },
    ko: { title: 'RGB·깊이·카메라: 실제 3D 조작 비교', description: 'DA3·Aether·NuRec 시점을 바꾸고 시간을 움직이며 RGB 픽셀의 3D 위치를 확인합니다.' },
  },
  {
    id: 'reality-aether-generation', lab: 'nurec-rgb-reality', duration: '0:05', width: 1440, height: 550,
    media: { en: 'reality-aether-generation.en', ko: 'reality-aether-generation.ko' },
    en: { title: 'Observed RGB versus Aether-generated RGB', description: 'Compare observed RGB with Aether-generated frames from an image and a camera path.' },
    ko: { title: '관측 RGB와 Aether 생성 RGB 비교', description: '관측 RGB와 이미지·카메라 경로로 생성한 Aether 영상을 비교합니다.' },
  },
  {
    id: 'human-rigged-3dgs', lab: 'human-4d-gaussian', duration: '0:32', width: 1280, height: 680,
    media: { en: 'human-4d-dance/rigged-3dgs', ko: 'human-4d-dance/rigged-3dgs' },
    en: { title: 'Rigged 3DGS avatar: four views', description: 'View one rigged 3DGS avatar from the front, sides and back.' },
    ko: { title: '리깅한 3DGS 아바타를 네 방향에서 보기', description: '리깅한 3DGS 아바타의 정면·측면·후면을 한 번에 비교합니다.' },
  },
  {
    id: 'nurec-browser-preview', lab: 'nurec-rgb-reality', duration: '0:30', width: 1920, height: 1080,
    media: { en: 'nurec-browser-preview.en', ko: 'nurec-browser-preview.ko' },
    en: { title: 'Smooth browser 3D preview, then GPU refinement', description: 'Move through the browser preview, then inspect GPU refinement after the camera stops.' },
    ko: { title: '부드러운 브라우저 3D 미리보기, 멈추면 GPU 보정', description: '브라우저에서 시점을 움직이고 멈춘 뒤 GPU 보정 결과를 확인합니다.' },
  },
  {
    id: 'nurec-adaptive-quality', lab: 'nurec-rgb-reality', duration: '0:08', width: 1920, height: 1080,
    media: { en: 'nurec-adaptive-quality.en', ko: 'nurec-adaptive-quality.ko' },
    en: { title: 'Preview quality and stationary HQ: different references', description: 'Compare fast preview and refined output at the same camera position.' },
    ko: { title: '미리보기 화질과 정지 후 고화질: 다른 기준으로 비교하기', description: '같은 카메라 위치에서 빠른 미리보기와 보정된 화면을 비교합니다.' },
  },
  {
    id: 'nurec-exact-speed', lab: 'nurec-rgb-reality', duration: '0:30', width: 1920, height: 1080,
    media: { en: 'nurec-speed-live.en', ko: 'nurec-speed-live.ko' },
    en: { title: 'Exact-pixel optimization', description: 'Compare the original decoder with exact-pixel optimization.' },
    ko: { title: '같은 픽셀로 줄인 디코딩 계산', description: '기존 디코더와 픽셀을 유지하는 최적화를 비교합니다.' },
  },
  {
    id: 'nurec-speed-quality', lab: 'nurec-rgb-reality', duration: '0:08', width: 1920, height: 1080,
    media: { en: 'nurec-speed-quality.en', ko: 'nurec-speed-quality.ko' },
    en: { title: 'Same raw pixels, less decoding: matched quality crops', description: 'Inspect matching image regions before and after decoding optimization.' },
    ko: { title: '같은 RGB 픽셀로 줄인 계산: 화질 확대 비교', description: '디코딩 최적화 전후의 같은 이미지 영역을 확대해 살펴봅니다.' },
  },
  {
    id: 'nurec-temporal-initial', lab: 'nurec-rgb-reality', duration: '0:27', width: 1280, height: 888,
    media: { en: 'nurec-temporal-live.en', ko: 'nurec-temporal-live.ko' },
    en: { title: 'Mouse-controlled temporal enhancement', description: 'Explore the first mouse-controlled Harmonizer demo.' },
    ko: { title: '보존한 첫 시간축 GPU 뷰어', description: '마우스로 시점을 바꾸는 Harmonizer 데모를 살펴봅니다.' },
  },
  {
    id: 'nurec-temporal', lab: 'nurec-rgb-reality', duration: '0:24', width: 1280, height: 640,
    media: { en: 'nurec-temporal.en', ko: 'nurec-temporal.ko' },
    en: { title: 'Matched native / independent / temporal comparison', description: 'Compare native NuRec renders with frame-by-frame and temporal Harmonizer enhancement.' },
    ko: { title: '같은 시점의 원본·프레임별·시간축 보정 비교', description: 'NuRec 원본과 프레임별·시간축 Harmonizer 보정을 비교합니다.' },
  },
  {
    id: 'nurec-overview', lab: 'nurec-rgb-reality', duration: '0:35', width: 1280, height: 720,
    media: { en: 'nurec-overview.en', ko: 'nurec-overview.ko' },
    en: { title: 'Reconstruction, recognition and prediction', description: 'Explore the NuRec road with RGB recognition and Alpamayo paths.' },
    ko: { title: '복원·인식·예측 연결', description: 'NuRec 도로에서 RGB 객체 인식과 Alpamayo 경로를 살펴봅니다.' },
  },
  {
    id: 'human-4d-control-render', lab: 'human-4d-gaussian', duration: '0:39', width: 1280, height: 816,
    media: { en: 'human-4d-control/comparison', ko: 'human-4d-control/comparison' },
    en: { title: 'Full SOMA control: fixed RGB and Gaussian orbit', description: 'Compare SOMA synthetic mesh motion with a rigged Gaussian rendering.' },
    ko: { title: 'SOMA 전체 동작: 고정 RGB와 Gaussian 회전 영상', description: 'SOMA 합성 메시 동작과 리깅한 Gaussian 렌더링을 비교합니다.' },
  },
  {
    id: 'nurec-guided-interaction', lab: 'nurec-rgb-reality', duration: '0:14', width: 1280, height: 720,
    media: { en: 'nurec-guided-interaction.en', ko: 'nurec-guided-interaction.ko' },
    en: { title: 'Explore the depth-guided scene', description: 'Switch reconstruction models, orbit the road and replay the path.' },
    ko: { title: '깊이 기반 장면 직접 조작하기', description: '복원 모델을 바꾸고 도로를 회전하며 경로를 재생합니다.' },
  },
  {
    id: 'nurec-guidance', lab: 'nurec-rgb-reality', duration: '0:16', width: 1280, height: 720,
    media: { en: 'nurec-guidance.en', ko: 'nurec-guidance.ko' },
    en: { title: 'Depth-guided reconstruction: original and production model', description: 'Inspect original and depth-guided NuRec renders at matching camera views.' },
    ko: { title: '깊이 기반 복원: 기존 모델과 고해상도 모델 비교', description: '같은 카메라에서 기존 NuRec과 깊이 기반 복원을 비교합니다.' },
  },
  {
    id: 'nurec-interactive', lab: 'nurec-rgb-reality', duration: '0:27', width: 1280, height: 720,
    media: { en: 'nurec-rgb-reality.en', ko: 'nurec-rgb-reality.ko' },
    en: { title: 'Actual mouse interaction with the NuRec-trained preview', description: 'Source-RGB detections, 3D contacts and actual Alpamayo predictions. Toggle the overlays, change cameras and rotate the same Gaussian scene.' },
    ko: { title: 'NuRec 학습 장면을 실제 마우스로 조작한 영상', description: '원본 RGB 인식, 3D 접점과 Alpamayo 실제 예측을 확인합니다. 표시를 껐다 켜고 카메라를 바꾸며 같은 Gaussian 장면을 회전합니다.' },
  },
  {
    id: 'nurec-harmonizer', lab: 'nurec-rgb-reality', duration: '0:08', width: 1280, height: 720,
    media: { en: 'nurec-harmonizer.en', ko: 'nurec-harmonizer.ko' },
    en: { title: 'Native NuRec renders and Harmonizer at the same 48 poses', description: 'Compare a NuRec render with its Harmonizer-enhanced view.' },
    ko: { title: '같은 시점 48곳의 NuRec 원본·Harmonizer 보정 비교', description: 'NuRec 원본과 Harmonizer 보정 화면을 나란히 비교합니다.' },
  },
  {
    id: 'rgb-reality-view-orbit', lab: 'rgb-reality-view', duration: '0:27', width: 1280, height: 720,
    media: { en: 'rgb-reality-view.en', ko: 'rgb-reality-view.ko' },
    en: { title: 'Original RGB reconstruction: mouse orbit and driver view', description: 'The same 400k-Gaussian scene before adding object perception. Actual mouse rotation, pan, zoom and camera-path replay.' },
    ko: { title: '인식 표시를 추가하기 전의 RGB 복원 영상', description: '같은 Gaussian 40만 개 장면에서 실제 마우스로 회전·이동·확대하고 카메라 경로를 재생한 원래 영상입니다.' },
  },
  {
    id: 'reality-view-nurec', lab: 'reality-view', duration: '0:08', width: 1280, height: 720,
    tags: ['NuRec 26.04', 'gsplat'],
    en: { title: 'NuRec novel-camera sweep', description: 'Forty held-out camera poses, 1 m higher than capture. This is the neural render before enhancement.' },
    ko: { title: 'NuRec 새 시점만 보기', description: '촬영할 때보다 1m 높은 카메라 40곳의 결과입니다. 보정을 적용하기 전의 신경 렌더링입니다.' },
  },
  {
    id: 'reality-view-harmonizer', lab: 'reality-view', duration: '0:08', width: 1280, height: 720,
    tags: ['Harmonizer', 'NVIDIA Cosmos', 'Non-temporal'],
    en: { title: 'Harmonizer on the same camera sweep', description: 'The released non-temporal checkpoint processes each frame independently. Built on NVIDIA Cosmos.' },
    ko: { title: '같은 시점에 Harmonizer 적용', description: '공개된 non-temporal 체크포인트로 한 장씩 처리했습니다. Built on NVIDIA Cosmos.' },
  },
  {
    id: 'reality-view-alpamayo', lab: 'reality-view', duration: '0:08', width: 1280, height: 720,
    tags: ['Alpamayo 2 Edge', 'Predicted trajectory'],
    en: { title: 'The actual 64-pose prediction', description: 'One Alpamayo output projected onto the display camera and BEV. No controls or new decisions are applied.' },
    ko: { title: '실제로 출력한 미래 자세 64개', description: 'Alpamayo의 단일 예측을 카메라와 BEV에 표시했습니다. 제어 명령이나 추가 추론을 적용하지 않았습니다.' },
  },
  {
    id: 'worldgen-dynamic-navigation-gate', lab: 'worldgen-dynamic-navigation', duration: '0:23', width: 960, height: 540,
    en: { title: 'Stop for a closing gate, then continue', description: 'A moving physical collider blocks the passage. The robot waits with zero wheel commands and resumes from new observations when a path opens.' },
    ko: { title: '닫히는 차단벽 앞에서 기다렸다 다시 출발', description: '움직이는 실제 충돌체가 통로를 막습니다. 바퀴 명령을 0으로 두고 대기하다가 새 관측으로 통과할 경로를 찾으면 다시 움직입니다.' },
  },
  {
    id: 'worldgen-dynamic-navigation-cart', lab: 'worldgen-dynamic-navigation', duration: '0:28', width: 960, height: 540,
    en: { title: 'A moving box enters the first detour', description: 'A box enters the route; the robot brakes and plans a detour.' },
    ko: { title: '주행하던 우회로에 상자가 들어오면', description: '주행 경로에 상자가 들어오면 로봇이 제동하고 우회합니다.' },
  },
  {
    id: 'worldgen-dynamic-navigation-static', lab: 'worldgen-dynamic-navigation', duration: '0:19', width: 960, height: 540,
    en: { title: 'Previous controller: the physical gate opens, but map memory remains', description: 'Compare how the previous controller reacts when the gate reopens.' },
    ko: { title: '이전 방식: 벽이 물러나도 지도에는 관측이 남습니다', description: '차단벽이 다시 열렸을 때 이전 제어기의 반응을 비교합니다.' },
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
    en: { title: 'A closer view of waypoint control', description: 'Follow a planned detour through the generated laboratory.' },
    ko: { title: '경유점 제어를 가까이서 보기', description: '생성한 실험실에서 정해 둔 우회 경로를 주행합니다.' },
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
    en: { title: en, description: 'Explore the generated scene along a moving 3D camera path.' },
    ko: { title: ko, description: '생성한 3D 장면에서 카메라를 움직이며 공간을 둘러봅니다.' },
  })),
  ...[
    ['city-clear', 'Clear city', '맑은 도심'],
    ['junction-rain', 'Heavy-rain junction', '폭우가 내리는 교차로'],
    ['suburb-sunset', 'Wet suburb at sunset', '해 질 무렵의 젖은 주택가'],
    ['highway-fog', 'Foggy highway', '안개 낀 고속도로'],
  ].map(([id, en, ko]) => ({
    id: `carla-${id}`, lab: 'carla-ego', duration: '0:16', width: 768, height: 432,
    tags: ['CARLA 0.9.16', 'Ego RGB', 'Traffic Manager'],
    en: { title: en, description: 'Drive through this environment with a CARLA ego RGB camera.' },
    ko: { title: ko, description: 'CARLA 차량의 RGB 카메라로 이 도로 환경을 둘러봅니다.' },
  })),
  ...[
    ['city', 'City from one image', '사진 한 장에서 복원한 도심'],
    ['suburb', 'Suburb from one image', '사진 한 장에서 복원한 주택가'],
  ].map(([id, en, ko]) => ({
    id: `sharp-${id}`, lab: 'spatial-reconstruction', duration: '0:08', width: 640, height: 360,
    tags: ['Apple SHARP', 'fVDB renderer', 'Single-view reconstruction'],
    en: { title: en, description: 'Reconstruct a CARLA image with SHARP and render nearby views with fVDB.' },
    ko: { title: ko, description: 'CARLA 사진 한 장을 SHARP로 복원하고 fVDB로 주변 시점을 렌더링합니다.' },
  })),
  {
    id: 'four-domain-grid', lab: 'world-driving', route: 'topics', labRoute: 'topics', duration: '0:20', width: 1280, height: 720,
    tags: ['cuRobo', 'Newton', 'Cosmos3-Edge', 'Alpamayo2-Edge', 'Isaac Sim'],
    en: { title: 'Four fields on one GPU', description: 'See cuRobo planning, Newton physics, Alpamayo paths and Cosmos video in one grid.' },
    ko: { title: 'GPU 한 대에서 네 분야 실험하기', description: 'cuRobo 경로 계획·Newton 물리·Alpamayo 경로·Cosmos 영상을 한눈에 비교합니다.' },
  },
  {
    id: 'gr00t-transfer-check', lab: 'gr00t-placement', duration: '0:20', width: 960, height: 540, guide: 'groot-model',
    en: { title: 'GR00T placement attempts', description: 'Compare two GR00T trials that lift the cube but miss the bowl.' },
    ko: { title: 'GR00T 배치 시도 비교', description: '큐브를 들었지만 그릇에 넣지 못한 GR00T 시도 두 개를 비교합니다.' },
  },
  {
    id: 'curobo-replan', lab: 'robot-motion', duration: '0:11', width: 960, height: 540, guide: 'curobo',
    en: { title: 'Same goal, a new obstacle', description: 'Add an obstacle and watch cuRobo plan a new arm trajectory in Isaac Sim.' },
    ko: { title: '같은 목적지, 새로 생긴 장애물', description: '장애물을 추가하고 cuRobo가 다시 계산한 팔의 경로를 Isaac Sim에서 확인합니다.' },
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
