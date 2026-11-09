# Holoscan SDK

[← Catalog](../../README.md) · [한국어](../ko/holoscan-sdk.md)

Holoscan SDK builds streaming sensor applications that combine acquisition, accelerated processing and visualization with controlled latency.

![Holoscan 4.0 application and fragments](https://docscontent.nvidia.com/dims4/default/911ae77/2147483647/strip/true/crop/1834x714+0+0/resize/1440x561!/quality/90/?url=https%3A%2F%2Fk3-prod-nvidia-docs.s3.us-west-2.amazonaws.com%2Fbrightspot%2Fsphinx%2F0000019d-4b57-dcf2-ab9d-6b5fc9eb0000%2Fholoscan%2Farchive%2F4.0.0%2F_images%2Fcore_concepts_application.png)

*This 4.0 figure shows how fragments group operators and ports. The 5.0 graph API described below has different authoring primitives.* [Official figure source](https://docs.nvidia.com/holoscan/archive/4.0.0/holoscan_core.html)

## How it works

In the documented 5.0 graph API, operators declare typed input and output ports. A graph wires them together, a contract describes timing rules, and compilation resolves an execution plan. A run session activates that plan and moves samples between operators. The earlier 4.x application and fragment APIs are documented separately.

```mermaid
flowchart LR
    S["Capture operator"] -->|timestamped frame| P["Preprocessing operator"]
    P -->|tensor| I["Inference operator"]
    I -->|mask or result| V["Visualization operator"]
    C["Graph contracts and clock"] -.-> P
    C -.-> I
```

## A practical workflow

Connect a camera, image format conversion, a segmentation model and a display. Trace sample timestamps from capture to display. Add an artificial delay to inference and observe the queue behavior before tuning the graph’s latency settings.

## What to verify

Check device memory ownership, sample timing, queue policy and behavior under input bursts. Verify that examples use the API version installed in the environment.

## License and availability

Apache-2.0; external components have separate terms. Models, data, dependencies and hosted services may have separate terms; check each source before use.

## Official references

- [Architecture and workflow documentation](https://docs.nvidia.com/holoscan/sdk-user-guide/getting-started/core-concepts)
- [Holoscan 4.x core concepts](https://docs.nvidia.com/holoscan/sdk-user-guide/using-the-sdk/holoscan-core)
- [Related official resource · github.com](https://github.com/nvidia-holoscan/holoscan-sdk)
