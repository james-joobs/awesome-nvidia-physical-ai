# RGB만으로 NuRec, Harmonizer, Alpamayo 연결하기

[실습 목록](../../../labs/README.ko.md) · [English](../../en/labs/nurec-rgb-reality.md)

실사 도로를 **NuRec**에서 복원하고, 같은 시점의 렌더링에 **Harmonizer**를 적용해 비교합니다. 여기에 **Alpamayo 2 Edge**의 예측 경로와 원본 카메라의 객체 인식 결과를 연결합니다. 복원 입력은 RGB 픽셀뿐입니다. 먼저 저장된 장면과 영상을 둘러보고 RTX 5090 한 장으로 각 단계를 따라 해 보세요.

## 동작 원리

![RGB로 카메라와 장면을 추정해 NuRec에 입력하고, NuRec 렌더링은 Harmonizer로 보정하며, 원본 RGB와 추정 주행 이력은 Alpamayo로 전달하는 흐름](../../../assets/lessons/nurec-rgb-reality/pipeline.ko.svg)

### 1. 이번 실습에서 실제로 실행하는 도구

| 단계 | 실제 입력 → 출력 | 담당하는 일 |
| --- | --- | --- |
| COLMAP | RGB 사진 162장 → 카메라 보정값·자세·희소 3D 점 | 사진의 특징점을 맞춰 카메라와 기하 구조를 추정합니다. |
| Rig bundle adjustment | 사진별 추정치 → 카메라 6대·촬영 시점 27개의 고정 배열 | NuRec 입력 형식에 맞춰 카메라의 상대 위치를 함께 보정합니다. |
| NCore | 추정 카메라·RGB·SfM 점 → NuRec 시퀀스와 Gaussian 초기값 | 데이터를 묶는 형식과 API입니다. 신경망 모델은 아닙니다. |
| NuRec 26.04 | NCore와 RGB 기반 초기값 → 학습 산출물·새 시점 RGB·Gaussian | 실제 NuRec 런타임의 3DGUT COLMAP 구성을 실행합니다. |
| Harmonizer | NuRec의 실제 렌더링 → 같은 시점의 보정 RGB | 공개된 **non-temporal** 체크포인트로 이미지 한 장씩 처리합니다. 3D 모델 자체는 바꾸지 않습니다. |
| Alpamayo 2 Edge | 원본 RGB·추정한 과거 이동·주행 지시 → 시점마다 미래 자세 64개 | 실제 VLA 모델을 실행하고 예측을 표시합니다. 제어 명령은 적용하지 않습니다. |
| Mask R-CNN | 원본 RGB → 종류·점수·검출 박스·객체별 마스크 | Alpamayo나 보정 영상과 독립적으로 주변 차량과 사람을 인식합니다. |

[독립 실행형 3DGUT 실습](rgb-reality-view.md)은 비교 자료로 유지합니다. 여기서도 NuRec 내부의 3DGUT 구성을 쓰지만, **NuRec의 데이터 입력·학습·렌더링·내보내기를 실제 호출**한다는 점이 다릅니다. 독립 실행형 학습 결과를 NuRec 실행 결과로 바꿔 부르지 않습니다.

### 2. RGB-only로 어디까지 추정할까?

공개 예제에서 받는 파일은 카메라 JPEG와 원래 데이터 이용 조건뿐입니다. COLMAP은 겹쳐 찍힌 사진을 비교해 `K[3,3]`, 카메라 자세 `[4,4]`, 희소 점 `XYZ[N,3]`을 구합니다. LiDAR·외부 깊이·GPS·IMU·제공된 카메라 자세·보정값·센서 시각·객체 정답 라벨은 복원에 사용하지 않습니다.

