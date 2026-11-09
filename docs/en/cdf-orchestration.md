# CDF Orchestration

[← All projects](../../README.md) · [한국어](../ko/cdf-orchestration.md)

CDF Orchestration runs the reference blueprints as Airflow DAGs on Kubernetes. The build packages DAGs and plugins into the Airflow controller image. Individual jobs can deploy inference services or run batch processing.

## Official control and execution flow

![NVIDIA CDF Orchestration architecture](https://raw.githubusercontent.com/NVIDIA/cdf-orchestration/main/docs/assets/architecture_diagram.png)

Read the Airflow controller as the dependency manager. Kubernetes is the execution environment for the jobs and the in-cluster services. Object storage holds input and output artifacts. For documented OSMO routes, the workflow uses external model endpoints. [Official architecture](https://github.com/NVIDIA/cdf-orchestration#architecture) · [Getting started](https://github.com/NVIDIA/cdf-orchestration/blob/main/docs/getting-started.md)

![NVIDIA SMT defect workflow](https://raw.githubusercontent.com/NVIDIA/cdf-orchestration/main/docs/defect-image-generation/assets/smt-workflow.png)

The SMT blueprint makes the distinction concrete. Simulation creates labeled board or component renders, augmentation adjusts appearance, and defect generation produces more defect examples. Separate artifacts let an operator inspect or rerun one part of the workflow. [SMT blueprint](https://github.com/NVIDIA/cdf-orchestration/blob/main/docs/defect-image-generation/getting-started.md)

## Worked example — diagnose a failed defect run

Pin the DAG image and model endpoints for a small board job. Record the scene, job configuration and output prefix. If a later stage fails, inspect intermediate renders and task logs to tell apart scene/configuration failures, storage access errors and endpoint failures. Confirm output counts and sample IDs before restarting a failed run or publishing an export.

The repository is Apache-2.0. Check underlying services, model endpoints and third-party dependencies separately. [Official terms](https://github.com/NVIDIA/cdf-orchestration#license-and-contributions)
