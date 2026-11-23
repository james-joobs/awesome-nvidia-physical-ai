# RGB 카메라만으로 도로를 복원하고 자유 시점으로 보기

[실습 목록](../../../labs/README.ko.md) · [English](../../en/labs/rgb-reality-view.md)

카메라로 찍은 도로를 하나의 3D 장면으로 복원한 뒤, Volvo S90 주변을 마우스로 돌려봅니다. 먼저 뷰어와 조작 영상을 살펴보고, RTX 5090 한 장으로 같은 과정을 실행해 보세요. **입력은 RGB 픽셀뿐**이며 카메라 정보와 촬영 위치, 3D 점을 모두 사진에서 추정합니다.

## 동작 원리

![RGB 사진에서 COLMAP으로 카메라와 3D 점을 추정하고 NVIDIA 3DGUT으로 학습한 뒤 Spark에서 Volvo와 함께 다른 시점으로 보는 흐름](../../../assets/lessons/rgb-reality-view/pipeline.ko.svg)

### 1. 사진에서 어떻게 3D 위치를 찾을까?

사진 한 장의 픽셀은 색을 알려주지만, 그 물체까지의 거리는 바로 알려주지 않습니다. COLMAP은 겹쳐 찍힌 사진에서 같은 무늬나 모서리 같은 **특징점**을 찾습니다. 여러 사진의 특징점이 같은 공간의 점을 가리키도록 카메라 위치와 3D 점을 함께 추정합니다. 그 점을 다시 사진에 투영했을 때 관측한 위치와 가까워지도록 다듬는 과정이 bundle adjustment입니다.

이 예제는 여섯 방향 카메라의 **RGB 사진 162장**을 사용합니다. 사진은 가로 최대 1024픽셀로 줄이고 원래 EXIF를 제거합니다. 데이터셋이 제공하는 카메라 K, 촬영 위치, 깊이, GPS, IMU, LiDAR는 입력에 넣지 않습니다. 예제 다운로더도 카메라 JPEG와 원본 약관만 선택해서 받습니다.

```text
RGB 사진:             uint8[높이,너비,3]
사진 사이 특징점:      같은 점으로 추정한 픽셀 좌표 쌍
추정한 카메라 K:       float[3,3]
추정한 카메라 자세:    float[4,4]
삼각측량한 희소 점군:  float[N,3] + RGB
```

K에는 픽셀 단위 초점거리와 광학 중심이 들어 있습니다. 자세 행렬은 카메라의 위치와 방향을 표현합니다. 카메라는 오른쪽·아래·앞을 기준으로 하고, 뷰어는 복원한 도로가 위쪽 Z축을 향하도록 정렬합니다. 실제 값은 [cameras.json](../../../labs/rgb-reality-view/evidence/cameras.json)에서 볼 수 있습니다.

실행 예제에서는 **162장 모두를 연결**하고 약 **2만 9천 개의 3D 점**을 찾았습니다. 재투영 오차는 사진 속 특징점이 얼마나 잘 맞는지를 나타냅니다. 실제 도로 좌표를 센티미터 단위로 측정했다는 뜻은 아닙니다. 촬영 위치도 정답 좌표를 복사한 값이 아니라 RGB에서 추정한 결과입니다.

아래는 실제로 추정한 정면 카메라 한 프레임입니다. `K`는 픽셀 단위이고 `camera_position`은 뷰어의 상대 단위입니다. x·y가 거의 0인 것은 중간 촬영 위치를 화면 원점으로 삼았기 때문이며 GPS 값이 아닙니다. 높이 0.9482는 카메라 높이의 중앙값을 1로 맞춘 상대값입니다.

```json
{
  "image": "front_camera/39.jpg",
  "time_seconds": 3.9,
  "K": [
    [
      1055.495,
      0.0,
      512.0
    ],
    [
      0.0,
      1056.31,
      284.5
    ],
    [
      0.0,
      0.0,
      1.0
    ]
  ],
  "image_size": [
    1024,
    569
  ],
  "camera_position": [
    -0.0,
    0.0,
    0.9482
  ]
}
```

