# cuRobo
[← 목록으로](../../README.ko.md) · [English](../en/curobo.md)

GPU 기반 로봇 역기구학·동작계획.

**공식 자료:** [저장소](https://github.com/NVlabs/curobo)  
**라이선스와 범위:** 저장소 Apache-2.0; AutoData 배포의 특정 구성 요소는 별도 약관 확인.

![cuRobo robot collision geometry](https://raw.githubusercontent.com/NVlabs/curobo/main/docs/images/franka_spheres.png)
*이미지 출처: [Repository](https://github.com/NVlabs/curobo)*

## 구성과 워크플로

아래는 활용 흐름을 이해하기 위한 개념도입니다. 공식 아키텍처나 자동 연결을 뜻하지 않습니다.

**로봇 모델 + 충돌 형상 + 목표 자세 → 역기구학·동작계획 → 충돌 검사된 궤적**

## 활용 사례

장애물을 피해 목표 자세로 이동하는 로봇팔 경로를 계획합니다.

## 연결 기술

Isaac Sim, AutoData, Isaac ROS.

버전과 사용 환경에 따라 호환성, 데이터 형식, 모델 및 의존성 조건을 공식 자료에서 확인하세요.
