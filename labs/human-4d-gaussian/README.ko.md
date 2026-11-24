# 인체 4D Gaussian 실습 코드

[English](README.md) · [한국어 학습 가이드](../../docs/ko/labs/human-4d-gaussian.md) · [출처·이용 조건](SOURCES.md)

두 경로를 구분합니다.

- **공개 합성 인체 예제:** SOMA 공식 예제 동작 → 실제 Warp 스키닝 → 합성 RGB·정점 Gaussian. 영상에서 외형을 학습한 결과가 아닙니다.
- **개인 단안 영상 재구성:** 로컬 영상 → 공식 GEM-X motion-video → SOMA/SAM2 → 원본을 유지하는 4DAnyone seed → 얼굴·손·MoGe 제약 → 전체 동작 구간 학습 → 렌더링·브라우저 패키지.

공개 샘플 검사는 GPU 없이 실행할 수 있습니다.

```bash
python3 labs/human-4d-gaussian/pipeline.py \
  --root "$HOME/physical-ai-labs/control-check" --mode control \
  --package-dir site/public/showcase/human-4d-control --deep check
```

새 학습에는 Linux GPU 환경과 실제 모델·체크포인트 설정이 필요합니다. `setup` 첫 실행은 출력 폴더에 `runtime.json` 예제를 만든 뒤, 환경을 채우라는 오류로 종료합니다. 설치가 끝난 것처럼 표시하지 않습니다. [영문 실행 설명](README.md)의 환경별 공식 설치 링크와 [runtime.example.json](runtime.example.json)을 따라 Python·소스·자산 경로를 설정한 뒤 다시 실행하세요. 전역 Python이나 Isaac Sim 환경에 설치하지 않습니다.

단안 재구성 프리셋은 고정 카메라의 9:16 세로 영상, 단일 인물, 30Hz 기준 최소 121프레임을 사용합니다. 다른 화면비를 몰래 늘리거나 새 모델로 대체하지 않습니다. 원본 해상도를 유지한 30Hz 입력과 540×960 작업용 RGB를 따로 만듭니다.

```bash
export HUMAN_4D_ROOT="$HOME/physical-ai-labs/human-4d"
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" setup
# runtime.json과 공식 모델 환경을 준비한 다음 setup을 다시 실행합니다.
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" prepare --video "$HOME/Videos/my-motion.mp4"
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" rig
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" multiview
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" train
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" refine --seed-only
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" render
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" package
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" --deep check
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" serve
```

`multiview`는 기준 구간에서 Base24 6방향과 Turbo4 중간 6방향을 생성합니다. `train`은 seed를, `refine`은 고해상도·원본 ROI·MoGe 분기를 학습합니다. 위 첫 실습은 `refine --seed-only`로 처음 121프레임부터 완성합니다. 결과를 확인한 뒤 별도 `extend` 단계로 전체 동작을 처리합니다.

전체 동작은 짧은 구간을 완성한 뒤 `extend`로 처리합니다. 후속 구간마다 Turbo4 6방향과 중간 각도 6방향을 새로 생성하고, native 4D 모델·고해상도 RGB·원본 얼굴과 손·MoGe-3 제약을 차례로 학습합니다. 첫 구간의 Base24+Turbo 생성 조건과 구분합니다. 121프레임 창을 120프레임 간격으로 옮기며, 겹친 프레임이나 마지막 패딩을 재생 길이에 중복해서 넣지 않습니다.

```bash
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" extend
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" render
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" \
  --package-dir "$HUMAN_4D_ROOT/package-full" package
python3 labs/human-4d-gaussian/pipeline.py --root "$HUMAN_4D_ROOT" \
  --package-dir "$HUMAN_4D_ROOT/package-full" --deep check
```

모든 구간을 확인한 뒤 전체 재생 목록을 씁니다. 완료한 단계는 입력·실행 조건·코드·출력 해시를 확인한 뒤 재사용합니다. 중단됐다면 같은 명령을 다시 실행하며, 조건을 바꾸는 실험은 새 출력 폴더에서 진행합니다. 렌더링은 `renders/<모델·렌더러 해시>`에 나눠 저장해 짧은 결과를 보존합니다. Pages에서 `package-full` 폴더를 열어 비교하세요.

기존 `refine --trajectory-experiment`는 같은 외형 스냅샷을 SOMA 궤적에 연결하고, 원본 RGB만 있는 후속 구간을 조건부 공분산 방식으로 학습하는 비교 실험입니다. 새 시점 기반 학습보다 번짐이 커서 별도 옵션으로 남겼습니다. 일반 `refine`과 `refine --seed-only`는 짧은 기준 구간부터 완성합니다.

## 긴 구간을 학습하기 전 입력 검사

