# AutoData
[← 목록으로](../../README.ko.md) · [English](../en/autodata.md)

소수의 시연을 다양한 작업 조건의 궤적으로 확장.

**공식 자료:** [저장소](https://github.com/isaac-sim/AutoData)  
**라이선스와 범위:** Apache-2.0; Isaac Sim 및 특정 cuRobo 구성 요소 별도 조건.

![AutoData demonstration generation](https://media.githubusercontent.com/media/isaac-sim/AutoData/main/docs/images/autodata.gif)
*이미지 출처: [Repository](https://github.com/isaac-sim/AutoData)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**초기 시연 → 작업·장면 조건 변화 → 궤적 생성 → 검토·학습**

## 주요 구성과 공식 아키텍처

![AutoData 시스템 아키텍처](https://raw.githubusercontent.com/isaac-sim/AutoData/main/docs/images/System_Architecture.svg)

*이미지 출처: [Official repository](https://github.com/isaac-sim/AutoData)*

AutoData는 소수의 시연을 바탕으로 작업 조건을 바꾼 추가 로봇 궤적을 생성합니다. 사용 가능한 환경과 로봇 구성은 시뮬레이션·계획 의존성에 따라 달라집니다. 생성한 궤적과 성공 조건을 검토한 뒤 학습 데이터에 포함하세요.

## 활용 사례

소수의 시연으로 다양한 로봇 조작 데이터를 만듭니다.

## 연결 기술

Isaac Sim, cuRobo, Isaac Lab.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
