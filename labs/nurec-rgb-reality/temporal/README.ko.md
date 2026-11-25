# 시간축 Reality View: RGB 데모 따라 하기

[English](README.md) · [전체 실습](../../../docs/ko/labs/nurec-rgb-reality.md) · [출처와 사용 조건](../SOURCES.md)

RGB로 복원한 NuRec 장면을 공간 기준으로 두고, 현재 렌더링과 이전 보정 출력 네 장을 Harmonizer에 넣습니다. 객체 인식과 Alpamayo는 원본 카메라 사진을 사용하며, 표식은 생성 이후에 따로 겹칩니다. **Built on NVIDIA Cosmos.** 미리 복원한 장면에 선택형 GPU 보정을 연결한 실습이며, Tesla 구현이나 실제 차량 제어기는 아닙니다.

## GPU 없이 저장 결과부터 살펴보기

```bash
python3 labs/nurec-rgb-reality/temporal/check.py
python3 labs/rgb-reality-view/serve.py --root site/public/showcase/nurec-rgb-reality --port 8092
```

**http://127.0.0.1:8092/?lang=ko**를 여세요. 개선 모델을 골라 Volvo 주변을 돌려 보고 운전자 시점, 원본 RGB 인식과 예측 경로를 확인합니다. ‘RGB 깊이 근거’ 모델은 예측 깊이와 맞는 카메라 수를 Gaussian 중심별로 표시합니다. 빨강 0개·노랑 1개·청록 2개 이상입니다. 형상은 유지하며, 실측 가시성이나 환각 판정은 아닙니다. 이 검사에는 CUDA GPU나 가중치 다운로드가 필요 없습니다.

## 같은 입력으로 V1·V5 비교하기

Linux x86_64, **Python 3.12 이상**, uv, NVIDIA Container Toolkit이 연결된 Docker, Git, `flock`이 필요합니다. [GPU 환경 설정](../../../docs/ko/onboarding/nvidia-linux.md)과 기존 NuRec 실습부터 마치세요. 명령은 저장소 최상위 폴더에서 한 줄씩 실행합니다. 공개 가중치 약 5GB 외에도 컨테이너·캐시·결과를 저장할 공간이 필요합니다.

```bash
export NUREC_RGB_ROOT="$HOME/physical-ai-labs/nurec-rgb-road"
export RV_TEMPORAL_ROOT="$HOME/physical-ai-labs/reality-temporal"
export RV_INPUT="$NUREC_RGB_ROOT/renders/orbit/front_camera"
python3 labs/nurec-rgb-reality/temporal/pipeline.py --root "$RV_TEMPORAL_ROOT" setup
python3 labs/nurec-rgb-reality/temporal/pipeline.py --root "$RV_TEMPORAL_ROOT" --input "$RV_INPUT" compare
python3 labs/nurec-rgb-reality/temporal/pipeline.py --root "$RV_TEMPORAL_ROOT" --input "$RV_INPUT" evaluate
python3 labs/nurec-rgb-reality/temporal/pipeline.py --root "$RV_TEMPORAL_ROOT" check
```

`RV_INPUT`에는 하나로 이어지는 시점 경로의 16:9 PNG·JPEG를 순서대로 넣습니다. 짧게 시험하려면 `compare` 앞에 `--max-frames 6`을 넣고, 실행 폴더 안의 새 `--comparison-dir`을 지정하세요. 네 장 문맥을 실제로 비교하려면 여섯 프레임 이상이 필요합니다. 이미 결과가 든 폴더는 덮어쓰지 않습니다. 컷이 여러 개면 같은 컨테이너 환경의 `enhance.py --cut-frames`를 쓰거나 연속 구간별로 나누어 실행하세요.

`setup`은 공식 코드·Cosmos 의존성·NVIDIA PyTorch 베이스 이미지·모델 리비전과 해시를 고정합니다. **`nvidia/Harmonizer/diffusion_harmonizer.pkl`만 받습니다.** 공개 파일에 포함된 완전한 live DiT·VAE 가중치로 초기화하고, 래퍼 이름을 맞춘 뒤 학습 파라미터 전체가 공개 텐서와 같은지 자료형 변환 후 값까지 검사합니다. 접근 제한이 있는 Cosmos 베이스 가중치는 받지 않습니다. 학습하지 않는 구조용 버퍼는 고정한 공식 구현을 따릅니다. 추출한 구성 요소 캐시는 로컬에만 두며 재배포하지 않습니다.

공식 코드 커밋은 `826c1998796e024bc82c9843b3ec515c50737573`, 모델 리비전은 `20ca33d4612b1e98e0526b3a7ee604af5b289f58`입니다. 코드와 가중치는 **서로 다른 라이선스**를 따릅니다. pickle은 역직렬화 때 코드를 실행할 수 있으므로 고정한 공식 파일만 사용하세요.

### 공개 영상의 160개 시점 만들기

기존 복원과 깊이 제약 실습의 **production** 모드에서 `train`·`export`까지 별도 폴더로 마치세요. 이어서 기존·개선 모델을 동일한 160개 시점으로 렌더링합니다.

