# DeepStream

[← Catalog](../../README.md) · [한국어](../ko/deepstream.md)

DeepStream assembles GStreamer plugins into GPU-accelerated pipelines for continuous video analytics. Its main interface is a graph of video buffers and metadata.

![DeepStream graph architecture](https://docs.nvidia.com/deepstream/_fern-files/_img/5fdf8ab2ed4a2aeaffbd54df8069478f95071121dbf460cf0ebff3a293da95e2.webp)

*Read across the GStreamer plugins and compare them with the accelerator blocks underneath. The diagram separates processing from the sinks that consume results.* [Official figure source](https://docs.nvidia.com/deepstream/text/DS_Overview)

## How it works

For an RTSP application, a source and hardware decoder produce frames. `nvstreammux` batches frames from different sources. `nvinfer` or a Triton integration runs inference and attaches metadata. A tracker can attach persistent IDs, then branches can render overlays, publish metadata or encode the video. GPU buffers and batch metadata make it possible to avoid copying raw frames back to the CPU in compatible paths.

### Component interfaces

| Component | Input | Output |
|---|---|---|
| Source and decoder | RTSP stream, local file or camera | Decoded video buffers |
| Batch and inference | Frames and model configuration | Batch metadata with detections or tensors |
| Tracking and sinks | Frames, detections and source IDs | Track IDs, overlays, metadata or encoded video |

## A practical workflow

Attach two cameras to a facility detector. Start with recording output and overlayed boxes; verify per-source timestamps and IDs. Then publish object metadata for a downstream application. Measure per-camera freshness after increasing the batch size or adding a slow stream.

## What to verify

Profile decode, batch wait, preprocessing, inference and output separately. Confirm camera drop/reconnect behavior and the timestamp meaning on each branch. Validate model labels and coordinate transforms before consuming detections as application events.

## License and availability

Product SDK; samples and binaries have separate terms. Verify the exact version and the terms of any models, datasets, binaries and dependencies before use.

## Official references

- [Architecture and workflow documentation](https://docs.nvidia.com/deepstream/text/DS_Overview)
- [Related official resource · docs.nvidia.com](https://docs.nvidia.com/metropolis/deepstream/dev-guide/text/DS_Overview.html)
- [Related official resource · developer.nvidia.com](https://developer.nvidia.com/deepstream-sdk)
