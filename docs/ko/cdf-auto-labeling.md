# CDF Auto Labeling (formerly paidf-auto-labeling)

[전체 목록](../../README.ko.md) · [English](../en/cdf-auto-labeling.md)

CDF Auto Labeling은 이미지와 영상에 적용할 주석 작업을 조합한다. 실행기가 지정된 순서에 따라 서비스를 실행하고, 각 단계는 공용 장면 디렉터리에서 파일을 읽고 쓴다.

## 공식 아키텍처 읽기

![NVIDIA CDF Auto Labeling 워크스페이스 구성도](https://raw.githubusercontent.com/NVIDIA/cdf-auto-labeling/main/docs/assets/architecture_diagram_cdf_ual.png)

실행기가 서비스를 호출하면 서비스는 작업 패키지를 실행한다. 탐지·추적, 캡션, 시각 질의응답, 그라운딩, 학습 내보내기는 각각 장면 파일 규격에 맞춰 결과를 남긴다. JSONL의 DataEntry는 id로 샘플을, media_path로 원본을, data_path로 DAFT 장면 경로를 지정한다. 장면 디렉터리의 sidecars/raw.<ext>에는 원본을 보존할 수 있고, sidecars/active.<ext>에는 다음 단계에서 사용할 변환 미디어가 들어갈 수 있다. [서비스 개요](https://github.com/NVIDIA/cdf-auto-labeling/blob/main/docs/developer/architecture/services-overview.md) · [아티팩트 규격](https://github.com/NVIDIA/cdf-auto-labeling/blob/main/docs/developer/architecture/artifact-contract.md)

```json
{"id":"warehouse-clip-17","media_path":"/data/clip17.mp4","data_path":"/output/warehouse-clip-17"}
```

이 예제 레코드는 원본 영상 한 개와 단계별 출력 교환 경로를 연결한다. 어떤 주석 파일이 만들어지는지는 선택한 서비스에 따라 달라진다.

## 활용 예시 — 교차하는 지게차 추적

지게차 두 대가 서로 지나가는 영상에서 탐지와 추적을 실행한다. 후속 작업에 따라 그라운딩이나 캡션을 추가한 뒤 학습용 데이터로 내보낸다. 지게차가 겹치는 프레임에서 트랙 ID가 뒤바뀌는지 본다. 전처리로 영상이 바뀌었다면 여러 배치를 합치기 전에 좌표와 타임스탬프를 현재 사용 영상에 대조한다. [공식 빠른 시작](https://github.com/NVIDIA/cdf-auto-labeling#quick-start)

코드는 Apache-2.0이다. 모델, 엔드포인트, 의존성은 각 이용 조건을 따른다. [라이선스와 재배포 안내](https://github.com/NVIDIA/cdf-auto-labeling#license-and-contributions)
