from Bash2PythonFuncs import karawun_run, register, run, get_pixel_range, norm_nii, skew, mirror_nifti
from final_dcm import create_brainlab_object
import nibabel as nib
import numpy as np
import pydicom
import os

"""After masking"""

def registration(pt_dir, template_file, tract_name, debug):

    nii_dir = f"{pt_dir}Processed/11_nifti/"
    overlay_dir = f"{pt_dir}Processed/12_overlays/"
    final_dir = f"{pt_dir}Processed/14_volume/"
    
    binarised_object = f"{overlay_dir}binarised_object.nii.gz"
    t1_object = f"{overlay_dir}t1_object.nii.gz"
    t1_hole = f"{overlay_dir}t1_hole.nii.gz"
    binarised_skew = f"{overlay_dir}binary_skew.nii.gz"
    t1_dicom_range = f"{overlay_dir}t1_dicom_range.nii.gz"
    object_dicom_range = f"{overlay_dir}object_dicom_range.nii.gz"
    t1_burned = f"{overlay_dir}t1_burned.nii.gz"
    t1_burned_final = f"{overlay_dir}t1_burned_final.nii.gz"

    relevant_dcm = pydicom.dcmread(template_file[0])
    data_dicom = relevant_dcm.pixel_array
    pixel_values_dicom = data_dicom.flatten()
    max_value = max(pixel_values_dicom)

    print()

    while True:

        correct_trans, registered = register(pt_dir, debug)

        print()

        happy = input('Do you want to register another object? (y/n): ')

        if happy.lower() == 'n':

            break

    for i in os.listdir(nii_dir):
        if 't1.nii' in i:
            t1_nii = f"{nii_dir}{i}"


    norm_nii(registered, binarised_object, 0, 1)
    modified_file = skew(binarised_object, 10)
    nib.save(modified_file, f"{binarised_skew}")

    mult_cmd = f"fslmaths {t1_nii} -mul {binarised_object} {t1_object}"
    sub_cmd = f"fslmaths {t1_nii} -sub {t1_object} {t1_hole}"

    run(mult_cmd)
    run(sub_cmd)

    nifti_file = nib.load(f"{t1_hole}")
    nii_data = nifti_file.get_fdata()
    max_hole = np.max(nii_data)
    norm_num = 60 / max_hole

    mult_2_cmd = f"fslmaths {t1_hole} -mul {norm_num} {t1_dicom_range}"
    mult_3_cmd = f"fslmaths {binarised_skew} -mul {max_value - 60} {object_dicom_range}"
    add_cmd = f"fslmaths {t1_dicom_range} -add {object_dicom_range} {t1_burned}"

    run(mult_2_cmd)
    run(mult_3_cmd)
    run(add_cmd)

    mirror_nifti(t1_burned, t1_burned_final)

    object_path = f"{final_dir}Brainlab_Object.dcm"

    while True:
        print()
        print("Dicom creation.  Please open the resultant dicom in the 14/volume folder and play around with the parameters as necessary.")
        print()
        wind_factor = input('Type in the maximum factor (default = 0.5): ')
        print()
        max_factor = input('Type in the window factor (default = 0.66: ')
        print()
        create_brainlab_object(tract_name, t1_burned_final, template_file[0], object_path, float(max_factor), float(wind_factor))
        print()
        check = input('Is the dicom file flipped? (y/n):  ')
        if check == 'y':
            create_brainlab_object(tract_name, t1_burned, template_file[0], object_path, float(max_factor), float(wind_factor))
        print()
        happy = input('Is the dicom contrast sufficient? (y/n): ')
        print()

        if happy.lower() == 'y':
            break

