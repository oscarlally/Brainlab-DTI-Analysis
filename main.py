#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 15/02/2023

@author: oscarlally
"""

import os

from Bash2PythonFuncs import BC, test_image, run, get_volumes
from mask import create_mask
from tensor_estimation import tensor_estimation
from gentck import gentck
from registration import registration


#Lists to access files
convert_files = []
test_file = []
concat_file = []
denoise_file = []
denoise_resid_file = []
dwi_PA_denoise = []


def debug(skip_list, bvalue_folders, pt_dir, pt_id, DWI_shell):

    """Initialise the method variable"""

    method = None

    """Information from the inputs of skip list tells which method to run"""

    if sum(skip_list) == 0:

        method = 4

    else:

        method = skip_list.index(1) + 1
    
    processed_dir = f"{pt_dir}Processed"
    
    nii_files = []
    
    template_file = []

    """This method is for when you want to start from the beginning"""

    if method == 4:
    
        """Use convert folder to convert and then concat - checking if the final file created in this junk already exists"""

        if not os.path.exists(f"{processed_dir}/1_convert/b_all.mif"):

            for i in bvalue_folders:

                if 't1' not in i and 'T1' not in i:

                    if 'PA' in i and 'flipped' not in i:

                        """Getting the reverse phase encoding file"""

                        output = f"{processed_dir}/1_convert/rev_b0_PA.mif"

                    else:

                        """The rest of the files that are not reversed phase encoding or t1"""

                        output = f"{processed_dir}/1_convert/{i.split('/')[-2]}.mif"

                    """First converted file path is appended"""

                    convert_files.append(output)

                    """Converting all of the files into .mif files"""

                    mrconvert_cmd = f"mrconvert {i} {output} -force"

                    mrinfo_cmd = f"mrinfo {output} -shell_bvalues"

                    run(mrconvert_cmd)

                    run(mrinfo_cmd)

                """Specific code for the t1 file as it needs to be converted to a .nii as well"""
                
                if 't1' in i or 'T1' in i:

                    files = os.listdir(i)

                    for j in files:

                        if 'dcm' in j:

                            t1_dcm = f"{i}{j}"

                            template_file.append(t1_dcm)

                            """Specify the conversion parameters and directory for the nii"""

                            t1_nii = f"{processed_dir}/11_nifti/t1.nii.gz"

                            t1_conv_cmd = f"mrconvert -strides -1,2,3 {t1_dcm} {t1_nii}"

                            """Conversion of t1 to mif here"""

                            output = f"{processed_dir}/1_convert/{i.split('/')[-2]}.mif"

                            mrconvert_cmd = f"mrconvert {i} {output} -force"

                            nii_files.append(t1_dcm)

                            run(t1_conv_cmd)

                            run(mrconvert_cmd)

        convert_dir = f"{processed_dir}/1_convert/"

        phase_files = os.listdir(convert_dir)

        for i in phase_files:

            if 'ap' in i.lower() or 'rev' in i.lower():

                ap_size_pre = get_volumes(f"{convert_dir}{i}")

            if 'pa' in i.lower():

                pa_size_pre = get_volumes(f"{convert_dir}{i}")
    
        print("DEBUG STEP: Check all images in b0 file look like the signal intensity of a b0 image")

        print(convert_files)

        b_size, test_bval = test_image(convert_files, test_file)

        print(f"The test image (b{test_bval}) has {b_size} volumes.")

        dwiextract_cmd = f"dwiextract {test_file[0]} {test_file[1]} -force"

        mrview_cmd = f"mrview -load {output} -interpolation 0"

        run(dwiextract_cmd)

        run(mrview_cmd)

        print("Concatenate data in 1_convert file")

        output = f"{os.path.split(output)[0]}/b_all.mif"

        concat_file.append(output)

        BC('mrcat', convert_files, output, '-force')

        """DENOISE steps"""

        if not os.path.isfile(f"{processed_dir}/2_denoise/dwi_denoise.mif"):

            print("Step 2: Denoising the data")

            # Call dwidenoise function with appropriate arguments

            output = f"{processed_dir}/2_denoise/dwi_denoise.mif"

            denoise_file.append(output)

            dwidenoise_cmd = f"dwidenoise {concat_file[0]} {output} -force"

            run(dwidenoise_cmd)

            # Call mrcalc function with appropriate arguments

            resid_output = f"{processed_dir}/2_denoise/dwi_denoise_residuals.mif"

            denoise_resid_file.append(resid_output)

            BC('mrcalc', concat_file[0], output, '-subtract', resid_output, '-force')

            output_PA = f"{processed_dir}/2_denoise/dwi_PA_denoise.mif"

            dwi_PA_denoise.append(output_PA)

            rev_file = []

            """Getting the file with reverse phase encoding for the denoising"""

            for i in convert_files:

                if 'rev' in i:

                    rev_file.append(i)

            dwidenoise_cmd = f"dwidenoise {rev_file[0]} {output_PA} -force"

            run(dwidenoise_cmd)

        print("DEBUG STEP: Check the denoised data and residuals in mrview")

        # Call mrview function with appropriate arguments

        mrview_cmd = f"mrview -load {concat_file[0]} -interpolation 0 -load {denoise_file[0]} -interpolation 0 -load {denoise_resid_file[0]} -interpolation 0 "

        run(mrview_cmd)
            
        """DEGIBBS step"""

        degibbs_input_1 = f"{processed_dir}/2_denoise/dwi_denoise.mif"
        degibbs_input_2 = f"{processed_dir}/2_denoise/dwi_PA_denoise.mif"
        degibbs_output_1 = f"{processed_dir}/3_degibbs/dwi_degibbs.mif"
        degibbs_output_2 = f"{processed_dir}/3_degibbs/b0_PA_degibbs.mif"
        dwi_extract_output_1 = f"{processed_dir}/3_degibbs/b0_AP_degibbs.mif"

        if not os.path.isfile(degibbs_output_1):

            print("Step 3: Remove GIBBS ringing artfact")

            # Call mrdegibbs function with appropriate arguments

            degibbs_cmd_1 = f"mrdegibbs {degibbs_input_1} {degibbs_output_1} -force"

            run(degibbs_cmd_1)

            # Call mrdegibbs function again with different arguments

            degibbs_cmd_2 = f"mrdegibbs {degibbs_input_2} {degibbs_output_2} -force"

            run(degibbs_cmd_2)

        print("DEBUG STEP: Check the the degibbs results in mrview")

        # Call mrview function with appropriate arguments

        BC('mrview', '-load', degibbs_input_1, '-interpolation 0 -load', degibbs_output_1, '-interpolation 0')

        os.chdir(f"{pt_dir}Processed")

        dwiextract_eddy_cmd = f"dwiextract -bzero {degibbs_output_1} {dwi_extract_output_1} -force"

        run(dwiextract_eddy_cmd)
        
        print()

        pa_size = get_volumes(degibbs_input_2)

        ap_size = get_volumes(degibbs_output_2)

        if ap_size == pa_size == pa_size_pre == ap_size_pre:

            print(f"There are {pa_size} volumes in the PA image and there are {ap_size} volumes in the AP image.")

        else:

            print(f"Originally there were {pa_size_pre} volumes in the PA image and {ap_size_pre} volumes in the AP image.")

            print(f"Now there are {pa_size} volumes in the PA image and there are {ap_size} volumes in the AP image.")

        print()

        mrview_cmd_1 = f"mrview -load {degibbs_input_2} -interpolation 0"

        mrview_cmd_2 = f"mrview -load {degibbs_output_2} -interpolation 0"

        run(mrview_cmd_1)

        run(mrview_cmd_2)

        """EDDY CURRENTS"""
    
        N = min(pa_size, ap_size)

        convert_output = f"{processed_dir}/3_degibbs/b0_AP_degibbs_N.mif"

        cat_output = f"{processed_dir}/3_degibbs/b0_degibbs_AP_PA.mif "

        mrconvert_cmd = f"mrconvert {dwi_extract_output_1} -coord 3 1:{N} {convert_output} -quiet -force"

        mrcat_cmd = f"mrcat {convert_output} {degibbs_output_2} {cat_output} -force"

        run(mrconvert_cmd)

        run(mrcat_cmd)

        print("DEBUG STEP: Check the resulting data has $N_B0_PA images with phase encoding AP followed by $N_B0_PA images phase encoded PA")

        mrview_cmd = f"mrview -load {cat_output} -interpolation 0 -force"

        run(mrview_cmd)
        
        print("Phase encoding direction not in header info, code automatically uses ap")
        
        dwi_eddy_file = f"{processed_dir}/4_eddy/dwi_eddy.mif"

        if not os.path.exists(dwi_eddy_file):

            dwifslpreproc_cmd = f"dwifslpreproc {degibbs_output_1} {dwi_eddy_file} -rpe_pair -se_epi {cat_output} -pe_dir ap -force"

            run(dwifslpreproc_cmd)
            
            # Upsample the DWI data with mrgrid

            upsample_out = f"{processed_dir}/4_eddy/dwi_eddy_upsamp.mif"

            mrgrid_cmd = f"mrgrid {dwi_eddy_file} regrid -voxel 1.3 {upsample_out} -force"

            run(mrgrid_cmd)

        print("DEBUG STEP: Check the eddy results")

        mrview_cmd = f"mrview {degibbs_output_1} -interpolation 0 -load {dwi_eddy_file} -interpolation 0 -force"

        run(mrview_cmd)
            
        """RESPONSE steps"""

        response_wm = f"{processed_dir}/5_response/response_wm.txt"

        response_gm = f"{processed_dir}/5_response/response_gm.txt"

        response_csf = f"{processed_dir}/5_response/response_csf.txt"

        response_voxels = f"{processed_dir}/5_response/response_voxels.mif"

        if not os.path.exists(response_wm):

            print("Step 5: Response function")

            # Estimate the response functions for WM, GM and CSF

            dwi2response_cmd = f"dwi2response dhollander {dwi_eddy_file} {response_wm} {response_gm} {response_csf} -voxels {response_voxels} -force"

            run(dwi2response_cmd)


        print("DEBUG STEP: Check the response functions and the voxel positions")

        print(" The WM should go from sphere to flat. The GM and CSF should go from sphere to smaller sphere")

        shview_wm_cmd = f"shview {response_wm}"

        shview_gm_cmd = f"shview {response_gm}"

        shview_csf_cmd = f"shview {response_csf}"

        run(shview_wm_cmd)

        run(shview_gm_cmd)

        run(shview_csf_cmd)

        print("Check the voxels are assigned to the correct tissue types. RED = CSF, GREEN = GM, BLUE = WM")

        mrview_cmd = f"mrview -load {dwi_eddy_file} -interpolation 0 -overlay.load {response_voxels} -overlay.interpolation 0"

        run(mrview_cmd)

        print()
        
        create_mask(pt_id, pt_dir, nii_files, 'debug')

        tensor_estimation(pt_dir, DWI_shell, 'debug')

        tract_name = gentck(pt_dir, 'debug')

        registration(pt_dir, template_file, tract_name, 'debug')
        
    else:

        if len(template_file) == 0:

            for i in bvalue_folders:

                if 't1' in i or 'T1' in i:

                    files = os.listdir(i)

                    for j in files:

                        if '.dcm' in j:

                            template_file.append(f"{i}{j}")

        if len(nii_files) == 0:

            nii_dir = f"{pt_dir}Processed/11_nifti/"

            files = os.listdir(nii_dir)

            for j in files:

                if 't1' in j.lower():

                    nii_files.append(f"{nii_dir}{j}")
                    
        if method == 1:

            create_mask(pt_id, pt_dir, nii_files, 'debug')

            tensor_estimation(pt_dir, DWI_shell, 'debug')

            tract_name = gentck(pt_dir, 'debug')

            registration(pt_dir, template_file, tract_name, 'debug')
            
        elif method == 2:

            tract_name = gentck(pt_dir, 'debug')

            registration(pt_dir, template_file, tract_name, 'debug')

        elif method == 3:

            tract_name = input('Please type in the tract name for labelling purposes:  ')

            registration(pt_dir, template_file, tract_name, 'debug')



def no_debug(skip_list, bvalue_folders, pt_dir, pt_id, DWI_shell):

    method = None

    if sum(skip_list) == 0:

        method = 4

    else:
        method = skip_list.index(1) + 1
        
    processed_dir = f"{pt_dir}Processed"
    
    nii_files = []
    
    template_file = []

    if method == 4:
    
        # Use convert folder to convert and then concat
        if not os.path.exists(f"{processed_dir}/1_convert/b_all.mif"):
            for i in bvalue_folders:
                
                if 't1' not in i and 'T1' not in i:
                    if 'PA' in i and 'flipped' not in i:
                        output = f"{processed_dir}/1_convert/rev_b0_PA.mif"
                    else:
                        output = f"{processed_dir}/1_convert/{i.split('/')[-2]}.mif"
                    convert_files.append(output)
                    mrconvert_cmd = f"mrconvert {i} {output} -force"

                    run(mrconvert_cmd)
                    mrinfo_cmd = f"mrinfo {output} -shell_bvalues"
                    run(mrinfo_cmd)
                
                if 't1' in i or 'T1' in i:
                    files = os.listdir(i)
                    for j in files:
                        if 'dcm' in j:
                            t1_dcm = f"{i}{j}"
                            t1_nii = f"{processed_dir}/11_nifti/t1.nii.gz"
                            t1_conv_cmd = f"mrconvert -strides -1,2,3 {t1_dcm} {t1_nii}"
                            output = f"{processed_dir}/1_convert/{i.split('/')[-2]}.mif"
                            mrconvert_cmd = f"mrconvert {i} {output} -force"
                            nii_files.append(t1_dcm)
                            run(t1_conv_cmd)
                            run(mrconvert_cmd)
                            

    
                            
        convert_dir = f"{processed_dir}/1_convert/"
        phase_files = os.listdir(convert_dir)
        for i in phase_files:
            if 'ap' in i.lower() or 'rev' in i.lower():
                ap_size_pre = get_volumes(f"{convert_dir}{i}")
            if 'pa' in i.lower():
                pa_size_pre = get_volumes(f"{convert_dir}{i}")
                

        print("Concatenating data into a single_convert file")
        output = f"{os.path.split(output)[0]}/b_all.mif"
        concat_file.append(output)
        BC('mrcat', convert_files, output, '-force')


        """DENOISE"""

        if not os.path.isfile(f"{processed_dir}/2_denoise/dwi_denoise.mif"):
            print("Step 2: Denoising the data")
            # Call dwidenoise function with appropriate arguments
            output = f"{processed_dir}/2_denoise/dwi_denoise.mif"
            denoise_file.append(output)
            dwidenoise_cmd = f"dwidenoise {concat_file[0]} {output} -force"
            run(dwidenoise_cmd)
            # Call mrcalc function with appropriate arguments
            resid_output = f"{processed_dir}/2_denoise/dwi_denoise_residuals.mif"
            denoise_resid_file.append(resid_output)
            BC('mrcalc', concat_file[0], output, '-subtract', resid_output, '-force')
            output_PA = f"{processed_dir}/2_denoise/dwi_PA_denoise.mif"
            dwi_PA_denoise.append(output_PA)
            rev_file = []
            for i in convert_files:
                if 'rev' in i:
                    rev_file.append(i)
            dwidenoise_cmd = f"dwidenoise {rev_file[0]} {output_PA} -force"
            run(dwidenoise_cmd)

            
        """DEGIBBS"""

        degibbs_input_1 = f"{processed_dir}/2_denoise/dwi_denoise.mif"
        degibbs_input_2 = f"{processed_dir}/2_denoise/dwi_PA_denoise.mif"
        degibbs_output_1 = f"{processed_dir}/3_degibbs/dwi_degibbs.mif"
        degibbs_output_2 = f"{processed_dir}/3_degibbs/b0_PA_degibbs.mif"
        dwi_extract_output_1 = f"{processed_dir}/3_degibbs/b0_AP_degibbs.mif"

        if not os.path.isfile(degibbs_output_1):
            print("Step 3: Remove GIBBS ringing artfact")
            # Call mrdegibbs function with appropriate arguments
            degibbs_cmd_1 = f"mrdegibbs {degibbs_input_1} {degibbs_output_1} -force"
            run(degibbs_cmd_1)
            # Call mrdegibbs function again with different arguments
            degibbs_cmd_2 = f"mrdegibbs {degibbs_input_2} {degibbs_output_2} -force"
            run(degibbs_cmd_2)


        os.chdir(f"{pt_dir}Processed")
        dwiextract_eddy_cmd = f"dwiextract -bzero {degibbs_output_1} {dwi_extract_output_1} -force"
        run(dwiextract_eddy_cmd)
        
        print()
        pa_size = get_volumes(degibbs_input_2)
        ap_size = get_volumes(degibbs_output_2)
        if ap_size == pa_size == pa_size_pre == ap_size_pre:
            print(f"There are {pa_size} volumes in the PA image and there are {ap_size} volumes in the AP image.")
        else:
            print(f"Originally there were {pa_size_pre} volumes in the PA image and {ap_size_pre} volumes in the AP image.")
            print(f"Now there are {pa_size} volumes in the PA image and there are {ap_size} volumes in the AP image.")
        print()

        
        
        """EDDY CURRENTS"""
    
        N = min(pa_size, ap_size)
        convert_output = f"{processed_dir}/3_degibbs/b0_AP_degibbs_N.mif"
        cat_output = f"{processed_dir}/3_degibbs/b0_degibbs_AP_PA.mif "
        mrconvert_cmd = f"mrconvert {dwi_extract_output_1} -coord 3 1:{N} {convert_output} -quiet -force"
        mrcat_cmd = f"mrcat {convert_output} {degibbs_output_2} {cat_output} -force"
        run(mrconvert_cmd)
        run(mrcat_cmd)
        
        

        print("Phase encoding direction not in header info, code automatically uses ap")
        
        dwi_eddy_file = f"{processed_dir}/4_eddy/dwi_eddy.mif"
        if not os.path.exists(dwi_eddy_file):
            dwifslpreproc_cmd = f"dwifslpreproc {degibbs_output_1} {dwi_eddy_file} -rpe_pair -se_epi {cat_output} -pe_dir ap -force"
            run(dwifslpreproc_cmd)
            
            # Upsample the DWI data with mrgrid
            upsample_out = f"{processed_dir}/4_eddy/dwi_eddy_upsamp.mif"
            mrgrid_cmd = f"mrgrid {dwi_eddy_file} regrid -voxel 1.3 {upsample_out} -force"
            run(mrgrid_cmd)
        
            
        """RESPONSE"""

        response_wm = f"{processed_dir}/5_response/response_wm.txt"
        response_gm = f"{processed_dir}/5_response/response_gm.txt"
        response_csf = f"{processed_dir}/5_response/response_csf.txt"
        response_voxels = f"{processed_dir}/5_response/response_voxels.mif"
        if not os.path.exists(response_wm):
            print("Step 5: Response function")
            # Estimate the response functions for WM, GM and CSF
            dwi2response_cmd = f"dwi2response dhollander {dwi_eddy_file} {response_wm} {response_gm} {response_csf} -voxels {response_voxels} -force"
            run(dwi2response_cmd)

        print()
        
        create_mask(pt_id, pt_dir, nii_files, 'no_debug')
        tensor_estimation(pt_dir, DWI_shell, 'no_debug')
        tract_name = gentck(pt_dir, 'no_debug')
        registration(pt_dir, template_file, tract_name, 'no_debug')
        
    else:
    
        if len(template_file) == 0:
            for i in bvalue_folders:
                if 't1' in i or 'T1' in i:
                    files = os.listdir(i)
                    for j in files:
                        if '.dcm' in j:
                            template_file.append(f"{i}{j}")
    
        if len(nii_files) == 0:
            nii_dir = f"{pt_dir}Processed/11_nifti/"
            files = os.listdir(nii_dir)
            for j in files:
                if 't1' in j.lower():
                    nii_files.append(f"{nii_dir}{j}")

            
        if method == 1:
            create_mask(pt_id, pt_dir, nii_files, 'no_debug')
            tensor_estimation(pt_dir, DWI_shell, 'no_debug')
            tract_name = gentck(pt_dir, 'no_debug')
            registration(pt_dir, template_file, tract_name, 'no_debug')
            
        elif method == 2:
            tract_name = gentck(pt_dir, 'no_debug')
            registration(pt_dir, template_file, tract_name, 'no_debug')

        elif method == 3:
            tract_name = input('Please type in the tract name for labelling purposes:  ')
            registration(pt_dir, template_file, tract_name, 'debug')

