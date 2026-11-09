# NeMo Curator

[← 전체 목록](../../README.ko.md) · [English](../en/nemo-curator.md)

텍스트·이미지·영상·오디오 데이터셋 분산 정제.

![NeMo Curator 파이프라인](https://raw.githubusercontent.com/NVIDIA-NeMo/Curator/main/fern/assets/images/architecture-diagram.png)

파이프라인의 데이터 처리 로직과 별도로 단계 구성과 자원 배정을 확인할 수 있습니다. [공식 그림 출처](https://github.com/NVIDIA-NeMo/Curator)

## 아키텍처와 데이터 흐름

Curator는 전처리, 점수 계산과 필터링을 조합 가능한 단계로 구성합니다. 파이프라인은 데이터와 자원을 기술하고 실행기가 각 단계를 스케줄링합니다. 공식 Xenna 실행기는 처리 단계를 Ray 액터 작업으로 변환합니다. NeMo Curator와 Cosmos Curator는 별도 저장소입니다. Cosmos Curator의 레시피는 영상 등 물리 AI 데이터에 초점을 둡니다.

## 물리 AI 활용 예시

작업자 음성이 포함된 센서 기록에서 전사와 클립 메타데이터를 준비하고 품질이 낮은 샘플을 걸러 학습 목록을 만듭니다. 영상 분할과 품질 평가가 핵심이라면 Cosmos Curator의 영상 레시피를 확인합니다.

## 검증할 항목

모달리티를 결합할 때 원본 ID와 촬영 시각을 보존합니다. 필터 전후에 샘플 보존율과 다양성을 비교합니다. 릴리스에 맞는 실행기와 의존성을 선택합니다.

## 공개 범위와 라이선스

저장소 코드는 Apache-2.0입니다. 모델 가중치, 외부 서비스와 의존성에는 별도 조건이 적용될 수 있습니다.

## 공식 자료

- [저장소](https://github.com/NVIDIA-NeMo/Curator)
- [영상 정제 아키텍처](https://docs.nvidia.com/nemo/curator/about/concepts/video/architecture)
- [저장소 라이선스](https://github.com/NVIDIA-NeMo/Curator/blob/HEAD/LICENSE)

## 관련 가이드

[Cosmos Curator](cosmos-curator.md) · [Cosmos Xenna](cosmos-xenna.md)