카메라 폴더와 같은 프레임 번호를 기준으로 **명목상 같은 촬영 시점**을 묶습니다. 이후 카메라 상대 위치, rig의 이동, 3D 점을 함께 조정하고 왜곡 보정한 카메라의 내부 보정값은 고정합니다. 사진별 자유로운 카메라 모델의 재투영 오차는 약 0.875픽셀, 고정 배열 제약을 둔 모델은 약 1.150픽셀입니다. 배열을 고정했다고 이미지 오차가 더 작아지는 것은 아니며, 프레임 번호만으로 정밀한 센서 동기화를 입증하지도 않습니다.

NuRec에는 RGB 관측 162개와 사진에서 삼각측량한 점 약 2만 8,600개를 전달합니다. 이 점군은 **RGB로 추정한 결과**이며 거리 센서로 측정한 값이 아닙니다. NCore에는 rig의 이동, 고정된 카메라 상대 자세, 내부 보정값과 RGB를 저장합니다. LiDAR 데이터와 정답 객체 궤적은 없습니다.

RGB만으로는 실제 길이 단위를 확정할 수 없습니다. 카메라와 도로면 사이 높이의 중앙값을 화면 단위 1로 맞춥니다. 도로면 역시 사진의 특징점으로 추정합니다. 따라서 측량한 도로 지도나 미터 단위 좌표가 아닙니다. 모든 이미지가 SfM에 관여하므로 독립적인 새 시점 정확도 벤치마크로도 해석하지 않습니다.

### 3. NuRec과 Harmonizer는 무엇을 바꿀까?

NuRec은 Gaussian의 위치·회전·크기·불투명도·방향별 색을 조정합니다. 새 카메라에서 같은 Gaussian을 그리면 다른 시점의 RGB를 얻습니다. 저장된 실행은 16,000단계를 학습했습니다. 실제 시간과 모델 식별 값, Gaussian 개수는 [recorded.json](../../../labs/nurec-rgb-reality/recorded.json)에 있습니다.

Harmonizer에는 NuRec이 실제 렌더링한 프레임을 값 범위 `[-1,1]`의 `float[1,3,1,576,1024]`로 넣습니다. 비교 영상의 좌우는 **같은 카메라 자세와 프레임 번호**를 사용합니다. 공개된 non-temporal 모델은 각 프레임을 독립적으로 처리하므로 세부 묘사가 바뀌거나 깜박일 수 있습니다. 도로처럼 빈 공간을 채워도 그 부분을 실제로 관측했다는 뜻은 아닙니다. **Built on NVIDIA Cosmos.**

브라우저에서는 NuRec의 공식 `export-gaussian-plys` 출력물을 SPZ로 압축해 Spark/Three.js로 그립니다. Gaussian은 유지하고 방향별 색은 degree 1로 줄입니다. 따라서 **NuRec 학습 결과의 브라우저용 미리보기**이며, 압축과 렌더러 차이로 NuRec 원본 렌더링과 조금 다를 수 있습니다. 마우스를 움직일 때마다 Harmonizer를 실행한다고 설명하지 않습니다. NuRec 원본과 Harmonizer의 실제 출력은 별도 비교 영상으로 확인합니다.

### 4. Alpamayo 경로는 어디서 나올까?

Alpamayo에는 보정 영상이 아닌 원본 카메라 픽셀을 넣습니다. 실제 RGB 스트림 네 개에서 모델용 여섯 뷰를 만듭니다. 왼쪽·정면·오른쪽은 원래 화면을 사용하고, 후면 사진에서 좌우 하위 뷰 두 개를, 정면에서 망원에 해당하는 뷰를 잘라 만듭니다. 모든 샘플링 광선은 실제 이미지 안에 머뭅니다.

이것은 **카메라 배열을 맞추기 위한 명시적인 어댑터**입니다. 모델이 원래 기대하는 화각보다 좁고, 실제 NVIDIA AV 카메라 보정과 같은 구성이 아닙니다. 관측하지 않은 후방 화면을 만들어서 실제 카메라로 표시하지 않습니다.

```text
선택한 RGB 뷰 22개:  uint8[22,1,3,576,1024]
카메라 ID / 명목 시각: int64[22]
과거 위치:           float[1,20,3], 현재의 -1.9초부터 0초까지
과거 회전:           float[1,20,3,3]
주행 지시:           “Continue straight on the road and yield to pedestrians.”
예측 위치:           float[1,1,1,64,3]
예측 회전:           float[1,1,1,64,3,3]
```

