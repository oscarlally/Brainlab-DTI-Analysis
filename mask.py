#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 15/02/2023

@author: oscarlally
"""

import os
from shutil import rmtree
from Bash2PythonFuncs import masking



def create_mask(pt_id, pt_dir, nii_list, debug):


    os.chdir(f"{pt_dir}Processed/")
    upsample_out = f"{os.getcwd()}/4_eddy/dwi_eddy_upsamp.mif"
    b0_extract = f"{os.getcwd()}/6_mask/extracted_b0.mif"
    b0_1_extract = f"{os.getcwd()}/6_mask/extracted_b0_1.mif"
    b0_extract_nii = f"{os.getcwd()}/6_mask/extracted_b0.nii"
    b0_upsamp = f"{os.getcwd()}/6_mask/b0_upsamp.nii.gz"
    b0_upsamp_mask = f"{os.getcwd()}/6_mask/b0_upsamp_mask.nii.gz"
    mask_final = f"{os.getcwd()}/6_mask/mask_final.nii.gz"
    mask_mif = f"{os.getcwd()}/6_mask/mask_final.mif"
    nii_list.append(b0_extract_nii)
    

    #if os.path.exists(f"{b0_extract}") == False:
    if os.path.exists(f"{mask_mif}") == False:
        os.chdir(os.path.split(mask_final)[0])
        dwi_cmd = f"dwiextract -bzero {upsample_out} {b0_extract}"
        mr_conv_1_cmd = f"mrconvert -strides -1,2,3 {b0_extract} {b0_1_extract}"
        mr_conv_2_cmd = f"mrconvert -strides -1,2,3 {b0_1_extract} {b0_extract_nii}"

        masking(pt_id, pt_dir, dwi_cmd, mr_conv_1_cmd, mr_conv_2_cmd, debug)
        continue_yn = input('Mask correct and continue with analysis? (y/n): ')
        if continue_yn.lower() != 'y':
            rmtree(f"{pt_dir}Processed/6_mask/")
            os.makedirs(f"{pt_dir}Processed/6_mask/")
            create_mask()
        else:
            print('Mask Successfully Made')
 
 
    else:
        mask_input = input("Are you sure you want to create a new mask? (y/n):  ")
        if mask_input.lower() == 'y':
            os.chdir(os.path.split(mask_final)[0])
            dwi_cmd = f"dwiextract -bzero {upsample_out} {b0_extract} -force"
            mr_conv_1_cmd = f"mrconvert {b0_extract} {b0_1_extract} -force"
            mr_conv_2_cmd = f"mrconvert {b0_1_extract} {b0_extract_nii} -force"

            masking(pt_id, pt_dir, dwi_cmd, mr_conv_1_cmd, mr_conv_2_cmd)
            continue_yn = input('Mask correct and continue with analysis? (y/n): ')
            if continue_yn.lower() != 'y':
                rmtree(f"{pt_dir}Processed/6_mask/")
                os.makedirs(f"{pt_dir}Processed/6_mask/")
                create_mask()
            else:
                print('Mask Successfully Made')



