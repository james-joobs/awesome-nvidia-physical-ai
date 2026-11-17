// Each step shows a data example or file name, followed by what it means in the lab.
export const lessonFlows = {
  'gr00t-placement': {
    en: [
      ['What the robot sees', 'camera image + joint positions + instruction', 'Arena sends an image, the arm’s current joint positions, and the instruction to put the cube in the bowl.'],
      ['What the policy decides', 'joint and gripper targets', 'GR00T uses that observation to choose where the joints and gripper should move.'],
      ['What the simulator records', 'episode_results_*.jsonl', 'Isaac Sim applies the targets. Arena writes one trial per line, with separate lift and placement events.'],
    ],
    ko: [
      ['로봇이 보는 것', '카메라 영상 + 관절 위치 + 지시문', 'Arena가 카메라 영상, 팔의 현재 관절 위치, 큐브를 그릇에 놓으라는 지시를 보냅니다.'],
      ['모델이 정하는 동작', '관절과 그리퍼의 목표 위치', 'GR00T가 입력을 보고 관절을 어디로 움직이고 그리퍼를 얼마나 열지 정합니다.'],
      ['시뮬레이터가 남기는 기록', 'episode_results_*.jsonl', 'Isaac Sim이 팔을 움직입니다. Arena는 시도마다 한 줄을 쓰고, 들기와 놓기를 따로 기록합니다.'],
    ],
    loop: { en: 'The robot moves, the cameras see the new scene, and the policy gets a new observation.', ko: '팔이 움직이면 카메라 영상과 관절 위치가 바뀝니다. 그 정보로 다음 동작을 정합니다.' },
  },
  'replicator-outputs': {
    en: [
      ['One scene and camera', 'replicator-live.usda · /World/SensorCamera', 'USD describes the cube, lights, and the camera used for capture.'],
      ['Read one render three ways', 'RGB · camera-plane depth · class ID', 'Each annotator reads the same pixel location for a different kind of information.'],
      ['One folder per frame', 'rgb.png · depth_m.npy · semantic_ids.npy', 'The PNG stores colors. The arrays store meters or class numbers. The JSON file gives those numbers names.'],
    ],
    ko: [
      ['장면과 카메라 한 대', 'replicator-live.usda · /World/SensorCamera', 'USD 파일에 큐브, 조명, 촬영할 카메라가 들어 있습니다.'],
      ['한 화면에서 세 가지 읽기', 'RGB · 카메라 기준 깊이 · 클래스 번호', '같은 픽셀에서 색, 카메라 평면으로부터의 거리, 어떤 물체인지 읽습니다.'],
      ['프레임별 결과 폴더', 'rgb.png · depth_m.npy · semantic_ids.npy', 'PNG는 색, 배열은 미터 단위 깊이와 클래스 번호를 담습니다. 번호의 뜻은 JSON에 적혀 있습니다.'],
    ],
  },
  'scene-to-data': {
    en: [
      ['Camera data', 'USD camera + depth.npy + semantic mask', 'The mask tells us which pixels belong to the cube. The USD camera gives us the lens and position.'],
      ['Place the pixels in 3D', 'pixel (u, v) + depth → point (x, y, z)', 'Use the lens, depth, and camera position to place each visible cube pixel in the scene.'],
      ['Compare the cube’s movement', 'surface-00.npy · result.json', 'Compare the median of the visible points with frame 0 to estimate movement.'],
    ],
    ko: [
      ['카메라 정보와 센서 데이터', 'USD 카메라 + 깊이 배열 + 분할 마스크', '마스크는 큐브에 해당하는 픽셀을, USD는 렌즈와 카메라 위치를 알려줍니다.'],
      ['픽셀을 3D 점으로 바꾸기', '픽셀 (u, v) + 깊이 → 좌표 (x, y, z)', '카메라 위치와 깊이를 이용해 큐브가 보이는 픽셀을 장면 속 좌표로 옮깁니다.'],
      ['큐브가 얼마나 움직였나', 'surface-00.npy · result.json', '보이는 점들의 중앙값을 첫 프레임과 비교해 상대 이동량을 구합니다.'],
    ],
  },
  physics: {
    en: [
      ['Scene and collision shapes', '.usda · rigid body · collider · material', 'The rigid body can move. The collider tells the physics engine where surfaces touch.'],
      ['Step the simulation', 'gravity → contact → next pose', 'Gravity pulls the object down. Friction and bounce settings affect what happens at contact.'],
      ['Watch and measure', 'viewport · capture.json · pose arrays', 'Look for where the object stops or how far it slides. Code can compare the saved positions.'],
    ],
    ko: [
      ['움직일 물체와 닿을 면', '.usda · 강체 · 충돌체 · 물리 재질', '강체는 움직일 물체입니다. 충돌체는 엔진이 물체끼리 닿는 면을 찾는 데 씁니다.'],
      ['물리 엔진으로 한 단계 계산', '중력 → 접촉 → 다음 위치', '중력이 물체를 아래로 당깁니다. 닿았을 때 얼마나 미끄러지고 튀는지는 마찰과 반발 값에 달려 있습니다.'],
      ['화면과 위치 기록 확인', '뷰포트 · capture.json · 위치 배열', '어디에 멈추고 얼마나 미끄러졌는지 화면에서 보고 파일에 남은 좌표로 비교합니다.'],
    ],
  },
  'robot-motion': {
    en: [
      ['Start, goal, and obstacle', 'arm joints + target pose + obstacle box', 'Keep the start and goal fixed. Add a box to the world for the second plan.'],
      ['Find a path for the arm', 'cuRobo → joint waypoints', 'The planner checks the arm’s collision shapes and searches for a path to the goal.'],
      ['Compare two paths', 'motion.npz · result.json', 'Compare waypoint arrays and check whether the tool center enters the new obstacle.'],
    ],
    ko: [
      ['출발 자세, 목적지, 장애물', '관절 위치 + 목표 자세 + 장애물 상자', '출발과 목적지는 그대로 둡니다. 두 번째 계획에서만 경로 앞에 상자를 넣습니다.'],
      ['팔이 갈 경로 계산', 'cuRobo → 관절 위치의 순서', 'cuRobo가 팔의 충돌 형상을 보며 목표 자세까지 갈 경로를 찾습니다.'],
      ['두 경로를 비교', 'motion.npz · result.json', '경로를 이루는 중간 지점과 팔 끝이 새 장애물 안을 지났는지 확인합니다.'],
    ],
  },
  microduck: {
    en: [
      ['Tell the robot how to walk', 'target speed + observed robot state', 'Each simulated robot gets a requested velocity and information about its current motion.'],
      ['Act and learn from rewards', 'policy → joint targets → Newton → reward', 'Newton moves the robot. RSL-RL updates the policy using how well the robot follows the task.'],
      ['Save a policy to replay', 'model_499.pt · training log', 'The checkpoint saves the learned weights. The log records the reward and how long episodes lasted.'],
    ],
    ko: [
      ['걷기 목표와 현재 몸 상태', '목표 속도 + 로봇 상태', '가상 로봇마다 목표 속도와 현재의 움직임 정보가 주어집니다.'],
      ['움직이고 보상으로 배우기', '정책 → 관절 목표 → Newton → 보상', 'Newton이 움직임을 계산하고, RSL-RL은 얼마나 잘 걸었는지를 보상으로 받아 정책을 업데이트합니다.'],
      ['배운 정책을 저장하고 재생', 'model_499.pt · 학습 로그', '체크포인트에는 학습된 모델 값이, 로그에는 보상과 한 시도가 얼마나 이어졌는지가 남습니다.'],
    ],
    loop: { en: 'Repeat with the new robot state, and reset when an episode ends.', ko: '움직인 뒤의 상태로 다음 동작을 정하고, 한 시도가 끝나면 다시 시작합니다.' },
  },
  'everyday-robots': {
    en: [
      ['A camera view of the drawer', 'color image of card, hand, and slot', 'Start with the snack drawer. A synthetic camera image shows what is near the drawer.'],
      ['Make a decision from the image', 'card seen? · slot occupied?', 'OpenCV checks color in specific image regions. Those checks decide whether the drawer should move.'],
      ['Move one joint and keep a trace', 'slide position · result.json', 'The simulation applies motion to the drawer’s sliding joint. The trace tells you when it moved.'],
    ],
    ko: [
      ['서랍 앞 카메라 영상', '카드·손·서랍 입구가 보이는 컬러 영상', '과자 서랍 예제부터 봅니다. 가상 카메라가 서랍 앞에 있는 것을 보여줍니다.'],
      ['영상에서 움직일 조건 판단', '카드가 보이나? · 입구가 막혔나?', 'OpenCV가 지정한 영역의 색을 확인합니다. 그 결과로 서랍을 움직일지 정합니다.'],
      ['서랍을 움직이고 기록 남기기', '슬라이드 위치 · result.json', '시뮬레이터가 서랍이 미끄러지는 방향으로 관절을 움직입니다. 로그에서 언제 움직였는지 볼 수 있습니다.'],
    ],
  },
  'warp-particles': {
    en: [
      ['Particles and starting motion', 'positions (x, y, z) + velocities', 'The example starts with a collection of particles, including their locations and speeds.'],
      ['Find neighbors and compute contacts', 'nearby pairs → contact force → next position', 'Warp groups particles by location so only nearby ones need contact checks on the GPU.'],
      ['Check what moved', 'result.json · optional OpenGL viewer', 'The report stores counts and mean displacement. The viewer draws a subset of the computed particles.'],
    ],
    ko: [
      ['입자와 시작 상태', '위치 (x, y, z) + 속도', '각 입자가 어디에 있고 얼마나 빠르게 움직이는지부터 계산을 시작합니다.'],
      ['가까운 입자와의 접촉 계산', '이웃 → 접촉 힘 → 다음 위치', 'Warp가 공간을 나눠 가까운 입자만 짝지어 GPU에서 접촉을 계산합니다.'],
      ['얼마나 움직였는지 확인', 'result.json · OpenGL 뷰어', '보고서에는 입자 수와 평균 이동 거리가 남습니다. 뷰어는 계산된 입자 중 일부를 그립니다.'],
    ],
  },
  'workbench-capstone': {
    en: [
      ['Start with the CAD shape', 'workbench.step → cad_meshes.json', 'CadQuery reads the CAD solids and divides their surfaces into triangles that can be placed in USD.'],
      ['Make a scene the cube can land on', 'workbench_scene.usda · collider · camera', 'Isaac Sim adds the tabletop collision shape and the camera. PhysX moves the falling cube.'],
      ['Capture and verify camera data', 'PNG + depth/mask arrays → check/report.json', 'Replicator saves three channels per frame. The checker uses the saved data to measure cube movement.'],
    ],
    ko: [
      ['CAD의 작업대 형상', 'workbench.step → cad_meshes.json', 'CadQuery가 CAD를 읽고 표면을 작은 삼각형으로 나눠 USD에 옮길 수 있게 합니다.'],
      ['큐브가 떨어질 장면 만들기', 'workbench_scene.usda · 충돌체 · 카메라', 'Isaac Sim이 상판에 충돌체와 촬영용 카메라를 추가합니다. PhysX가 큐브 낙하를 계산합니다.'],
      ['카메라 데이터 저장하고 검사', 'PNG + 깊이·분할 배열 → check/report.json', 'Replicator가 한 프레임에 세 채널을 저장합니다. 검사 코드는 데이터를 읽어 큐브 이동량을 확인합니다.'],
    ],
  },
  'isaac-sim-first-cube': {
    en: [
      ['Same cube and floor', 'cube-drop.usda · collider variant', 'The two runs use the same cube, drop height, and camera. Only the cube’s collider changes.'],
      ['Gravity and contact', 'Rigid Body + optional Collider → PhysX', 'The rigid body can fall. Only the version with a collider registers contact with the floor.'],
      ['Watch the final position', 'Isaac Sim viewport', 'After Play, see where the cube ends up. Stop before choosing the other variant.'],
    ],
    ko: [
      ['같은 큐브와 바닥', 'cube-drop.usda · 충돌체 켜기/끄기', '두 번 모두 같은 초기 높이와 카메라를 씁니다. 큐브의 충돌체 설정만 달라집니다.'],
      ['중력과 접촉 계산', '강체 + 충돌체 설정 → PhysX', '강체라서 큐브가 떨어집니다. 충돌체를 켜면 바닥에 닿는 순간을 계산합니다.'],
      ['마지막 위치를 화면으로 확인', 'Isaac Sim 뷰포트', 'Play 후 큐브가 어디로 갔는지 보세요. 다른 설정으로 바꾸기 전에 Stop을 누릅니다.'],
    ],
  },
  'workbench-cad-to-isaac-sim': {
    en: [
      ['A CAD file with known dimensions', 'cad_source/workbench.step', 'Use a tabletop with measured dimensions so you know whether the conversion kept its scale.'],
      ['Convert and check', 'AIF + HOOPS → workbench.usdc', 'The converter writes USD geometry. Verify size, up axis, and missing references before simulating.'],
      ['Reference it in a simulation', 'workbench_scene.usd · collider', 'Keep a separate simulation scene. Give the tabletop a collider and use it for camera or robot tasks.'],
    ],
    ko: [
      ['치수를 아는 CAD 파일', 'cad_source/workbench.step', '상판 치수를 미리 알아두면 변환 후 크기가 맞는지 확인할 수 있습니다.'],
      ['변환하고 확인하기', 'AIF + HOOPS → workbench.usdc', '변환기가 USD 형상을 저장합니다. 실습 전에 크기, 위쪽 축, 빠진 참조가 있는지 살펴봅니다.'],
      ['시뮬레이션 장면에 배치', 'workbench_scene.usd · 충돌체', '별도 장면에서 변환 파일을 불러오고 상판에 충돌체를 붙여 카메라나 로봇 실습에 씁니다.'],
    ],
  },
  'alpasim-closed-loop': {
    en: [
      ['A scene for the camera', 'NuRec .usdz · ego pose', 'The renderer can draw a camera image at the simulated vehicle’s position.'],
      ['Let the policy drive', 'camera observation → trajectory', 'The baseline policy proposes a path. AlpaSim moves the vehicle along its simulated motion.'],
      ['Log the drive', 'metrics.parquet · metrics_results.txt', 'The rollout records events such as collisions and going off-road.'],
    ],
    ko: [
      ['카메라가 볼 주행 장면', 'NuRec .usdz · 자차 위치와 방향', '렌더러가 가상 차량이 있는 위치에서 카메라 영상을 만듭니다.'],
      ['정책이 갈 길 정하기', '카메라 영상 → 주행 궤적', '기준 정책이 갈 경로를 정하면 AlpaSim이 가상 차량을 움직입니다.'],
      ['주행 중 일어난 일 기록', 'metrics.parquet · metrics_results.txt', '차량이 충돌했는지, 도로를 벗어났는지 기록합니다.'],
    ],
    loop: { en: 'Moving the vehicle changes the next camera image. That image is the next policy input.', ko: '차량이 움직이면 다음 카메라 영상도 달라집니다. 그 영상으로 다시 경로를 정합니다.' },
  },
};
