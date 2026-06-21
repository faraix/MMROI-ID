#!/usr/bin/env python3

import argparse
import subprocess
from pathlib import Path


def run_cmd(cmd):
    print("\nRunning:")
    print(" ".join(str(x) for x in cmd))
    subprocess.run(cmd, check=True)


def read_1d_values(path):
    with open(path, "r") as f:
        line = f.readline().strip()
    return line.split()


def main():
    parser = argparse.ArgumentParser(
        description="MMROI-ID wrapper for ROI overlap, Dice, and Jaccard metrics using FSL and AFNI."
    )

    parser.add_argument("--base", required=True, help="Base directory")
    parser.add_argument("--subdir", required=True, help="Subject/parcellation directory name")
    parser.add_argument("--parc", default="parc.nii.gz", help="Input parcellation image")
    parser.add_argument("--brain", default="brain.nii.gz", help="Reference brain image")
    parser.add_argument("--atlas", default="aparc.DKTatlas+aseg.nii.gz", help="Reference atlas image")
    parser.add_argument("--n-rois", type=int, default=333, help="Number of ROIs to extract")
    parser.add_argument("--skip-registration", action="store_true", help="Skip FSL FLIRT registration")

    args = parser.parse_args()

    base = Path(args.base).expanduser().resolve()
    subj_data = base / args.subdir

    parc = subj_data / args.parc
    brain = subj_data / args.brain
    atlas = subj_data / args.atlas
    gordon = subj_data / "Gordonx.nii.gz"

    roi_dir = subj_data / "rois"
    tmp_dir = subj_data / "tmp"
    overlap_dir = subj_data / "roiOverlap"
    dice_dir = subj_data / "dice"

    for d in [roi_dir, tmp_dir, overlap_dir, dice_dir]:
        d.mkdir(parents=True, exist_ok=True)

    if not args.skip_registration:
        run_cmd([
            "flirt",
            "-in", parc,
            "-ref", brain,
            "-out", gordon,
            "-omat", subj_data / "invol2refvolx.mat",
            "-dof", "6",
            "-datatype", "int",
            "-interp", "nearestneighbour",
        ])

    for roi_id in range(1, args.n_rois + 1):
        roi_mask = roi_dir / f"{roi_id}.nii.gz"

        run_cmd([
            "fslmaths",
            gordon,
            "-thr", str(roi_id),
            "-uthr", str(roi_id),
            "-bin", roi_mask,
        ])

    for roi_mask in sorted(roi_dir.glob("*.nii.gz")):
        roi_id = roi_mask.name.replace(".nii.gz", "")
        overlap_img = overlap_dir / f"{roi_id}_gm.nii.gz"

        run_cmd([
            "3dcalc",
            "-echo_edu",
            "-a", roi_mask,
            "-b", atlas,
            "-expr", "ifelse(a*b,b,0)",
            "-datum", "float",
            "-prefix", overlap_img,
            "-overwrite",
        ])

    output_file = overlap_dir / "lab_fin.txt"

    with open(output_file, "w") as out:
        out.write(
            "roi best_atlas_label overlap_voxels total_overlap_voxels "
            "dominant_overlap_fraction roi_voxels atlas_label_voxels "
            "jaccard dice_mean dice_max dice_n_slices\n"
        )

        for overlap_img in sorted(overlap_dir.glob("*_gm.nii.gz")):
            name = overlap_img.name.replace(".nii.gz", "")
            roi_id = name.replace("_gm", "")
            roi_mask = roi_dir / f"{roi_id}.nii.gz"

            roi_stats = overlap_dir / f"{name}_roi.1D"
            roi_stats_row = overlap_dir / f"{name}_t2.1D"

            with open(roi_stats, "w") as f:
                subprocess.run([
                    "3dROIstats",
                    "-nzvoxels",
                    "-1Dformat",
                    "-mask", overlap_img,
                    overlap_img,
                ], check=True, stdout=f)

            run_cmd([
                "1d_tool.py",
                "-infile", roi_stats,
                "-select_rows", "0",
                "-write", roi_stats_row,
                "-overwrite",
            ])

            values = read_1d_values(roi_stats_row)

            best_label = 0
            max_voxels = 0
            total_voxels = 0

            for idx in range(0, len(values), 2):
                label = int(float(values[idx]))
                voxels = int(float(values[idx + 1]))

                total_voxels += voxels

                if voxels > max_voxels:
                    max_voxels = voxels
                    best_label = label

            atlas_label_mask = tmp_dir / f"{roi_id}_atlasLabel_{best_label}.nii.gz"

            run_cmd([
                "3dcalc",
                "-a", atlas,
                "-expr", f"equals(a,{best_label})",
                "-prefix", atlas_label_mask,
                "-overwrite",
            ])

            roi_voxels = int(subprocess.check_output([
                "3dBrickStat",
                "-count",
                "-non-zero",
                roi_mask,
            ]).decode().strip())

            atlas_label_voxels = int(subprocess.check_output([
                "3dBrickStat",
                "-count",
                "-non-zero",
                atlas_label_mask,
            ]).decode().strip())

            if total_voxels > 0:
                dominant_overlap_fraction = max_voxels / total_voxels
            else:
                dominant_overlap_fraction = "NA"

            union = roi_voxels + atlas_label_voxels - max_voxels

            if union > 0:
                jaccard = max_voxels / union
            else:
                jaccard = "NA"

            dice_prefix = dice_dir / f"{roi_id}_label_{best_label}_dice"

            run_cmd([
                "3dSliceNDice",
                "-insetA", roi_mask,
                "-insetB", atlas_label_mask,
                "-out_domain", "AorB",
                "-prefix", dice_prefix,
                "-no_cmd_echo",
            ])

            dice_files = list(dice_dir.glob(f"{roi_id}_label_{best_label}_dice_*.1D"))

            dice_values = []

            for dice_file in dice_files:
                with open(dice_file, "r") as f:
                    for line in f:
                        if line.startswith("#") or not line.strip():
                            continue
                        parts = line.split()
                        if len(parts) >= 5:
                            dice_values.append(float(parts[4]))

            if dice_values:
                dice_mean = sum(dice_values) / len(dice_values)
                dice_max = max(dice_values)
                dice_n_slices = len(dice_values)
            else:
                dice_mean = "NA"
                dice_max = "NA"
                dice_n_slices = 0

            out.write(
                f"{roi_id} {best_label} {max_voxels} {total_voxels} "
                f"{dominant_overlap_fraction} {roi_voxels} {atlas_label_voxels} "
                f"{jaccard} {dice_mean} {dice_max} {dice_n_slices}\n"
            )

    print(f"\nDone. Results saved to: {output_file}")


if __name__ == "__main__":
    main()
