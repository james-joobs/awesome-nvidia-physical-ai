# OSMO

[전체 목록](../../README.ko.md) · [English](../en/osmo.md)

OSMO는 컨테이너로 실행되는 Physical AI 작업을 스케줄링한다. 워크플로에 의존성과 필요한 자원을 선언하고, 풀에서 작업이 실행될 위치를 정한다. 서로 다른 장비에서 실행되는 단계는 아티팩트를 통해 연결할 수 있다.

## 공식 배포 아키텍처 읽기

![NVIDIA OSMO 배포 아키텍처](https://raw.githubusercontent.com/NVIDIA/OSMO/main/docs/deployment_guide/introduction/deployment_architecture.svg)

요청이 서비스 클러스터에 들어가는 경로를 본다. Core Service가 요청을 검증하고 관리하며, Worker가 실행을 조율한다. 각 컴퓨트 클러스터의 Backend Operator가 작업 자원을 만들고 모니터링한다. 실행 상태는 제어 영역으로 돌아온다. 제어와 컴퓨트는 논리적 경계이며 지원되는 통합 구성에서는 같은 클러스터에 배치할 수도 있다. [공식 배포 아키텍처](https://nvidia.github.io/OSMO/main/deployment_guide/introduction/architecture.html)

![NVIDIA OSMO 워크플로 실행 시퀀스](https://raw.githubusercontent.com/NVIDIA/OSMO/main/docs/deployment_guide/introduction/workflow_sequence.svg)

이 그림은 제출, 스케줄링, 백엔드 상태 전환을 순서대로 보여준다. 작업이 자원을 기다리는지, 백엔드에 할당돼 실행 중인지 구분할 때 참고할 수 있다. [공식 배포 가이드](https://github.com/NVIDIA/OSMO/blob/main/docs/deployment_guide/introduction/architecture.rst)

## 활용 예시 — 로봇 학습과 평가를 단계별로 실행

시뮬레이터 롤아웃 생성, 정책 학습, 분리된 데이터에서의 평가를 별도 작업으로 둔다. 생성 단계에서 버전이 붙은 데이터셋을, 학습 단계에서 체크포인트를 기록한다. 평가 단계에는 해당 체크포인트와 평가용 설정을 전달한다. GPU 작업이 대기하면 풀과 자원 요청을 확인한다. 실행은 됐지만 체크포인트를 읽지 못하면 저장소와 앞 단계 결과를 확인한다. [공식 사용자 가이드](https://nvidia.github.io/OSMO/main/user_guide/) · [Isaac Lab](isaac-lab.md)

OSMO는 Apache-2.0이다. 컨테이너 이미지, 클라우드 서비스, 시뮬레이터와 학습 도구에는 각 이용 조건이 적용된다. [공식 저장소](https://github.com/NVIDIA/OSMO)
