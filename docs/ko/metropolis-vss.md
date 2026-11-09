# Metropolis / VSS

[← 전체 목록](../../README.ko.md) · [English](../en/metropolis-vss.md)

Metropolis는 NVIDIA의 영상 AI 생태계입니다. Video Search and Summarization Blueprint(VSS)는 영상 분석, 타임스탬프 기반 추론, 에이전트 검색을 위한 참조 구성을 제공합니다.

![VSS 전체 아키텍처](https://docs.nvidia.com/vss/_fern-files/_img/e3a2810a613f30c365cd8ad42ca684fad69f222838e3d9e49ec4226044fba0de.webp)

*실시간 특징 추출, 분석, 에이전트 워크플로가 나뉘고 기록과 영상 근거가 이들을 연결합니다.* [공식 그림 출처](https://docs.nvidia.com/vss)

![VSS 파일 요약 아키텍처](https://docs.nvidia.com/vss/_fern-files/_img/6bb9edc3e4cd755a499d9dfb3bd00f777d5bc3e06186d02b1f2909770f025206.webp)

*파일 업로드에서 VLM 이벤트와 통합 요약까지 따라가 보세요. 타임스탬프로 각 이벤트를 원본 영상과 연결합니다.* [공식 그림 출처](https://docs.nvidia.com/vss/system-components/vision-microservices/video-summarization)

## 어떻게 동작하나

VSS는 실시간 특징 추출, 후속 분석, 에이전트·오프라인 처리를 분리합니다. DeepStream은 탐지와 추적 결과를, 실시간 VLM은 캡션이나 이벤트 후보를 생성할 수 있습니다. 하위 서비스는 타임스탬프로 기록과 영상 클립을 찾습니다. 파일 요약 구성에서는 영상을 구간으로 나누고 VLM을 호출해 시간별 이벤트를 저장한 뒤 요약 모델로 통합합니다. 스트리밍 구성에는 메시지 버스를 추가할 수 있습니다.

### 구성 요소별 입출력

| 구성 요소 | 입력 | 출력 |
|---|---|---|
| 실시간 CV 또는 VLM | 영상 스트림, 처리 구성과 모델 | 탐지, 추적, 캡션 또는 이벤트 후보 |
| 이벤트 저장 및 검증 | 타임스탬프 이벤트와 관련 클립 | 원본 참조가 있는 검색용 이벤트 |
| 에이전트와 요약 | 질문 또는 요약 요청과 검색한 근거 | 답변, 시간별 요약 또는 클립 참조 |

## 실전 워크플로

시설 영상을 짧게 색인한 뒤 이벤트 발생 시각이 포함된 요약을 요청합니다. 반환된 시각의 원본 클립을 열어 실제 관측과 답변을 대조합니다. 파일 처리부터 검증한 뒤 연속 RTSP 입력을 붙입니다.

## 검증할 항목

이벤트 재현율, 오탐, 클립 시간 정렬과 처리 지연을 따로 측정합니다. 하위 기록에서 탐지 원본과 모델 설명, 검증된 이벤트를 구별합니다. 지원 서비스 이미지와 배포 구성을 확인합니다.

## 공개 범위와 라이선스

플랫폼·서비스; 개별 SDK·모델의 조건 별도. 사용 전 해당 버전과 모델·데이터·바이너리·의존성의 조건을 각각 확인한다.

## 공식 자료

- [아키텍처와 워크플로 공식 문서](https://docs.nvidia.com/vss)
- [영상 요약 배포 구성](https://docs.nvidia.com/vss/system-components/vision-microservices/video-summarization)
- [관련 공식 자료 · developer.nvidia.com](https://developer.nvidia.com/metropolis)

## 연관 도구

VSS와 문서 RAG를 결합한 공식 사례는 [NemoClaw](nemoclaw.md)를 참고하세요. [NeMo Retriever Library](nemo-retriever.md)는 문서 근거 파이프라인을, [NeMo Switchyard](nemo-switchyard.md)는 후속 모델 요청을 라우팅하는 활용 예를 다룹니다.
