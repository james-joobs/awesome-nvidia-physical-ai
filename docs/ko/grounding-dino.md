# Grounding DINO

[← 전체 목록](../../README.ko.md) · [English](../en/grounding-dino.md)

Grounding DINO는 이미지와 함께 넣은 문구에 해당하는 2D 박스를 반환합니다. 프롬프트가 탐지할 물체를 지정합니다.

![Grounding DINO 모델 구성도](https://raw.githubusercontent.com/IDEA-Research/GroundingDINO/main/.asset/model_explan1.PNG)

*디코더가 위치를 반환하기 전에 영상과 텍스트 특징이 만나는 위치를 확인하세요.* [공식 그림 출처](https://github.com/IDEA-Research/GroundingDINO)

![Grounding DINO 탐지 예시](https://raw.githubusercontent.com/IDEA-Research/GroundingDINO/main/.asset/hero_figure.png)

*탐지한 물체를 이를 설명하는 프롬프트와 대조할 수 있습니다.* [공식 그림 출처](https://github.com/IDEA-Research/GroundingDINO)

## 어떻게 동작하나

영상·언어 백본이 각각 특징을 추출합니다. 특징 강화 계층에서 두 모달리티의 정보가 교환됩니다. 언어 기반 쿼리 선택이 후보 영역을 고르고 교차 모달 디코더가 박스와 토큰 대응을 보정합니다. 응용 단계에서는 임계값을 적용하고 박스를 원본 좌표로 복원합니다.

## 실전 워크플로

작업대 기록 영상에서 빨간 상자와 파란 상자를 문구로 탐지합니다. 박스를 [SAM 2](sam-2-sam-3d.md)의 프롬프트로 전달해 라벨링용 마스크를 생성합니다.

## 검증할 항목

동의어와 구체적인 문구를 비교합니다. 분할 또는 자세 추정에 전달하기 전에 박스 형식, 영상 크기 보정과 신뢰도 기준을 확인합니다.

## 공개 범위와 라이선스

저장소 코드 라이선스, 체크포인트 조건과 제3자 구성 요소를 각각 확인하세요.

## 공식 자료

- [공식 기술 자료](https://arxiv.org/html/2303.05499)
