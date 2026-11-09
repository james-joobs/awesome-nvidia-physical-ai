# NVIDIA Warp

[← 전체 목록](../../README.ko.md) · [English](../en/nvidia-warp.md)

Warp는 Python으로 작성한 수치 계산 커널을 CPU 또는 CUDA GPU에서 병렬 실행할 코드로 컴파일한다. 배열, 기하 연산과 자동 미분을 제공해 시뮬레이션 프로젝트가 필요한 계산을 직접 구현할 수 있게 한다.

## 아키텍처

| 구성 요소 | 역할과 데이터 경계 |
|---|---|
| `@wp.kernel` / `wp.launch` | 커널에 논리 스레드 한 개가 수행할 작업을 정의한다. 실행 호출에서 반복 차원과 타입이 지정된 배열 및 매개변수를 전달한다. |
| 컴파일 및 캐시 | Warp가 Python 모듈의 커널과 함수를 대상 장치의 네이티브 코드로 변환한다. 모듈 캐시로 같은 컴파일을 반복하는 비용을 줄인다. |
| `wp.array`와 상호 운용 | 호스트 코드에서 배열을 만들고 배치 장치를 선택한다. Warp/PyTorch 연결은 호환 메모리를 공유할 수 있어 프레임워크 사이에 버퍼를 넘길 때 장치와 동기화가 중요하다. |
| `wp.Tape` | Tape가 미분 가능한 커널 호출과 배열 참조를 기록한다. 역방향 커널은 필요한 순방향 값을 읽어 기울기 버퍼에 누적한다. |

아래 공식 자료를 바탕으로 이 가이드에서 재구성한 그림입니다.

```mermaid
flowchart LR
    p["타입을 지정한 Python 커널"]
    c["모듈 컴파일과 캐시"]
    a["장치 배열"]
    k["순방향 병렬 실행"]
    loss["스칼라 손실"]
    t["Tape와 수반 커널"]
    g["입력 기울기"]
    p --> c
    c --> k
    a --> k
    k --> loss
    k --> t
    loss --> t
    t --> g
```

### 공식 그림과 예시

![Warp 공식 컴파일 흐름. 커널 선언을 장치 코드로 변환하며 Python 애플리케이션에서 배열 할당과 실행을 제어한다.](https://nvidia.github.io/warp/latest/_images/compiler_pipeline.svg)

Warp 공식 컴파일 흐름. 커널 선언을 장치 코드로 변환하며 Python 애플리케이션에서 배열 할당과 실행을 제어한다. [그림 출처와 원문 설명](https://nvidia.github.io/warp/latest/user_guide/programming_model.html)

![공식 Tape 그림은 순방향 커널 실행과 기울기를 전달하는 역방향 실행을 구분해 보여 준다.](https://nvidia.github.io/warp/latest/_images/tape.svg)

공식 Tape 그림은 순방향 커널 실행과 기울기를 전달하는 역방향 실행을 구분해 보여 준다. [그림 출처와 원문 설명](https://nvidia.github.io/warp/latest/user_guide/differentiability.html)

## 워크플로 예시

1. 스프링 상수 추정에 필요한 초기 위치, 속도, 강성 배열을 만든다. 상태를 진행하는 커널과 예측한 종점을 관측 종점과 비교하는 커널을 작성한다.
2. wp.Tape 안에서 커널을 실행하고 역전파에 필요한 상태를 보존한다. 손실에 대해 backward를 호출하고 강성 기울기를 최적화기에 전달한다.
3. 첫 사용 컴파일을 포함하는 준비 실행 후 정상 실행 시간을 잰다. 실행 순서가 반복된다면 데이터 흐름과 장치 배치를 확정한 뒤 그래프 캡처·재생을 검토한다.

## 검증 포인트

- Tape는 배열 참조를 기록한다. 반복 커널이 역전파에 필요한 값을 덮어쓰면 스텝별 상태를 분리하거나 체크포인팅으로 보존한다.
- 작은 문제에서 미분 결과를 유한차분과 비교한 뒤 롤아웃 길이를 늘리거나 GPU 그래프를 적용한다.

## 라이선스와 범위

Warp는 Apache-2.0이다. 런타임과 GPU 요구사항은 릴리스에 따라 달라진다.

## 관련 가이드

[Newton](newton.md) · [MuJoCo Warp](mujoco-warp.md)

## 공식 자료

- [Warp 소스와 예제](https://github.com/NVIDIA/warp)
- [프로그래밍 모델과 컴파일러](https://nvidia.github.io/warp/latest/user_guide/programming_model.html)
- [자동 미분과 배열 수명](https://nvidia.github.io/warp/latest/user_guide/differentiability.html)
