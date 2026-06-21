# MMROI-ID: Multimodal ROI Identification

MMROI-ID is an open-source toolkit for identifying anatomical correspondence between neuroimaging parcellations and reference atlases.The toolkit prioritizes **Dominant Overlap Fraction (DOF)** for cross-atlas label assignment, while also reporting conventional overlap metrics including **Jaccard** and **Dice**. MMROI-ID complements Neuroparc by prioritizing anatomical correspondence over segmentation agreement alone. Dice remains useful for quality control, while DOF improves interpretability when comparing atlases with different ROI sizes, resolutions, or boundary definitions.

[
\text{DOF} =
\frac{\max_i |A \cap B_i|}{|A \cap \bigcup_i B_i|}
]

where (A) is the query ROI and (B_i) are candidate atlas labels.

DOF answers:

> Which anatomical label does this ROI primarily correspond to?

while Dice and Jaccard quantify spatial similarity between regions.


### Bash workflow

The repository includes a Bash script that performs the full workflow:

1. Registers the query parcellation to reference space using `flirt`
2. Extracts individual ROI masks using `fslmaths`
3. Computes atlas-label overlap using `3dcalc`
4. Identifies the best-matching atlas label using `3dROIstats`
5. Computes DOF, Jaccard, and slice-wise Dice
6. Writes results to `lab_fin.txt`

### Python wrapper

A Python wrapper is also included for users who prefer a configurable Python interface while still relying on AFNI and FSL command-line tools underneath.

## Output Metrics

Each ROI is summarized with:

* ROI ID
* Best-matching atlas label
* Overlap voxels
* Total overlap voxels
* Dominant Overlap Fraction
* ROI voxel count
* Atlas-label voxel count
* Jaccard coefficient
* Mean slice-wise Dice
* Maximum slice-wise Dice
* Number of Dice slices

## Installation

```bash
git clone https://github.com/faraix/MMROI-ID.git
cd MMROI-ID
```

Required tools:

* AFNI (https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/background_install/install_instructs/index.html)
* FSL (https://fsl.fmrib.ox.ac.uk/fsl/docs/install/index.html)
* Python 3

Optional Python packages:

* NumPy
* Pandas
* NiBabel

## Status

⚠️ **Work in progress:** MMROI-ID is under active development and currently focused on gray matter atlas correspondence.

## Future Directions

Planned extensions include diffusion MRI applications, where DOF will be evaluated for identifying white matter tracts derived from DTI and tractography pipelines relative to established white matter atlases.


