# Grounding DINO

[← Catalog](../../README.md) · [한국어](../ko/grounding-dino.md)

Grounding DINO returns 2D boxes for text phrases supplied with an image. The prompt determines which objects the detector should seek.

![Grounding DINO model diagram](https://raw.githubusercontent.com/IDEA-Research/GroundingDINO/main/.asset/model_explan1.PNG)

*Find where image and text features interact before the decoder returns localized results.* [Official figure source](https://github.com/IDEA-Research/GroundingDINO)

![Grounding DINO detection examples](https://raw.githubusercontent.com/IDEA-Research/GroundingDINO/main/.asset/hero_figure.png)

*Compare each localized object with the prompt that describes it.* [Official figure source](https://github.com/IDEA-Research/GroundingDINO)

## How it works

Image and language backbones produce features. A feature enhancer exchanges information across modalities. Language-guided query selection chooses candidate regions, and a cross-modal decoder refines boxes and token alignment. Applications apply thresholds and transform the predicted boxes back to the input image coordinates.

## A practical workflow

Prompt for a “red bin” and a “blue bin” on recorded workstation frames. Convert the selected boxes into prompts for [SAM 2](sam-2-sam-3d.md) to obtain masks for a labeling experiment.

## What to verify

Compare synonyms and separate generic from precise prompts. Check box format, resizing offsets and confidence thresholds before passing boxes to a segmentation or pose stage.

## License and availability

Check the repository code license, checkpoint terms, and any third-party components separately.

## Official references

- [Official technical reference](https://arxiv.org/html/2303.05499)
