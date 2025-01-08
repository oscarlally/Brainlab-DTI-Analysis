#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 15/02/2023

@author: oscarlally
"""

import os
import shutil
from shutil import rmtree
import numpy as np
import nibabel as nib
import subprocess
import signal
import shutil
import re
from tkinter import ttk
import tkinter as tk
import pydicom


def find_dir(pid, base_dir):
    x = 0
    for root, subdirs, files in os.walk(base_dir):
        for d in subdirs:
            if d == pid:
                x += 1
                return os.path.join(root, d)
    if x == 0:
        print('Please retype in patient ID')
        new_pid = input()
        find_dir(new_pid, base_dir)


def check_and_handle_directories(dir_list):
    for directory in dir_list:
        if not os.path.exists(directory):
            # Create directory if it doesn't exist
            print(f"Creating directory: {directory}")
            os.makedirs(directory)
        else:
            # Directory exists
            if os.listdir(directory):
                # Directory is not empty
                print(f"The directory '{directory}' exists and is not empty.")
                while True:
                    choice = input(f"Do you want to delete its contents and recreate it? (y/n): ").lower()
                    if choice == 'y':
                        # Delete and recreate the directory
                        print(f"Deleting contents of {directory} and recreating it.")
                        shutil.rmtree(directory)
                        os.makedirs(directory)
                        break
                    elif choice == 'n':
                        print(f"Leaving the directory '{directory}' as is.")
                        break
                    else:
                        print("Invalid input. Please enter 'y' or 'n'.")
            else:
                print(f"The directory '{directory}' exists and is empty.")



def get_full_file_names(directory_path):
    """Retrieve full file paths while excluding hidden files."""
    if not os.path.isdir(directory_path):
        print(f"Directory {directory_path} does not exist.")
        return []
    file_names = [f for f in os.listdir(directory_path) if not f.startswith('.')]
    full_file_names = [os.path.join(directory_path, file) for file in file_names]
    return full_file_names


def delete_files_in_folder(folder_path):
    """Deletes all files in a specified folder."""
    if os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f'Deleted: {file_path}')
    else:
        print(f'The path {folder_path} is not a valid directory.')


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
        print(
            "The application is not in your user directory or your local directory. Please move it to either of these directories")


def run(cmd):
    current_dir = os.getcwd()
    home_dir = os.path.expanduser("~")
    functions_path = find_app('mrtrix3', '/usr/local/', home_dir)
    functions_path = f"{functions_path}/bin"
    os.chdir(functions_path)
    process = subprocess.run(cmd.split())
    os.chdir(current_dir)


def get_counts(tck_image):
    cmd = f"tckinfo -count {tck_image}"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)

    output = result.stdout

    last_line = output.split('\n')[-2:-1]

    match = re.search(r'\d+', last_line[0])

    if match:
        number = int(match.group())

    out_file = tck_image.split('/')[-1]

    print(f"Actual Tract Count in {out_file} is {number}")

    return int(number)


def convert_tracts(t1_mif, debug):
    current_dir = os.getcwd()
    nii_dir = f"{current_dir}/mrtrix3_files/nifti/"
    tract_dir = f"{current_dir}/mrtrix3_files/tracts/"
    fa_tensor = f"{current_dir}/mrtrix3_files/tensors/fa.mif"

    tract_files = []
    dir_files = os.listdir(tract_dir)
    for i in dir_files:
        if '.tck' in i:
            tract_files.append(f"{i}")

    for i in tract_files:
        mif_file = f"{tract_dir}{i.split('.')[0]}.mif"
        tck_file = f"{tract_dir}{i.split('.')[0]}.tck"
        norm_file = f"{tract_dir}{i.split('.')[0]}_NORM.mif"
        tck_to_mif = f"tckmap -template {fa_tensor} {tck_file} {mif_file}"
        run(tck_to_mif)
        N_tracts = get_counts(f"{tract_dir}{i}")
        run(f"mrcalc {mif_file} {N_tracts} -div {norm_file}")
        if debug == 'debug':
            mrview_cmd = f"mrview -mode 2 -load {t1_mif} -interpolation 0 -overlay.load {norm_file} -comments 0"
            run(mrview_cmd)
        norm_nii_file = f"{nii_dir}{i.split('.')[0]}_NORM.nii"
        run(f"mrconvert -strides -1,2,3 {norm_file} {norm_nii_file} -axes 0,1,2")

    nii_files = os.listdir(nii_dir)
    for i in nii_files:
        if 't1' in i.lower():
            t1_nii_file = f"{nii_dir}{i}"
            t1_bet_file = f"{nii_dir}{i.split('.')[0]}_bet.nii.gz"
            bet_cmd = f"bet {t1_nii_file} {t1_bet_file} -n -m"
            run(bet_cmd)


def get_volumes(mif_image):
    cmd = f"mrinfo -size {mif_image}"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)

    if result.returncode == 0:
        size_str = result.stdout.strip()
        size = tuple(map(int, size_str.split()))
        print(f"Image dimensions: {size}")
    else:
        print(f"Error: {result.stderr.strip()}")

    output = result.stdout
    print(output)
    volumes = int(output.split(' ')[-1])

    return volumes


def masking(dwi_cmd, mr_conv_1_cmd, mr_conv_2_cmd, debug):
    current_dir = os.getcwd()
    run(dwi_cmd)
    run(mr_conv_1_cmd)
    run(mr_conv_2_cmd)

    b0_extract_nii = f"{current_dir}/mrtrix3_files/masking/extracted_b0.nii"
    moved_b0_extract_nii = f"{current_dir}/mrtrix3_files/nifti/extracted_b0.nii"
    b0_upsamp = f"{current_dir}/mrtrix3_files/masking/b0_upsamp.nii.gz"
    b0_upsamp_mask = f"{current_dir}/mrtrix3_files/masking/b0_upsamp_mask.nii.gz"

    # Ensure the 'nifti' directory exists
    os.makedirs(os.path.dirname(moved_b0_extract_nii), exist_ok=True)
    shutil.copy(b0_extract_nii, moved_b0_extract_nii)

    g = input("g-value vertical gradient in fractional intensity threshold (-1->1); default=0: ")
    f = input("f-value fractional intensity threshold (0->1); default=0.5: ")

    bet_cmd = f"bet {b0_extract_nii} {b0_upsamp} -n -m -f {f} -g {g}"
    run(bet_cmd)

    if debug == 'debug':
        print('Check if the mask has worked. If it has not, re-run this script or check_mask function in mask.py.')
        fsleyes_path = os.environ.get('FSLDIR')
        fsleyes_bin = f"{fsleyes_path}/bin/fsleyes"
        fsl_cmd = f"{fsleyes_bin} {b0_extract_nii} {b0_upsamp_mask}"
        subprocess.run(fsl_cmd.split())
        os.chdir(current_dir)

    os.rename(b0_upsamp_mask, f"{current_dir}/mrtrix3_files/masking/mask_final.nii.gz")
    with open(f"{current_dir}/mrtrix3_files/masking/mask_params.txt", 'a') as param_file:
        param_file.write(f"The g-value is {g} and f-value is {f}\n")


def create_mask(nii_list, debug):
    current_dir = os.getcwd()
    upsample_out = f"{current_dir}/mrtrix3_files/eddy/dwi_eddy_upsamp.mif"
    b0_extract = f"{current_dir}/mrtrix3_files/masking/extracted_b0.mif"
    b0_1_extract = f"{current_dir}/mrtrix3_files/masking/extracted_b0_1.mif"
    b0_extract_nii = f"{current_dir}/mrtrix3_files/masking/extracted_b0.nii"
    mask_final = f"{current_dir}/mrtrix3_files/masking/mask_final.nii.gz"
    mask_mif = f"{current_dir}/mrtrix3_files/masking/mask_final.mif"

    nii_list.append(b0_extract_nii)

    if not os.path.exists(mask_mif):
        dwi_cmd = f"dwiextract -bzero {upsample_out} {b0_extract} -force"
        mr_conv_1_cmd = f"mrconvert {b0_extract} {b0_1_extract} -coord 3 0 -axes 0,1,2"
        mr_conv_2_cmd = f"mrconvert -strides -1,2,3 {b0_1_extract} {b0_extract_nii}"

        masking(dwi_cmd, mr_conv_1_cmd, mr_conv_2_cmd, debug)

        continue_yn = input('Mask correct and continue with analysis? (y/n): ')
        if continue_yn.lower() != 'y':
            rmtree(f"{current_dir}/mrtrix3_files/masking/")
            os.makedirs(f"{current_dir}/mrtrix3_files/masking/")
            create_mask(nii_list, debug)
        else:
            print('Mask Successfully Made')
    else:
        mask_input = input("Are you sure you want to create a new mask? (y/n): ")
        if mask_input.lower() == 'y':
            dwi_cmd = f"dwiextract -bzero {upsample_out} {b0_extract} -force"
            mr_conv_1_cmd = f"mrconvert {b0_extract} {b0_1_extract} -coord 3 0 -axes 0,1,2"
            mr_conv_2_cmd = f"mrconvert -strides -1,2,3 {b0_1_extract} {b0_extract_nii}"

            masking(dwi_cmd, mr_conv_1_cmd, mr_conv_2_cmd, debug)

            continue_yn = input('Mask correct and continue with analysis? (y/n): ')
            if continue_yn.lower() != 'y':
                rmtree(f"{current_dir}/mrtrix3_files/masking/")
                os.makedirs(f"{current_dir}/mrtrix3_files/masking/")
                create_mask(nii_list, debug)
            else:
                print('Mask Successfully Made')


def tensor_estimation(DWI_shell, debug):
    current_dir = os.getcwd()
    mask_final = f"{current_dir}/mrtrix3_files/masking/mask_final.nii.gz"
    mask_mif = f"{current_dir}/mrtrix3_files/masking/mask_final.mif"
    mr_conv_3_cmd = f"mrconvert {mask_final} {mask_mif}"
    run(mr_conv_3_cmd)

    response_wm = f"{current_dir}/mrtrix3_files/response/response_wm.txt"
    response_gm = f"{current_dir}/mrtrix3_files/response/response_gm.txt"
    response_csf = f"{current_dir}/mrtrix3_files/response/response_csf.txt"
    response_voxels = f"{current_dir}/mrtrix3_files/response/response_voxels.mif"

    """TENSOR ESTIMATION"""

    upsample_out = f"{current_dir}/mrtrix3_files/eddy/dwi_eddy_upsamp.mif"
    dwi_tensor = f"{current_dir}/mrtrix3_files/tensors/dwi_tensor.mif"
    fa_tensor = f"{current_dir}/mrtrix3_files/tensors/fa.mif"
    ev_tensor = f"{current_dir}/mrtrix3_files/tensors/ev.mif"
    fa_nii = f"{current_dir}/mrtrix3_files/tensors/fa.nii.gz"

    if not os.path.exists(dwi_tensor):
        print("Step 7: Tensor estimation")
        dwi2tensor_cmd = f"dwi2tensor {upsample_out} {dwi_tensor} -mask {mask_mif}"
        tens2metr_cmd = f"tensor2metric -mask {mask_mif} -fa {fa_tensor} -vector {ev_tensor} {dwi_tensor}"
        conv_fa = f"mrconvert {fa_tensor} {fa_nii}"
        run(dwi2tensor_cmd)
        run(tens2metr_cmd)
        run(conv_fa)

    if debug == 'debug':
        print("DEBUG STEP: Check the FA and EV maps")
        mrview_tensor = f"mrview -load {fa_tensor} -interpolation 0 -load {ev_tensor} -interpolation 0 -odf.load_tensor {dwi_tensor}"
        run(mrview_tensor)

    wm_fod = f"{current_dir}/mrtrix3_files/fods/wm_fod.mif"
    wm_fod_int = f"{current_dir}/mrtrix3_files/fods/wm_fod_int.mif"
    csf_fod = f"{current_dir}/mrtrix3_files/fods/csf_fod.mif"
    gm_fod = f"{current_dir}/mrtrix3_files/fods/gm_fod.mif"
    tissue_vf = f"{current_dir}/mrtrix3_files/fods/tissue_vf.mif"

    # Perform multi shell multi tissue constrained spherical deconvolution
    if DWI_shell.lower() == 'n':
        print("Single shell data")
        dwi2fod_cmd = f"dwi2fod msmt_csd -mask {mask_mif} {upsample_out} {response_wm} {wm_fod} {response_csf} {csf_fod} "
        run(dwi2fod_cmd)
    elif DWI_shell.lower() == 'y':
        print("Multi-shell data")
        dwi2fod_cmd = f"dwi2fod msmt_csd -mask {mask_mif} {upsample_out} {response_wm} {wm_fod} {response_gm} {gm_fod} {response_csf} {csf_fod} "
        run(dwi2fod_cmd)
        mrconv_cmd = f"mrconvert {wm_fod} {wm_fod_int} -coord 3 0"
        run(mrconv_cmd)
        mrcat_cmd = f"mrcat {csf_fod} {gm_fod} {wm_fod_int} {tissue_vf}"
        run(mrcat_cmd)
        if debug == 'debug':
            mrview_cmd = f"mrview -mode 2 -load {tissue_vf} -interpolation 0"
            run(mrview_cmd)


def mirror_nifti(input_nifti_path, output_nifti_path):
    # Load NIfTI file
    nifti_data = nib.load(input_nifti_path)
    nifti_data = nib.as_closest_canonical(nifti_data)

    # Get voxel data
    voxel_data = nifti_data.get_fdata()

    # Mirror along the X-axis
    mirrored_data = np.flip(voxel_data, axis=1)

    # Create a new NIfTI object with mirrored data
    mirrored_nifti = nib.Nifti1Image(mirrored_data, nifti_data.affine, nifti_data.header)

    # Save the mirrored NIfTI file
    nib.save(mirrored_nifti, output_nifti_path)


def norm_nii(input_file, output_file, min_value, max_value):
    # Load the NIfTI image
    img = nib.load(input_file)
    data = img.get_fdata()

    # Normalize the voxel values to the specified range
    normalized_data = (data - np.min(data)) / (np.max(data) - np.min(data)) * (max_value - min_value) + min_value

    # Save the normalized data to a new NIfTI file
    normalized_img = nib.Nifti1Image(normalized_data, img.affine)
    nib.save(normalized_img, output_file)


def skew(binarised_object, skew_factor):
    nifti_file = nib.load(binarised_object)
    array = nifti_file.get_fdata()
    skewed_array = np.where(array <= 0, 0, np.where(array >= 1, 1, 1 - (1 - array) ** skew_factor))
    modified_file = nib.Nifti1Image(skewed_array, nifti_file.affine)
    return modified_file


def copy_directory(source_dir, destination_dir):
    try:
        # Ensure the destination directory exists
        target_path = os.path.join(destination_dir, os.path.basename(source_dir))

        # Check if the directory already exists
        if os.path.exists(target_path):
            print(f"Directory {target_path} already exists. Deleting it...")
            shutil.rmtree(target_path)  # Remove the existing directory

        # Copy the entire directory
        shutil.copytree(source_dir, target_path)
        print(f"Directory copied from {source_dir} to {destination_dir}")
    except Exception as e:
        print(f"An error occurred: {e}")