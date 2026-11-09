# 3D 에셋과 환경

[전체 목록](../../README.ko.md) · [English](../en/datasets-3d-assets.md)

이 목록은 시뮬레이션에서 재사용할 기하 모델, 장면, 물체를 모았다. 창고 시나리오와 로봇이 집는 소품, MJCF 물체 라이브러리는 쓰는 시뮬레이터와 통합 과정이 다르다.

## 카탈로그에서 사용할 장면까지

| 단계 | 확인할 내용 |
|---|---|
| 선택 | 파일 형식, 패키지 의존성, 에셋 분류, 라벨, 이용 조건 |
| 구성 | 상대 참조와 페이로드, 위쪽 축과 단위, 시맨틱 라벨 |
| 물리 설정 | 충돌체 형상, 질량, 강체나 관절, 접촉 거동 |
| 검증 | 대상 시뮬레이터에서 열고 렌더링한 뒤, 배치 생성 전에 짧은 상호작용을 실행 |

![강체를 추가할 에셋을 선택하는 NVIDIA Isaac Sim 공식 화면](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01/resolve/main/images/PhysicalAI_Dataset_02.png)

창고 카드의 공식 가이드에서는 Stage에서 에셋 최상위 Xform을 선택한다. USD 장면은 개별 자산을 페이로드로 연결한다. 공식 장면에는 충돌체가 들어 있으며, 움직여야 하는 에셋에는 문서대로 강체를 설정할 수 있다. CSV 카탈로그에서 경로, 분류, 시맨틱 Q코드, 대략적인 질량을 확인할 수 있다. [공식 창고 카드와 설정 절차](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01#how-to-use)

## 활용 예시 — 선반의 물체 집기

카탈로그에서 창고 물체 몇 개를 고른다. USD 장면을 불러와 물체 하나에 대해 중력과 그리퍼 접촉을 시험한다. 그리퍼와 크기가 맞는지, 질량과 충돌체가 작업에 맞는지, 물체 배치를 무작위로 바꾸기 전에 카메라에서 보이는지 확인한다. MJCF 주방 벤치마크라면 호환되는 물체 패키지의 메시와 접촉 설정을 해당 실행 환경에서 검토한다. [주방 MJCF 데이터 카드](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF) · [SimReady](simready.md)

## 데이터셋 상세

<a id="simready-assets"></a>
### simready-assets

SimReady 3D 소품·물체 자산.

**라이선스·접근:** CC BY 4.0; 공개.  
**공식 데이터셋 카드:** [simready-assets](https://huggingface.co/datasets/nvidia/simready-assets)

<a id="simready-dsx"></a>
### simready-dsx

AI 팩토리 디지털 트윈용 SimReady 자산.

**라이선스·접근:** CC BY 4.0; 공개.  
**공식 데이터셋 카드:** [simready-dsx](https://huggingface.co/datasets/nvidia/simready-dsx)

<a id="isaacsim-assets"></a>
### isaacsim-assets

Isaac Sim 자산 및 예제 콘텐츠.

**라이선스·접근:** 라이선스 미확인.  
**공식 데이터셋 카드:** [isaacsim-assets](https://huggingface.co/datasets/nvidia/isaacsim-assets)

<a id="physicalai-simready-warehouse-01"></a>
### PhysicalAI-SimReady-Warehouse-01

OpenUSD 기반 창고 시뮬레이션 장면.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-SimReady-Warehouse-01](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01)

![SimReady warehouse simulation scene](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01/resolve/main/images/PhysicalAI_Dataset_01.png)

이미지 출처: [PhysicalAI-SimReady-Warehouse-01](https://huggingface.co/datasets/nvidia/PhysicalAI-SimReady-Warehouse-01)

<a id="physicalai-digitalcousin-assets"></a>
### PhysicalAI-DigitalCousin-Assets

GR1 탁상 작업 환경용 시뮬레이션 자산.

**라이선스·접근:** CC-BY-NC-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-DigitalCousin-Assets](https://huggingface.co/datasets/nvidia/PhysicalAI-DigitalCousin-Assets)

<a id="physicalai-robotics-manipulation-objects-kitchen-mjcf"></a>
### PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF

MJCF 형식의 주방 물체 자산.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF)

![PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF official example](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF/resolve/main/4x4_collage_images.png)

이미지 출처: [PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects-Kitchen-MJCF)

<a id="physicalai-robotics-physicalassets-vomp"></a>
### PhysicalAI-Robotics-PhysicalAssets-VoMP

시각 기반 로봇 동작계획 연구용 자산.

**라이선스·접근:** 라이선스 미확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-PhysicalAssets-VoMP](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-PhysicalAssets-VoMP)

<a id="physicalai-robotics-physicalassets-vomp-eval"></a>
### PhysicalAI-Robotics-PhysicalAssets-VoMP-Eval

시각 기반 동작계획 평가용 자산.

**라이선스·접근:** 라이선스 미확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-PhysicalAssets-VoMP-Eval](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-PhysicalAssets-VoMP-Eval)
