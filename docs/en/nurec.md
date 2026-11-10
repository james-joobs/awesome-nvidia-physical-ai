# NuRec

[← All projects](../../README.md) · [한국어](../ko/nurec.md)

Omniverse NuRec reconstructs a captured scene as a neural representation so a simulator can render sensor observations from new viewpoints. An AV pipeline typically converts driving logs into NCore, trains or initializes a Gaussian representation and exports a USDZ artifact for rendering.

## Reconstruction from sensor logs

![NVIDIA NuRec workflow from driving logs to reconstructed USDZ](https://docs.nvidia.com/nurec/_images/nurec-pipeline-overview.png)

The official pipeline separates conversion, reconstruction and packaging. In the published layered example, fixed background, moving rigid actors, pedestrians and road use distinct Gaussian layers, while sky uses an environment map. Tracking and semantic labels help assign observations to layers. [Official scaling and layering guide](https://docs.nvidia.com/nurec/best-practices/scaling-neural-reconstruction.html)

## Read the official sensor adaptation workflow

![NVIDIA NuRec carline adaptation architecture](https://developer-blogs.nvidia.com/wp-content/uploads/2026/08/image-39.webp)

Start at the reconstructed USDZ scene. A target camera rig defines the sensor geometry for re-rendering. The illustrated workflow can run NVIDIA Harmonizer on generated frames before training a perception model. In a live simulator integration, NuRec gRPC receives a scene and camera or LiDAR render request. The client receives the requested observation product. [Official carline adaptation walkthrough](https://developer.nvidia.com/blog/scale-av-perception-across-vehicle-platforms-with-nvidia-omniverse-nurec) · [gRPC API guide](https://docs.nvidia.com/nurec/api/grpc_api_guide.html)

| Boundary | Check |
|---|---|
| Capture to NCore | Calibration, synchronized timestamps and ego motion are consistent |
| Reconstruction to USDZ | Confirm the artifact and reference render load with the expected scene ID |
| Runtime to client | Match camera intrinsics, requested pose and output format |
| Synthetic to validation | Check occlusion, moving objects and appearance for positions outside recorded coverage |

## Worked example — assess a new camera placement

Re-render one reconstructed drive with its original pose first, then with the new rig. Compare the source view and original-rig render for lane-edge alignment and dynamic actor timing before interpreting the new view. New perspectives can expose occluded regions never captured by the source sensors. Flag those samples during dataset review. [Official reconstruction guide](https://docs.nvidia.com/nurec/nurec/model.html) · [Scaling neural reconstruction](https://docs.nvidia.com/nurec/best-practices/scaling-neural-reconstruction.html)

Access, runtime, trained artifacts and data terms vary by distribution. [Official NuRec overview](https://developer.nvidia.com/omniverse/nurec)

## Source and runtime distribution

The public NuRec SDK contains reconstruction and rendering libraries, training systems, and application entry points under Apache-2.0. Runtime containers are distributed through NGC under the terms on their catalog pages. Model checkpoints and scene data have separate terms. NCore provides an Apache-2.0 format and conversion tooling for the sensor recordings that enter the pipeline. [NuRec SDK and distribution matrix](https://github.com/NVIDIA/NuRec#source-containers-and-models) · [SDK license](https://github.com/NVIDIA/NuRec/blob/main/LICENSE.md) · [NCore](https://github.com/NVIDIA/ncore)

[Follow a closed-loop AlpaSim evaluation using a prepared NuRec scene](workflows/alpasim-closed-loop.md).
