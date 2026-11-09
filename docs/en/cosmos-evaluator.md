# Cosmos Evaluator

[Catalog](../../README.md) · [한국어](../ko/cosmos-evaluator.md)

Cosmos Evaluator applies separate checks to synthetic video. A pipeline can call one checker directly or submit several through the orchestration service.

## Read the official service architecture

![NVIDIA Cosmos Evaluator architecture](https://raw.githubusercontent.com/NVIDIA/cosmos-evaluator/main/docs/assets/architecture_diagram.png)

Arbitrator discovers available checkers and orders jobs by their dependencies. A client submits at /process/async and receives an execution ID. Polling /executions/{request_id} yields run state and per-checker rows. The Database REST API records results in PostgreSQL when configured according to the orchestration guide. [Official architecture](https://github.com/NVIDIA/cosmos-evaluator#architecture-diagram) · [Orchestration endpoints](https://github.com/NVIDIA/cosmos-evaluator/blob/main/docs/services/orchestration.md)

| Checker | Question |
|---|---|
| Hallucination | Is motion added or removed relative to the source motion mask? |
| Objects | Are expected objects where the reference says they should be? |
| Attribute verification | Does the generated scene contain the requested attribute? |
| Physical plausibility | Does temporal motion appear physically plausible to the configured model? |

## Worked example — review wet-road variants

Run an attribute check for rain and a motion comparison against a source clip. Record scores separately and inspect cases where one check passes but the other fails. Compare a reviewed subset to your acceptance thresholds before processing the whole batch. A checker score expresses model agreement with its task and inputs. It cannot certify safe vehicle behavior. [Official checker definitions](https://github.com/NVIDIA/cosmos-evaluator#whats-included) · [CDF Augmentation](cdf-augmentation.md)

Repository code is Apache-2.0. Check redistributed model notices and dependencies for each checker. [Official terms](https://github.com/NVIDIA/cosmos-evaluator#license-and-contributions)
