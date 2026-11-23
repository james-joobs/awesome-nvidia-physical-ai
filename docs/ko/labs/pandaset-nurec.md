# 실사 도로를 복원하고 Volvo를 중심으로 둘러보기

**RGB + LiDAR 비교 실험입니다.** 외부 센서 정보 없이 사진에서 카메라를 추정하고 마우스로 조작하는 새 실습은 [RGB 전용 도로 복원](rgb-reality-view.md)을 보세요.

[실습 목록](../../../labs/README.ko.md) · [English](../../en/labs/pandaset-nurec.md)

실제 주행 중 촬영한 사진과 LiDAR로 도로를 복원한 뒤, 내 차를 따라가는 시점으로 살펴봅니다. 주변 환경은 PandaSet 실측 데이터로 NuRec이 복원하고, 자차 위치에는 **Volvo S90 Recharge**의 상세 3D 모델을 배치합니다. GPU가 없어도 저장된 영상과 데이터부터 확인할 수 있습니다.

## 동작 원리

### 1. 사진만 있으면 다른 시점에서도 볼 수 있을까?

```text
실제 카메라 6대의 RGB + 카메라 정보·시각별 위치
                         + LiDAR 실측 XYZ
                                ↓
                  NCore V4 데이터 + 색을 입힌 초기 점군
                                ↓ NuRec 학습
                         3D Gaussian / USDZ
                                ↓ 새 카메라 위치와 K
                           다른 시점의 RGB
                                ↓ 선택적으로 Harmonizer
                      보정된 영상 + Volvo 차량 레이어
```

사진은 픽셀의 색만 저장합니다. 다른 위치에서 보려면 카메라가 어디에 있었는지, 픽셀이 공간의 어느 방향을 가리키는지, 물체가 얼마나 떨어져 있는지를 알아야 합니다. 이 예제는 시뮬레이터의 가상 깊이 대신 **실제로 측정한 LiDAR와 카메라 위치**를 사용합니다.

원래 1920×1080 사진을 1024×576으로 줄이면 RGB 데이터는 `uint8[576,1024,3]` 배열이 됩니다. 각 픽셀에 빨강·초록·파랑 값이 0–255로 들어 있습니다. 사진을 줄일 때 카메라 행렬도 같은 비율로 바꿉니다. 전방 카메라의 실제 값은 다음과 같습니다.

```text
K = [[1050.674,    0,     517.333],
     [   0,    1050.672,  257.759],
     [   0,       0,        1   ]]
```

`fx/fy`는 픽셀 단위 초점거리, `cx/cy`는 광학 중심입니다. 여기에 촬영 시각과 **4×4 카메라→월드 변환 행렬**을 붙여 사진을 실제 공간에 배치합니다. 카메라는 오른쪽·아래·앞 방향을 쓰고, 자차 좌표는 앞·왼쪽·위 방향을 씁니다. 위치의 단위는 미터입니다.

