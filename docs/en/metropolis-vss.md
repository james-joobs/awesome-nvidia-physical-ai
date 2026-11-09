# Metropolis / VSS

[← Catalog](../../README.md) · [한국어](../ko/metropolis-vss.md)

Metropolis is NVIDIA’s video AI ecosystem. Its Video Search and Summarization Blueprint (VSS) describes reference architectures for analytics, timestamped video reasoning and agent-driven search.

![VSS high-level architecture](https://docs.nvidia.com/vss/_fern-files/_img/e3a2810a613f30c365cd8ad42ca684fad69f222838e3d9e49ec4226044fba0de.webp)

*The diagram splits real-time extraction from analytics and agent workflows. Locate the shared records and video evidence that connect them.* [Official figure source](https://docs.nvidia.com/vss)

![VSS file summarization architecture](https://docs.nvidia.com/vss/_fern-files/_img/6bb9edc3e4cd755a499d9dfb3bd00f777d5bc3e06186d02b1f2909770f025206.webp)

*Follow a file upload to VLM events and the aggregated summary. The timestamps connect each event back to the source media.* [Official figure source](https://docs.nvidia.com/vss/system-components/vision-microservices/video-summarization)

## How it works

VSS separates real-time extraction, downstream analytics and agent/offline processing. DeepStream can emit detections and tracks, while a real-time VLM can produce captions or event candidates. Consumers retrieve records and video clips using timestamps. In the file summarization profile, a service chunks the file, calls the VLM, stores timestamped events and aggregates them with a summarization model. The streaming profile can add message-bus components.

### Component interfaces

| Component | Input | Output |
|---|---|---|
| Real-time CV or VLM | Video stream, processing profile and models | Detections, tracks, captions or event candidates |
| Event storage and verification | Timestamped events and relevant clips | Searchable events with source references |
| Agent and summarization | Question or summary request and retrieved evidence | Answer, timestamped summary or clip reference |

## A practical workflow

Index a short facility video and ask for a timestamped summary of an event. Use the returned timestamps to retrieve the original clip and compare the claim with visible evidence. Start with a file before adding a continuous RTSP workload.

## What to verify

Measure event recall, false positives, clip timestamp alignment and processing latency separately. Keep raw detections, model explanations and verified events distinguishable in downstream records. Check supported service images and deployment profiles.

## License and availability

Platform and services; individual SDKs and models have separate terms. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official references

- [Architecture and workflow documentation](https://docs.nvidia.com/vss)
- [Video summarization deployment profiles](https://docs.nvidia.com/vss/system-components/vision-microservices/video-summarization)
- [Related official resource · developer.nvidia.com](https://developer.nvidia.com/metropolis)
