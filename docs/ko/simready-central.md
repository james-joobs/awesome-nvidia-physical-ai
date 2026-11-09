# SimReady Central

[← 전체 목록](../../README.ko.md) · [English](../en/simready-central.md)

SimReady Central의 GitHub 저장소는 제출·검토 인덱스다. 기여자가 에셋 패키지를 자신의 Hugging Face 데이터셋에 두고, 검토받을 정확한 버전을 GitHub 제출에 기재한다.

## 아키텍처

| 구성 요소 | 역할과 데이터 경계 |
|---|---|
| 에셋 준비와 호스팅 | 제출 도구가 OpenUSD 에셋을 검사·패키징하고 기여자의 Hugging Face 데이터셋에 업로드한다. 패키지 정의에 메타데이터와 검증 근거를 담는다. |
| 고정 버전 제출 목록 | `submissions/<namespace>/<dataset>`의 파일에 Hugging Face 커밋 해시가 포함된 불변 패키지 정의 URL을 적는다. 갱신할 때는 최종 목록 전체를 제출한다. |
| PR 검증과 색인 | 자동 검사와 검토를 거쳐 병합한다. 승인된 데이터는 서비스와 라이선스 조건에 따라 검색에 포함될 수 있다. 패키지는 소유자가 보관한다. |

아래 공식 자료를 바탕으로 이 가이드에서 재구성한 그림입니다.

```mermaid
flowchart LR
    usd["OpenUSD 에셋과 검증 근거"]
    pkg["검증 및 패키징"]
    hf["소유자 Hugging Face 데이터셋 리비전"]
    index["PR의 고정 패키지 URL"]
    review["승인 검사와 검토"]
    browse["승인 인덱스와 검색"]
    usd --> pkg
    pkg --> hf
    hf --> index
    index --> review
    review --> browse
```

### 공식 그림과 예시

![NVIDIA 기여자 그림은 OEM 에셋 제작·검증에서 제출을 거쳐 개발자 검색으로 이어지는 흐름을 보여 준다.](https://cdn-uploads.huggingface.co/production/uploads/6abfe9e7d7cf09a9b38ef308/_o9mV5oHYpmPQzpHkzpDV.png)

NVIDIA 기여자 그림은 OEM 에셋 제작·검증에서 제출을 거쳐 개발자 검색으로 이어지는 흐름을 보여 준다. [그림 출처와 원문 설명](https://huggingface.co/blog/nvidia/simready-central-assets-robotics-ai-factories)

## 워크플로 예시

1. 그리퍼를 공개할 장비 제조사는 문서의 온보딩을 완료한다. 프로파일을 고르고 에셋을 검증한 뒤 라이선스·검증 자료와 함께 자신의 데이터셋에 패키징한다.
2. 대상 데이터셋 커밋에 고정된 패키지 정의 URL을 제출한다. 목록을 갱신할 때 계속 제공할 다른 패키지 줄도 유지한다.
3. 저장소의 로컬 라이브러리 워크플로로 소유자, 버전, 라이선스와 검증 등 제출 패키지 필드를 확인한다. 오류를 패키지에서 수정한 뒤 다시 검토를 요청한다.

## 검증 포인트

- 불변 커밋 URL을 쓴다. 변경될 수 있는 브랜치 URL은 검토한 에셋 재현을 어렵게 한다.
- 온보딩, 승인, 검색 등록은 별도 단계다. 제출 전에 적용 라이선스와 승인 기준을 확인한다.

## 라이선스와 범위

제출 저장소에는 Apache-2.0 라이선스가 있다. 온보딩, 호스팅 서비스와 제출 에셋 패키지의 이용 조건은 별도다.

## 관련 가이드

[SimReady Central Library](simready-central-library.md) · [SimReady Foundation](simready-foundation.md)

## 공식 자료

- [공식 제출 인덱스와 흐름](https://github.com/NVIDIA-Omniverse/simready-central)
- [승인 기준](https://github.com/NVIDIA-Omniverse/simready-central/blob/main/docs/acceptance-criteria.md)
- [제출 패키지 로컬 검사](https://github.com/NVIDIA-Omniverse/simready-central/blob/main/docs/index-to-library-guide.md)
- [제출 저장소 라이선스](https://github.com/NVIDIA-Omniverse/simready-central/blob/main/LICENSE)
