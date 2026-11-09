# NeMo Guardrails

[← 전체 목록](../../README.ko.md) · [English](../en/nemo-guardrails.md)

모델 입력·검색 문맥·도구 실행·출력의 정책 검사.

![Guardrails 요청 흐름](https://raw.githubusercontent.com/NVIDIA-NeMo/Guardrails/develop/docs/_static/images/programmable_guardrails_flow.png)

모델·도구 호출 주변에서 애플리케이션 검사를 수행하는 위치를 보여 줍니다. [공식 그림 출처](https://github.com/NVIDIA-NeMo/Guardrails)

## 아키텍처와 데이터 흐름

설정에 따라 입력, 검색 문맥, 대화 흐름, 도구 실행이나 출력을 검사합니다. 런타임은 Colang 흐름과 별도의 안전·주제 분류 모델을 사용할 수 있습니다. 도구 검사는 입력과 실행 동작을 확인할 수 있는 애플리케이션 경계에 배치합니다.

## 물리 AI 활용 예시

VSS 에이전트의 정비 티켓에 원본 클립 ID와 허용된 목적지가 있는지 실행 검사로 확인합니다. 영향이 큰 작업에는 사람 검토를 두고, 조작된 이벤트와 도구 인자로 정책을 시험합니다.

## 검증할 항목

기록된 예제로 허용과 차단을 검증합니다. 물리 시스템의 로봇 동작 한계, 비상정지와 안전 검증은 별도로 관리합니다.

## 공개 범위와 라이선스

저장소 코드는 Apache-2.0입니다. 모델 가중치, 외부 서비스와 의존성에는 별도 조건이 적용될 수 있습니다.

## 공식 자료

- [저장소](https://github.com/NVIDIA-NeMo/Guardrails)
- [라이브러리 아키텍처와 검사 유형](https://docs.nvidia.com/nemo/guardrails/about-nemo-guardrails-library/how-it-works)
- [저장소 라이선스](https://github.com/NVIDIA-NeMo/Guardrails/blob/HEAD/LICENSE.md)

## 관련 가이드

[Metropolis / VSS](metropolis-vss.md) · [NVIDIA NeMo Platform](nemo-platform.md)
