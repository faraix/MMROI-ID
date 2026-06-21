# MMROI-ID

# MMROI-ID: Multimodal ROI Identification via Dominant Overlap Mapping

MMROI-ID is an open-source toolkit for identifying anatomical correspondence between neuroimaging parcellations and reference atlases.

Unlike methods that rely primarily on Dice similarity coefficients, MMROI-ID introduces the **Dominant Overlap Fraction (DOF)**, a metric designed for cross-atlas label assignment.

[
\text{DOF} =
\frac{\max_i |A \cap B_i|}{|A \cap \bigcup_i B_i|}
]

where (A) is the query ROI and (B_i) are candidate atlas labels.

DOF addresses the question:

> "Which anatomical region does this ROI primarily correspond to?"

whereas Dice addresses:

> "How similar are the sizes and shapes of two regions?"

MMROI-ID reports DOF alongside conventional volumetric and slice-wise Dice coefficients, providing complementary measures of anatomical assignment and spatial concordance.

## Features

* Cross-atlas ROI mapping
* Dominant Overlap Fraction (DOF)
* Volumetric and slice-wise Dice metrics
* Support for NIfTI and AFNI datasets
* Batch processing and summary tables
* Integration with AFNI and FSL workflows

## Relationship to Neuroparc

MMROI-ID complements Neuroparc by prioritizing anatomical correspondence over segmentation agreement alone. Dice metrics remain useful for quality control, while DOF improves interpretability when comparing atlases with different resolutions, parcel sizes, or construction principles.

## Status

⚠️ **Work in progress:** MMROI-ID is under active development and currently focused on gray matter atlas correspondence.

## Future Directions

Planned extensions include diffusion MRI applications, where DOF will be evaluated for identifying white matter tracts derived from DTI and tractography pipelines relative to established white matter atlases.

## Installation

```bash
git clone https://github.com/faraix/MMROI-ID.git
cd MMROI-ID
```

## Contributing

Contributions, feature requests, and validation datasets are welcome.

