from Bash2PythonFuncs import zero_test, karawun_run, get_transform_matrix, register, run
from final_dcm import final_dicom_conversion
import os
import subprocess


"""After masking"""


def registration(pt_dir, nii_files, dcm_template):

    nii_dir = f"{pt_dir}Processed/11_nifti/"
    dcm_dir = f"{pt_dir}Processed/12_volumes/"
    final_dir = f"{pt_dir}Processed/14_dicom/"
    
    binarised_object = f"{nii_dir}binarised_object.nii.gz"
    t1_object = f"{nii_dir}t1_object.nii.gz"
    t1_hole = f"{nii_dir}t1_hole.nii.gz"
    t1_dicom_range = f"{nii_dir}t1_dicom_range.nii.gz"
    object_dicom_range = f"{nii_dir}object_dicom_range.nii.gz"
    t1_burned = f"{nii_dir}t1_burned.nii.gz"
    dcm_file = f"{dcm_dir}t1_burned.dcm"
    
    
    norm = f"{nii_dir}mrtrix3-OR_uni_NORM.nii"
    b0_extract_nii = f"{nii_dir}extracted_b0.nii"
    t1_bet_nii = f"{nii_dir}t1_bet_mask.nii.gz"
    orig_tract = f"{pt_dir}Processed/9_tract/mrtrix3-OR_uni.mif"

    tract_input = input('Please type in the tract you want to register.  ')
    
    correct_register, object_file_reg = register(pt_dir, tract_input)
    
    object_file = object_file_reg.replace('_registered', '')
    
    print(object_file)
    
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
    
    mult_2_cmd = f"fslmaths {t1_hole} -mul 2.05 {t1_dicom_range}"
    mult_3_cmd = f"fslmaths {binarised_object} -mul 4090 {object_dicom_range}"
    add_cmd = f"fslmaths {t1_dicom_range} -add {object_dicom_range} {t1_burned}"
    
    
    run(div_cmd)
    run(mult_cmd)
    run(sub_cmd)
    run(mult_2_cmd)
    run(mult_3_cmd)
    run(add_cmd)
    
    dcm_conversion = karawun_run(pt_dir, dcm_template, t1_burned, dcm_dir, t1_nii)
    
    dcm_dir = f"{dcm_dir}t1_burned/"

    modified_dicom_path = f"{final_dir}Brainlab_Object.dcm"

    final_dicom_conversion(dcm_dir, dcm_template, modified_dicom_path)
    
    
    
    stats_cmd = f"fslstats {t1_nii} -R"
    result = subprocess.run(stats_cmd.split(), capture_output=True, text=True)
    result_str = result.stdout.strip()
    print(result_str)

    stats_cmd = f"fslstats {object_file} -R"
    result = subprocess.run(stats_cmd.split(), capture_output=True, text=True)
    result_str = result.stdout.strip()
    print(result_str)

    stats_cmd = f"fslstats {t1_object} -R"
    result = subprocess.run(stats_cmd.split(), capture_output=True, text=True)
    result_str = result.stdout.strip()
    print(result_str)
    
    stats_cmd = f"fslstats {registered} -R"
    result = subprocess.run(stats_cmd.split(), capture_output=True, text=True)
    result_str = result.stdout.strip()
    print(result_str)
    
    stats_cmd = f"fslstats {b0_extract_nii} -R"
    result = subprocess.run(stats_cmd.split(), capture_output=True, text=True)
    result_str = result.stdout.strip()
    print(result_str)
    
    stats_cmd = f"fslstats {t1_bet_nii} -R"
    result = subprocess.run(stats_cmd.split(), capture_output=True, text=True)
    result_str = result.stdout.strip()
    print(result_str)
    
    stats_cmd = f"fslstats {norm} -R"
    result = subprocess.run(stats_cmd.split(), capture_output=True, text=True)
    result_str = result.stdout.strip()
    print(result_str)
    
    stats_cmd = f"fslstats {orig_tract} -R"
    result = subprocess.run(stats_cmd.split(), capture_output=True, text=True)
    result_str = result.stdout.strip()
    print(result_str)
   
   
