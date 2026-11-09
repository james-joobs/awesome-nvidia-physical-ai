# OSMO

[Catalog](../../README.md) · [한국어](../ko/osmo.md)

OSMO schedules containerized physical AI workloads. A workflow declares task dependencies and resource needs. A pool determines where tasks can execute, and artifacts link stages that can run on different machines.

## Read the deployment architecture

![NVIDIA OSMO deployment architecture](https://raw.githubusercontent.com/NVIDIA/OSMO/main/docs/deployment_guide/introduction/deployment_architecture.svg)

Follow the submission into the service cluster. Core Service validates and manages the request, its Worker coordinates execution, and status updates flow back from compute backends. A Backend Operator on each compute cluster launches and monitors workload resources. Control and compute planes are logical boundaries and can share a cluster in the supported converged mode. [Official deployment architecture](https://nvidia.github.io/OSMO/main/deployment_guide/introduction/architecture.html)

![NVIDIA OSMO workflow sequence](https://raw.githubusercontent.com/NVIDIA/OSMO/main/docs/deployment_guide/introduction/workflow_sequence.svg)

The sequence shows submission, scheduling and backend status transitions. Use it to tell apart a task waiting for resources and a task already running on the backend. [Official deployment guide](https://github.com/NVIDIA/OSMO/blob/main/docs/deployment_guide/introduction/architecture.rst)

## Worked example — separate robot training and evaluation

Place simulator rollout generation, policy training and held-out evaluation in separate tasks. Write a versioned dataset artifact from the rollout task and a checkpoint from training. Pass only the checkpoint and the held-out configuration into evaluation. If a GPU job queues, check the selected pool and resource request. If it starts but cannot load a checkpoint, inspect storage and upstream task outputs. [Official user guide](https://nvidia.github.io/OSMO/main/user_guide/) · [Isaac Lab](isaac-lab.md)

OSMO is Apache-2.0. Images, cloud services and the underlying simulator and training tools have their own terms. [Official repository](https://github.com/NVIDIA/OSMO)
