<div align="center">

# Awesome NVIDIA Physical AI

[English](README.md) · **한국어**

<img src="assets/social-preview.jpg" alt="Awesome NVIDIA Physical AI · 시뮬레이션, 로보틱스, 월드 모델" width="460">

**NVIDIA 피지컬 AI 도구를 한곳에서 찾고, 어떻게 연결해 쓰는지 살펴보세요.**

시뮬레이션, 로봇 학습, 자율주행에 필요한 도구와 데이터를 목표별로 정리한 커뮤니티 가이드입니다.

[🧪 목표별 실습](#만들고-싶은-것부터-시작하세요) · [🗺️ 생태계 지도](#생태계-한눈에-보기) · [📚 전체 카탈로그](CATALOG.ko.md) · [🌐 GitHub Pages](https://james-joobs.github.io/awesome-nvidia-physical-ai/ko/)

</div>

[![작업대 CAD를 Isaac Sim으로 가져오는 실습 미리보기. 눌러서 직접 체험하세요.](assets/repo-tour/preview.ko.gif)](https://james-joobs.github.io/awesome-nvidia-physical-ai/ko/#repo-tour)

[▶ 실습 흐름 직접 체험하기](https://james-joobs.github.io/awesome-nvidia-physical-ai/ko/#repo-tour)

## 만들고 싶은 것부터 시작하세요

| 목표 | 시작할 가이드 | 먼저 확인할 내용 |
| --- | --- | --- |
| **시뮬레이션 기초 익히기** | [Isaac Sim에서 큐브 떨어뜨리기](docs/ko/workflows/isaac-sim-first-cube.md) | 충돌체를 켰을 때와 껐을 때 큐브가 어떻게 움직이는지 비교합니다. |
| **CAD로 시뮬레이션 장면 만들기** | [작업대 CAD → OpenUSD → Isaac Sim](docs/ko/workflows/workbench-cad-to-isaac-sim.md) | 상판 치수가 맞는지, 큐브가 상판 위에 멈추는지 확인합니다. |
| **가상 카메라로 라벨이 붙은 데이터 만들기** | [SimReady](docs/ko/simready.md) → [Isaac Sim](docs/ko/isaac-sim.md) → [Replicator](docs/ko/replicator.md) | 같은 프레임의 RGB, 깊이값, 분할 마스크를 저장합니다. |
| **자율주행 정책 평가하기** | [AlpaSim 폐루프 평가 실습](docs/ko/workflows/alpasim-closed-loop.md) | 주행 영상과 충돌·도로 이탈 지표를 확인합니다. |
| **로봇 정책 테스트하기** | [로봇 파운데이션 모델 고르고 평가하기](docs/ko/robot-foundation-models.md) | 로봇이나 벤치마크에 맞는 체크포인트를 골라 비교 기준이 될 실행 기록을 남깁니다. |

**시뮬레이션에서 실물 로봇까지.** [Microduck 가이드](docs/ko/microduck.md)에서 Isaac Lab과 Newton으로 보행 정책을 학습시키는 과정을 볼 수 있습니다. [브라우저에서 조종해 보기](https://huggingface.co/spaces/pollen-robotics/microduck-simulator).

## 생태계 한눈에 보기

CAD로 만든 작업대 장면은 시뮬레이션과 라벨링된 카메라 데이터 생성에 쓸 수 있습니다. 주행 로그가 있다면 자율주행 정책을 평가하고, 로봇 시연이 있다면 정책을 학습하는 흐름도 지도에서 볼 수 있습니다.

![NVIDIA 피지컬 AI 생태계 지도. CAD로 시뮬레이션 장면을 만들고, 주행 로그를 복원해 자율주행 정책을 평가하고, 로봇 시연으로 정책을 학습하는 세 가지 흐름.](assets/ecosystem/physical-ai-ecosystem.ko.svg)

## 분야별 자료 찾아보기

<a name="1-오픈소스-코드가-확인된-프로젝트"></a>
<a name="데이터와-시뮬레이션-자산"></a>
<a name="nemo와-물리-ai-도구"></a>
<a name="최근-업스트림-릴리스"></a>
<a name="2-플랫폼모델제품표준-및-제한적-공개-항목"></a>
<a name="3-대화에서-함께-언급된-외부-모델도구"></a>
<a name="4-연결-관계와-명칭-정리"></a>
<a name="로봇-파운데이션-모델과-vla"></a>

| 분야 | 대표 가이드 | 카탈로그 |
| --- | --- | --- |
| **물리·3D·시뮬레이션** | [OpenUSD](docs/ko/openusd.md) · [Isaac Sim](docs/ko/isaac-sim.md) · [Newton](docs/ko/newton.md) | [시뮬레이션 도구](CATALOG.ko.md#물리-3d-및-시뮬레이션) |
| **로봇 학습·제어** | [Isaac Capture](docs/ko/isaac-capture.md) · [Isaac Lab](docs/ko/isaac-lab.md) | [로봇 도구](CATALOG.ko.md#로봇-학습-수집-및-제어) |
| **데이터·시뮬레이션 에셋** | [SimReady](docs/ko/simready.md) · [Video to Data](docs/ko/video-to-data.md) · [AutoData](docs/ko/autodata.md) | [데이터셋과 에셋](CATALOG.ko.md#데이터와-시뮬레이션-자산) |
| **로봇 파운데이션 모델** | [GR00T](docs/ko/isaac-gr00t.md) · [Physical Intelligence π](docs/ko/physical-intelligence-pi.md) | [로봇 모델과 VLA](CATALOG.ko.md#로봇-파운데이션-모델과-vla) |
| **자율주행** | [NuRec](docs/ko/nurec.md) · [Alpamayo](docs/ko/alpamayo.md) · [AlpaSim](docs/ko/alpasim.md) | [자율주행 도구](CATALOG.ko.md#자율주행) |
| **월드 모델·NeMo** | [Cosmos](docs/ko/cosmos.md) · [NeMo Curator](docs/ko/nemo-curator.md) · [NeMo Switchyard](docs/ko/nemo-switchyard.md) | [NeMo와 피지컬 AI 도구](CATALOG.ko.md#nemo와-물리-ai-도구) |

카탈로그에서 공식 자료, 라이선스, 공개 범위를 확인할 수 있습니다. 오픈소스 목록에는 각 저장소의 최근 커밋 날짜도 표시합니다.

[📚 전체 Markdown 카탈로그](CATALOG.ko.md) · [🔎 Pages에서 검색·필터](https://james-joobs.github.io/awesome-nvidia-physical-ai/ko/catalog/) · [📰 주요 도구 업데이트](CATALOG.ko.md#최근-업스트림-릴리스)

[🤝 기여 방법](CONTRIBUTING.md#기여-방법) · [📄 MIT 라이선스](LICENSE) · [🖼️ 외부 자료 출처](NOTICE.md) · [🏷️ 저장소 최신 릴리스](https://github.com/james-joobs/awesome-nvidia-physical-ai/releases/latest)
