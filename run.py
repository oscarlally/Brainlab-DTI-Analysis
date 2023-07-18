#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 15/02/2023

@author: oscarlally
"""

import sys
import os
import subprocess



from Bash2PythonFuncs import get_bvalue_folders, find_dir, fsl_path_finder, rem_dir
from main import debug, no_debug

home_dir = os.path.expanduser("~")


# FUNCTIONS
def help():
  print("This file analyses DTI data using mrtix software")
  print("If this script is in /Desktop then the DTI data should be stored in the following manner: /Desktop/iMRI_DATA/pt_id/raw/data_folder_here")
  print(f"DEBUG MODE: When prompted you can opt to run in debug mode. If you opt 'yes' then the script will open mrview at each analysis step for you to inspect the result. Don't choose debug mode if you want to leave the code running unsupervised")
  print("The code performs the following steps:")
  print("1. Convert dicom data to .mif")
  print("2. Denoises the data")
  print("3. Performs degibbs")
  print("4. Eddy correction")
  print("5. Calculate response function")
  print("6. Brain masking using fsl bet")
  print("7. Tensor estimation")
  print("To draw ROIs and generate tracts use code CCL_DTI_ROI_TCK.mif")
  print("The code will stop for user interaction at step 6 unless a brain mask has already been created")
  print("Outputs will be stored in iMRI_DATA/pt_id/processed")

# HELP
if len(sys.argv) == 2 and sys.argv[1] == "-h":
  help()
  exit()


pt_id = input('Patient ID: ')
DWI_multishell = input('Is the data multi-shelled? (y/n): ')
pt_dir = find_dir(pt_id, home_dir)
pt_dir = f"{pt_dir}/raw/"
masking_list = []
gentrck_list = []


# INITIALISATION
if os.path.isdir(pt_dir):
    print("Directory for patient ID exists, checking which DTI was acquired.")
    os.chdir(pt_dir)
    bvalue_folders = get_bvalue_folders()
    
    # Check if data is already there and give the option to delete it
    remove = rem_dir(pt_dir)

    isExist = os.path.exists(f"{pt_dir}Processed/1_convert/")
    if isExist == False:
        os.makedirs("1_convert/")
        os.makedirs("2_denoise/")
        os.makedirs("3_degibbs/")
        os.makedirs("4_eddy/")
        os.makedirs("5_response/")
        os.makedirs("6_mask/")
        os.makedirs("7_tensor/")
        os.makedirs("8_msmt/")
        os.makedirs("9_tract/")
        os.makedirs("10_ROI/")
        os.makedirs("11_nifti/")
        os.makedirs("12_overlays")
        os.makedirs("13_dicom")
        os.makedirs("14_misc/")
        os.makedirs("15_volume/")
else:
    print("Error: Folder for the entered patient ID does not exists.")
    print("Exit analysis pipeline due to no pt data found")
    exit(1)
    

while True:
    masking = input("Skip to brain masking? (y/n): ")
    gentrck = input("Skip to tract generation? (y/n: ")

    if masking.lower() == 'y' and gentrck.lower() == 'y':
        print("Skipping all processing steps, going straight to tract generation")
        mask_skip = 'yes'
        gentrck_skip = 'yes'
        masking_list.append(mask_skip)
        gentrck_list.append(gentrck_skip)
        break
    elif masking.lower() == 'y'and gentrck.lower() == 'n':
        print("Skipping all processing steps, going straight to mask creation")
        mask_skip = 'yes'
        gentrck_skip = 'no'
        masking_list.append(mask_skip)
        gentrck_list.append(gentrck_skip)
        break
    elif masking.lower() == 'n' and remove != 1:
        print("Running all processing steps")
        mask_skip = 'no'
        gentrck_skip = 'no'
        masking_list.append(mask_skip)
        gentrck_list.append(gentrck_skip)
        break
    else:
        print("Invalid response")
        
    
        
while True:
    debug_binary = input("Run debug version? (y/n): ")

    if debug_binary.lower() == 'y':
        print("Running in debug mode")
        debug(masking_list[0], gentrck_list[0], bvalue_folders, pt_dir, pt_id, DWI_multishell)
        break
    elif debug_binary.lower() == 'n':
        print("Running without debug steps")
        no_debug(masking_list[0], gentrck_list[0], bvalue_folders, pt_dir, pt_id, DWI_multishell)
        break
    else:
        print("Invalid response")
        
        