과거 자세 20개는 RGB에서 추정한 움직임을 도로면에 투영해 만듭니다. 평면 도로와 yaw 회전을 가정하고, 위치를 평활화한 뒤 10Hz로 보간합니다. 각 입력 이미지는 요청 시각 **이전 또는 같은 시각**에 있는 가장 최근 프레임을 고릅니다. 미래 궤적 정답은 사용하지 않습니다. 다만 카메라 자세는 전체 사진으로 오프라인 복원한 값이므로, 이 실습을 미래 영상에 전혀 접근하지 않는 온라인 인지·주행 시스템으로 해석하지 않습니다.

모델은 미터 단위 주행 이력을 기대합니다. 예제에서는 상대 좌표를 바꾸기 위해 **카메라 높이 1.8m를 가정**합니다. RGB로 실측한 높이가 아니며 이 값을 바꾸면 예측도 달라질 수 있습니다. `--assumed-camera-height-m`으로 가정이 드러나고 교체할 수 있게 했습니다.

2.1·3.9·5.7·7.8초의 네 시점에서 실제 추론합니다. 초록색 점선은 현재 시점에 이미 얻을 수 있는 가장 최근 예측이며 입력 시각과 스케일 가정을 함께 표시합니다. 2.1초 이전에는 미래 시점의 예측을 미리 보여주지 않습니다. 선은 잘 보이게 높이를 조금 올려 그리며 원본 좌표는 그대로 보존합니다. 모델이 생성한 설명도 틀릴 수 있으므로 장면의 검증된 사실로 취급하지 않습니다. 이는 **폐루프 주행이 아닌 개방형 경로 추론**이며 실제 주행 품질 시험은 아닙니다.

### 5. 주변 차량과 사람은 어떻게 보여줄까?

Mask R-CNN은 원본 RGB에서 객체 종류·박스·이진 마스크를 예측합니다. 점수 0.8 이상인 도로 사용자 여섯 종류를 남깁니다. 차량은 청록색, 사람은 노란색, 자전거·이륜차는 보라색입니다. 카메라 패널에서 실제 사진과 예측을 확인하고 표시를 꺼서 원본과 비교할 수 있습니다.

마스크 아래쪽 픽셀에서 나온 광선을 추정한 도로면과 교차시켜 3D 접점을 표시합니다. 화면 가장자리에서 잘렸거나 수평선 근처이거나 너무 먼 객체는 2D 결과만 남깁니다. 표식은 실측한 3D 박스나 물리적 가림 관계가 아닙니다. 임시 ID가 바뀔 수 있고 여러 프레임의 검출 수는 고유한 사람·차량 수와 다릅니다. [마스크와 좌표의 상세 설명](rgb-reality-view.md)도 함께 보세요.

Volvo S90은 출처를 표시한 실제 3D 메시로, 자차 위치를 보여주기 위해 전경에 추가합니다. 원래 촬영 차량이나 차량 동역학 모델은 아닙니다. 장면 복원·외관 보정·객체 인식·주행 예측은 각각 확인할 수 있게 유지합니다.

## 따라 하기

### 1. CUDA GPU 없이 저장된 결과부터 보기

이 페이지의 뷰어와 NuRec·Harmonizer 비교 영상을 열어보세요. 원본 RGB 인식, 카메라 선택, 예측 경로와 마우스 조작을 직접 확인할 수 있습니다. 브라우저는 미리 실행해 둔 모델 출력을 읽습니다.

```bash
python3 labs/nurec-rgb-reality/check.py
python3 labs/rgb-reality-view/serve.py --root site/public/showcase/nurec-rgb-reality --port 8092
```

**http://127.0.0.1:8092/**에 접속합니다. 뷰어의 지정된 JavaScript 모듈을 불러오려면 인터넷 연결이 필요합니다. 영상 재생과 증거 파일 검사에는 NVIDIA GPU가 필요하지 않습니다.

