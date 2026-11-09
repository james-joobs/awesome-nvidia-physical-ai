# 로봇 시연과 동작

[전체 목록](../../README.ko.md) · [English](../en/datasets-robot-demonstrations.md)

실물 원격 조작, 시뮬레이션 궤적, 파지 데이터와 벤치마크 작업을 모았다. 정책 학습에서는 로봇 형태와 작업에 연결된 관측·행동 시계열을 한 에피소드로 읽는 경우가 많다.

## 공식 카드의 스키마 비교

| 카드 | 제공 데이터 | 통합 시 확인 |
|---|---|---|
| [GR00T Teleop G1](#physicalai-robotics-gr00t-teleop-g1) | MP4, HDF5에 관측 및 행동 벡터 43차원. 카드 기준 640 × 480 RGB, 20 FPS | 전신과 손 관절의 순서를 확인하고 영상과 궤적을 짝지음 |
| [Manipulation Kitchen](#physicalai-robotics-manipulation-kitchen) | 서랍과 식기세척기 열기 등 시뮬레이션 작업의 LeRobot 형식. 카드에 행동 34차원, 물체 상태 관측 13차원과 카메라 스트림 명시 | 머리, 손목, 외부 카메라 중 정책에 쓸 시점을 고르고 관절 및 관측 정의를 맞춤 |
| [GraspGen](#physicalai-robotics-graspgen) | 물체 자산과 파지 데이터 | 그리퍼 형상, 물체 좌표계와 단위 확인 |
| [GR00T Eval](#physicalai-robotics-gr00t-eval) | 평가 자산과 작업 | 평가 규약을 확인하고 학습 데이터와 분리 |

![공식 시뮬레이션 주방의 월드 카메라 롤아웃](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen/resolve/main/assets/episode_000004_world.gif)

공식 주방 예제의 외부 월드 뷰다. 카드의 머리와 손목 뷰도 비교할 수 있다. 손목 카메라를 입력받는 정책에서는 월드 뷰 평가 화면과 물체의 보이는 영역이나 움직임이 다르다. [공식 주방 카메라·스키마 예제](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen#dataset-format)

## 활용 예시 — 궤적 하나로 로더 검증

G1의 물체 옮기기 궤적 하나를 읽고 대응하는 MP4를 디코딩한다. 접촉 프레임을 기준으로 주요 관절의 행동과 관측을 그려 보거나 재생한다. 차원, 관절 순서, 단위, 샘플링 시점과 제어기에 맞는 행동 표현인지 확인한다. 실측과 합성을 섞을 때는 로봇 형태와 출처를 남기고 원본 에피소드 또는 수집 세션 단위로 분할한다. [공식 G1 카드](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-G1) · [GR00T 모델](groot-model.md)

## 데이터셋 상세

<a id="physicalai-robotics-gr00t-x-embodiment-sim"></a>
### PhysicalAI-Robotics-GR00T-X-Embodiment-Sim

여러 로봇 형태의 GR00T 후학습용 시뮬레이션 궤적.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-GR00T-X-Embodiment-Sim](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-X-Embodiment-Sim)

<a id="physicalai-gr00t-tuned-tasks"></a>
### PhysicalAI-GR00T-Tuned-Tasks

GR1 탁상 조작을 위한 멀티모달 궤적.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-GR00T-Tuned-Tasks](https://huggingface.co/datasets/nvidia/PhysicalAI-GR00T-Tuned-Tasks)

<a id="physicalai-robotics-gr00t-gr1"></a>
### PhysicalAI-Robotics-GR00T-GR1

GR1 로봇 작업을 촬영한 제3자 시점 영상.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-GR00T-GR1](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-GR1)

<a id="physicalai-robotics-gr00t-teleop-g1"></a>
### PhysicalAI-Robotics-GR00T-Teleop-G1

원격 조작으로 수집한 Unitree G1 시연.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-GR00T-Teleop-G1](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-G1)

![PhysicalAI-Robotics-GR00T-Teleop-G1 official example](https://cdn-uploads.huggingface.co/production/uploads/67b8da81d01134f89899b4a7/nnQttu2PywkTLVMcuNL42.jpeg)

이미지 출처: [PhysicalAI-Robotics-GR00T-Teleop-G1](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-G1)

<a id="gr00t-n1-7-appletoplate"></a>
### GR00T-N1.7-AppleToPlate

G1 사과 옮기기 원격 조작 시연.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [GR00T-N1.7-AppleToPlate](https://huggingface.co/datasets/nvidia/GR00T-N1.7-AppleToPlate)

<a id="physicalai-robotics-gr00t-teleop-sim"></a>
### PhysicalAI-Robotics-GR00T-Teleop-Sim

시뮬레이션 원격 조작 시연.

**라이선스·접근:** CC-BY-NC-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-GR00T-Teleop-Sim](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-Sim)

<a id="physicalai-robotics-gr00t-teleop-gr1"></a>
### PhysicalAI-Robotics-GR00T-Teleop-GR1

GR1 원격 조작 데이터.

**라이선스·접근:** CC-BY-NC-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-GR00T-Teleop-GR1](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Teleop-GR1)

<a id="physicalai-robotics-gr00t-eval"></a>
### PhysicalAI-Robotics-GR00T-Eval

GR00T 로봇 평가 데이터.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-GR00T-Eval](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Eval)

![PhysicalAI-Robotics-GR00T-Eval official example](https://huggingface.co/datasets/nvidia/EVAL-175/resolve/main/gr1_behavior/0_Open%20the%20box.png)

이미지 출처: [PhysicalAI-Robotics-GR00T-Eval](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GR00T-Eval)

<a id="physicalai-robotics-manipulation-kitchen"></a>
### PhysicalAI-Robotics-Manipulation-Kitchen

LeRobot 형식의 주방 조작 시뮬레이션 궤적.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-Manipulation-Kitchen](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen)

![Robot dishwasher manipulation demonstration](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen/resolve/main/assets/episode_000009.gif)

이미지 출처: [PhysicalAI-Robotics-Manipulation-Kitchen](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen)

<a id="physicalai-robotics-manipulation-singlearm"></a>
### PhysicalAI-Robotics-Manipulation-SingleArm

단일 로봇팔 조작 시뮬레이션 데이터.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-Manipulation-SingleArm](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-SingleArm)