### 2. NVIDIA 3DGUT은 무엇을 학습할까?

NVIDIA가 공개한 [3DGRUT](https://github.com/nv-tlabs/3dgrut)에서 3DGUT 렌더러와 학습 코드를 사용합니다. COLMAP 점군을 초기값으로 삼아 색과 불투명도를 가진 작은 3D 타원체, **Gaussian**을 배치합니다. 이 타원체를 카메라에서 보았을 때 원래 사진과 비슷해지도록 위치·크기·회전·색을 조정합니다.

이 설정은 **16,000단계**를 학습하고 **Gaussian 400,000개**를 유지합니다. 전체 PLY에는 3차 spherical harmonics 색 계수가 들어 있습니다. 브라우저용 SPZ는 Gaussian을 모두 유지하고 색 계수를 1차로 줄여 약 7.8MB로 압축했습니다. 여러 각도의 영상을 미리 저장해 둔 파일이 아니라 **계속 다른 시점에서 그릴 수 있는 3D 장면**입니다. 사전학습 깊이 모델이나 승인이 필요한 모델 가중치를 받는 단계는 없습니다.

카메라 위치를 추정할 때는 모든 사진을 씁니다. 3DGRUT 내부에는 사진을 나누는 학습·검사 설정이 있지만, 이 예제를 독립적인 새 시점 정확도 벤치마크로 해석하면 안 됩니다. 움직이는 차도 하나의 정적 장면에 들어가므로 잔상이나 늘어난 형상이 생깁니다. 가려졌거나 촬영하지 못한 면은 불완전할 수 있습니다.

### 3. 마우스를 움직이면 무엇이 바뀔까?

[Spark](https://github.com/sparkjsdev/spark)가 같은 Gaussian 장면을 현재 브라우저 카메라에서 투영해 그립니다. 드래그하면 카메라가 회전하고, 확대하면 대상과의 거리가 달라집니다. 옆으로 이동하면 가까운 물체와 먼 물체의 움직임 차이인 시차도 나타납니다. 화면은 매번 같은 3D 데이터에서 렌더링됩니다.

**Volvo S90 Recharge**는 [lazercar의 실제 차량 메시](https://sketchfab.com/3d-models/volvo-s90-recharge-free-9462b07c10244fd4a28d86846dc9e3a9)를 약 1MB GLB로 단순화한 것입니다. CC BY 4.0에 따라 출처와 수정 내용을 표시했습니다. 차체도 3D여서 보는 방향에 따라 옆면·앞면·뒷면이 달라집니다. 원래 촬영한 차종을 뜻하지는 않습니다. 위치를 알기 쉽게 전경에 따로 그리는 참조 모델이며, 주변 물체와의 정확한 가림이나 차량 동역학을 검증한 결과는 아닙니다.

경로 슬라이더는 **COLMAP이 추정한 카메라 이동**을 따라갑니다. 주행 정책이 새 경로를 계획하거나 조향 명령을 보내는 단계가 아닙니다. ‘운전자’를 누르면 참조 차량을 숨기고, 추정한 전방 카메라의 위치와 화각으로 전환합니다.

외부 크기 기준이 없는 RGB 복원에는 전체 크기가 정해지지 않는 문제가 있습니다. 뷰어는 추정한 카메라와 도로 사이 높이를 1로 맞추고 차량을 상대 비율로 배치합니다. 도로 평면도 **RGB 특징점으로 만든 3D 점**에서 추정합니다. 화면의 단위는 실측 미터가 아닙니다.

## 따라 하기

### 1. NVIDIA GPU 없이 저장된 결과 보기

이 페이지의 3D 뷰어나 [한국어 조작 영상](../../../labs/rgb-reality-view/evidence/rgb-reality-view.ko.mp4)을 열어보세요. 회전·확대·이동, 운전자 시점, 경로 재생을 확인할 수 있습니다. 3D에는 WebGL2를 지원하는 브라우저가 필요합니다. MP4 재생과 결과 파일 검사에는 NVIDIA GPU가 필요하지 않습니다.

```bash
python3 labs/rgb-reality-view/check.py
```

RGB 전용 입력 기록, Gaussian 개수, 좌표 변환, 실제 마우스 조작 기록과 파일 해시를 검사합니다. FFmpeg가 있으면 `--decode-video`를 붙여 두 영상의 전체 프레임도 읽어볼 수 있습니다.

학습 없이 저장된 3D 장면부터 열 수도 있습니다. 저장소 폴더에서 아래 명령을 실행하고 **http://127.0.0.1:8090/**에 접속하세요. 뷰어가 지정된 버전의 공개 JavaScript 모듈을 불러오므로 인터넷 연결이 필요합니다.

```bash
python3 labs/rgb-reality-view/serve.py --root site/public/showcase/rgb-reality-view
```

### 2. GPU 머신 준비하기

검증한 환경은 **Linux x86_64, RTX 5090 32GB 한 장, 시스템 RAM 약 32GB**입니다. NVIDIA 드라이버, CUDA **12.8 또는 12.9** 개발 도구, Python, C++ 컴파일러, `uv`, Git, Node.js/npm을 준비합니다. 설치 스크립트는 별도 Python 환경을 만들고 compute capability 12.0용 확장을 빌드합니다. 시스템 CUDA나 다른 서비스를 교체하지 않습니다.

처음이라면 [NVIDIA 머신 환경 설정](../onboarding/nvidia-linux.md)과 [uv 공식 설치 안내](https://docs.astral.sh/uv/getting-started/installation/)부터 확인하세요. 레포 폴더에서 터미널을 열고 각 줄이 끝나면 다음 줄을 입력합니다.

```bash
nvidia-smi
export RGB_VIEW_ROOT="$HOME/physical-ai-labs/rgb-road"
python3 labs/rgb-reality-view/pipeline.py --root "$RGB_VIEW_ROOT" setup
```

처음에는 몇 GB의 패키지를 받고 C++·CUDA 확장을 컴파일합니다. 핵심 패키지 버전과 소스 커밋은 고정했습니다. CUDA가 여러 개 있으면 호환되는 12.8/12.9 폴더를 고릅니다. 직접 지정하려면 명령에 `--cuda-home /path/to/cuda-12.9`를 추가하세요. 터미널에서 먼저 잡히는 오래된 `nvcc`와 실제 사용할 개발 도구가 다를 수 있습니다.

### 3. 공개 RGB 예제 복원하기

[데이터·차량 모델의 출처와 사용 조건](../../../labs/rgb-reality-view/SOURCES.md)을 먼저 확인합니다. 예제는 고정된 **비공식 커뮤니티 미러**의 PandaSet 001번 장면입니다. 원본 파일의 약관과 CC BY-SA로 표기한 제작사 안내의 차이를 보존했습니다. 새 장면·영상에는 CC BY-SA 4.0과 원래 데이터 약관을 적용하며, 코드의 MIT 라이선스와 구분합니다.

전체 과정을 이어서 실행하려면 다음 한 줄을 사용합니다.

```bash
python3 labs/rgb-reality-view/pipeline.py --root "$RGB_VIEW_ROOT" all
```

각 단계의 출력을 먼저 확인하려면 나눠서 실행할 수도 있습니다.

```bash
python3 labs/rgb-reality-view/pipeline.py --root "$RGB_VIEW_ROOT" example
python3 labs/rgb-reality-view/pipeline.py --root "$RGB_VIEW_ROOT" sfm
python3 labs/rgb-reality-view/pipeline.py --root "$RGB_VIEW_ROOT" train
python3 labs/rgb-reality-view/pipeline.py --root "$RGB_VIEW_ROOT" export
python3 labs/rgb-reality-view/pipeline.py --root "$RGB_VIEW_ROOT" serve
```

실행한 머신에서 **http://127.0.0.1:8090/** 를 엽니다. 원격 GPU 머신을 쓴다면 내 컴퓨터에서 `ssh -L 8090:127.0.0.1:8090 your-gpu-host`로 포트를 연결한 뒤 같은 주소를 여세요. `your-gpu-host`는 자신이 사용하는 SSH 별칭으로 바꿉니다.

| 단계 | 생성되는 파일 | 확인할 내용 |
| --- | --- | --- |
| RGB 예제 받기 / 내 영상 준비 | `work/images/`, `input-manifest.json` | JPEG만 있는지, 제공된 카메라 정보나 센서 데이터가 없는지 |
| COLMAP 복원 | `sfm-result.json`, `sfm-selected/`, `undistorted/sparse/0/` | 선택한 장면과 왜곡 보정 후의 연결 이미지 수가 같은지 |
| 3DGUT 학습 | `training-result.json`, `train/.../export_last.ply` | 완료 단계 수, 실제 시간, 측정한 GPU 메모리 |
| 뷰어 내보내기 | `viewer/road.spz`, `cameras.json`, `volvo-s90.glb` | 하나의 3D 장면, RGB에서 추정한 카메라 경로, 별도 차량 메시 |

다른 촬영본은 새 출력 폴더에서 시작합니다. 다른 실습의 점군을 이 폴더에 덮어쓰지 마세요. 입력 검사는 이미지 폴더에 다른 파일이 섞였거나 파일이 바뀌었을 때, 또는 기록에 RGB 이외의 센서를 사용했다고 표시되었을 때 실행을 중단합니다.

### 4. 내가 찍은 RGB 영상으로 실행하기

RGB 영상 하나를 넣으면 FFmpeg로 프레임을 추출하고 같은 복원 과정을 진행합니다. 서로 겹치는 장면과 카메라의 이동이 있어야 합니다. 제자리 회전만 있거나 무늬가 거의 없는 표면은 3D 위치를 찾기 어렵습니다.

```bash
python3 labs/rgb-reality-view/pipeline.py \
  --root "$HOME/physical-ai-labs/my-road" \
  --video "/absolute/path/to/road.mp4" --sample-fps 3 all
```

주변을 보는 여러 RGB 카메라가 있다면 카메라별 폴더로 이미지를 나눠 `--input /path/to/rgb-folders --front-folder front_camera all`을 사용합니다. 폴더 이름으로 같은 렌즈의 이미지를 묶으며 외부 보정값은 요구하지 않습니다. 전방 카메라 하나로는 실제로 본 영역을 복원할 수 있습니다. 뒤쪽이나 가려진 면을 보려면 그 부분을 담은 관측이 더 필요합니다.

## 결과 확인

기록한 예제는 **RGB 162장, RTX 5090 한 장, 학습 16,000단계, Gaussian 400,000개**를 사용했습니다. 사진 매칭과 촬영 위치 추정은 약 1분, 기준 실행의 학습 루프는 약 2분 걸렸습니다. 설치·첫 컴파일·압축·브라우저 로딩 시간은 별도입니다. 정확한 측정값과 범위는 [실행 기록](../../../labs/rgb-reality-view/recorded.json)에 있습니다.

```bash
python3 labs/rgb-reality-view/check.py --decode-video
```

마우스 조작 전후의 카메라 위치도 저장했습니다. 실제 드래그로 3D 카메라가 바뀌었는지, 경로 재생으로 추정 프레임이 이동했는지 확인합니다. 복원과 학습은 NVIDIA GPU 한 장에서 실행하고, 뷰어는 보고 있는 브라우저에서 렌더링합니다.

이 실습은 **RGB 클립을 미리 복원한 뒤 자유 시점으로 보는 파이프라인**입니다. 실차의 실시간 인지나 폐루프 자율주행을 구현한 결과와는 구분합니다. 카메라만으로 기하 구조를 찾고, 신경 렌더링으로 표현하고, 자차 중심으로 살펴보는 과정을 직접 재현하는 데 초점을 둡니다.
