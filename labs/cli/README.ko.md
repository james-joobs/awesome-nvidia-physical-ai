# Physical AI 실습 실행과 결과 확인

[English](README.md) · [한국어](README.ko.md)

기존 실습 프로그램을 명령어로 실행하고 결과를 검사하는 작은 도구입니다. Python 표준 라이브러리만 사용합니다. CLI-Anything의 명령어·JSON 출력·실행 근거 관리 방식을 참고했으며, CLI-Anything에 공식 통합된 기능은 아닙니다.

## 먼저 실행 환경 확인하기

Linux GPU 머신의 저장소 폴더에서 아래 명령을 입력합니다. `--python`에는 해당 플랫폼이 설치된 가상환경의 Python 경로를 넣습니다. 이 도구 자체는 Python 3.10 이상이면 실행할 수 있습니다.

```bash
python3 labs/cli.py list
python3 labs/cli.py --json doctor physics-friction \
  --python /path/to/isaaclab/.venv/bin/python --ffmpeg /usr/bin/ffmpeg
```

`doctor`는 소스 파일, Python 모듈, `nvidia-smi`, 화면과 녹화 도구의 준비 상태를 확인합니다. 시뮬레이터를 시작하거나 모델을 내려받지는 않습니다. 라이선스에 대신 동의하지 않으며, GPU 메모리에 모델이 실제로 올라가는지까지 확인하는 명령도 아닙니다. 준비가 부족하면 종료 코드는 1입니다.

## 실행할 명령을 확인한 뒤 실습하기

```bash
python3 labs/cli.py --json run physics-friction \
  --python /path/to/isaaclab/.venv/bin/python --ffmpeg /usr/bin/ffmpeg \
  --output /tmp/physical-ai/friction-001 --dry-run

python3 labs/cli.py --json run physics-friction \
  --python /path/to/isaaclab/.venv/bin/python --ffmpeg /usr/bin/ffmpeg \
  --output /tmp/physical-ai/friction-001

python3 labs/cli.py --json verify /tmp/physical-ai/friction-001
python3 labs/cli.py --json preview /tmp/physical-ai/friction-001
```

매번 **아직 존재하지 않는 결과 폴더**를 지정합니다. `--dry-run`은 실행할 명령과 준비 상태만 보여주며 폴더를 만들거나 실험을 실행하지 않습니다. 명령 구성이 올바르면 준비가 부족해도 종료 코드는 0이므로, JSON의 `preflight.ready`를 함께 확인합니다. 실제 실행에서 준비가 부족하면 실패 기록을 남기고 종료 코드 1을 반환합니다. `preview`는 결과와 파일 경로를 보여주며, 브라우저를 열거나 파일 무결성을 검사하지는 않습니다.

| 시나리오 | 실행 내용 | 남는 결과 | 추가 준비 |
|---|---|---|---|
| `physics-friction` | 마찰계수가 다른 물체 3개의 미끄러짐 비교 | 실제 Isaac Sim GUI 녹화와 PhysX 위치 기록 | Isaac Lab·Isaac Sim, X11 `DISPLAY`, `xwininfo`, ffmpeg |
| `physics-bounce` | 반발계수에 따른 공의 튀어 오름 비교 | 실제 Isaac Sim GUI 녹화와 PhysX 위치 기록 | 위와 같은 GUI 환경 |
| `curobo-replan` | 장애물을 추가하기 전후의 Franka 경로 계산 | 새 JSON 결과와 NPZ 궤적. 이 명령에 GUI 녹화는 포함되지 않음 | 호환되는 cuRobo 환경 |
| `warp-dem` | GPU 입자 시뮬레이션 200프레임 | Warp OpenGL 화면과 JSON 측정값. 영상 녹화는 별도 | Warp·NumPy·CUDA. `--headless`로 화면 생략 가능 |
| `newton-materials` | 공식 XPBD·VBD 천 시뮬레이션과 케이블 예제의 `--test` 실행 | 시간별 USD와 검토용 카메라 레이어. 이후 GUI에서는 저장된 결과를 **재생** | Newton 예제 의존성, Warp·NumPy·usd-core |
| `cosmos-i2v` | 실제 Cosmos 백엔드의 이미지→영상 추론 | 생성 MP4와 공식 성공 기록. 물리 시뮬레이션은 아님 | 준비된 Cosmos 소스·체크포인트·입력 JSON |
| `alpamayo-synthetic` | 합성 카메라 입력으로 실제 Alpamayo 추론 | 유효한 예측 궤적 텐서. 폐루프 주행이 아닌 인터페이스 검사 | 준비된 Alpamayo 환경·로컬 가중치·입력 폴더 |
| `gr00t-placement` | 준비 절차 안내 | 새 실험을 실행했다고 표시하지 않음 | [정책 서버·모델·Arena 설정](../../docs/ko/labs/gr00t-placement.md) |
| `microduck-walk` | 준비 절차 안내 | 새 실험을 실행했다고 표시하지 않음 | [Isaac Lab 환경과 학습한 PT 체크포인트](../../docs/ko/labs/microduck.md) |

Warp는 화면 없이 데이터만 생성할 수도 있습니다.

```bash
python3 labs/cli.py --json run warp-dem --headless \
  --python /path/to/warp-env/bin/python --output /tmp/physical-ai/warp-001
```