LiDAR 한 프레임은 `x,y,z,i,t,d` 열이 있는 표입니다. 차례로 공간 좌표, 반사 강도, 측정 시각, 센서 식별자를 뜻합니다. 실제 0번 프레임의 한 점은 `[-58.4572,-61.2693,2.8810]`m입니다. 이 데이터의 XYZ는 **이미 월드 좌표**입니다. 센서→월드 변환을 한 번 더 적용하면 위치가 잘못됩니다. [공식 좌표 투영 코드](https://github.com/scaleapi/pandaset-devkit/blob/master/python/pandaset/geometry.py)를 기준으로 카메라 역변환과 K를 적용해 RGB 색을 가져옵니다.

여섯 카메라에서 2–77번 프레임, **사진 456장**을 준비했습니다. NuRec은 8번째마다 검사 이미지로 남깁니다. 검사 프레임과 다른 LiDAR 19개 스캔으로 **Gaussian 320,000개**를 초기화합니다. 카메라마다 노출 시각이 달라 자차 위치를 시간에 맞게 보간한 다음 고정 카메라 위치를 추정했습니다. 실제 데이터와의 최대 차이는 1.44cm·0.131° 이내이며, 카메라별 기록을 남겼습니다.

### 2. 화면에서 무엇이 실사이고 무엇이 추가된 모델일까?

도로·건물·주변 차량은 PandaSet의 실제 사진과 LiDAR에서 왔습니다. NuRec은 이 관측에 맞춰 Gaussian의 위치·모양·색·불투명도를 조정합니다. 높은 시점과 사선 시점은 카메라를 옮겨 **새로 렌더링한 영상**입니다. 원본 영상을 그대로 재생한 화면과는 다릅니다. 추가 카메라는 `fx=fy=512`, 수평 화각 90°의 pinhole 카메라를 사용합니다.

흰색 **Volvo S90 Recharge**는 [lazercar가 제작한 상세 메시](https://sketchfab.com/3d-models/volvo-s90-recharge-free-9462b07c10244fd4a28d86846dc9e3a9)입니다. 차체·유리·휠·실내를 실제 3D 형상으로 렌더링했습니다. 도로를 촬영한 원래 차가 Volvo였다는 뜻은 아닙니다. 같은 카메라 위치로 차량을 따로 렌더링하고, LiDAR로 구한 도로 평면에 바닥을 맞춘 뒤 접촉 그림자를 더합니다. 마지막에 차량의 투명 배경 레이어를 합성합니다. 차량 자체는 Harmonizer의 보정 대상에 넣지 않습니다. 차량 레이어는 macOS의 Blender 4.5.1·Cycles CPU로 렌더링했고, NuRec과 Harmonizer는 Linux GPU 머신에서 실행했습니다.

### 3. 왜 일부 도로와 주변 차가 번져 보일까?

이 첫 예제는 **정적 장면 복원**입니다. 움직이는 차를 별도 추적해 동적 객체로 학습하지 않았으므로 잔상이나 겹침이 생길 수 있습니다. 원래 카메라에서 가려졌던 면을 새 시점에서 보면 빈틈도 드러납니다. Harmonizer는 프레임별로 보정하며, 차선 모양을 바꾸거나 깜빡임을 만들 수도 있습니다. **Built on NVIDIA Cosmos.**

Volvo는 자차 위치를 알려주는 표시용 모델입니다. 기록된 자차 위치를 따라가며, 바퀴 회전·상황별 조명·다른 물체와의 깊이 차이에 따른 가림 처리는 구현하지 않았습니다. Volvo 제어기나 타이어 물리를 검증한 것도 아닙니다. 이 실사 장면에 Alpamayo를 연결해 추론하거나 폐루프 주행을 수행했다는 주장은 하지 않습니다. 모델의 실제 입출력은 [별도의 합성 도로 실습](reality-view.md)에서 확인할 수 있습니다.

## 따라 하기

### 1. 저장된 결과부터 확인하기

[차량 중심 영상](../../../labs/pandaset-nurec/evidence/pandaset-nurec.ko.mp4), [Volvo 사선 시점](../../../labs/pandaset-nurec/evidence/volvo-quarter.mp4), [차량 레이어를 넣기 전 NuRec](../../../labs/pandaset-nurec/evidence/nurec-quarter.mp4)을 열어보세요. [결과 폴더](../../../labs/pandaset-nurec/evidence)에는 같은 프레임의 보정 전후 이미지와 검사 기록도 있습니다.

레포 폴더에서 터미널을 열고 아래 한 줄을 실행하면 GPU 없이 파일을 검사합니다.

```bash
python3 labs/pandaset-nurec/check.py
```

FFmpeg가 있으면 끝에 `--decode-video`를 붙여 모든 영상의 전체 프레임을 디코딩할 수 있습니다.

### 2. 사용할 데이터와 출력 폴더 준비하기

먼저 [데이터·차량 모델 사용 조건](../../../labs/pandaset-nurec/SOURCES.md)을 확인합니다. 원본 데이터 파일은 **CC BY 4.0 + PandaSet 추가 약관**을 담고 있지만 Scale의 Nucleus 안내는 CC BY-SA 4.0으로 표기합니다. 이 차이를 숨기지 않고 원본 약관을 보존하며, 새로 만든 데모 영상에는 CC BY-SA 4.0을 적용했습니다. 원본 약관도 함께 적용됩니다. 원래 배포 서버가 열리지 않아 **버전을 고정한 비공식 커뮤니티 미러**에서 가져옵니다. NVIDIA 데이터셋이나 공식 미러가 아닙니다.

직접 학습하려면 GPU를 사용할 수 있는 Linux와 Docker가 필요합니다. 이 예제는 **RTX 5090 32GB, 시스템 RAM 약 32GB**에서 실행했습니다. 여유 디스크는 15GB 이상을 준비하고, 차량 원본까지 받으면 압축 해제용 공간이 약 3GB 더 필요합니다. GPU가 보이지 않으면 [NVIDIA 머신 환경 설정](../onboarding/nvidia-linux.md)부터 진행하세요.

아래 명령은 저장 위치를 정하고 실행 환경과 장면 하나를 받습니다. 각 줄이 끝나면 다음 줄을 입력합니다.

```bash
export PANDASET_ROOT="$HOME/physical-ai-labs/pandaset-road"
mkdir -p "$PANDASET_ROOT"
nvidia-smi
docker pull nvcr.io/nvidia/nre/nre-ga:26.04
bash labs/pandaset-nurec/run.sh download
```

전체 44.5GB를 받지 않고, ZIP의 파일 목록과 001번 장면의 약 416MiB 구간만 받습니다. 파일마다 ZIP CRC와 크기를 검사하고 SHA-256을 기록합니다. 부분 다운로드이므로 **전체 ZIP의 SHA-256을 검증한 것은 아닙니다.** `data/001/LICENSE.txt`도 보존합니다.

### 3. 실사 장면 학습하고 시점 세 개 만들기

```bash
bash labs/pandaset-nurec/run.sh prepare
bash labs/pandaset-nurec/run.sh train
bash labs/pandaset-nurec/run.sh render
```

`prepare`는 카메라 정보와 사진을 NCore로 묶고 실측 LiDAR 초기 점군과 `ground-plane.json`을 만듭니다. 네트워크를 끄고 이 실습 폴더만 연결한 컨테이너에서, 허용한 생성자만 읽는 방식으로 원본 pickle을 처리합니다. `train`은 NuRec을 6,000회 최적화합니다. `render`는 `renders/front`, `renders/ego-elevated`, `renders/ego-quarter` 아래에 **각각 PNG 76장**을 저장합니다. 확인한 26.04 컨테이너와 `gsplat` 렌더러를 사용합니다.

선택적으로 보정하려면 [공식 Harmonizer 모델](https://huggingface.co/nvidia/Harmonizer)의 NVIDIA Open Model License를 확인한 뒤 `20ca33d4612b1e98e0526b3a7ee604af5b289f58` 버전의 `harmonizer_nontemporal.pt`를 받습니다. 파일이 있는 폴더를 지정하세요.

```bash
export HARMONIZER_WEIGHTS="/absolute/path/to/Harmonizer"
bash labs/pandaset-nurec/run.sh enhance
```

### 4. Volvo 상세 모델 넣기

[제작자의 원본 페이지](https://sketchfab.com/3d-models/volvo-s90-recharge-free-9462b07c10244fd4a28d86846dc9e3a9)에 안내된 **Google Drive 다운로드 링크**로 Blender 파일을 받고 압축을 풉니다. 파일 크기·SHA-256·출처는 [차량 모델 기록](../../../labs/reality-view/ego-car.json)에 있습니다. 1.2GB 원본 ZIP은 Git에 넣지 않습니다.

Blender 4.5가 설치되어 있다면, 아래 두 경로를 압축을 푼 실제 위치로 바꿔 실행하세요.

```bash
export VOLVO_BLEND="/absolute/path/to/Volvo S90.blend"
export VOLVO_TEXTURES="/absolute/path/to/textures"
blender --background --disable-autoexec "$VOLVO_BLEND" \
  --python labs/reality-view/render_ego_car.py -- \
  --textures "$VOLVO_TEXTURES" --views "$PANDASET_ROOT/ego-views.json" \
  --ground-plane "$PANDASET_ROOT/ground-plane.json" \
  --output "$PANDASET_ROOT/vehicle-layers"
```

`--disable-autoexec`는 내려받은 `.blend` 안의 스크립트가 자동으로 실행되지 않게 합니다. 시점별로 차량만 있는 PNG와 그림자가 있는 PNG를 따로 만듭니다. 영상 구성 단계에서는 그림자 강도를 22%로 낮춥니다. 보기 좋게 합성하기 위한 조정이며 실제 사진의 조명을 측정해 재현한 것은 아닙니다. [영상 구성 코드](../../../labs/pandaset-nurec/package.py)는 이 레이어를 같은 카메라의 NuRec 결과에 합성하고 출처가 있는 MP4를 만듭니다.

완료한 결과를 영상으로 저장하려면 Pillow와 FFmpeg를 설치한 뒤, 한글을 지원하는 폰트 경로를 지정해 실행합니다.

```bash
python3 labs/pandaset-nurec/package.py --input "$PANDASET_ROOT" \
  --output "$PANDASET_ROOT/published" \
  --font "/absolute/path/to/NotoSansKR.ttf"
```


## 결과 확인

저장된 실행은 **사진 456장, Gaussian 초기값 320,000개, NuRec 6,000단계**를 사용했습니다. NuRec이 기록한 순수 학습 시간은 **100.80초**이며 다운로드·변환·렌더링 시간은 제외합니다. USDZ는 **110,694,637바이트**입니다. 이 작은 예제의 시간이나 화질을 다른 복원 방법과 비교한 벤치마크로 해석하면 안 됩니다.

```bash
python3 labs/pandaset-nurec/check.py --decode-video
```

이 검사로 프레임 수, 카메라 변환, 파일 해시, 영상 손상 여부를 확인할 수 있습니다. 원래 카메라 사진과 NuRec의 같은 시점부터 비교한 다음, 새 시점의 보정 전후를 살펴보세요. 차선이 매끄러워졌더라도 원래 차선과 더 가까워졌다고 단정할 수는 없습니다. 높은 카메라 위치의 정답 사진이 없으므로 새 시점의 정확도 점수를 만들어내지 않았습니다.

결과를 옮길 때는 [PandaSet 약관과 제작자 표시](../../../labs/pandaset-nurec/SOURCES.md)도 함께 보존합니다. 이 예제는 실측 주변 환경을 복원하는 과정이며, 차량 제어 성능을 확인한 결과가 아닙니다.
