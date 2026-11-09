# Alpamayo

[← 전체 목록](../../README.ko.md) · [English](../en/alpamayo.md)

Alpamayo는 자율주행용 추론·행동 모델 계열입니다. R1 연구 아키텍처를 구체적인 예로 볼 수 있습니다. 다른 버전에 적용할 때는 모델 카드에서 구성과 입력 규약을 확인합니다.

![Alpamayo-R1 모델 아키텍처](https://arxiv.org/html/2511.00088v2/main_arch_1.png)

*다중 카메라와 자차 움직임이 VLM에 들어가는 경로를 따라가고 추론 토큰과 궤적 디코더의 웨이포인트를 구분해 보세요.* [공식 그림 출처](https://arxiv.org/html/2511.00088v2#S3)

![Alpamayo-R1 인과 추론 데이터 라벨링 파이프라인](https://arxiv.org/html/2511.00088v2/labeling_overview_new_2.png)

*주행 클립이 구체적인 판단과 연결된 라벨 데이터가 되는 과정을 보여줍니다. 추론과는 별도인 학습 데이터 흐름입니다.* [공식 그림 출처](https://arxiv.org/html/2511.00088v2#S3)

## 어떻게 동작하나

R1은 카메라 프레임과 자차 움직임 이력 등 관측을 바탕으로 추론과 궤적을 예측합니다. 비전 언어 백본에서 주행 근거를 생성하고 궤적 생성 구성 요소가 연속 웨이포인트를 출력합니다. 시뮬레이터 드라이버는 궤적을 받아 자차 상태를 진행할 수 있습니다. 추론 텍스트와 실제 움직임은 별도로 확인합니다.

## 실전 워크플로

부분적으로 가려진 장애물이나 복잡한 합류가 있는 AlpaSim 장면에 Alpamayo 지원 드라이버를 실행합니다. 생성 근거, 궤적과 롤아웃 지표를 함께 보고 같은 장면·경로의 기준 정책과 비교합니다.

## 검증할 항목

체크포인트가 받는 카메라, 문맥과 좌표계, 요구 메모리 및 접근 조건을 확인합니다. 설명의 그럴듯함과 궤적 품질·주행 동작을 독립적으로 평가합니다.

## 공개 범위와 라이선스

공개 가중치의 조건과 접근 절차는 모델 버전별 상이. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 자료

- [아키텍처와 워크플로 공식 문서](https://research.nvidia.com/labs/avg/publication/2025/12/alpamayo-r1/)
- [R1 모델 카드](https://huggingface.co/nvidia/Alpamayo-R1-10B)
- [AlpaSim 드라이버 튜토리얼](https://github.com/NVlabs/alpasim/blob/main/docs/TUTORIAL.md)
- [관련 공식 자료 · github.com](https://github.com/NVlabs/alpamayo-recipes)
