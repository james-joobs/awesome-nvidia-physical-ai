# Cosmos Predict2 code

[전체 목록](../../README.ko.md) · [English](../en/cosmos-predict2.md)

Cosmos Predict2는 주어진 조건에서 시각적 월드 상태를 생성한다. 아카이브된 공식 저장소에는 Text2Image와 Video2World 체크포인트, 로봇 영상 및 행동 조건을 위해 후학습한 예제가 따로 있다.

## 공식 아키텍처와 입력 규격

![NVIDIA Cosmos Predict2 아키텍처](https://raw.githubusercontent.com/nvidia-cosmos/cosmos-predict2/main/assets/cosmos-predict-diagram.png)

그림에서 생성 조건이 시각 결과로 이어지는 경로를 따라가면 된다. Video2World는 이미지 한 장이나 영상의 여러 프레임으로 시각 맥락을 잡고, 텍스트에 따라 장면을 생성한다. 여러 프레임은 움직임 단서도 준다. 기본 예제는 영상과 텍스트를 받는다. 행동을 조건으로 지정하려면 해당 체크포인트와 입력 형식을 선택한다. [공식 구조와 모델](https://github.com/nvidia-cosmos/cosmos-predict2#models) · [Video2World 추론 문서](https://github.com/nvidia-cosmos/cosmos-predict2/blob/main/documentations/inference_video2world.md)

Video2World 내부에서는 확산 Transformer가 영상 잠재 표현의 노이즈를 제거한다. 조건 프레임의 잠재 표현은 시간 축에서 생성할 프레임과 연결된다. 텍스트 조건은 교차 어텐션을 통해 생성 과정에 들어가고, 적응형 정규화는 확산 단계의 시간 정보를 전달한다. 해상도와 프레임 속도는 체크포인트에 따라 달라진다. 예를 들어 공식 720p 16 FPS 모델은 1280 × 704 프레임을 출력한다. [공식 2B 모델 카드와 입출력 규격](https://huggingface.co/nvidia/Cosmos-Predict2-2B-Video2World#model-architecture)

![공식 Video2World 예제의 조건 이미지](https://raw.githubusercontent.com/nvidia-cosmos/cosmos-predict2/main/assets/video2world/example_input.jpg)

공식 빠른 시작의 시각 입력이다. 생성된 후속 장면을 검토할 때 이 초기 관측과 비교할 수 있다. [공식 빠른 시작](https://github.com/nvidia-cosmos/cosmos-predict2#quick-start)

## 활용 예시 — 로봇 영상 이어 만들기

그리퍼의 초기 프레임과 다음 행동을 설명하는 프롬프트로 시작한다. 동일한 프롬프트와 시드를 유지하면서 정지 이미지와 다중 프레임을 각각 입력한다. 생성 영상과 저장된 프롬프트에 체크포인트와 조건 프레임 수를 함께 기록한다. 물체가 유지되는지, 카메라가 갑자기 이동하지 않는지, 그리퍼가 대상에 정렬된 상태로 움직이는지 비교한다. 배치 입력에는 공식 예제의 JSON 형식으로 영상, 프롬프트, 출력 경로를 묶는다. 행동 조건을 사용하는 경우 행동 값의 정규화와 로봇 형태를 먼저 맞춘다. [추론·후학습 예제](https://github.com/nvidia-cosmos/cosmos-predict2#user-guide)

저장소는 2025년 12월 아카이브됐으며 Predict2.5를 안내한다. 코드는 Apache-2.0이며 안내된 가중치는 NVIDIA Open Model License를 따른다. [저장소 및 이용 조건](https://github.com/nvidia-cosmos/cosmos-predict2#license-and-contact)
