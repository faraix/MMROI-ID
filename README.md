# MMROI-ID: Multimodal ROI Identification

MMROI-ID is an open-source toolkit for identifying anatomical correspondence between neuroimaging parcellations and reference atlases. This toolkit proposes the use of the **Overlap Fraction (OF)** for cross-atlas label assignment, while also reporting conventional overlap metrics including **Jaccard** and **Dice** [1]. MMROI-ID thus complements Neuroparc (https://github.com/neurodata/neuroparc) [3] by prioritizing anatomical correspondence over segmentation agreement alone. Dice remains useful for quality control, while OF improves interpretability when comparing atlases with different ROI sizes, resolutions, or boundary definitions, for which standard overlap metrics are often applied despite known limitations [2]. In addition, because ROIs may overlap multiple candidate parcels in a given atlas, MMROI-ID reports the number of overlapping non-zero voxels for each intersection. This simple voxel-count measure provides a practical criterion for assigning a region to the anatomical label with the greatest spatial support and can assist in resolving ambiguous correspondences when multiple candidate labels are present.

As an example application of the workflow, we identified overlaps between atlas-defined regions and white matter tracts in diffusion MRI. To facilitate this, the JHU White-Matter Tractography Atlas (https://web.mit.edu/fsl_v5.0.10/fsl/doc/wiki/Atlases.html) is warped to subject space and binarized. Overlap between binarized tract masks and the target masks is then quantified using 3dcalc as follows:

<img width="497" height="218" alt="Screenshot from 2026-06-26 18-16-06" src="https://github.com/user-attachments/assets/d497fc46-c4bd-4d6e-842c-64187ec8c768" />

Probabilistic tracks may intersect with multiple masks, so we calculated the number of voxels with non-zero values in each of these intersections using 3dROIstats and the track identity was assigned to the masks with the most voxels as follows:

<img width="497" height="218" alt="Screenshot from 2026-06-26 18-16-24" src="https://github.com/user-attachments/assets/c349f93c-3847-4d36-8bbd-75c7c5c3542a" />

where multiple masks provided equal number of voxels:

<img width="502" height="108" alt="Screenshot from 2026-06-26 18-16-35" src="https://github.com/user-attachments/assets/1f991715-1be4-4add-8ecd-5fe71196048a" />

OF answers:

> Which anatomical label does this ROI primarily correspond to?

while Dice and Jaccard quantify spatial similarity between regions.

### Bash workflow

The repository includes a Bash script that performs the full workflow:

1. Registers the query parcellation to reference space using `flirt`
2. Extracts individual ROI masks using `fslmaths`
3. Computes atlas-label overlap using `3dcalc`
4. Identifies the best-matching atlas label using `3dROIstats`
5. Computes OF, Jaccard, and Dice
6. Writes results to `lab_fin.txt`

### Python wrapper

A Python wrapper is also included for users who prefer a configurable Python interface while still relying on AFNI and FSL command-line tools underneath.

## Installation

```bash
git clone https://github.com/faraix/MMROI-ID.git
cd MMROI-ID
```

Required tools:

* AFNI (https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/background_install/install_instructs/index.html)
* FSL (https://fsl.fmrib.ox.ac.uk/fsl/docs/install/index.html)
* Python 3

## Future Directions

Planned extensions include diffusion MRI applications, where OF will be evaluated for identifying white matter tracts derived from DTI and tractography pipelines relative to established white matter atlases.

## Acknowledgements
https://github.com/neurodata/neuroparc

## References

This toolkit was developed for assignment of labels to regions of the Gordon et al atlas in the paper (in press):
Groenewold, N. A., Bethlehem, R. A., Amod, A. R., Nwosu, E. C., **Mberi**, **F**., Wedderburn, C. J., ... & Ipser, J. C. (2024). Morphometric Integration of Brain Networks in Young Children Exposed to Maternal Depression in a South African Birth Cohort. Biological Psychiatry, 95(10), S45-S46.

1. Taha, A. A., & Hanbury, A. (2015). Metrics for evaluating 3D medical image segmentation: analysis, selection, and tool. BMC medical imaging, 15(1), 29.
2. Reinke, A., Tizabi, M. D., Baumgartner, M., Eisenmann, M., Heckmann-Nötzel, D., Kavur, A. E., ... & Maier-Hein, L. (2024). Understanding metric-related pitfalls in image analysis validation. Nature methods, 21(2), 182-194.
3. Lawrence, R.M., Bridgeford, E.W., Myers, P.E. et al. Standardizing human brain parcellations. Sci Data 8, 78 (2021). https://doi.org/10.1038/s41597-021-00849-3


