from Bash2PythonFuncs import zero_test, karawun_run, get_transform_matrix, register, run
import os
import subprocess


"""After masking"""


# Then use flirt of the b0s to t1 (both the nii files) to get the transform matrix - can use t1 from dcm straight to nii
# Save the transform matrix
# Apply the flirt the the tracks after weve generated them - apply the transform matrix to the tracks
# Check for strides
# keep the strides the same for both conversions (strides are a flirt argument)
# To check for the correct


# python3.8 -m pip install karawun


def registration(pt_dir, nii_files, dcm_template):

    nii_dir = f"{pt_dir}Processed/11_nifti/"
    dcm_dir = f"{pt_dir}Processed/12_dicom/"
    
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
    
    dcm_dir = f"{dcm_dir}t1_burned"
    
    
    
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
   
   
   
    '''
    run(f"fslmaths 11_nifti/binarised_object.nii -mul 4090 11_nifti/object_dicom_range.nii")

    # 4. multiply to the T1 and then subtract that part of the T1 from the original to make a T1_hole
    run(f"fslmaths 11_nifti/T1_dicom_range.nii -add 11_nifti/object_dicom_range.nii 11_nifti/T1_object_burned.nii")

    # 5. scale the T1 to be 0-2048

    # 6. scale the object to be 3072-4095 (use the unthresholded but registered one)

    # 7. add them together using mrcalc or fslmaths

    # convert to dicom

    # maximum values (for scaling)
    run("fslstats 11_nifti/mrtrix3-OR_uni.nii -R")
    run("fslstats 11_nifti/T1.nii -R")
    '''
    
    

    
    


#    To use the "applyxfm" command from FSL, you first need to have a transformation matrix file (in .mat format) that describes the transformation you want to apply to your image. Once you have this file, you can use the "applyxfm" command to apply the transformation to your input image.
#
#    Here is an example command:
#
#
#    applyxfm -i input.nii.gz -r reference.nii.gz -o output.nii.gz -omat transformation.mat
#
#    In this command, "input.nii.gz" is the image you want to transform, "reference.nii.gz" is the reference image that you want the transformed image to be aligned with, and "transformation.mat" is the .mat file that contains the transformation matrix. The output of the command will be written to "output.nii.gz".
#
#    There are also several optional parameters that you can use to modify the behavior of the "applyxfm" command. For example, you can use the "-applyxfm" option to specify a different transformation matrix file to use, or the "-interp" option to choose the interpolation method used during the transformation.
#
#    You can find more information about the "applyxfm" command and its options in the FSL documentation.


















nii_files = ['/Users/oscarlally/Desktop/CCL/12345/raw/T1/t1.nii.gz',  '/Users/oscarlally/Desktop/CCL/12345/raw/Processed/6_mask/extracted_b0.nii']

"""Useful Notes"""

#script_dir = os.path.dirname(os.path.abspath(__file__))
#p38_file = f"{script_dir}/p38_script.py"
#karawun_dir = "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages"
#importTractography --dicom-template path/to/a/dicom --nifti T1.nii.gz fa.nii.gz --tract-files left_cst.tck right_cst.tck --label-files lesion.nii.gz white_matter.nii.gz  --output-dir path/to/output/folder




''' importTractography: error: argument -d/--dicom-template: /Users/oscarlally/Desktop/CCL/170030027/raw/Processed/12_dicom/t1_burned.dcm does not exist or is not readable'''