```bash
export RGB_GUIDED_PROD="$HOME/physical-ai-labs/nurec-guidance-production"
uv run --no-project --with numpy --with scipy python labs/nurec-rgb-reality/guidance/render_comparison.py --root "$RGB_GUIDED_PROD" --reference "$NUREC_RGB_ROOT"
export RV_INPUT="$RGB_GUIDED_PROD/preview/guided-orbit/front_camera"
```

이 `RV_INPUT`으로 **새 결과 폴더**에서 비교 명령을 실행하세요. 160장은 카메라 관측을 더 수집한 것이 아니라 렌더링 시점을 촘촘히 샘플링한 것입니다. 공개 실행은 1024×576·BF16·seed 42·timestep 250을 사용했습니다. GPU 호스트에서 배포용 setup·여섯 프레임 V1/V5 GPU 비교·CPU 평가를 실행했고, 160프레임 추론과 실제 뷰어에도 같은 어댑터와 전체 파라미터 검사를 사용했습니다.

## 실시간 뷰어 연결하기

GPU 머신의 별도 터미널에서 다음 명령을 계속 켜두세요. 공유 GPU 잠금을 잡고 모델을 메모리에 유지합니다.

```bash
python3 labs/nurec-rgb-reality/temporal/pipeline.py --root "$RV_TEMPORAL_ROOT" serve
```

서버는 공개 주소가 아닌 **127.0.0.1:8765**에만 연결됩니다. 다른 노트북에서 보려면 새 터미널을 열고 SSH 터널을 만드세요. `GPU_HOST`를 자신의 SSH 별칭으로 바꿉니다.

```bash
ssh -N -L 127.0.0.1:8765:127.0.0.1:8765 GPU_HOST
```

노트북에서는 명시적으로 로컬 프록시를 연결해 뷰어를 켭니다.

```bash
python3 labs/rgb-reality-view/serve.py --root site/public/showcase/nurec-rgb-reality --port 8092 --enhancer-url http://127.0.0.1:8765
```

**http://127.0.0.1:8092/?lang=ko**에서 장면을 열고 **현재 시점 보정**을 누르세요. 이전 출력 네 장이 모이면 기록이 `0/4`에서 `4/4`로 바뀝니다. 작은 마우스 이동은 이력을 유지하고, 큰 시점 점프는 오래된 형상을 재사용하지 않도록 초기화합니다. **자동 갱신**을 켜면 이전 응답이 끝난 뒤 최신 화면을 캡처합니다. 밀린 요청을 쌓지 않는 비동기 미리보기이며 36fps diffusion은 아닙니다. 현재 구현은 로컬 세션 두 개까지 유지합니다.

모델에는 표식이 없는 3D 렌더링을 보냅니다. 원본 RGB의 검출 접점과 Alpamayo의 개방 루프 예측을 같은 캡처 좌표로 투영하고, 보정이 끝난 뒤 두 패널에 그립니다. 생성 픽셀에서 인식한 결과로 바꿔 표시하지 않습니다. 공개 Pages에는 이 서버 주소가 없으며 방문자의 localhost에 추론 요청을 보내지 않습니다.

## 검사와 녹화

- `comparison/{independent,temporal}/result.json`: 입력·출력 해시, 실제 이전 출력 수, 프레임별 GPU 계산 시간과 학습 파라미터 일치 기록.
- `comparison/evaluation.json`: 원본에서 구한 공통 optical flow와 왕복 일치 검사, V1·V5의 warp 오차와 윤곽 크기. 평활화만으로 지표가 좋아질 수 있으며 미관측 시점의 정확도는 아닙니다.
- `live-captures/`: 표식 없는 실제 입력·출력과 시점 기록. 공개 전에 검토하고 원시 실행 폴더는 커밋하지 마세요.

```bash
python3 -m unittest discover -s labs/nurec-rgb-reality/temporal -p 'test_*.py'
node labs/nurec-rgb-reality/temporal/record_viewer.mjs --language ko --url 'http://127.0.0.1:8092/?lang=ko' --output ./runs/local-temporal-recording
```

기하 검사에는 NumPy가 필요하므로 독립 환경을 쓰세요. 녹화에는 Chrome·Playwright가 필요하며, 별도 설치 모듈은 `PLAYWRIGHT_MODULE`로 지정할 수 있습니다. 실제 GPU 응답, 작은 마우스 회전, 문맥 구성·초기화와 모바일 레이아웃을 검사합니다. 가짜 추론 화면을 끼워 넣지 않습니다. 녹화는 Git에서 제외되는 `runs/` 아래에 두세요.