<a id="physicalai-robotics-manipulation-objects"></a>
### PhysicalAI-Robotics-Manipulation-Objects

물체 집기·놓기 시뮬레이션 궤적.

**라이선스·접근:** 라이선스 미확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-Manipulation-Objects](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects)

![PhysicalAI-Robotics-Manipulation-Objects official example](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects/resolve/main/assets/episode_000028.gif)

이미지 출처: [PhysicalAI-Robotics-Manipulation-Objects](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Objects)

<a id="physicalai-robotics-manipulation-augmented"></a>
### PhysicalAI-Robotics-Manipulation-Augmented

합성·주석 처리된 큐브 쌓기 시연.

**라이선스·접근:** 라이선스 미확인; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-Manipulation-Augmented](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Augmented)

<a id="physicalai-robotics-manipulation-kitchen-demos"></a>
### PhysicalAI-Robotics-Manipulation-Kitchen-Demos

사람의 원격 조작으로 수집한 주방 작업 시연.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-Manipulation-Kitchen-Demos](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen-Demos)

<a id="physicalai-robotics-graspgen"></a>
### PhysicalAI-Robotics-GraspGen

여러 그리퍼와 물체에 대한 파지 후보.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-GraspGen](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GraspGen)

![PhysicalAI-Robotics-GraspGen official example](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GraspGen/resolve/main/assets/cover.png)

이미지 출처: [PhysicalAI-Robotics-GraspGen](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-GraspGen)

<a id="physicalai-robotics-locomanipulation-grail"></a>
### PhysicalAI-Robotics-Locomanipulation-GRAIL

로봇 이동·조작 동작 데이터.

**라이선스·접근:** CC-BY-NC-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-Locomanipulation-GRAIL](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Locomanipulation-GRAIL)

![PhysicalAI-Robotics-Locomanipulation-GRAIL official example](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Locomanipulation-GRAIL/resolve/main/assets/videos/pickup_table.gif)

이미지 출처: [PhysicalAI-Robotics-Locomanipulation-GRAIL](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Locomanipulation-GRAIL)

<a id="physicalai-robotics-open-h-embodiment"></a>
### PhysicalAI-Robotics-Open-H-Embodiment

수술 로봇·초음파 자율화 데이터 이니셔티브.

**라이선스·접근:** CC-BY-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-Open-H-Embodiment](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Open-H-Embodiment)

<a id="physicalai-robotics-mindmap-gr1-drill-in-box"></a>
### PhysicalAI-Robotics-mindmap-GR1-Drill-in-Box

GR1 드릴을 상자에 넣는 작업 궤적.

**라이선스·접근:** CC-BY-NC-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-mindmap-GR1-Drill-in-Box](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-mindmap-GR1-Drill-in-Box)

<a id="physicalai-robotics-mindmap-gr1-stick-in-bin"></a>
### PhysicalAI-Robotics-mindmap-GR1-Stick-in-Bin

GR1 막대를 통에 넣는 작업 궤적.

**라이선스·접근:** CC-BY-NC-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-mindmap-GR1-Stick-in-Bin](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-mindmap-GR1-Stick-in-Bin)

<a id="physicalai-robotics-mindmap-franka-mug-in-drawer"></a>
### PhysicalAI-Robotics-mindmap-Franka-Mug-in-Drawer

Franka 머그잔을 서랍에 넣는 작업 궤적.

**라이선스·접근:** CC-BY-NC-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-mindmap-Franka-Mug-in-Drawer](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-mindmap-Franka-Mug-in-Drawer)

<a id="physicalai-robotics-mindmap-franka-cube-stacking"></a>
### PhysicalAI-Robotics-mindmap-Franka-Cube-Stacking

Franka 큐브 쌓기 작업 궤적.

**라이선스·접근:** CC-BY-NC-4.0; 공개.  
**공식 데이터셋 카드:** [PhysicalAI-Robotics-mindmap-Franka-Cube-Stacking](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-mindmap-Franka-Cube-Stacking)
