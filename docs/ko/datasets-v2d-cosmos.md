# V2D 및 Cosmos 데이터셋

[전체 목록](../../README.ko.md) · [English](../en/datasets-v2d-cosmos.md)

공식 데이터셋 카드를 기준으로 형식, 접근 조건과 라이선스를 각각 확인한다. 공개 접근과 제한 없는 이용 권한은 다르다.

## 선택 및 활용 흐름

이 그림은 개념적 사용 흐름이다.

```mermaid
flowchart LR
  S0["작업과 데이터 선택"]
  S1["데이터셋 카드 및 조건 확인"]
  S2["형식 준비"]
  S3["학습 또는 평가"]
  S0 --> S1 --> S2 --> S3
```

## 데이터셋별 상세

<a id="video-to-data-robot-dexterity-task-library-and-dataset"></a>
### video-to-data-robot-dexterity-task-library-and-dataset

V2D 사람 손 시연을 로봇 손으로 리타기팅한 데이터.

**라이선스·접근:** CC BY 4.0; 공개.  
**공식 데이터셋 카드:** [video-to-data-robot-dexterity-task-library-and-dataset](https://huggingface.co/datasets/nvidia/video-to-data-robot-dexterity-task-library-and-dataset)

<a id="cosmos-reason1-rl-dataset"></a>
### Cosmos-Reason1-RL-Dataset

추론 강화학습용 영상·텍스트 주석.

**라이선스·접근:** 라이선스 미확인; 공개.  
**공식 데이터셋 카드:** [Cosmos-Reason1-RL-Dataset](https://huggingface.co/datasets/nvidia/Cosmos-Reason1-RL-Dataset)

<a id="cosmos-reason1-benchmark"></a>
### Cosmos-Reason1-Benchmark

영상 추론 평가 주석.

**라이선스·접근:** 라이선스 미확인; 공개.  
**공식 데이터셋 카드:** [Cosmos-Reason1-Benchmark](https://huggingface.co/datasets/nvidia/Cosmos-Reason1-Benchmark)

<a id="cosmos-reason1-sft-dataset"></a>
### Cosmos-Reason1-SFT-Dataset

지도 추론 학습용 영상·텍스트 주석.

**라이선스·접근:** CC BY 4.0; 공개.  
**공식 데이터셋 카드:** [Cosmos-Reason1-SFT-Dataset](https://huggingface.co/datasets/nvidia/Cosmos-Reason1-SFT-Dataset)

<a id="cosmos-transfer-lidargen-example"></a>
### Cosmos-Transfer-LidarGen-Example

LiDAR 생성 예제 데이터.

**라이선스·접근:** 별도 약관; 접근 제한.  
**공식 데이터셋 카드:** [Cosmos-Transfer-LidarGen-Example](https://huggingface.co/datasets/nvidia/Cosmos-Transfer-LidarGen-Example)

<a id="cosmos-transfer1-7b-sample-av-data-example"></a>
### Cosmos-Transfer1-7B-Sample-AV-Data-Example

Cosmos Transfer용 자율주행 입력 예제.

**라이선스·접근:** CC BY 4.0; 접근 제한.  
**공식 데이터셋 카드:** [Cosmos-Transfer1-7B-Sample-AV-Data-Example](https://huggingface.co/datasets/nvidia/Cosmos-Transfer1-7B-Sample-AV-Data-Example)

<a id="aloha-cosmos-policy"></a>
### ALOHA-Cosmos-Policy

Cosmos Policy 학습용 실제 양손 조작 데이터.

**라이선스·접근:** CC 태그; 상세 약관 확인 필요.  
**공식 데이터셋 카드:** [ALOHA-Cosmos-Policy](https://huggingface.co/datasets/nvidia/ALOHA-Cosmos-Policy)

<a id="libero-cosmos-policy"></a>
### LIBERO-Cosmos-Policy

Cosmos Policy용 LIBERO 시뮬레이션 데이터.

**라이선스·접근:** CC 태그; 상세 약관 확인 필요.  
**공식 데이터셋 카드:** [LIBERO-Cosmos-Policy](https://huggingface.co/datasets/nvidia/LIBERO-Cosmos-Policy)

<a id="robocasa-cosmos-policy"></a>
### RoboCasa-Cosmos-Policy

Cosmos Policy용 RoboCasa 시뮬레이션 데이터.

**라이선스·접근:** CC 태그; 상세 약관 확인 필요.  
**공식 데이터셋 카드:** [RoboCasa-Cosmos-Policy](https://huggingface.co/datasets/nvidia/RoboCasa-Cosmos-Policy)

<a id="cosmos-humaneval-v1"></a>
### Cosmos-HumanEval-v1

Cosmos 출력의 사람 평가 데이터.

**라이선스·접근:** 별도 약관 확인.  
**공식 데이터셋 카드:** [Cosmos-HumanEval-v1](https://huggingface.co/datasets/nvidia/Cosmos-HumanEval-v1)

<a id="cosmos-anomalygen-pcb-dataset"></a>
### Cosmos-AnomalyGen-PCB-Dataset

PCB 결함 생성 데이터.

**라이선스·접근:** 별도 약관 확인.  
**공식 데이터셋 카드:** [Cosmos-AnomalyGen-PCB-Dataset](https://huggingface.co/datasets/nvidia/Cosmos-AnomalyGen-PCB-Dataset)

<a id="cosmos-anomalygen-glass-masks"></a>
### Cosmos-AnomalyGen-Glass-Masks

유리 결함 생성용 마스크.

**라이선스·접근:** 라이선스 미확인; 공개.  
**공식 데이터셋 카드:** [Cosmos-AnomalyGen-Glass-Masks](https://huggingface.co/datasets/nvidia/Cosmos-AnomalyGen-Glass-Masks)

<a id="cosmos3-droid"></a>
### Cosmos3-DROID

Cosmos 3용 로봇 조작 시연.

**라이선스·접근:** OpenMDW-1.1; 공개.  
**공식 데이터셋 카드:** [Cosmos3-DROID](https://huggingface.co/datasets/nvidia/Cosmos3-DROID)

<a id="cosmos3-driving-simulation-evaluation"></a>
### Cosmos3-Driving-Simulation-Evaluation

자율주행 시뮬레이션 평가용 제어 영상·설명.

**라이선스·접근:** OpenMDW-1.1; 공개.  
**공식 데이터셋 카드:** [Cosmos3-Driving-Simulation-Evaluation](https://huggingface.co/datasets/nvidia/Cosmos3-Driving-Simulation-Evaluation)