장면은 정적이고 RGB 스케일은 상대값입니다. 가려진 면은 검증되지 않았으며 카메라 배열도 근사 어댑터를 사용합니다. [측정 결과·한계·원본 출처](../../../docs/ko/labs/nurec-rgb-reality.md#결과-확인).

## 같은 픽셀로 더 빠르게 실행하기

로컬 뷰어는 **화질 동일** 모드로 시작합니다. 입력 다섯 장의 encoder·DiT는 유지하고 causal decoder의 첫 출력만 복원합니다. 같은 160프레임에서 모델 중앙값은 483.6ms에서 271.3ms로 줄었고, 원본 RGB 픽셀이 모두 일치했습니다. GPU 이력 캐시·비동기 캡처와 기록·캔버스 직접 표시·손실 없는 WebP로 표시까지의 부하도 줄입니다. **추가 가속**은 합성곱 메모리 배치·커널을 바꿔 238ms를 기록했으며, 기존 대비 평균 PSNR52.76dB·SSIM0.99736으로 작은 차이가 있습니다. 기본값은 픽셀 일치를 유지합니다.

공유 GPU로 비교하려면 먼저 서버 터미널을 종료하세요.

```bash
python3 labs/nurec-rgb-reality/temporal/pipeline.py --root "$RV_TEMPORAL_ROOT" --input "$RV_INPUT" benchmark
python3 labs/nurec-rgb-reality/temporal/check_speed.py
```

기존 실험을 보존하려면 새 `--comparison-dir`을 고르세요. 짧게 확인할 때는 `--max-frames 12`를 추가합니다. 프레임별 해시와 실제 계산 시간이 기록되며 두 번째 검사는 GPU 없이 실행됩니다. [전체 성능·화질 표](../../../docs/ko/labs/nurec-rgb-reality.md#최적화-뒤의-fps지연화질).

`record_speed.mjs --profile baseline`과 `--profile exact`는 **GPU 한 장에서 순서대로** 같은 실제 마우스 동작을 실행합니다. `--language en` 또는 `ko`, 로컬 `--url`과 Git에서 제외되는 결과 폴더를 지정하세요. 실제 표시한 보정 화면 수, 3D 렌더링 FPS, 모델 계산 시간과 캡처→표시 지연을 구분해 남깁니다. 실제 조작 비교 영상에는 프레임 보간이나 재생 가속을 넣지 않습니다.

서버를 다시 켜도 기존 숫자 파일명 다음부터 기록해 앞선 캡처를 보존합니다. 최적화 모드의 기록은 최대 세 작업까지 백그라운드에 맡기며, 저장이 밀리면 `recording=skipped_busy`로 빠진 디버그 캡처를 표시합니다. 표시할 프레임을 만들어 내거나 요청을 쌓는 동작은 아닙니다. 이전 영상과 160프레임 결과도 보존합니다.

## 이동 중 미리보기와 정지 후 보정 직접 해 보기

[시간축 보정 설치 안내](#실시간-뷰어-연결하기)에 따라 GPU 서비스와 노트북의 로컬 뷰어를 실행하세요. 노트북에서 **http://127.0.0.1:8092/?lang=ko&execution=adaptive**를 열면 AI 미리보기를 선택할 수 있습니다. 더 부드러운 브라우저 3D 미리보기는 주소 끝을 **`execution=native`**로 바꾸면 됩니다. 장면을 불러온 뒤 **자동 갱신**을 켜고 드래그했다가 놓아 보세요. 오른쪽 캡션에 **512×288 AI 미리보기**, **브라우저 3D · AI 생성 아님**, **1024×576 고화질**이 구분되어 표시됩니다. 고화질 보정이 끝나면 다시 움직일 때까지 새 요청을 보내지 않습니다. 기존 **화질 동일 · 연속 고화질** 방식도 그대로 선택할 수 있습니다.

GPU 화질 검사를 재현하려면 먼저 서비스 터미널에서 Ctrl+C로 실행을 멈추세요. 시간축 보정 README의 안내대로 `RV_INPUT`은 개선 모델의 순서 있는 렌더링 폴더, `RGB_GUIDED_PROD`는 그 모델의 비공개 production 폴더로 지정합니다.

```bash
python3 labs/nurec-rgb-reality/temporal/pipeline.py --root "$RV_TEMPORAL_ROOT" --comparison-dir "$RV_TEMPORAL_ROOT/adaptive-check" --input "$RV_INPUT" --rig "$RGB_GUIDED_PROD/rig-orbit.json" --max-frames 12 adaptive-benchmark
python3 labs/nurec-rgb-reality/temporal/check_adaptive.py
```

첫 명령은 한 GPU에서 연속 고화질 기준, 저해상도 미리보기, 정지 후 고화질을 실제로 실행합니다. 기존 결과 폴더가 있으면 덮어쓰지 않고 중단합니다. 전체 160개 시점을 확인하려면 `--max-frames 12`를 빼세요. 160개는 렌더링한 카메라 시점 수이며 새로 촬영한 사진 수가 아닙니다. 두 번째 명령은 GPU 없이 공개 측정 기록과 영상 파일을 검사합니다. [GPU 비교 코드](../../nurec-rgb-reality/temporal/benchmark_adaptive.py) · [움직임 판단 코드](../../rgb-reality-view/motion-policy.mjs) · [실제 이동·정지 녹화 코드](../../nurec-rgb-reality/temporal/record_adaptive.mjs).
