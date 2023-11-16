#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 15/02/2023

@author: oscarlally
"""

import os
import argparse


from Bash2PythonFuncs import get_bvalue_folders, find_dir, rem_dir
from intro import intro

from main import debug, no_debug

home_dir = os.path.expanduser("~")

intro()


def run_function(debug_binary):

    pt_id = input('Patient ID: ')
    DWI_multishell = input('Is the data multi-shelled? (y/n): ')
    pt_dir = find_dir(pt_id, home_dir)
    pt_dir = f"{pt_dir}/raw/"
    processed_path = f"{pt_dir}Processed/"
    skip_list = []


    # INITIALISATION
    if os.path.isdir(pt_dir):
        print("Directory for patient ID exists.")
        bvalue_folders = get_bvalue_folders(pt_dir)
        
        # Check if data is already there and give the option to delete it
        remove = rem_dir(processed_path)

        isExist = os.path.exists(f"{processed_path}/1_convert/")
        if isExist == False:
            os.makedirs("1_convert/")
            os.makedirs("2_denoise/")
            os.makedirs("3_degibbs/")
            os.makedirs("4_eddy/")
            os.makedirs("5_response/")
            os.makedirs("6_mask/")
            os.makedirs("7_tensor/")
            os.makedirs("8_msmt/")
            os.makedirs("9_ROI/")
            os.makedirs("10_tract/")
            os.makedirs("11_nifti/")
            os.makedirs("12_overlays")
            os.makedirs("13_misc")
            os.makedirs("14_volume/")
    else:
        print("Error: Folder for the entered patient ID cannot be found.")
        exit(1)
        

    masking = input("Skip to brain masking? (y/n): ")

    if masking.lower() == 'y':
        print("Skipping processing steps, going straight to mask creation")
        skip_list.append(1)
        skip_list.append(0)
        skip_list.append(0)

    elif masking.lower() == 'n':

        gentrck = input("Skip to tract generation? (y/n): ")

        if gentrck.lower() == 'y':
            print("Skipping processing steps, going straight to tract generation")
            skip_list.append(0)
            skip_list.append(1)
            skip_list.append(0)

        elif gentrck.lower() == 'n':

            reg = input("Skip to registration? (y/n): ")

            if reg.lower() == 'y':
                skip_list.append(0)
                skip_list.append(0)
                skip_list.append(1)

            else:
                print('Processing all steps')
                skip_list.append(0)
                skip_list.append(0)
                skip_list.append(0)

    if debug_binary.lower() == 'y':
        print("Running in debug mode")
        debug(skip_list, bvalue_folders, pt_dir, pt_id, DWI_multishell)

    elif debug_binary.lower() == 'n':
        print("Running without debug steps")
        no_debug(skip_list, bvalue_folders, pt_dir, pt_id, DWI_multishell)


def cmd_line():
    # Define the description string
    description = "This file analyzes DTI data using mrtix software. If this script is in /Desktop, then the DTI data should be stored in the following manner: /Desktop/iMRI_DATA/pt_id/raw/DATA FOLDERS HERE"

    # Step 2: Create an instance of the ArgumentParser class
    parser = argparse.ArgumentParser(description=description)

    # Step 3: Define command-line arguments
    parser.add_argument('--debug', type=str, required=True, help='Run this script debug mode. Type the command and then --debug y for yes and --debug n for no.')

    # Step 4: Parse the command-line arguments
    args = parser.parse_args()

    # Call the appropriate function based on user input
    if args.debug == 'y':
        run_function(args.debug)  # You should define run_function somewhere in your code
    elif args.debug == 'n':
        run_function(args.debug)
    else:
        print("Invalid input for --debug. Use 'y' or 'n'.")


if __name__ == "__main__":
    cmd_line()

