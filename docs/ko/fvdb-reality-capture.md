# fVDB Reality Capture

[← 전체 목록](../../README.ko.md) · [English](../en/fvdb-reality-capture.md)

촬영한 사진과 카메라 자세를 바탕으로 3D 가우시안 장면을 복원합니다. 완성한 장면을 새 시점에서 렌더링하거나, 다음 작업에 맞춰 가우시안과 삼각형 메시를 각각 내보낼 수 있습니다.

## 촬영한 사진이 어떻게 새 시점을 보여 줄까요?

### 입력에서 가우시안까지

공식 `safety_park` 예제는 COLMAP으로 처리한 사진을 사용합니다. 각 사진에는 카메라 내부 파라미터와 촬영 위치·회전이 있고, 여러 사진에서 대응점을 찾아 만든 **희소 점군**이 함께 들어 있습니다. fVDB Reality Capture는 이를 `SfmScene`으로 읽습니다. 희소 점의 위치에 가우시안을 초기화한 뒤, 알려진 카메라 위치에서 렌더링한 이미지가 원본 사진과 닮도록 가우시안의 위치·크기·회전·불투명도·색 표현을 반복해서 조정합니다.

### 공식 실행 기록에서 실제 입력과 출력 읽기

| 처리 시점 | `safety_park` 기록 | 읽는 법 |
|---|---|---|
| COLMAP 결과 읽기 | 사진 124장, 희소 점 199,702개 | 점은 사진의 픽셀 총수가 아니라 여러 시점에서 맞춘 3D 위치입니다. |
| 입력 정리 | 사진 124장, 점 168,661개 | `000079.jpg`는 3,840 × 2,160에서 960 × 540으로 축소했습니다. 크기 조정과 점 필터링을 거칩니다. |
| 복원 시작 → 최적화 종료 | 초기 가우시안 168,661개 → 마지막 진행 로그에서 1,552,032개 | 최적화 중 가우시안을 추가하거나 제거할 수 있습니다. 가우시안 개수는 메시 면 수와 별도로 읽습니다. |

![공식 safety_park 예제에서 다중 시점 사진에 희소 3D 점을 투영한 그림](https://raw.githubusercontent.com/openvdb/fvdb-reality-capture/7b3264827e782959f55a6536acb2db1d5e8b2ce1/docs/tutorials/radiance_field_and_mesh_reconstruction_files/radiance_field_and_mesh_reconstruction_6_1.png)

공식 예제는 입력을 읽고 복원하는 과정을 보여 줍니다. 새 시점의 복원 품질을 수치로 평가하려면 일부 카메라 시점을 학습에서 빼고, 해당 시점의 사진을 검증용으로 사용합니다. [공식 예제의 데이터와 실행 로그](https://github.com/openvdb/fvdb-reality-capture/blob/7b3264827e782959f55a6536acb2db1d5e8b2ce1/docs/tutorials/radiance_field_and_mesh_reconstruction.md)

## 다음 작업에 맞춰 파일 고르기

| 파일 | 담기는 정보 | 쓸 곳 |
|---|---|---|
| `reconstructed_model.ply` 또는 가우시안 USD | 가우시안의 좌표·크기·방향과 외관 | 새 시점 렌더링과 장면 미리보기 |
| `reconstructed_mesh.ply` | 삼각형을 이루는 꼭짓점과 면 | 표면 검사, 편집, 충돌체를 만들 때 참고할 형상 |

확장자가 둘 다 PLY여도 저장한 속성과 쓰는 방식이 다릅니다. 시뮬레이터에서 접촉을 계산하려면 메시의 단위와 표면을 점검하고 장면에 충돌체를 설정합니다. [OpenUSD](openusd.md) · [SimReady](simready.md) · [주행 센서 복원에서 NuRec 사용하기](nurec.md)

## 공식 자료와 라이선스

[fVDB Reality Capture 저장소](https://github.com/openvdb/fvdb-reality-capture) · [Apache-2.0 코드 라이선스](https://github.com/openvdb/fvdb-reality-capture/blob/7b3264827e782959f55a6536acb2db1d5e8b2ce1/LICENSE). 예제 데이터와 의존성의 이용 조건도 각각 확인하세요.
