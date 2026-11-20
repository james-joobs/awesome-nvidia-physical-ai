const referenceSections = ['architecture', 'example', 'verification', 'license', 'related-tools', 'official-sources'];
const pipelineSections = ['architecture', 'example', 'verification', 'official-sources', 'related-tools'];

function guide(source, topic, sections, title, en, ko, loop) {
  const [enDescription, ...enFlow] = en;
  const [koDescription, ...koFlow] = ko;
  return {
    source,
    page: `tools/${source}`,
    topic,
    sections: ['implementation', ...sections],
    en: { title: typeof title === 'string' ? title : title.en, description: enDescription },
    ko: { title: typeof title === 'string' ? title : title.ko, description: koDescription },
    flow: { en: enFlow, ko: koFlow, loop },
  };
}

export const toolGuides = [
  guide('spatial-worlds', 'world-models', ['architecture', 'verification', 'related-tools'], { en: 'Choose a 3D world workflow', ko: '3D 세계 생성·렌더링 도구 고르기' }, [
    'Compare explorable 3D worlds, measured Gaussian scenes, procedural geometry, and action-conditioned video.',
    ['Choose the scene input', 'prompt · photograph · calibrated views · random seed', 'Different inputs lead to different kinds of uncertainty.'],
    ['Keep the representation explicit', '3DGS · mesh/materials · collider · RGB video', 'A video is not a reusable 3D scene, and a splat is not a collision surface.'],
    ['Render, inspect and simulate', 'Spark browser view · Blender · CARLA ego camera', 'Use our recordings and code; check model terms before running a generative checkpoint.'],
  ], [
    '탐색 가능한 3D 세계, 촬영한 Gaussian 장면, 절차적 기하 구조와 카메라 동작 기반 영상을 비교합니다.',
    ['장면을 만들 입력 고르기', '프롬프트 · 사진 · 카메라 정보가 있는 여러 시점 · 시드', '입력에 따라 새로 생성하는 부분과 추정해야 할 부분이 달라집니다.'],
    ['출력 형식 구분하기', '3DGS · 메시/재질 · 충돌체 · RGB 영상', '영상은 재사용할 3D 공간이 아니며 splat만으로 충돌을 계산할 수도 없습니다.'],
    ['그려 보고 직접 확인하기', 'Spark 브라우저 · Blender · CARLA 운전자 카메라', '직접 실행한 영상·코드를 살펴보고 생성 모델은 가중치 조건을 확인한 뒤 실행합니다.'],
  ]),
  guide('simready', 'simulation', referenceSections, 'SimReady', [
    'Read the physical and semantic properties that turn a USD asset into a simulation input.',
    ['Visual asset', 'USD mesh and materials', 'These describe the shape and its appearance.'],
    ['Author simulation properties', 'collider · mass · class label', 'Add the properties the solver and camera annotators will read.'],
    ['Test it in a scene', 'contact position · class pixels', 'Drop a probe and check what the camera labels.'],
  ], [
    'USD 에셋에 어떤 물리 속성과 라벨이 있어야 시뮬레이션에 쓸 수 있는지 살펴봅니다.',
    ['화면에 보이는 에셋', 'USD 메시와 재질', '에셋의 모양과 화면에 보이는 모습을 정합니다.'],
    ['시뮬레이션 속성 추가', '충돌체 · 질량 · 클래스 라벨', '물리 엔진과 카메라 어노테이터가 읽을 속성을 붙입니다.'],
    ['장면에 넣어 확인', '접촉 위치 · 라벨 픽셀', '물체가 어디에 닿고 카메라가 어떤 픽셀에 라벨을 붙이는지 봅니다.'],
  ]),
  guide('newton', 'simulation', ['release', ...referenceSections], 'Newton', [
    'Follow rigid-body state through a Newton step and compare its saved poses with PhysX.',
    ['Build the physics model', 'bodies · colliders · joints', 'Set geometry and initial poses.'],
    ['Advance time', 'contacts + solver + Δt', 'The solver computes the next configuration.'],
    ['Inspect the states', 'newton-poses.npy', 'Compare equivalent bodies and timestamps across runs.'],
  ], [
    'Newton이 한 스텝의 물리를 계산하는 과정과 PhysX 결과를 비교하는 법을 배웁니다.',
    ['물리 모델 구성', '강체 · 충돌체 · 관절', '형상과 초기 자세를 정합니다.'],
    ['한 스텝 계산', '접촉 + 솔버 + 시간 간격', '솔버가 다음 상태를 계산합니다.'],
    ['저장된 상태 확인', 'newton-poses.npy', '같은 강체와 시점의 좌표를 골라 두 실행을 비교합니다.'],
  ]),
  guide('openusd', 'synthetic-data', referenceSections, 'OpenUSD', [
    'Trace how reusable asset references and scene edits produce the USD stage Isaac Sim opens.',
    ['Reusable asset', 'workbench.usdc', 'Store the workbench geometry in its own file.'],
    ['Compose the scene', 'reference + placement opinions', 'Place the asset and author scene-specific properties.'],
    ['Inspect the result', 'stage · prim paths · units', 'Check what the simulator actually reads.'],
  ], [
    '참조와 레이어를 합성해 Isaac Sim이 여는 장면이 어떻게 만들어지는지 살펴봅니다.',
    ['재사용할 에셋', 'workbench.usdc', '작업대 형상을 별도 파일에 저장합니다.'],
    ['장면 합성', '참조 + 배치 속성', '에셋을 배치하고 장면마다 필요한 속성을 추가합니다.'],
    ['합성 결과 점검', '스테이지 · 프림 경로 · 단위', '시뮬레이터가 최종적으로 읽을 값을 확인합니다.'],
  ]),
  guide('replicator', 'synthetic-data', referenceSections, 'Replicator', [
    'Connect a camera to annotators and see how their outputs become files.',
    ['Configure the view', 'camera prim + resolution', 'A render product represents the image to sample.'],
    ['Read channels', 'annotators → RGB · depth · label IDs', 'Each annotator returns a different view of the same frame.'],
    ['Save matching outputs', 'writer or Python → frame files', 'Keep the frame index and label lookup together.'],
  ], [
    '카메라와 어노테이터를 연결해 RGB·깊이·분할 값이 어떤 파일로 저장되는지 살펴봅니다.',
    ['촬영 설정', '카메라 프림 + 해상도', '렌더 프로덕트가 읽을 화면을 지정합니다.'],
    ['채널별 데이터 읽기', '어노테이터 → RGB · 깊이 · 라벨 ID', '같은 프레임에서 필요한 정보를 채널마다 읽습니다.'],
    ['결과 묶어서 저장', '라이터 또는 Python → 프레임 파일', '프레임 번호와 라벨 매핑을 함께 보관합니다.'],
  ]),
  guide('isaac-lab', 'robotics', ['release', ...referenceSections], 'Isaac Lab', [
    'Follow observations, actions, rewards, and resets through parallel robot training environments.',
    ['Task and state', 'robot model + command + observations', 'The task defines sensors, controls, and success criteria.'],
    ['Step many environments', 'policy action → physics → reward', 'Each environment produces its next observation.'],
    ['Update and replay', 'rollouts → RL update → checkpoint', 'The training library updates shared policy weights.'],
  ], [
    '여러 로봇 환경에서 관측·행동·보상이 어떻게 오가고 정책을 학습시키는지 설명합니다.',
    ['과제와 로봇 상태', '로봇 모델 + 목표 + 관측', '과제에서 센서와 제어, 성공 조건을 정합니다.'],
    ['여러 환경을 한 스텝 실행', '정책 행동 → 물리 → 보상', '환경마다 새로운 관측값을 만듭니다.'],
    ['정책 학습과 재생', '롤아웃 → 가중치 갱신 → 체크포인트', '학습 라이브러리가 공용 정책을 갱신합니다.'],
  ]),
  guide('isaac-capture', 'robotics', pipelineSections, 'Isaac Capture', [
    'Understand how tracked human poses become robot commands and synchronized demonstrations.',
    ['Track the operator', 'device pose + timestamp', 'The device reports hand or controller motion.'],
    ['Retarget the motion', 'device coordinates → robot commands', 'Retargeting adapts motion to the robot’s joints and limits.'],
    ['Save a demonstration', 'aligned observations and actions', 'Check coordinate frames and timestamp alignment before training.'],
  ], [
    '사용자의 움직임을 로봇 명령으로 바꾸고 학습용 시연으로 기록하는 과정을 살펴봅니다.',
    ['조작자 움직임 추적', '장치 자세 + 타임스탬프', '장치가 손이나 컨트롤러의 움직임을 기록합니다.'],
    ['로봇에 맞게 리타기팅', '장치 좌표 → 로봇 명령', '로봇 관절과 동작 범위에 맞춰 움직임을 바꿉니다.'],
    ['시연으로 저장', '시점을 맞춘 관측과 행동', '학습에 쓰기 전 좌표계와 타임스탬프가 맞는지 봅니다.'],
  ]),
  guide('autodata', 'robotics', pipelineSections, 'AutoData', [
    'See how a seed demonstration becomes new simulator-checked training examples.',
    ['Start from demonstrations', 'seed episode + object poses', 'Locate action segments such as grasp and placement.'],
    ['Generate for a new scene', 'retargeted segment → simulation', 'Adapt the segments to rearranged objects and execute them.'],
    ['Save successful attempts', 'episodes + success counters', 'Use the task checks to decide which attempts to keep.'],
  ], [
    '기존 로봇 시연을 새 장면에 적용하고 성공한 시연을 학습 데이터로 남기는 과정을 살펴봅니다.',
    ['원본 시연에서 시작', '시연 에피소드 + 물체 자세', '집기·놓기처럼 재사용할 동작 구간을 찾습니다.'],
    ['새 장면에 맞춰 생성', '변환한 동작 → 시뮬레이터', '물체 배치에 맞춘 동작을 가상 로봇으로 실행합니다.'],
    ['성공 시연 저장', '에피소드 + 시도·성공 기록', '과제의 성공 조건을 만족한 시연을 남깁니다.'],
  ]),
  guide('video-to-data', 'robotics', pipelineSections, 'Video-to-Data', [
    'Trace how human manipulation video becomes a robot training candidate.',
    ['Find task clips', 'video → selected time intervals', 'Choose clips that show a coherent manipulation task.'],
    ['Recover motion in 3D', 'camera and motion estimates', 'Use the selected pipeline to recover spatial observations.'],
    ['Prepare training examples', 'robot-compatible observation/action pairs', 'Review the reconstruction and match the target robot’s action space.'],
  ], [
    '사람의 작업 영상에서 로봇 학습에 쓸 만한 관측과 행동 쌍을 얻는 흐름을 설명합니다.',
    ['작업 구간 고르기', '영상 → 시작·종료 시각', '작업 흐름이 드러나는 구간을 선별합니다.'],
    ['3D 움직임 추정', '카메라와 움직임 추정값', '사용할 파이프라인에 맞춰 공간상의 움직임을 복원합니다.'],
    ['학습용 데이터 준비', '로봇용 관측·행동 쌍', '복원 결과를 검토하고 대상 로봇의 행동 표현에 맞춥니다.'],
  ]),
  guide('nurec', 'autonomous-driving', ['architecture', 'sensor-adaptation', 'example', 'distribution'], 'NuRec', [
    'See how sensor logs become a scene that can render new camera views.',
    ['Recorded observations', 'images + calibration + sensor poses', 'The scene reconstruction needs aligned times and known viewpoints.'],
    ['Reconstruct the scene', '3D Gaussians + scene metadata', 'Fit a scene representation to the observations.'],
    ['Render a new view', 'scene asset + requested camera → image', 'Use a new camera pose or the next simulated ego position.'],
  ], [
    '주행 기록에서 새 카메라 시점으로 렌더링할 수 있는 장면을 만드는 과정을 살펴봅니다.',
    ['기록된 관측값', '영상 + 캘리브레이션 + 센서 자세', '시점과 촬영 위치를 맞춰 관측값을 준비합니다.'],
    ['장면 재구성', '3D 가우시안 + 장면 메타데이터', '촬영된 모습에 맞춰 장면 표현을 복원합니다.'],
    ['새 시점에서 렌더링', '장면 에셋 + 요청 카메라 → 영상', '새 카메라 배치나 가상 차량 위치에서 다시 렌더링합니다.'],
  ]),
  guide('cosmos-curator', 'world-models', ['architecture', 'example', 'related-tools'], 'Cosmos Curator', [
    'Follow raw recordings through clipping, filtering, and annotation to a training dataset.',
    ['Raw recordings', 'video files + source metadata', 'Keep a link to the original recording.'],
    ['Curate the clips', 'segment → filter → annotate', 'Run stages suited to the dataset and document their settings.'],
    ['Review retained clips', 'clips + metadata + rejection reasons', 'Check accepted and rejected examples before training.'],
  ], [
    '원본 영상을 짧은 구간으로 나누고 선별·주석해 학습 데이터를 만드는 과정을 봅니다.',
    ['원본 기록', '영상 파일 + 출처 정보', '어디에서 온 영상인지 추적할 수 있게 합니다.'],
    ['구간 선별과 가공', '분할 → 필터 → 주석', '데이터 목적에 맞는 단계를 실행하고 설정을 기록합니다.'],
    ['남긴 데이터 검토', '클립 + 메타데이터 + 제외 사유', '학습을 시작하기 전에 통과·탈락 사례를 표본으로 확인합니다.'],
  ]),
  guide('cosmos-data-factory', 'world-models', ['architecture', 'example', 'related-tools'], 'Cosmos Data Factory', [
    'Trace a blueprint from data sources through generation and quality checks to an exported dataset.',
    ['Choose data and controls', 'source clip + generation conditions', 'Pick a blueprint for the sample you need.'],
    ['Run stages', 'curation → generation → evaluation', 'The workflow connects the selected tools and models.'],
    ['Export traceable samples', 'generated files + provenance', 'Keep originals, settings, and checks linked to each sample.'],
  ], [
    '블루프린트가 선별·생성·평가 단계를 거쳐 데이터셋을 내보내는 과정을 살펴봅니다.',
    ['원본과 생성 조건 선택', '원본 클립 + 장면 조건', '필요한 표본에 맞춰 블루프린트를 고릅니다.'],
    ['단계 실행', '선별 → 생성 → 평가', '워크플로가 단계에 맞는 도구와 모델을 연결합니다.'],
    ['생성 데이터 내보내기', '생성 파일 + 출처 기록', '원본과 설정, 검사 결과를 표본마다 연결합니다.'],
  ]),
  guide('metropolis-vss', 'world-models', ['architecture', 'example', 'verification', 'license', 'official-sources', 'related-tools'], 'Metropolis VSS', [
    'See how video intervals become evidence for search and answers.',
    ['Read the video', 'clip + source timestamps', 'Keep offsets so results point back to the footage.'],
    ['Index or analyze intervals', 'clip descriptions or visual evidence', 'Video models and the configured pipeline extract evidence.'],
    ['Answer a question', 'retrieved interval → answer + timestamp', 'Confirm that the cited interval supports the answer.'],
  ], [
    '영상 구간을 분석해 검색하고, 답변의 근거를 원본 영상에서 확인하는 방법을 살펴봅니다.',
    ['영상 읽기', '클립 + 원본 타임스탬프', '결과에서 원본 영상의 위치로 돌아갈 수 있게 합니다.'],
    ['구간 분석과 검색 준비', '클립 설명 또는 영상 근거', '구성한 파이프라인과 모델로 영상의 단서를 찾습니다.'],
    ['질문에 답변', '찾은 영상 구간 → 답변 + 시각', '인용된 구간이 실제로 답변의 근거가 되는지 확인합니다.'],
  ]),
  guide('fvdb-reality-capture', 'synthetic-data', ['outputs', 'official-sources'], 'fVDB Reality Capture', [
    'Reconstruct a scene from calibrated photos, render another viewpoint, and compare the available exports.',
    ['Load a calibrated capture', 'COLMAP images + camera poses + sparse points', 'Each image is associated with a viewpoint in the scene.'],
    ['Fit a Gaussian scene', 'render → compare with source → update', 'Optimize splat parameters against the source images.'],
    ['Render and export', 'reconstructed_model.ply · USD · triangle mesh', 'Choose an export based on the downstream use.'],
  ], [
    '촬영 위치를 아는 사진에서 3D 장면을 복원하고, 새 시점을 렌더링하고 내보냅니다.',
    ['촬영 데이터 읽기', 'COLMAP 이미지 + 카메라 자세 + 희소 점군', '사진마다 어느 위치와 방향에서 촬영했는지 기록합니다.'],
    ['가우시안 장면 맞추기', '렌더링 → 원본과 비교 → 파라미터 갱신', '원본 이미지와 비슷해지도록 가우시안 속성을 조정합니다.'],
    ['새 시점 렌더링과 내보내기', 'reconstructed_model.ply · USD · 삼각형 메시', '다음에 장면을 어떻게 쓸지에 맞춰 출력을 고릅니다.'],
  ]),
  guide('alpamayo', 'autonomous-driving', ['release', 'architecture', 'example', 'verification', 'license', 'official-sources'], 'Alpamayo', [
    'Read the public 2 Super inference sample from camera and ego history through reasoning and future waypoints.',
    ['Prepare the observation', 'clip_id + t0_us → cameras and ego history', 'Select a common instant for the visual and motion inputs.'],
    ['Reason and predict motion', 'vision-language context → action expert', 'The action expert samples future positions and rotations.'],
    ['Inspect predictions', 'reasoning + 64 waypoints + minADE', 'Compare trajectory geometry with the recorded future and review the reasoning.'],
  ], [
    '2 Super 공식 추론 예제에서 카메라 영상과 자차 상태가 설명과 미래 궤적으로 바뀌는 과정을 봅니다.',
    ['관측 시점 정하기', 'clip_id + t0_us → 영상과 자차 이동 기록', '영상과 자차 입력을 같은 기준 시각에 맞춥니다.'],
    ['주행 상황 해석과 궤적 예측', '시각·언어 특징 → 궤적 생성 모듈', '미래 위치와 회전을 시점별로 예측합니다.'],
    ['결과 읽기', '판단 설명 + 64개 경유점 + minADE', '기록된 주행과 예측 경로를 비교하고 설명을 검토합니다.'],
  ]),
  guide('alpagym', 'autonomous-driving', ['architecture', 'example', 'verification', 'license', 'official-sources', 'related-tools'], 'AlpaGym', [
    'Trace a configured AlpaSim rollout through reward calculation and Cosmos-RL policy updates.',
    ['Resolve the run', 'scene_ids + policy + reward config', 'Choose scenes, an adapter, and the scoring terms.'],
    ['Collect a closed-loop drive', 'observation ↔ policy trajectory', 'AlpaSim advances the vehicle and returns the next observation.'],
    ['Score and update', 'episode metrics → reward → Cosmos-RL', 'Combine measured terms and use the returned trajectories for training.'],
  ], [
    '설정 파일에서 고른 주행 장면이 폐루프 경험과 보상으로 이어져 정책을 갱신하는 과정을 봅니다.',
    ['실행 조건 구성', 'scene_ids + 정책 + 보상 설정', '장면과 어댑터, 보상 항목을 정합니다.'],
    ['폐루프 주행으로 경험 수집', '관측 ↔ 정책 궤적', 'AlpaSim이 차량을 움직인 뒤 새 관측을 돌려줍니다.'],
    ['점수 계산과 정책 갱신', '에피소드 지표 → 보상 → Cosmos-RL', '지표를 합산한 보상과 주행 데이터를 학습에 전달합니다.'],
  ], {
    en: 'The updated policy can produce a different rollout on the next training round.',
    ko: '다음 학습 라운드에서는 갱신된 정책으로 새 주행 경험을 모읍니다.',
  }),
  guide('isaac-sim', 'simulation', ['release', ...referenceSections], 'Isaac Sim', [
    'Follow one USD stage through physics, RTX rendering, and sensor capture.',
    ['Describe the stage', 'USD prims + physics and camera properties', 'Geometry, colliders, and sensors live in the stage.'],
    ['Advance and render', 'PhysX state → RTX camera view', 'Advance body state and render it from the camera pose.'],
    ['Use the outputs', 'viewport · captured images · scene data', 'Inspect the animation or capture files for downstream checks.'],
  ], [
    'USD 장면을 열어 물리를 계산하고 RTX로 센서 데이터를 만드는 구조를 봅니다.',
    ['장면 정의', 'USD 프림 + 물리·카메라 속성', '장면에 형상, 충돌체, 센서를 지정합니다.'],
    ['물리 계산과 렌더링', 'PhysX 상태 → RTX 카메라 화면', '강체 상태를 갱신하고 카메라 시점의 화면을 그립니다.'],
    ['출력 사용', '뷰포트 · 촬영 이미지 · 장면 데이터', '화면에서 움직임을 보거나 데이터 파일로 검사합니다.'],
  ]),
  guide('nvidia-physx', 'simulation', referenceSections, 'PhysX', [
    'Understand how gravity and contact change a rigid body and how to read the resulting poses.',
    ['Initial state', 'rigid body + geometry + gravity', 'Define which objects can move and how they contact.'],
    ['Solve contacts', 'collision candidates → contact response', 'Advance motion with the step size and material parameters.'],
    ['Read the body state', 'physx-poses.npy', 'Compare positions at matching times.'],
  ], [
    '중력과 접촉이 강체를 어떻게 움직이고, 그 결과가 좌표로 어떻게 기록되는지 봅니다.',
    ['초기 상태', '강체 + 충돌 형상 + 중력', '어떤 물체가 움직이고 어디에 닿을지 설정합니다.'],
    ['접촉 계산', '충돌 후보 → 접촉 반응', '시간 간격과 물리 재질을 반영해 물체를 움직입니다.'],
    ['강체 상태 읽기', 'physx-poses.npy', '같은 시점의 물체 좌표를 골라 비교합니다.'],
  ]),
  guide('nvidia-warp', 'simulation', ['release', ...referenceSections], 'Warp', [
    'Follow particle arrays from a Python launch through CUDA kernels to simulation and viewer outputs.',
    ['Prepare arrays', 'particle positions + velocities', 'Store one position and velocity per particle.'],
    ['Launch GPU kernels', 'spatial grid → contacts → integration', 'Find nearby particles and compute the next state.'],
    ['Measure and draw', 'full arrays + sampled viewport', 'The viewer draws a subset and the script reports all-particle statistics.'],
  ], [
    'Python에서 준비한 입자 배열이 GPU 커널로 들어가고, 계산 결과를 뷰어와 검사 코드가 읽는 과정을 봅니다.',
    ['입자 배열 준비', '입자 위치 + 속도', '입자마다 위치와 속도를 저장합니다.'],
    ['GPU 커널 실행', '공간 격자 → 접촉 → 상태 갱신', '가까운 입자를 찾아 다음 상태를 계산합니다.'],
    ['측정과 화면 출력', '전체 배열 + 표시용 표본', '뷰어는 일부를 그리고 검사 코드는 전체 입자의 통계를 구합니다.'],
  ]),
  guide('curobo', 'robotics', pipelineSections, 'cuRobo', [
    'Compare how a fixed target and a changed obstacle produce different joint trajectories.',
    ['Specify the problem', 'start joints + target pose + world geometry', 'Fix the target and choose which obstacles to include.'],
    ['Optimize a motion', 'kinematics + collision checks → waypoints', 'Find joint states that reach the goal and clear the obstacle.'],
    ['Verify in saved data', 'motion.npz · result.json', 'Read the planned joints separately from tool-center coordinates.'],
  ], [
    '같은 목표에서 장애물 배치에 따라 관절 경로가 어떻게 달라지는지 봅니다.',
    ['계획 문제 정의', '시작 관절 + 목표 자세 + 장애물 형상', '목표를 고정하고 장애물 배치를 정합니다.'],
    ['동작 계획', '기구학과 충돌 검사 → 중간 자세', '목표까지 닿고 도중에 장애물을 피하는 자세를 찾습니다.'],
    ['저장된 경로 검사', 'motion.npz · result.json', '관절 값과 로봇 팔 끝의 좌표를 각각 읽습니다.'],
  ]),
  guide('isaac-lab-arena', 'robotics', referenceSections, 'Isaac Lab-Arena', [
    'Follow one robot policy episode through task setup, policy adaptation, and milestone scoring.',
    ['Compose a task', 'scene + embodiment + task criteria', 'Specify objects, the robot, and how the task completes.'],
    ['Execute the policy', 'observations → policy adapter → actions', 'Arena connects the model and simulated robot for evaluation.'],
    ['Read the episode', 'progress.events + success', 'Check lift and stable placement by reading independent events.'],
  ], [
    '로봇 평가에서 과제를 구성하고 모델을 실행한 뒤 에피소드의 성공 여부를 판정하는 과정을 봅니다.',
    ['과제 구성', '장면 + 로봇 + 판정 조건', '물체, 로봇, 과제 완료 조건을 지정합니다.'],
    ['정책 실행', '관측 → 정책 어댑터 → 행동', 'Arena가 모델과 가상 로봇을 연결해 평가를 진행합니다.'],
    ['에피소드 읽기', 'progress.events + success', '들기와 안정적으로 놓기를 기록에서 따로 확인합니다.'],
  ]),
  guide('cosmos-rl', 'world-models', ['architecture', 'example', 'verification', 'license', 'official-sources', 'related-tools'], 'Cosmos RL', [
    'See how the rollout and trainer roles exchange scored experience in AlpaGym.',
    ['Request experience', 'scene/start + rollout settings', 'The trainer requests candidate runs for the training problem.'],
    ['Collect and score', 'policy actions + environment → reward', 'A rollout worker gathers the episode and its score.'],
    ['Update the policy', 'scored experience → training step', 'The trainer updates policy weights and logs the result.'],
  ], [
    'AlpaGym에서 경험 수집 프로세스와 학습 프로세스가 주행 기록과 보상을 어떻게 주고받는지 봅니다.',
    ['경험 요청', '장면·시작 조건 + 롤아웃 설정', '학습에 사용할 주행을 실행하도록 요청합니다.'],
    ['주행과 보상 계산', '정책 행동 + 환경 → 보상', '롤아웃 워커가 에피소드와 평가 점수를 모읍니다.'],
    ['정책 갱신', '점수가 붙은 경험 → 학습 스텝', '학습 프로세스가 가중치를 갱신하고 결과를 기록합니다.'],
  ]),
];
