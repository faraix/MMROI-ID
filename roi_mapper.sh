#!/usr/bin/env bash
set -euo pipefail

base="/home/farai/Test/sub-t1.ses-multiAtlasreg"
subj_data="${base}/sub-001"

atlas="${subj_data}/aparc.DKTatlas+aseg.nii.gz"

mkdir -p \
    "${subj_data}/rois" \
    "${subj_data}/tmp" \
    "${subj_data}/roiOverlap" \
    "${subj_data}/dice"

flirt \
    -in "${subj_data}/parc.nii.gz" \
    -ref "${subj_data}/brain.nii.gz" \
    -out "${subj_data}/Gordonx.nii.gz" \
    -omat "${subj_data}/invol2refvolx.mat" \
    -dof 6 \
    -datatype int \
    -interp nearestneighbour

for i in $(seq 1 333); do
    fslmaths "${subj_data}/Gordonx.nii.gz" \
        -thr "${i}" \
        -uthr "${i}" \
        -bin "${subj_data}/rois/${i}.nii.gz"
done

for roi in "${subj_data}"/rois/*.nii.gz; do
    roi_name=$(basename "${roi}" .nii.gz)

    3dcalc -echo_edu \
        -a "${roi}" \
        -b "${atlas}" \
        -expr 'ifelse(a*b,b,0)' \
        -datum float \
        -prefix "${subj_data}/roiOverlap/${roi_name}_gm.nii.gz" \
        -overwrite
done

cd "${subj_data}/roiOverlap"

echo "roi best_atlas_label overlap_voxels total_overlap_voxels dominant_overlap_fraction roi_voxels atlas_label_voxels jaccard dice_mean dice_max dice_n_slices" > lab_fin.txt

for overlap in *_gm.nii.gz; do
    name=$(basename "${overlap}" .nii.gz)
    roi_id="${name%_gm}"

    roi_mask="${subj_data}/rois/${roi_id}.nii.gz"

    3dROIstats \
        -nzvoxels \
        -1Dformat \
        -mask "${overlap}" \
        "${overlap}" > "${name}_roi.1D"

    1d_tool.py \
        -infile "${name}_roi.1D" \
        -select_rows '0' \
        -write "${name}_t2.1D" \
        -overwrite

    read -r -a array < "${name}_t2.1D"

    max_voxels=0
    best_label=0
    total_voxels=0

    for ((idx=0; idx<${#array[@]}; idx+=2)); do
        label="${array[idx]}"
        voxels="${array[idx+1]}"

        total_voxels=$((total_voxels + voxels))

        if (( voxels > max_voxels )); then
            max_voxels="${voxels}"
            best_label="${label}"
        fi
    done

    atlas_label_mask="${subj_data}/tmp/${roi_id}_atlasLabel_${best_label}.nii.gz"

    3dcalc \
        -a "${atlas}" \
        -expr "equals(a,${best_label})" \
        -prefix "${atlas_label_mask}" \
        -overwrite

    roi_voxels=$(3dBrickStat -count -non-zero "${roi_mask}")
    atlas_label_voxels=$(3dBrickStat -count -non-zero "${atlas_label_mask}")

    dominant_overlap_fraction=$(awk -v x="${max_voxels}" -v y="${total_voxels}" \
        'BEGIN {if(y>0) print x/y; else print "NA"}')

    jaccard=$(awk \
        -v inter="${max_voxels}" \
        -v a="${roi_voxels}" \
        -v b="${atlas_label_voxels}" \
        'BEGIN {
            union=a+b-inter;
            if(union>0) print inter/union;
            else print "NA"
        }')

    dice_prefix="${subj_data}/dice/${roi_id}_label_${best_label}_dice"

    3dSliceNDice \
        -insetA "${roi_mask}" \
        -insetB "${atlas_label_mask}" \
        -out_domain AorB \
        -prefix "${dice_prefix}" \
        -no_cmd_echo

    dice_mean=$(awk '!/^#/ && $5 != "" {sum+=$5; n++} END {if(n>0) print sum/n; else print "NA"}' "${dice_prefix}"_*.1D)

    dice_max=$(awk '!/^#/ && $5 != "" {if($5>max) max=$5} END {if(max!="") print max; else print "NA"}' "${dice_prefix}"_*.1D)

    dice_n_slices=$(awk '!/^#/ && $5 != "" {n++} END {print n+0}' "${dice_prefix}"_*.1D)

    echo "${roi_id} ${best_label} ${max_voxels} ${total_voxels} ${dominant_overlap_fraction} ${roi_voxels} ${atlas_label_voxels} ${jaccard} ${dice_mean} ${dice_max} ${dice_n_slices}" >> lab_fin.txt
done
