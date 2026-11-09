# Cosmos Data Factory (CDF; formerly Physical AI Data Factory)

[Catalog](../../README.md) · [한국어](../ko/cosmos-data-factory.md)

Cosmos Data Factory (CDF) packages reference pipelines and composable skills. The selected blueprint determines which tools retrieve, simulate, augment, label and evaluate the data.

## How the blueprints fit together

![Official CDF video augmentation workflow](https://raw.githubusercontent.com/NVIDIA/cosmos-data-factory/main/docs/workflows/physical-ai-video-data-augmentation/media/main_workflow.png)

This figure shows the video augmentation blueprint, where existing footage supplies the scene. An AV retrieval workflow can start with search. A PCB defect workflow can start from a rendered component. [CDF blueprint overview](https://github.com/NVIDIA/cosmos-data-factory#reference-blueprints)

| Layer | Boundary |
|---|---|
| Blueprint | Defines input data, execution order and configuration for AV, event, attribute, video or defect generation |
| Execution | [CDF Orchestration](cdf-orchestration.md) schedules Airflow tasks and GPU services. The documented event-video and video-augmentation paths can also use OSMO |
| Processing | [Curator](cosmos-curator.md) and [CDS](cosmos-embed-search.md) find clips. [Augmentation](cdf-augmentation.md) calls generation endpoints. [Simulation](cdf-simulation.md) renders 3D scenes. [Auto Labeling](cdf-auto-labeling.md) exports annotations |
| Evaluation | [Cosmos Evaluator](cosmos-evaluator.md) returns checker results. Your training export defines which variants qualify |

![Official CDF defect image generation workflows](https://raw.githubusercontent.com/NVIDIA/cosmos-data-factory/main/docs/workflows/physical-ai-defect-image-generation/media/dig_workflows.png)

The red Day 0 path starts with USD and a component list, then renders and augments the board. The purple Day 1 path uses normal component photos as the image input to AnomalyGen. The upper fine-tuning path uses defect/mask pairs and defect specifications. Follow the separate structural and textural defect arrows into Auto Labeling to see which generator produced each label candidate. [Official defect image generation guide](https://github.com/NVIDIA/cosmos-data-factory/tree/main/docs/workflows/physical-ai-defect-image-generation)

## Worked example — expand a rare driving scenario

Start with a clip that illustrates the event. Retrieve similar clips, then optionally generate weather variants conditioned on RGB footage or prepared world scenario controls. Preserve each original drive ID and split by source drive before adding variants. Review actor motion and lane geometry before training, and keep the model, control input and evaluation result with accepted and rejected candidates. [Official AV blueprint](https://github.com/NVIDIA/cdf-orchestration/blob/main/docs/autonomous-vehicle-dataset-generation/getting-started.md)

The entry repository specifies Apache-2.0 for code and CC-BY-4.0 for documentation and skills. Each component, dataset and model endpoint has its own terms and prerequisites. [Official license](https://github.com/NVIDIA/cosmos-data-factory#license)

## Related tools

[NeMo Data Designer](nemo-data-designer.md) can generate candidate structured records or questions using clip metadata. CDF workflows cover video generation, augmentation and labeling.
