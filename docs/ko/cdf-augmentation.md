# CDF Augmentation (formerly paidf-augmentation)

[전체 목록](../../README.ko.md) · [English](../en/cdf-augmentation.md)

CDF Augmentation은 이미지, 영상, 텍스트 변환을 YAML로 구성하는 클라이언트 파이프라인이다. 생성과 선택적 캡션 단계는 설정에 지정한 HTTP 엔드포인트를 호출한다. 가중치는 추론 서버에서 관리한다.

## 공식 파이프라인 읽기

![NVIDIA CDF Augmentation 파이프라인](https://raw.githubusercontent.com/NVIDIA/cdf-augmentation/main/docs/Augmentation_v1.1.0.png)

미디어와 프롬프트가 엔드포인트 호출로 들어가고 생성 후보가 검증 단계로 이어지는 경로를 보면 된다. 품질 검사 실패 시 시드를 바꿔 다시 생성할 수 있다. 외부 서비스 호출 실패는 별도 경로로 처리한다. [공식 파이프라인과 어댑터](https://github.com/NVIDIA/cdf-augmentation#pipeline-flow)

| 계층 | 설정 항목 |
|---|---|
| 원본 | 이미지, 영상 또는 텍스트와 YAML 실행 구성 |
| 프롬프트 | 고정 문구, 변수를 채운 템플릿, 프롬프트 파일 또는 모델 캡션 |
| 어댑터 | API와 역할. 예를 들어 NIM /v1/infer 또는 OpenAI 호환 영상 API |
| 평가 | 움직임 비교, 속성 검증 또는 Cosmos Evaluator Arbitrator 호출을 선택 |

## 활용 예시 — 행인의 움직임을 유지하며 날씨 변경

보행자 경로를 알고 있는 클립으로 날씨 변형을 생성한다. 엔드포인트 버전과 후보별 시드를 기록한다. 원하는 날씨가 반영됐는지 확인하고, 보행자 경로, 가림, 이벤트 시점을 원본과 대조한다. 움직임이 바뀌면 라벨을 검토하거나 다시 만든다. 추론 서버를 원격 또는 자체 운영할 수 있으며, 로컬 H.264 디코딩과 일부 정렬 단계에는 별도의 GPU 요구사항이 있다. [공식 설정 레시피](https://github.com/NVIDIA/cdf-augmentation/tree/main/configs/cookbook) · [실행 요구사항](https://github.com/NVIDIA/cdf-augmentation#requirements)

저장소 코드는 Apache-2.0이다. 사용하는 모델과 서비스의 조건을 확인한다. [공식 저장소](https://github.com/NVIDIA/cdf-augmentation)
