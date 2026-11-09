# CDF Orchestration

[← 전체 목록](../../README.ko.md) · [English](../en/cdf-orchestration.md)

CDF Orchestration은 Kubernetes에서 참조 블루프린트를 Airflow DAG로 실행한다. 빌드한 Airflow 컨트롤러 이미지에 DAG와 플러그인을 묶는다. 개별 작업은 추론 서비스를 배포하거나 배치 처리를 실행할 수 있다.

## 공식 제어 및 실행 흐름

![NVIDIA CDF Orchestration 아키텍처](https://raw.githubusercontent.com/NVIDIA/cdf-orchestration/main/docs/assets/architecture_diagram.png)

Airflow 컨트롤러는 작업 의존성을 관리하고, Kubernetes에서는 작업과 클러스터 내부 서비스가 실행된다. 객체 스토리지에는 입력과 결과 파일이 있다. 공식 문서에 있는 OSMO 실행 경로는 외부 모델 엔드포인트를 사용한다. [공식 아키텍처](https://github.com/NVIDIA/cdf-orchestration#architecture) · [공식 시작 문서](https://github.com/NVIDIA/cdf-orchestration/blob/main/docs/getting-started.md)

![NVIDIA SMT 결함 생성 워크플로](https://raw.githubusercontent.com/NVIDIA/cdf-orchestration/main/docs/defect-image-generation/assets/smt-workflow.png)

SMT 블루프린트에서 각 작업의 역할을 볼 수 있다. 시뮬레이션에서 주석이 붙은 기판과 부품을 렌더링하고, 증강으로 외관을 조정한 뒤 결함 예시를 늘린다. 중간 결과가 분리돼 있어 단계별로 검토하거나 재실행할 수 있다. [공식 SMT 블루프린트](https://github.com/NVIDIA/cdf-orchestration/blob/main/docs/defect-image-generation/getting-started.md)

## 활용 예시 — 결함 생성 실행 실패 진단

작은 기판 작업의 DAG 이미지와 모델 엔드포인트를 고정하고, 장면, 작업 구성, 출력 경로를 기록한다. 후속 단계가 실패하면 중간 렌더와 작업 로그를 열어 장면·구성 문제, 저장소 접근 오류, 엔드포인트 오류를 구분한다. 실패 작업을 재개하거나 학습 데이터를 공개하기 전에 산출물 개수와 샘플 ID를 맞춰 본다.

저장소는 Apache-2.0이다. 실행 서비스, 모델 엔드포인트, 외부 의존성의 조건은 별도로 확인한다. [공식 이용 조건](https://github.com/NVIDIA/cdf-orchestration#license-and-contributions)
