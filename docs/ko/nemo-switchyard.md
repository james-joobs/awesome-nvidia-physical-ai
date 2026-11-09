# NeMo Switchyard

[← 전체 목록](../../README.ko.md) · [English](../en/nemo-switchyard.md)

LLM 에이전트와 애플리케이션의 모델 요청 라우팅.

![Switchyard 구성 요소](https://raw.githubusercontent.com/NVIDIA-NeMo/Switchyard/main/docs/assets/switchyard-components.png)

공식 구성도에서 호스트 또는 게이트웨이와 모델 선택·상위 모델 호출의 경계를 확인할 수 있습니다. [공식 그림 출처](https://github.com/NVIDIA-NeMo/Switchyard)

## 아키텍처와 데이터 흐름

Switchyard는 애플리케이션의 작업 로직과 모델 선택을 분리합니다. 호스트는 요청, 사용 가능한 모델 목록과 라우팅 전략을 라이브러리에 전달합니다. 작업 기반 라우팅은 모델에 요청 분류를 맡길 수 있고 단계 기반 라우팅은 최근 도구 사용을 참고합니다. 호스트가 상위 모델 호출을 수행하고 라우팅 결과를 사용합니다. 게이트웨이 통합에서는 OpenAI·Anthropic 요청, 응답과 스트림 형식을 변환할 수 있습니다.

## 물리 AI 활용 예시

설비 검사 보조 에이전트에서 이미지·영상 분석은 VSS처럼 영상 입력을 처리하는 서비스에 맡깁니다. 후속 텍스트 요약과 보고서 작성 요청을 모델 풀에 라우팅합니다. 동일 클립과 프롬프트로 고정 모델과 라우팅 구성의 결과를 비교합니다.

## 검증할 항목

보고서가 성공적으로 완성된 건을 기준으로 비용과 지연을 측정합니다. 도구 호출, 스트리밍, 상위 서비스 오류와 지원 입력을 함께 검증합니다. 독립 서버는 데모 및 로컬 평가용입니다. 배포 시 사용할 게이트웨이 통합과 버전을 확인합니다.

## 공개 범위와 라이선스

저장소 코드는 Apache-2.0입니다. 모델 가중치, 외부 서비스와 의존성에는 별도 조건이 적용될 수 있습니다.

## 공식 자료

- [저장소](https://github.com/NVIDIA-NeMo/Switchyard)
- [아키텍처](https://nvidia-nemo.github.io/Switchyard/architecture/)
- [Relay 통합](https://github.com/NVIDIA-NeMo/Switchyard/blob/main/docs/integrations/nemo_relay.md)
- [저장소 라이선스](https://github.com/NVIDIA-NeMo/Switchyard/blob/HEAD/LICENSE)

## 관련 가이드

[NeMo Relay](nemo-relay.md) · [Metropolis / VSS](metropolis-vss.md)
