// Each step shows a data example or file name, followed by what it means in the lab.
export const lessonFlows = {
  'rgb-reality-view': {
    en: [
      ['Start from RGB pixels', '162 JPEGs · uint8[H,W,3] → feature matches', 'The input guard excludes depth, LiDAR, supplied calibration, GPS and camera poses.'],
      ['Recover cameras, then learn the scene', 'COLMAP K[3,3] + poses[4,4] + XYZ → 400k Gaussians', 'NVIDIA 3DGUT learns a static scene on one RTX 5090. RGB alone leaves global scale ambiguous.'],
      ['Move the viewing camera', 'Mouse drag → camera change → new-view RGB', 'Spark renders the same 3D scene. The Volvo is a real mesh reference; the replay path comes from estimated cameras.'],
    ],
    ko: [
      ['RGB 픽셀에서 시작', 'JPEG 162장 · uint8[H,W,3] → 특징점 매칭', '깊이·LiDAR·제공된 보정값·GPS·카메라 자세를 입력에서 제외합니다.'],
      ['카메라와 장면 복원', 'COLMAP K[3,3] + 자세[4,4] + XYZ → Gaussian 40만 개', 'RTX 5090 한 장에서 NVIDIA 3DGUT를 학습합니다. RGB만으로는 실제 길이 단위를 확정할 수 없습니다.'],
      ['마우스로 관찰 시점 바꾸기', '드래그 → 3D 카메라 이동 → 새 시점 RGB', 'Spark가 같은 3D 장면을 그립니다. Volvo는 실제 메시이며 재생 경로는 사진에서 추정한 카메라 위치입니다.'],
    ],
  },
  'pandaset-nurec': {
    en: [
      ['Read measured surroundings', 'Six RGB cameras + timestamps + 4×4 poses + real LiDAR XYZ', 'PandaSet supplies real observations. Align asynchronous exposures before packaging NCore V4.'],
      ['Reconstruct and change the viewpoint', '456 images + 320k seed Gaussians → USDZ → new-view RGB', 'A static NuRec baseline can smear moving traffic and expose holes in unobserved surfaces.'],
      ['Place an identifiable ego car', 'Same camera pose → Blender Volvo RGBA → composite', 'Align the detailed CC BY Volvo mesh with a measured road plane. It does not supply vehicle control.'],
    ],
    ko: [
      ['실제 주행 관측 읽기', '카메라 6대 RGB + 시각 + 4×4 자세 + 실측 LiDAR XYZ', 'PandaSet의 실제 데이터를 씁니다. 카메라마다 다른 촬영 시각에 맞춰 NCore V4로 묶습니다.'],
      ['복원한 도로를 다른 시점에서 보기', '사진 456장 + Gaussian 초기값 32만 개 → USDZ → 새 시점 RGB', '정적 NuRec 예제라 움직이는 차는 번지고, 가려졌던 면에는 빈틈이 생길 수 있습니다.'],
      ['실제 차종으로 자차 위치 표시', '같은 카메라 → Blender Volvo RGBA → 합성', 'CC BY Volvo 상세 모델을 실측 도로 높이에 맞춥니다. 차량 제어 기능을 제공하는 모델은 아닙니다.'],
    ],
  },
  'reality-view': {
    en: [
      ['Capture our road', '120 RGB + z-depth images · K · camera-to-world', 'Only training-view depth seeds the Gaussian model. Keep 40 elevated camera views for comparison.'],
      ['Reconstruct and enhance', 'NuRec novel RGB → non-temporal Harmonizer RGB', 'Compare against the original USD. A learned enhancement can reduce pixel fidelity.'],
      ['Show a predicted route', 'Six raw cameras + ego history → 64 future poses', 'Project the actual Alpamayo output onto the display. This does not apply vehicle controls.'],
    ],
    ko: [
      ['직접 만든 도로 촬영', 'RGB·깊이 120장 · K · 카메라 자세', '학습용 깊이만 초기화에 쓰고, 높이를 올린 카메라 40곳은 비교용으로 남깁니다.'],
      ['장면 복원 후 프레임 보정', 'NuRec 새 시점 RGB → Harmonizer RGB', '원래 USD와 비교합니다. 생성 모델의 보정이 픽셀 정확도를 낮출 수도 있습니다.'],
      ['주행 모델의 예측 표시', '원본 여섯 카메라 + 과거 자세 → 미래 자세 64개', '실제 Alpamayo 출력을 화면에 투영합니다. 차량에 제어 명령을 적용하는 단계는 포함하지 않습니다.'],
    ],
  },
  'worldgen-dynamic-navigation': {
    en: [
      ['Read a timestamped observation', 'ranges[180] + hit positions[180,3] + sensor time', 'The controller sees measurements and ego pose. The actuator schedule stays outside the planner.'],
      ['Refresh the map and check motion', 'clear visible space → expire old hits → A* → stop supervisor', 'A passage can reopen. Missing data or an unavailable route stops the wheel commands.'],
      ['Replan and physically move again', 'new path → wheel drives → next measured pose', 'Verify a stationary hold, a changed detour, and matching collider/display positions in the actual run.'],
    ],
    ko: [
      ['거리와 측정 시각 함께 읽기', '거리[180] + 측정 지점[180,3] + 측정 시각', '로봇은 측정값과 자기 위치를 받습니다. 장애물의 이동 일정은 계획기에 넘기지 않습니다.'],
      ['지도를 갱신하고 움직임 판단', '빈 곳 확인 → 오래된 관측 제거 → A* → 정지 판단', '통로가 다시 열릴 수 있습니다. 센서 데이터가 오래됐거나 경로가 없으면 바퀴를 멈춥니다.'],
      ['경로를 다시 정해 실제로 이동', '새 경로 → 바퀴 드라이브 → 다음 위치 측정', '정지 유지와 우회 방향 변경, 충돌체와 표시 위치의 일치를 실제 기록으로 검사합니다.'],
    ],
  },
  'worldgen-navigation': {
    en: [
      ['Measure the surroundings', 'ranges: float[180] + hit positions: float[180,3]', 'An ideal Physics Raycast Sensor measures colliders. The planner receives no object names or transforms.'],
      ['Build a route from observations', '5 cm occupancy grid → 0.43 m inflation → A*', 'A known flat test boundary and simulator ego pose are assumed. The route is recalculated at 10 Hz.'],
      ['Drive and measure again', 'path → v, ω → wheel drives → next scan', 'Missing scans stop the robot. A changed box layout changes the generated route.'],
    ],
    ko: [
      ['주변까지의 거리 측정', '거리 float[180] + 측정 지점 float[180,3]', '이상적인 물리 거리 센서로 충돌체를 감지합니다. 계획기에 물체 이름이나 좌표를 넘기지 않습니다.'],
      ['관측으로 경로 계산', '5cm 점유 격자 → 0.43m 확장 → A*', '평평한 시험 구역 경계와 로봇의 현재 위치는 알고 있다고 가정합니다. 초당 10번 경로를 계산합니다.'],
      ['주행 후 다시 측정', '경로 → v, ω → 바퀴 드라이브 → 다음 스캔', '센서 데이터가 없으면 정지합니다. 상자 배치가 바뀌면 우회 경로도 달라집니다.'],
    ],
  },
  'worldgen-isaac': {
    en: [
      ['Choose a coordinate and scale convention', 'WorldGen RGB + distance → 80k-vertex textured mesh', 'Fit a floor plane; assume a 1.5 m camera height. This establishes a simulation scale, not measured truth.'],
      ['Check what can collide', 'static generated mesh / 5×4 m floor / added crate', 'Compare real cube drops and raycasts. The robot run uses explicit proxy collisions.'],
      ['Close the control loop through physics', 'pose + waypoint → v, ω → wheel drives → PhysX pose', 'A hand-authored route guides the AMR. Native GUI recording shows live joint and contact simulation.'],
    ],
    ko: [
      ['좌표계와 크기 기준 정하기', 'WorldGen RGB·거리 → 정점 8만 개의 텍스처 메시', '바닥을 평면으로 맞추고 카메라 높이를 1.5m로 가정합니다. 실제 크기를 측정한 값은 아닙니다.'],
      ['부딪히는 형상 확인', '정적 추정 메시 / 5×4m 바닥 / 추가 시험 상자', '큐브 낙하와 광선 충돌을 비교합니다. 주행에는 따로 작성한 충돌체를 사용합니다.'],
      ['물리 결과를 읽어 다음 제어 명령 계산', '자세·경유점 → v, ω → 바퀴 드라이브 → PhysX 자세', '미리 정한 경유점을 따라갑니다. 실제 GUI에서 관절·접촉을 계산하며 녹화했습니다.'],
    ],
  },
  'worldgen-scenes': {
    en: [
      ['Describe or show a place', 'prompt / RGB + 3×3 camera K + fill mask', 'Text creates a full panorama. An image fixes observed pixels and generates its surroundings.'],
      ['Generate appearance and infer distance', 'FLUX + panorama LoRA → RGB 1600×800 → DA-2', 'The distance map has one inferred ray distance per pixel. Max 20 is a normalization, not measured meters.'],
      ['Build and render a persistent scene', '1,280,000 Gaussians + mesh → PLY / SPZ / MP4', 'XYZ = unit ray × distance. Translated cameras reveal parallax and hidden-surface artifacts.'],
    ],
    ko: [
      ['장소를 글이나 이미지로 지정', '프롬프트 / RGB + 카메라 K(3×3) + 생성 마스크', '글은 파노라마 전체를 만들고, 이미지는 보이는 영역을 유지한 채 주변을 채웁니다.'],
      ['겉모습 생성 후 거리 추정', 'FLUX + 파노라마 LoRA → RGB 1600×800 → DA-2', '픽셀마다 카메라에서 표면까지의 거리를 추정합니다. 최댓값 20은 정규화 값이며 실측 미터가 아닙니다.'],
      ['3D 데이터로 바꿔 다른 시점에서 보기', 'Gaussian 128만 개 + 메시 → PLY / SPZ / MP4', '단위 광선 × 거리로 XYZ를 구합니다. 카메라를 옮기면 시차와 가려진 면의 한계가 드러납니다.'],
    ],
  },
  'carla-ego': {
    en: [
      ['Choose a world', 'Town10HD · Town03 · Town02 · Town04 + weather', 'CARLA owns the map, vehicles, physics and sensor simulation.'],
      ['Advance the driver and simulation', 'Traffic Manager controls → 0.05 s tick', 'The rule-based driver reads actor/road state. It does not read the RGB video.'],
      ['Record the observation', '960×540 RGB + frame ID + XYZ + speed', 'Ego and chase cameras share the tick. Published videos are resized to 768×432.'],
    ],
    ko: [
      ['환경 고르기', 'Town10HD · Town03 · Town02 · Town04와 날씨', 'CARLA가 맵·차량·물리·센서를 시뮬레이션합니다.'],
      ['운전 명령으로 한 스텝 진행', 'Traffic Manager 제어 → 0.05초', '규칙 기반 제어기는 차량·도로 상태를 읽습니다. RGB 영상을 입력으로 쓰지는 않습니다.'],
      ['관측 기록하기', '960×540 RGB + 프레임 번호 + XYZ + 속도', '운전자·추적 카메라를 같은 스텝에 찍습니다. 공개 개별 영상은 768×432로 줄였습니다.'],
    ],
    loop: { en: 'New actor states return to Traffic Manager for the next control step.', ko: '다음 차량 상태를 Traffic Manager가 읽어 새 제어 명령을 정합니다.' },
  },
  'spatial-reconstruction': {
    en: [
      ['Capture the measured world', '72 RGB images + K + 4×4 poses + depth (m)', 'CARLA supplies known camera geometry. Reserve every eighth view.'],
      ['Optimize a radiance field', '63 training images → 345,318 Gaussians', 'fVDB adjusts position, scale, opacity and color. Held-out depth is excluded from initialization.'],
      ['Render another viewpoint', 'full PLY → MP4 / 345k-point SPZ → Spark', 'The browser view loads on demand. No physics or collision mesh is included.'],
    ],
    ko: [
      ['장면 촬영하기', 'RGB 72장 + K + 4×4 자세 행렬 + 깊이(m)', 'CARLA의 정확한 카메라 정보를 사용합니다. 8번째마다 검사 시점으로 남깁니다.'],
      ['공간의 겉모습 학습', '학습 사진 63장 → Gaussian 345,318개', 'fVDB가 위치·크기·불투명도·색을 조정합니다. 검사 시점의 깊이는 초기 점군에서 제외합니다.'],
      ['새 시점으로 그리기', '전체 PLY → MP4 / 345,318개 SPZ → Spark', '버튼을 누를 때만 브라우저 모델을 받습니다. 물리나 충돌체는 포함되지 않습니다.'],
    ],
  },
  'scene-generation': {
    en: [
      ['Choose generation rules', 'random seed + room count + furniture generators', 'Infinigen constructs a new furnished house from procedural rules.'],
      ['Plan a camera tour', 'mesh geometry → RRT camera path + transforms', 'The example selects a path through connected rooms. This is camera navigation, not a robot policy.'],
      ['Render the geometry', '.blend + camera.npz → Cycles RGB', 'CPU rendering and OpenImageDenoise produce the preview. The 48-frame path is played at 8 fps.'],
    ],
    ko: [
      ['생성 규칙 정하기', '랜덤 시드 + 방 개수 + 가구 생성기', 'Infinigen이 규칙에 따라 가구가 있는 새 집을 만듭니다.'],
      ['카메라 이동 경로 찾기', '메시 → RRT 카메라 경로·변환 행렬', '연결된 방 안의 경로를 정합니다. 로봇 정책을 학습한 것은 아닙니다.'],
      ['기하 구조를 화면에 그리기', '.blend + camera.npz → Cycles RGB', 'CPU 렌더링과 OpenImageDenoise를 사용했습니다. 48프레임을 8 FPS로 재생합니다.'],
    ],
  },
  'world-driving': {
    en: [
      ['Two independent inputs', 'Cosmos: RGB + camera actions; Alpamayo: 22 RGB frames + ego history', 'Both examples use scenes we authored. They test different model interfaces.'],
      ['Run released model weights', 'Cosmos3-Edge · Alpamayo2-Edge', 'Cosmos generates pixels. Alpamayo proposes future vehicle positions and rotations.'],
      ['Inspect each result', '61-frame MP4 · 64 future poses', 'Check decoded frames and finite tensors. The car shown in Isaac Sim replays the predicted trajectory.'],
    ],
    ko: [
      ['두 모델에 각각 입력 준비', 'Cosmos: RGB와 카메라 동작 / Alpamayo: RGB 22장과 과거 자세', '직접 만든 장면을 사용합니다. 서로 다른 모델의 입출력을 확인하는 두 실험입니다.'],
      ['공개 가중치로 추론', 'Cosmos3-Edge · Alpamayo2-Edge', 'Cosmos는 영상 픽셀을 생성하고, Alpamayo는 차량의 미래 위치와 회전을 예측합니다.'],
      ['각 결과 확인', 'MP4 61프레임 · 미래 자세 64개', '영상과 저장된 텐서를 검사합니다. Isaac Sim 속 차량은 예측 경로를 재생합니다.'],
    ],
  },
  'newton-materials': {
    en: [
      ['Connected geometry', 'mesh vertices + material + fixed points', 'A grid describes cloth. Cable bodies have stiffness and joints.'],
      ['Solve the motion', 'forces + contacts → updated XYZ positions', 'Newton advances the model. Official example tests check the resulting state.'],
      ['Inspect the recorded states', 'time-sampled USD · result.json · GUI MP4', 'Replay the solver output in Isaac Sim and check finite positions and deformation.'],
    ],
    ko: [
      ['연결된 점과 재료 설정', '메시의 점 + 물성 + 고정점', '천은 격자로, 케이블은 강성과 관절을 가진 몸체로 표현합니다.'],
      ['움직임 계산', '힘과 접촉 → 새 XYZ 좌표', 'Newton이 다음 상태를 구합니다. 공식 예제의 테스트로 계산 결과를 검사합니다.'],
      ['시간별 상태 확인', 'USD · result.json · GUI 녹화', 'Isaac Sim에서 계산 결과를 재생하고 좌표와 변형을 확인합니다.'],
    ],
  },
  'gr00t-placement': {
    en: [
      ['What the robot sees', 'camera views + joint state + instruction', 'Arena packages the simulated observations for the GR00T DROID checkpoint.'],
      ['What the policy predicts', 'sequence of joint and gripper targets', 'The runner executes a portion of the prediction before requesting a new one.'],
      ['What the simulator records', 'episode_results_*.jsonl', 'Isaac Sim applies the targets. Arena writes one trial per line, with separate lift and placement events.'],
    ],
    ko: [
      ['로봇이 보는 것', '카메라 영상 + 관절 상태 + 지시문', 'Arena가 가상 로봇의 관측을 DROID 체크포인트가 읽을 수 있는 형태로 묶습니다.'],
      ['모델이 제안하는 동작', '관절·그리퍼 목표의 시퀀스', '동작 예측의 일부를 실행한 뒤 새 관측으로 다시 예측합니다.'],
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
      ['A camera view of the drawer', 'BGR image of card, hand, and slot', 'The lab draws a synthetic camera frame to test the control rule.'],
      ['Make a decision from the image', 'card seen? · slot occupied?', 'OpenCV checks color in specific image regions. Those checks decide whether the drawer should move.'],
      ['Move one joint and keep a trace', 'slide position · result.json', 'The simulation applies motion to the drawer’s sliding joint. The trace tells you when it moved.'],
    ],
    ko: [
      ['서랍 앞 카메라 입력', '카드·손·서랍 입구가 보이는 BGR 배열', '실습은 카메라가 볼 법한 이미지를 코드로 그려 제어 규칙을 시험합니다.'],
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
  selection: {
    en: [
      ['Observe and specify the task', 'camera views + task + robot state', 'Match these inputs to the checkpoint and robot.'],
      ['Predict commands', 'VLA → action sequence', 'Translate each action to the controller’s joint order, units, and coordinates.'],
      ['Score the episode', 'task success + event log', 'Check what actually happened after the robot applied the actions.'],
    ],
    ko: [
      ['현재 상태와 할 일 전달', '카메라 + 작업 지시 + 로봇 상태', '선택한 체크포인트와 로봇에 맞는 입력을 준비합니다.'],
      ['행동 예측', 'VLA → 행동 시퀀스', '관절 순서, 단위, 좌표계를 제어기 규약에 맞춥니다.'],
      ['작업 결과 판정', '성공 여부 + 이벤트 로그', '예측한 동작을 적용하고 나서 실제로 일어난 일을 확인합니다.'],
    ],
  },
  cosmos: {
    en: [
      ['Choose the conditioning', 'clip + question or scene controls', 'Select inputs for the task your checkpoint supports.'],
      ['Choose the task', 'reasoning · generation · prediction', 'Each task uses the video or conditioning in a different way.'],
      ['Evaluate the output', 'text, video, or a predicted rollout', 'Use checks suited to what the checkpoint produced.'],
    ],
    ko: [
      ['사용할 조건 고르기', '영상 + 질문 또는 장면 조건', '체크포인트가 지원하는 과제의 입력을 준비합니다.'],
      ['수행할 과제 고르기', '추론 · 생성 · 예측', '과제에 따라 영상이나 조건을 쓰는 방식이 달라집니다.'],
      ['출력 확인하기', '텍스트 · 영상 · 예측 롤아웃', '출력에 맞춰 조건을 따랐는지 평가합니다.'],
    ],
  },
  'nemo-switchyard': {
    en: [
      ['Prepare an app request', 'observation → summary request', 'The app turns a video observation into a text task.'],
      ['Select a model', 'request + model pool + routing strategy', 'Switchyard helps the host select the model for the request.'],
      ['Call the endpoint', 'model selection → response', 'The host calls the selected provider and the app uses its response.'],
    ],
    ko: [
      ['앱 요청 만들기', '영상 관찰 → 요약 요청', '영상에서 관찰한 내용을 텍스트 과제로 바꿉니다.'],
      ['호출할 모델 고르기', '요청 + 모델 목록 + 선택 전략', 'Switchyard가 호스트의 모델 선택을 돕습니다.'],
      ['엔드포인트 호출하기', '선택된 모델 → 응답', '호스트가 해당 모델을 호출하면 앱이 응답을 사용합니다.'],
    ],
  },
  'nvidia-linux': {
    en: [
      ['Start with the machine', 'Linux + NVIDIA GPU', 'Check the device and operating system on the host.'],
      ['Check access from the lab', 'driver → runtime or container', 'Check GPU visibility in the environment that will run the lab.'],
      ['Run a workload', 'Python or simulator process', 'Start the application to confirm it can perform GPU work.'],
    ],
    ko: [
      ['머신부터 확인', 'Linux + NVIDIA GPU', '호스트에서 운영체제와 GPU를 확인합니다.'],
      ['실습 환경에서 접근 확인', '드라이버 → 런타임 또는 컨테이너', '실습을 실제로 실행할 환경에서 GPU가 보이는지 확인합니다.'],
      ['실제 연산 실행', 'Python 또는 시뮬레이터', '애플리케이션을 실행해 GPU 연산이 시작되는지 확인합니다.'],
    ],
  },
  'isaac-sim-tools': {
    en: [
      ['Open one scene', 'USD → Stage and Property', 'Find the scene objects and inspect their settings in the GUI.'],
      ['Repeat the run', 'script + camera path', 'Use those same scene settings for a scripted capture.'],
      ['Read the output', 'RGB · depth · masks · result report', 'Inspect generated files with the CPU checker.'],
    ],
    ko: [
      ['장면 하나 열기', 'USD → Stage와 Property', 'GUI에서 물체를 찾고 설정을 읽습니다.'],
      ['같은 조건으로 실행', '스크립트 + 카메라 경로', '확인한 장면 설정으로 스크립트 촬영을 실행합니다.'],
      ['출력 파일 읽기', 'RGB · 깊이 · 마스크 · 검사 보고서', '저장된 파일을 CPU 검사 코드로 확인합니다.'],
    ],
  },
};