### 2. GPU 머신 준비하기

검증에 사용한 환경은 Linux x86_64, RTX 5090 32GB 한 장, 시스템 메모리 약 32GB입니다. 호환되는 NVIDIA 드라이버, NVIDIA Container Toolkit이 연결된 Docker, Python, Git, uv, Node.js/npm을 준비하세요. [NVIDIA Linux 온보딩](../onboarding/nvidia-linux.md)부터 확인하면 됩니다.

```bash
nvidia-smi
export NUREC_RGB_ROOT="$HOME/physical-ai-labs/nurec-rgb-road"
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" setup
```

먼저 [SOURCES.md](../../../labs/nurec-rgb-reality/SOURCES.md)의 이용 조건을 확인하세요. NuRec 런타임, 모델 가중치, 데이터셋, 차량 모델의 조건은 각각 다릅니다. `setup`은 지정한 런타임을 받고 격리된 환경을 설치한 뒤 공개 모델 체크포인트와 NuRec 지표 계산용 의존 파일을 받습니다. 다운로드와 첫 컴파일 시간은 예제의 실제 학습 시간보다 길 수 있습니다. 가중치·원본 로그·입력 캐시는 Git 밖에 저장합니다.

### 3. 한 단계씩 실행하기

저장소 폴더의 터미널에서 실행합니다. 앞 명령이 성공한 뒤 다음 명령을 넣으세요.

```bash
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" rgb
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" rig
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" prepare
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" train
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" render
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" enhance
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" --assumed-camera-height-m 1.8 policy
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" perceive
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" export
python3 labs/nurec-rgb-reality/pipeline.py --root "$NUREC_RGB_ROOT" serve
```

`rgb`에서 카메라를 추정하고 `rig`에서 고정 배열로 조정합니다. `prepare`는 NCore 입력을 만들고 `train`은 NuRec을 학습해 Gaussian을 내보냅니다. `render`는 정면·사선·회전 시점의 NuRec 원본을 만들며, `enhance`는 회전 프레임에 Harmonizer를 실행합니다. `policy`와 `perceive`는 원본 RGB로 각 모델을 실행하고, `export`가 뷰어를 묶습니다.

새 출력 폴더에서는 `pipeline.py --root "$NUREC_RGB_ROOT" all`로 전체 과정을 이어 실행할 수 있습니다. GPU 단계는 같은 잠금과 GPU 한 장을 사용합니다. 이 예제는 문서에 나온 PandaSet 방식의 카메라 폴더 여섯 개를 기대합니다. 정면 카메라 하나로는 후방 관측을 얻을 수 없으므로, 다른 카메라 배열은 입력을 명시적으로 맞춰야 합니다.

## 결과 확인

```bash
python3 labs/nurec-rgb-reality/check.py --decode-video
python3 -m unittest discover -s labs/rgb-reality-view -p 'test_*.py'
```

검사기는 입력 출처, 카메라·rig 기하 구조, NuRec 실제 완료 기록, 원본과 Harmonizer 프레임 짝, 예측 텐서의 형태와 회전·유한값, 원본 RGB 인식 결과, 압축 모델 개수, 파일 해시와 실제 조작 기록을 확인합니다. 영상 전체 디코딩에는 FFmpeg가 필요합니다. **구현과 파일 일관성 검사이며 주행 안전·검출 정확도·가려진 면의 정답을 검증하는 시험은 아닙니다.**

[독립 실행형 3DGUT](rgb-reality-view.md), [앞서 만든 RGB + LiDAR NuRec 비교 실험](pandaset-nurec.md), [직접 만든 합성 도로의 인터페이스 실험](reality-view.md)과 입력 조건을 비교해 보세요. 각 실행 경로를 구분해 표시합니다. 자차 중심 표현을 참고한 공개 실습이며 Tesla의 비공개 모델이나 실차 Reality View 시스템을 재현한 결과로 설명하지 않습니다.
