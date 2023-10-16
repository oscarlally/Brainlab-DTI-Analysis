from Bash2PythonFuncs import zero_test, karawun_run, register, run, skew
from final_dcm import final_dicom_conversion
import nibabel as nib
import numpy as np
import os
import subprocess


"""After masking"""



def registration(pt_dir, template_file):

    nii_dir = f"{pt_dir}Processed/11_nifti/"
    overlay_dir = f"{pt_dir}Processed/12_overlays/"
    dcm_dir = f"{pt_dir}Processed/14_dicom/"
    final_dir = f"{pt_dir}Processed/15_volume/"
    
    binarised_object = f"{overlay_dir}binarised_object.nii.gz"
    t1_object = f"{overlay_dir}t1_object.nii.gz"
    t1_hole = f"{overlay_dir}t1_hole.nii.gz"
    binarised_skew = f"{overlay_dir}binary_skew.nii.gz"
    t1_dicom_range = f"{overlay_dir}t1_dicom_range.nii.gz"
    object_dicom_range = f"{overlay_dir}object_dicom_range.nii.gz"
    t1_burned = f"{overlay_dir}t1_burned.nii.gz"
    dcm_file = f"{dcm_dir}t1_burned.dcm"
    
    
    norm = f"{nii_dir}mrtrix3-OR_uni_NORM.nii"
    b0_extract_nii = f"{nii_dir}extracted_b0.nii"
    t1_bet_nii = f"{nii_dir}t1_bet_mask.nii.gz"
    orig_tract = f"{pt_dir}Processed/10_tract/mrtrix3-OR_uni.mif"

    print()
    print()
    tract_input = input('Please type in the tract you want to register.  ')
    
    correct_register, object_file_reg = register(pt_dir, tract_input)
    
    object_file = object_file_reg.replace('_registered', '')
    
    
    # Binarize object
    
    for i in os.listdir(nii_dir):
        if 'register' in i:
            registered = f"{nii_dir}{i}"
        if 't1.nii' in i:
            t1_nii = f"{nii_dir}{i}"
            
    
    stats_cmd = f"fslstats {registered} -R"
    result = subprocess.run(stats_cmd.split(), capture_output=True, text=True)
    result_str = result.stdout.strip()
    min = float(result_str.split(' ')[0])
    max = float(result_str.split(' ')[1])
    
    
    
    div_cmd = f"fslmaths {registered} -div {max} {binarised_object}"
    mult_cmd = f"fslmaths {t1_nii} -mul {binarised_object} {t1_object}"
    sub_cmd = f"fslmaths {t1_nii} -sub {t1_object} {t1_hole}"
    
    run(div_cmd)
    run(mult_cmd)
    run(sub_cmd)


    nifti_file = nib.load(f"{binarised_object}")
    nii_data = nifti_file.get_fdata()
    modified_data = skew(nii_data, 10)
    modified_nifti_file = nib.Nifti1Image(modified_data, nifti_file.affine)
    nib.save(modified_nifti_file, f"{binarised_skew}")
    
    nifti_file = nib.load(f"{t1_hole}")
    nii_data = nifti_file.get_fdata()
    max_hole = np.max(nii_data)
    norm_num = 950/max_hole
    

    mult_2_cmd = f"fslmaths {t1_hole} -mul {norm_num} {t1_dicom_range}"
    mult_3_cmd = f"fslmaths {binarised_object} -mul 4095 {object_dicom_range}"
    add_cmd = f"fslmaths {t1_dicom_range} -add {object_dicom_range} {t1_burned}"
    
    run(mult_2_cmd)
    run(mult_3_cmd)
    run(add_cmd)

    dcm_conversion = karawun_run(pt_dir, template_file[0], t1_burned, dcm_dir, t1_nii)

    modified_dicom_path = f"{final_dir}Brainlab_Object.dcm"

    dcm_dir = f"{dcm_dir}t1_burned/"

    final_dicom_conversion(dcm_dir, template_file[0], modified_dicom_path, 4095)
