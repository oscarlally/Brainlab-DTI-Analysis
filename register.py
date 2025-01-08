from functions import run, norm_nii, skew, mirror_nifti, get_full_file_names, copy_directory
from final_dcm import create_brainlab_object
from functions import get_full_file_names
from tkinter import filedialog
import nibabel as nib
import numpy as np
import subprocess
import signal
import pydicom
import os


current_dir = os.getcwd()


class TimeoutException(Exception):
    pass


def find_app(application, dir_1, dir_2, timeout_duration=5):
    def find(application, dir, statement):
        x = 0
        for root, subdirs, files in os.walk(dir):
            for d in subdirs:
                if d == application:
                    x += 1
                    if x != 0:
                        a = os.path.join(root, d)
                        if a != None:
                            return os.path.join(root, d)
                        else:
                            print(statement)

    def timeout_handler(signum, frame):
        raise TimeoutException("Function timed out")

    result = None
    statement = "Could not find in first directory, trying another"
    for i in range(2):
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_duration)
            result = find(application, dir_1 if i == 0 else dir_2, statement)
            signal.alarm(0)
        except TimeoutException:
            print(f"Timed out while searching {'first' if i == 0 else 'second'} directory")
            result = None
        if result is not None:
            break
    return result

    if result is None:
        print("The application is not in your user directory or your local directory. \n"
              "Please move it to either of these directories")


def run_fsl(cmd):
    base_dir = os.getcwd()
    home_dir = os.path.expanduser("~")
    functions_path = find_app('fsl', '/usr/local/', home_dir)
    functions_path = f"{functions_path}/bin"
    os.chdir(functions_path)
    if 'extracted_b0' in cmd:
        output_file = 'extracted_b0.txt'
    else:
        output_file = 'object.txt'
    output_dir = f"{base_dir}/mrtrix3_files/misc/"
    current_dir = os.getcwd()
    with open(f"{output_dir}{output_file}", 'w') as f:
        process = subprocess.run(cmd.split(), stdout=f, stderr=subprocess.STDOUT)
    with open(f"{output_dir}{output_file}", 'r') as f:
        output = f.read()
    os.chdir(base_dir)


def zero_test(file_1, file_2):
    with open(f"{file_1}", 'r') as f1, open(f"{file_2}", 'r') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
    result = [line for line in lines1 if line not in lines2]
    if len(result) > 4:
        print()
        print('The headers are not the same; the nii conversion has been unsuccessful.  Please re-run.')
        print()
        return 0
    else:
        print()
        print('The headers are identical, the nii conversion has been successful.')
        print()
        return 1


def change_thresh(nii_dir, object_name, thresh, debug):

    thresholded_obj = f"{nii_dir}{object_name}_registered_threshold_{thresh}.nii.gz"
    chtrsh_cmd = f"fslmaths {nii_dir}{object_name}_registered.nii.gz -thr {thresh} {thresholded_obj}"
    view_cmd = f"fsleyes {thresholded_obj}"
    run(chtrsh_cmd)
    if debug == 'debug':
        run(view_cmd)
    return thresholded_obj


def actual_registration(debug):

    nii_dir = f"{current_dir}/mrtrix3_files/nifti/"
    misc_dir = f"{current_dir}/mrtrix3_files/misc/"
    b0_extract_nii = f"{nii_dir}extracted_b0.nii"
    t1_bet_nii = f"{nii_dir}t1_bet_mask.nii.gz"

    print()
    print('Please choose the tract that you would like to register')

    file_paths = filedialog.askopenfilenames(title='Select tract to register',
                                             filetypes=[('Nii Files', '*.nii'), ('All files', '*.*')],
                                             initialdir=nii_dir)

    object_nii = list(file_paths)[0]
    print(object_nii)
    object_pre_name = object_nii.split('/')[-1]
    object_name = object_pre_name.split('.')[0][8:]

    registered_object = f"{nii_dir}{object_name}_registered.nii.gz"

    fslhd_cmd_1 = f"fslhd {b0_extract_nii}"
    fslhd_cmd_2 = f"fslhd {object_nii}"

    run_fsl(fslhd_cmd_1)
    run_fsl(fslhd_cmd_2)

    identical = zero_test(f"{misc_dir}extracted_b0.txt", f"{misc_dir}object.txt")

    # 1. register the dwi to T1 and get transform
    trans_cmd_1 = f"flirt -in {b0_extract_nii} -ref {t1_bet_nii} -out {nii_dir}outvol.nii -omat {misc_dir}transform.mat -dof 6"
    run(trans_cmd_1)

    # 2. apply transform to object
    trans_cmd_2 = f"flirt -in {object_nii} -ref {t1_bet_nii} -out {registered_object} -init {misc_dir}transform.mat -applyxfm"
    run(trans_cmd_2)

    check = input('Do you want to threshold the registered tract? (y/n): ')

    if check.lower() == 'y':

        while True:
            print()

            thresh = input('Please type in the threshold value that you want to try: ')

            thresholded = change_thresh(nii_dir, object_name, thresh, debug)

            print()

            happy = input('Do you want to re-threshold? (y/n): ')

            if happy == 'n':

                break

    else:

        thresholded = f"{registered_object}"

    """Potential for problems here given that the thresholded object is not being subtracted"""

    if identical == 0:

        return 0, thresholded

    else:

        return 1, thresholded


