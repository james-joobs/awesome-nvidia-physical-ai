# NeMo Agent Toolkit

[← 전체 목록](../../README.ko.md) · [English](../en/nemo-agent-toolkit.md)

에이전트 연결·프로파일링 도구와 공식 로봇 합성 데이터 사례.

> **사용 중단 안내, 2026년 말 지원 종료 예정**

![로봇 합성 데이터를 위한 다중 에이전트 흐름](https://developer-blogs.nvidia.com/wp-content/uploads/2025/06/Multi-agent-SDG-workflow-1024x505.png)

시나리오 프롬프트와 USD 장면 생성, 이후 영상 처리가 연결되는 구조입니다. [공식 그림 출처](https://developer.nvidia.com/blog/scale-realistic-robot-simulation-using-the-nvidia-nemo-agent-toolkit-for-physical-ai/)

## 아키텍처와 데이터 흐름

NVIDIA 로봇 시뮬레이션 사례는 시나리오 프롬프트로 장면을 변형합니다. 에이전트가 USD 에셋 검색과 장면 수정 도구를 호출합니다. 화면 없이 실행한 Omniverse 스테이지가 로봇 시퀀스를 렌더링합니다. Cosmos Transfer로 외관을 바꾸고 Cosmos Reason으로 생성 영상을 검토할 수 있습니다. 단계마다 프롬프트, 에셋 또는 영상이 별도 인터페이스를 통과합니다.

## 물리 AI 활용 예시

고정된 작은 장면에서 장애물 배치 몇 가지를 만들어 봅니다. 변형별 프롬프트, 스테이지 버전, 에셋과 영상을 저장합니다. 학습 샘플로 쓰기 전에 의도한 위치와 생성 영상을 대조합니다.

## 검증할 항목

NVIDIA는 2026년 10월 이 도구를 사용 중단 대상으로 지정했고 2026년 말 지원 종료를 예고했습니다. 관측, 에이전트 실행, 평가에 맞는 후속 도구는 공식 전환 안내를 참고합니다. 사례의 모델·서비스는 해당 버전 기준입니다.

## 공개 범위와 라이선스

저장소 코드는 Apache-2.0입니다. 모델 가중치, 외부 서비스와 의존성에는 별도 조건이 적용될 수 있습니다.

## 공식 자료

- [저장소](https://github.com/NVIDIA/NeMo-Agent-Toolkit)
- [로봇 합성 데이터 공식 사례](https://developer.nvidia.com/blog/scale-realistic-robot-simulation-using-the-nvidia-nemo-agent-toolkit-for-physical-ai/)
- [지원 종료 및 전환 안내](https://docs.nvidia.com/nemo/agent-toolkit/1.9/resources/migration-guide.html)
- [저장소 라이선스](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/HEAD/LICENSE.md)

## 관련 가이드

[NeMo Relay](nemo-relay.md) · [NeMo Fabric](nemo-fabric.md) · [NeMo Helix](nemo-helix.md) · [Replicator](replicator.md)
