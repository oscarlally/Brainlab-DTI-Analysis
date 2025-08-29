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


def run_fsl(cmd, dependencies, pid):
    if dependencies['fsl']:
        if 'extracted_b0' in cmd:
            output_file = 'extracted_b0.txt'
        else:
            output_file = 'object.txt'
        output_dir = f"./mrtrix3_files/{pid}/misc/"
        with open(f"{output_dir}{output_file}", 'w') as f:
            process = subprocess.run(cmd.split(), stdout=f, stderr=subprocess.STDOUT)
        with open(f"{output_dir}{output_file}", 'r') as f:
            output = f.read()
    else:
        base_dir = os.getcwd()
        home_dir = os.path.expanduser("~")
        functions_path = find_app('fsl', '/usr/local/', home_dir)
        functions_path = f"{functions_path}/bin"
        os.chdir(functions_path)
        if 'extracted_b0' in cmd:
            output_file = 'extracted_b0.txt'
        else:
            output_file = 'object.txt'
        output_dir = f"{base_dir}/mrtrix3_files/{pid}/misc/"
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


def actual_registration(debug, dependencies, pid):

    nii_dir = f"{current_dir}/mrtrix3_files/{pid}/nifti/"
    misc_dir = f"{current_dir}/mrtrix3_files/{pid}/misc/"
    b0_extract_nii = f"{nii_dir}extracted_b0.nii"
    nii_files = os.listdir(nii_dir)
    for i in nii_files:
        if 'bet' in i:
            t1_bet_nii = f"{nii_dir}{i}"

    print()
    paths_to_convert = [p for p in os.listdir(nii_dir) if 'NORM' in p]
    print('Available tracts to register are are:')
    for idx, i in enumerate(paths_to_convert):
        print(f"{idx + 1}. {i}")
    print()
    select = input("Please type in the number of the tract you would like to register:  ")
    tract_to_reg = paths_to_convert[int(select) - 1]

    object_nii = f"{nii_dir}{tract_to_reg}"
    object_pre_name = object_nii.split('/')[-1]
    object_name = object_pre_name.split('.')[0]

    registered_object = f"{nii_dir}{object_name}_registered.nii.gz"

    fslhd_cmd_1 = f"fslhd {b0_extract_nii}"
    fslhd_cmd_2 = f"fslhd {object_nii}"

    run_fsl(fslhd_cmd_1, dependencies, pid)
    run_fsl(fslhd_cmd_2, dependencies, pid)

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
            print()
            print('NB: If you are changing the threshold via fsleyes and you want to save that threshold, \n'
                  'then please save the thresholded tract in the mrtrix3_files/nifti directory.')

            thresholded = change_thresh(nii_dir, object_name, thresh, debug)

            print()

            happy = input('Do you want to re-threshold? (y/n): ')

            if happy == 'n':

                break

    else:

        thresholded = f"{registered_object}"

    """Potential for problems here given that the thresholded object is not being subtracted"""

    if identical == 0:

        print()
        cont = input('Continue? (y/n): ')

        return 0, cont, thresholded

    else:

        print()
        cont = input('Continue? (y/n): ')

        return 1, cont, thresholded


def registration(debug, dependencies, pid):

    correct_trans, cont, registered = actual_registration(debug, dependencies, pid)

    return correct_trans, cont, registered