`PHYSICAL_AI_PYTHON`, `PHYSICAL_AI_FFMPEG` 환경변수로 기본 경로를 지정할 수 있습니다. 다른 체크아웃을 사용하려면 `--source /path/to/repo`를 넣습니다. 해당 폴더의 `labs/scenarios.json`을 읽습니다. 셸을 거치지 않고 프로그램을 직접 실행하므로 `python -m uv` 같은 명령 문자열 대신 실행 파일 경로를 입력합니다.

기존 vendor 체크아웃을 쓰기 위한 `PYTHONPATH` 등 환경변수는 자식 프로그램에도 전달됩니다. 패키지를 설치하거나 환경을 바꾸지는 않습니다. GPU 서버를 함께 쓴다면 같은 `flock` 잠금 파일을 사용해 실습을 순서대로 실행하세요.

## 모델 입력과 실행 환경 지정하기

아래 명령은 미리 준비한 환경과 가중치를 사용합니다. 백엔드 설치나 체크포인트 다운로드를 대신하지 않습니다. 확인한 소스·모델 버전은 `labs/world-driving/model-pins.json`에 있습니다.

```bash
python3 labs/cli.py --json run cosmos-i2v \
  --python /path/to/cosmos-framework/.venv/bin/python \
  --backend /path/to/cosmos-framework --input /path/to/workbench-right.json \
  --model /path/to/Cosmos3-Edge --seed 19 --output /tmp/physical-ai/cosmos-001

python3 labs/cli.py --json run alpamayo-synthetic \
  --python /path/to/alpamayo2-edge/.venv/bin/python \
  --input /path/to/synthetic-intersection --model /path/to/Alpamayo2-Edge \
  --seed 19 --output /tmp/physical-ai/alpamayo-001
```

Cosmos 입력은 로컬 `vision_path`를 담은 JSON 파일입니다. Alpamayo는 `input.json`과 여기에 지정된 카메라 이미지가 있는 폴더를 받습니다. 입력 파일 해시, 모델 메타데이터 해시, 체크포인트 파일 크기, 확인 가능한 Hugging Face 캐시 revision과 백엔드 Git revision을 기록합니다. 수GB인 가중치 전체를 해시하지는 않습니다. 등록된 참고 revision과 실제 로컬 캐시에서 읽은 revision은 구분합니다.

Cosmos 어댑터는 지정한 Python으로 백엔드 폴더에서 실행하며, 내부 `uv` 명령도 같은 환경을 찾도록 Python 실행 파일의 폴더를 `PATH` 앞에 넣습니다. 기본값은 공식 콘텐츠 필터를 유지합니다. Cosmos 전용 `--no-guardrails`를 직접 지정한 경우에만 필터를 끄고 두 실행 기록에 이를 표시합니다. 통제된 입력으로 해당 설정을 재현할 때 선택하는 옵션입니다. 기본 필터를 사용하면 추가 모델 다운로드와 GPU 메모리가 필요할 수 있습니다.

모델 결과 검사는 공식 성공 기록과 로컬 MP4가 있는지, 또는 Alpamayo가 예상 형태의 유효한 궤적 텐서를 저장했는지 확인합니다. 프롬프트를 잘 따르는지, 물리적으로 타당한지, 주행 능력과 안전성이 충분한지까지 판정하지는 않습니다.

## 무엇을 기록하고 검사하나요?

실행 전 `request.json`, 프로그램 출력 전체를 담은 `run.log`, 종료 후 최종 기록인 `run.json`을 저장합니다. 최종 기록에는 명령어, 소스의 SHA-256 해시, 시작·종료 시각, 종료 코드, 실행 방식, 검사 결과, 파일 크기와 해시가 들어갑니다. 기존 결과는 덮어쓰지 않습니다. 실행 중에는 `RUNNING` 파일이 있으며, 강제 종료하면 이 파일과 미완성 결과만 남을 수 있습니다.

`verify`는 파일 목록과 해시가 달라지지 않았는지 확인한 다음, 실습별 결과 검사를 다시 수행합니다. 물리 실험은 위치 기록과 마찰·반발 요약이 일치하는지 확인하고 MP4 파일도 검사합니다. cuRobo는 유한한 궤적 값, 같은 시작 위치와 목표, 장애물 대비 툴 위치를 검사합니다. 로봇 전체의 이동 중 충돌 검증은 cuRobo가 담당합니다. Warp는 200프레임 완료, 유효한 입자 이동량과 화면 실행 여부를 확인합니다. 화면 구도가 좋은지, 모델이 새로운 상황에도 잘 동작하는지까지 판정하지는 않습니다.

기존 GUI 녹화 프로그램은 내부 오류가 있어도 종료 코드 0을 반환할 수 있습니다. 이 도구는 `capture-failed` 파일이 있으면 실패로 처리하고 기록을 보존합니다. 영상을 공유하기 전 `run.json`과 `run.log`를 확인하세요. 외부에서 파일을 직접 수정할 수는 있습니다. 해시 검사는 저장된 최종 기록을 기준으로 변경을 감지하며, 최종 기록 자체의 악의적인 변조를 막는 장치는 아닙니다.

## GPU 없이 도구 검사하기

```bash
python3 -m unittest discover -s labs/cli -p 'test_*.py' -v
```

테스트용 프로그램이 만든 가상 결과로 JSON 출력 분리, 실행 실패 보존, GUI 오류 표시, 파일 변경 감지와 결과 폴더 재사용 방지를 검사합니다. 테스트 결과를 시뮬레이터 실행 결과로 표시하지 않습니다.