def registration(template_file, t1_nii, diff_data_dir, debug):
    tracts = get_full_file_names(f"{current_dir}/mrtrix3_files/tracts")

    nii_dir = f"{current_dir}/mrtrix3_files/nifti/"
    overlay_dir = f"{current_dir}/mrtrix3_files/overlays/"
    final_dir = f"{current_dir}/mrtrix3_files/volumes/"

    binarised_object = f"{overlay_dir}binarised_object.nii.gz"
    t1_object = f"{overlay_dir}t1_object.nii.gz"
    t1_hole = f"{overlay_dir}t1_hole.nii.gz"
    binarised_skew = f"{overlay_dir}binary_skew.nii.gz"
    t1_dicom_range = f"{overlay_dir}t1_dicom_range.nii.gz"
    object_dicom_range = f"{overlay_dir}object_dicom_range.nii.gz"
    t1_burned = f"{overlay_dir}t1_burned.nii.gz"
    t1_burned_final = f"{overlay_dir}t1_burned_final.nii.gz"

    relevant_dcm = pydicom.dcmread(template_file)
    data_dicom = relevant_dcm.pixel_array
    pixel_values_dicom = data_dicom.flatten()
    max_value = max(pixel_values_dicom)

    print()


    while True:

        correct_trans, registered = actual_registration(debug)

        pre_name = registered.split('/')[-1]
        tract_name = pre_name.split('.')[0][8:]

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
        brainlab_name_pre_pre = registered.split('/')
        brainlab_name_pre = brainlab_name_pre_pre[-1].split('_')
        brainlab_name = "" + brainlab_name_pre[0] + brainlab_name_pre[1]

        object_path = f"{final_dir}Brainlab_Object_{brainlab_name}.dcm"

        while True:
            print()
            print(
                "Dicom creation.  Open the resultant dicom in the volumes and play around with the parameters as necessary.")
            print()
            wind_factor = input('Type in the maximum factor (default = 0.5): ')
            print()
            max_factor = input('Type in the window factor (default = 0.66): ')
            print()
            create_brainlab_object(tract_name, t1_burned_final, template_file, object_path, float(max_factor),
                                   float(wind_factor))
            print()
            print('Please now open the dcm (in the volumes folder) and t1_burned.nii (nifti folder).')
            check = input('Is the dicom file flipped? (y/n):  ')
            if check == 'y':
                create_brainlab_object(tract_name, t1_burned, template_file, object_path, float(max_factor),
                                       float(wind_factor))
            print()
            happy = input('Is the dicom contrast sufficient? (y/n): ')
            print()

            if happy.lower() == 'y':
                copy_directory(os.getcwd(), f"{diff_data_dir}/Processed")
                break

        print()

        happy_overall = input('Do you want to register another object? (y/n): ')

        if happy.lower() == 'n':
            break

'''Incase of needing to start at this point, here is the code'''

# pt_dir = '/Users/oscarlally/Desktop/CCL/170087944/raw/'
# template_file = ['/Users/oscarlally/Desktop/CCL/170087944/raw/T1_POST/QUETTI_Luisa__M.MR.fMRI_v1_(old)_L.45.1.2024.07.03.11.44.06.595.47222652.dcm']
# tract_name = 'OR'
# debug = 'y'
# tract = '/Users/oscarlally/Desktop/CCL/170087944/raw/Processed/10_tract/mrtrix-OR_registered_threshold.nii.gz'
# from registration import registration
# registration(pt_dir, template_file, tract_name, debug, tract)