`inspect_masks.py --root "$HUMAN_4D_ROOT"`는 추정한 SOMA 머리 영역과 인물 마스크를 비교합니다. `coverage.json`과 비교 이미지는 사람이 확인할 프레임을 찾는 자료이며, 전신 분할 정확도나 정답 마스크가 아닙니다. 얼굴을 마스크가 지워버렸다면, 마스크를 적용한 RGB 점수가 높아도 얼굴 재구성이 좋아졌다고 볼 수 없습니다.

후속 구간은 생성 시점부터 따로 확인할 수 있습니다. 아래는 기본 RTX 5090 환경의 예입니다. `RECON_PY`·CUDA 경로·GPU 잠금 파일은 자신의 `runtime.json`과 맞추세요.

```bash
RECON_PY="$HUMAN_4D_ROOT/envs/reconstruction/bin/python"
export CUDA_HOME=/usr/local/cuda-12.9
export PATH="$CUDA_HOME/bin:$PATH"
export TORCH_CUDA_ARCH_LIST=12.0
flock "$HUMAN_4D_ROOT/.gpu.lock" "$RECON_PY" labs/human-4d-gaussian/fresh_interval.py \
  --root "$HUMAN_4D_ROOT" --name s01 --start 120 --views-only
"$RECON_PY" labs/human-4d-gaussian/inspect_teachers.py --root "$HUMAN_4D_ROOT" \
  --name s01 --out "$HUMAN_4D_ROOT/diagnostics/s01-base.jpg"
"$RECON_PY" labs/human-4d-gaussian/inspect_teachers.py --root "$HUMAN_4D_ROOT" \
  --name s01 --offset --out "$HUMAN_4D_ROOT/diagnostics/s01-offset.jpg"
```

직접 실행하는 GPU helper는 잠금을 중복으로 잡지 않습니다. 위처럼 주 실행기와 같은 잠금 파일·CUDA 환경을 사용하세요. 이후 `extend`로 이어가려면 단계별 학습 횟수도 설정 파일과 같아야 합니다. `--views-only`는 검토 대기 상태까지만 기록합니다. 같은 명령에서 이 옵션을 빼면 생성 결과의 해시를 검사한 뒤 학습을 계속합니다.

기준 6방향과 중간 6방향의 처음·중간·끝을 모두 확인하세요. `180°`인데 얼굴이 정면으로 나온 영상은 다른 방향과 모순되므로, 방향 수가 많다는 이유만으로 학습에 넣지 않습니다. `--exclude-base-cameras 3`은 기준 생성 카메라 3을 제외하는 옵션입니다. 남은 카메라 번호를 연속으로 다시 매기고 MoGe 제약도 새 번호에 대응시킵니다. 생성한 방향 수와 실제 학습에 쓴 수는 따로 기록합니다. **검토 대기 중이며 아직 학습을 시작하지 않았을 때만** 같은 생성 결과의 제외 목록을 바꿀 수 있고, 이전 실행 조건은 따로 보존합니다. 학습을 시작한 뒤 제외 목록을 바꾸거나 시드·생성 모드를 바꾸는 경우에는 새 구간 이름·출력 폴더를 사용하세요. 직접 실행한 비교 모델을 기존 `models.json`에 자동으로 선택하지 않습니다.

`repair_foreground.py --help`는 사람이 선택한 마스크 오류를 별도 데이터로 고치는 도구입니다. 앞뒤 RGB 프레임의 마스크를 optical flow로 옮기고, 두 결과가 모두 인물로 판단한 영역만 머리 주변에 보충합니다. 원본 마스크와 렌더러는 바꾸지 않습니다. 원본 픽셀에서 얼굴·손 ROI를 다시 만들고, 보정된 마스크를 확인한 뒤 별도 모델을 학습해 비교하세요. 보정이 타당한지 자동으로 판정하는 기능은 아닙니다.

출력은 로컬에 남으며 업로드·Git push·Pages 배포를 하지 않습니다. 다른 영상과 다른 조건은 새 출력 폴더에서 시작하세요. 원본 출처 표기와 파생 모델 재배포 권한은 별개입니다. YouTube 다운로더는 포함하지 않습니다.

Pages의 **로컬 결과 폴더 열기**에서 `manifest.json`이 있는 패키지를 고르면 파일을 브라우저 안에서 읽습니다. 원본 비교용 `source.mp4`도 패키지 안에 있어야 합니다. `serve`는 로컬 데이터 서버이며 GPU 학습이나 Pages 전체 앱을 대신 실행하지 않습니다.

`runtime.json`의 선택 항목 `source_credit`·`source_reference_url`로 내 입력 영상의 출처를 적을 수 있습니다. 모델 목록·브라우저 패키지에 함께 저장하며, 비교 영상에도 출처를 표시합니다. 기본 영상 폰트로 표시할 때는 영문 출처를 쓰거나 해당 문자를 지원하는 폰트를 준비하세요.
