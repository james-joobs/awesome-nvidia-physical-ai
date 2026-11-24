# 인체 4D Gaussian 실습 코드

[English](README.md) · [한국어 학습 가이드](../../docs/ko/labs/human-4d-gaussian.md) · [출처·이용 조건](SOURCES.md)

두 경로를 구분합니다.

- **공개 합성 제어 샘플:** SOMA 공식 예제 동작 → 실제 Warp 스키닝 → 합성 RGB·정점 Gaussian. 영상에서 외형을 학습한 결과가 아닙니다.
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

`multiview`는 기준 구간에서 Base24 6방향과 Turbo4 중간 6방향을 생성합니다. `train`은 seed를, `refine`은 고해상도·원본 ROI·MoGe 분기를 학습합니다. 위 첫 실습은 `refine --seed-only`로 처음 121프레임부터 완성합니다. 전체 길이 확장은 이 옵션을 뺀 심화 실험이며, 품질을 확인한 뒤 별도 출력 폴더에서 진행합니다.

전체 길이에서는 `warmstart.py`의 기본 `trajectory` 모드로 동일한 t=0 외형을 SOMA 피부 궤적에 연결합니다. 이후 `fit_interval.py`가 실제 RGB·원본 ROI·MoGe로 구간별 학습을 수행합니다. 속도와 시간 분산을 고정하고 공간 공분산을 독립적으로 최적화한 뒤 native 형식으로 저장합니다. 이 전체 구간 확장은 직접 GPU 검증을 진행 중인 구현입니다. 별도로 공개된 제어 샘플의 검증 결과를 실사 복원 정확도로 해석하지 않습니다.

출력은 로컬에 남으며 업로드·Git push·Pages 배포를 하지 않습니다. 다른 영상과 다른 조건은 새 출력 폴더에서 시작하세요. 원본 출처 표기와 파생 모델 재배포 권한은 별개입니다. YouTube 다운로더는 포함하지 않습니다.

Pages의 **로컬 결과 폴더 열기**에서 `manifest.json`이 있는 패키지를 고르면 파일을 브라우저 안에서 읽습니다. 원본 비교용 `source.mp4`도 패키지 안에 있어야 합니다. `serve`는 로컬 데이터 서버이며 GPU 학습이나 Pages 전체 앱을 대신 실행하지 않습니다.
