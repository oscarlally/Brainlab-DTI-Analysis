import os
import sys
import shutil
import pydicom
import numpy as np
import nibabel as nib
from final_dcm import create_brainlab_object
from functions import check_and_handle_directories, \
                      get_full_file_names, \
                      delete_files_in_folder, \
                      run, \
                      get_volumes, \
                      create_mask, \
                      find_dir, \
                      tensor_estimation, \
                      convert_tracts, \
                      copy_directory
from tract_roi_match import roi_table
from generate_tracts_original import gentck
from register import registration
from intro import intro
from functions import norm_nii, \
                      skew, \
                      mirror_nifti

# Define data directories
home_dir = os.path.expanduser("~")
pid = input('Please type in the patient number:  ')
diff_data_dir = find_dir(pid, home_dir)


# Add the desired path to sys.path
additional_path = "~/mrtrix3/bin/mrconvert"
if additional_path not in sys.path:
    sys.path.append(additional_path)


def main():
    intro()
    step = int(input('Please type in the step you would like to start on:  '))
    cont = 'y'

    # Centralized dictionary for all file paths
    file_paths = {
        "output_dirs": [
            "mrtrix3_files/converted",
            "mrtrix3_files/concatenated",
            "mrtrix3_files/denoised",
            "mrtrix3_files/calc",
            "mrtrix3_files/degibbs",
            "mrtrix3_files/eddy",
            "mrtrix3_files/response",
            "mrtrix3_files/masking",
            "mrtrix3_files/tensors",
            "mrtrix3_files/fods",
            "mrtrix3_files/misc",
            "mrtrix3_files/rois",
            "mrtrix3_files/tracts",
            "mrtrix3_files/t1",
            "mrtrix3_files/overlays",
            "mrtrix3_files/volumes",
            "mrtrix3_files/template",
            "mrtrix3_files/nifti"
        ],
        "converted": [],
        "b0": None,
        "b0_rev": None,
        "concat_file": f"{os.getcwd()}/mrtrix3_files/concatenated/combined_dwi.mif",
        "denoise_file": f"{os.getcwd()}/mrtrix3_files/denoised/denoised_dwi.mif",
        "denoise_ap": f"{os.getcwd()}/mrtrix3_files/denoised/denoised_ap.mif",
        "denoise_pa": f"{os.getcwd()}/mrtrix3_files/denoised/denoised_pa.mif",
        "resid_output": f"{os.getcwd()}/mrtrix3_files/calc/dwi_denoise_residuals.mif",
        "degibbs_file": f"{os.getcwd()}/mrtrix3_files/degibbs/dwi_degibbs.mif",
        "template_file": f"{os.getcwd()}/mrtrix3_files/template/template.dcm",
        "t1_nii": f"{os.getcwd()}/mrtrix3_files/nifti/t1.nii",
        "t1_mif": f"{os.getcwd()}/mrtrix3_files/converted/t1.mif",
        "degibbs_ap_file": f"{os.getcwd()}/mrtrix3_files/degibbs/dwi_degibbs_ap.mif",
        "degibbs_pa_file": f"{os.getcwd()}/mrtrix3_files/degibbs/dwi_degibbs_pa.mif",
        "degibbs_pair_file": f"{os.getcwd()}/mrtrix3_files/degibbs/degibbs_pair.mif",
        "degibbs_ap_n": f"{os.getcwd()}/mrtrix3_files/degibbs/b0_AP_degibbs_N.mif",
        "degibbs_ap_pa_n": f"{os.getcwd()}/mrtrix3_files/degibbs/b0_AP_PA_degibbs_N.mif",
        "eddy_file": f"{os.getcwd()}/mrtrix3_files/eddy/dwi_preprocessed_eddy.mif",
        "upsample_out": f"{os.getcwd()}/mrtrix3_files/eddy/dwi_eddy_upsamp.mif",
        "response_wm": f"{os.getcwd()}/mrtrix3_files/response/response_wm.txt",
        "response_gm": f"{os.getcwd()}/mrtrix3_files/response/response_gm.txt",
        "response_csf": f"{os.getcwd()}/mrtrix3_files/response/response_csf.txt",
        "response_voxels": f"{os.getcwd()}/mrtrix3_files/response/response_voxels.mif",
        "fa": f"{os.getcwd()}/mrtrix3_files/tensors/fa.mif",
        "ev": f"{os.getcwd()}/mrtrix3_files/tensors/ev.mif",
        "dwi_tensor": f"{os.getcwd()}/mrtrix3_files/tensors/dwi_tensor.mif",
        "nii_file": f"{os.getcwd()}/mrtrix3_files/masking/extracted_b0.nii",
        "registered": []
    }

    # Ensure output directories exist
    # check_and_handle_directories(file_paths["output_dirs"])

    b0s_check = get_full_file_names(f"{os.getcwd()}/mrtrix3_files/converted")
    if len(b0s_check) != 0:
        for i in b0s_check:
            if 'b0' in i and 'flipped' in i:
                file_paths["b0_rev"] = i
            if 'b0' in i and 'flipped' not in i:
                file_paths["b0"] = i


    if step == 1 and cont.lower() == 'y':
        # Convert diffusion files to .mif and categorize by type
        for i in get_full_file_names(diff_data_dir):
            if 'ep2d' in i.lower() and 'fa' not in i.lower():
                convert = f"{os.getcwd()}/mrtrix3_files/converted/{os.path.basename(i)}.mif"
                result_cmd = f"mrconvert {i} {convert}"
                run(result_cmd)
                file_paths["converted"].append(convert)
                if 'b0' in i.lower():
                    if 'flipped' in i.lower():
                        file_paths["b0_rev"] = convert
                    else:
                        file_paths["b0"] = convert
        step += 1
        cont = 'y'

    if step == 2 and cont.lower() == 'y':
        # Convert T1 file
        for i in get_full_file_names(diff_data_dir):
            if 't1' in i.lower() and 'dis3d' in i.lower():
                t1_file = get_full_file_names(i)[0]
                shutil.copy(t1_file, file_paths['template_file'])
                run(f"mrconvert {t1_file} {file_paths['t1_mif']}")
                run(f"mrconvert -strides -1,2,3 {t1_file} {file_paths['t1_nii']} -force")
        step += 1
        cont = 'y'

    if step == 3 and cont.lower() == 'y':
        # Concatenate diffusion files excluding `b0` or flipped files
        cat_cmd = "mrcat "
        cat_count = 0
        one_case = None
        for i in file_paths["converted"]:
            if 'b0' not in i.lower() and 'flipped' not in i.lower():
                cat_count += 1
                cat_cmd += f"{i} "
                one_case = f"{i}"
        if cat_count > 1:
            cat_cmd += f"{file_paths['concat_file']}"
            run(cat_cmd)
        else:
            shutil.copy2(one_case, file_paths['concat_file'])
        extract_cmd = f"dwiextract {file_paths['concat_file']} {file_paths['b0']} -bzero -force"
        run(extract_cmd)
        step += 1
        cont = 'y'

    if step == 4 and cont.lower() == 'y':

        run(f"mrinfo {file_paths['b0']}")
        run(f"mrinfo {file_paths['b0_rev']}")

        # Denoise files
        run(f"dwidenoise {file_paths['concat_file']} {file_paths['denoise_file']}")
        run(f"dwidenoise {file_paths['b0']} {file_paths['denoise_ap']}")
        run(f"dwidenoise {file_paths['b0_rev']} {file_paths['denoise_pa']}")

        # Calculate residuals
        calc_cmd = f"mrcalc {file_paths['concat_file']} {file_paths['denoise_file']} -subtract {file_paths['resid_output']}"
        run(calc_cmd)
        step += 1
        cont = 'y'

    if step == 5 and cont.lower() == 'y':
        # Degibbs processing
        run(f"mrdegibbs {file_paths['denoise_pa']} {file_paths['degibbs_pa_file']}")
        run(f"mrdegibbs {file_paths['denoise_file']} {file_paths['degibbs_file']}")
        run(f"dwiextract -bzero {file_paths['degibbs_file']} {file_paths['degibbs_ap_file']}")

        pa_size = get_volumes(file_paths['degibbs_file'])
        ap_size = get_volumes(file_paths['degibbs_ap_file'])
        pa_size_pre = get_volumes(file_paths["b0_rev"])
        ap_size_pre = get_volumes(file_paths["b0"])

        if ap_size == pa_size == pa_size_pre == ap_size_pre:

            print(f"There are {pa_size} volumes in the PA image and there are {ap_size} volumes in the AP image.")

        # Concatenate degibbs files
        run(f"mrcat {file_paths['degibbs_ap_file']} {file_paths['degibbs_pa_file']} {file_paths['degibbs_pair_file']} -force")

        # Extract the last 2 * N_B0_PA images
        N_B0_PA = 4
        run(f"mrconvert {file_paths['degibbs_ap_file']} -coord 3 1:{N_B0_PA} {file_paths['degibbs_ap_n']} -quiet -force")
        run(f"mrcat {file_paths['degibbs_ap_n']} {file_paths['degibbs_pa_file']} {file_paths['degibbs_ap_pa_n']} -force")

        print()
        print('--------------------------')
        print('Please assess the processed files before running the eddy current correction.')
        run(f"mrview -load {file_paths['degibbs_ap_pa_n']} -interpolation 0")

        step += 1
        cont = input('Continue? (y/n): ')

    if step == 6 and cont.lower() == 'y':
        # Eddy current corrections
        preproc_cmd = f"dwifslpreproc {file_paths['degibbs_file']} {file_paths['eddy_file']} -rpe_pair -se_epi {file_paths['degibbs_ap_pa_n']} -pe_dir ap -force"
        run(preproc_cmd)

        mrgrid_cmd = f"mrgrid {file_paths['eddy_file']} regrid -voxel 1.3 {file_paths['upsample_out']} -force"
        run(mrgrid_cmd)

        step += 1
        cont = input('Continue? (y/n): ')

    if step == 7 and cont.lower() == 'y':
        # Get response functions
        if not os.path.exists(file_paths['response_wm']):
            print("Step 7: Response function")
            # Estimate the response functions for WM, GM, and CSF
            dwi2response_cmd = (
                f"dwi2response dhollander {file_paths['upsample_out']} {file_paths['response_wm']} "
                f"{file_paths['response_gm']} {file_paths['response_csf']} -voxels {file_paths['response_voxels']} -force"
            )
            run(dwi2response_cmd)

        run(f"shview {file_paths['response_wm']}")
        run(f"shview {file_paths['response_gm']}")
        run(f"shview {file_paths['response_csf']}")

        print("Check the voxels are assigned to the correct tissue types. RED = CSF, GREEN = GM, BLUE = WM")
        run(
            f"mrview -load {file_paths['upsample_out']} -interpolation 0 "
            f"-overlay.load {file_paths['response_voxels']} -overlay.interpolation 0"
        )

        step += 1
        cont = input('Continue? (y/n): ')

    if step == 8 and cont.lower() == 'y':
        # Masking
        nii_files = []
        create_mask(nii_files, 'debug')
        file_paths['nii_file'] = '/Users/oscarlally/Documents/GitHub/Brainlab-DTI-Analysis/mrtrix3_files/masking/extracted_b0.nii'

        step += 1
        cont = input('Continue? (y/n): ')

    if step == 9 and cont.lower() == 'y':
        # Tensors
        dwi_shell = input('Is the data multi-shelled? (y/n): ')
        tensor_estimation(dwi_shell, 'debug')
        step += 1
        cont = input('Continue? (y/n): ')

    if step == 10 and cont.lower() == 'y':
        # Create ROIs
        print()
        print('-------------------------')
        print('The following tracts are created using the below ROIs.  Make sure to save the ROIs in this format for the code to be able to recognise them.')
        print()
        roi_table()
        print()
        print()
        print('-------------------------')

        while True:
            print('Please save any ROIs in the roi folder in the sub directory /mrtrix3/rois that is in the directory of this code.')
            print('This should be obvious as one of the sub directories will appear at the top of the ROI editor.')
            print()
            choice = input('Do you need to create any ROIs? (y/n). ')
            print()
            print('Please save the ROI under the following names for the script to be able to find them'.upper())

            if choice.lower() == 'y':
                run('echo -e "Opening mrview"')
                message = "Step 8: Draw ROIs"
                message = "\033[32m" + message + "\033[0m"
                command = "echo {}".format(message)
                run(command)

                # step size should be 0.5xvoxelsize (currently set to 1)
                fa = file_paths['fa']
                ev = file_paths['ev']
                dwi_tensor = file_paths['dwi_tensor']

                view_cmd = f"mrview -mode 2 -load {fa} -interpolation 0 -load {ev} -interpolation 0 -comments 0"
                run(view_cmd)

                break
            elif choice.lower() == 'n':
                print('Continue with analysis using ROIs already generated')
                break
            else:
                message = "Invalid response"
                message = "\033[31m" + message + "\033[0m"
                command = "echo {}".format(message)
                run(command)

        step += 1
        cont = input('Continue? (y/n): ')

        if step == 11 and cont.lower() == 'y':
            print()
            print('This step is currently a work in progress. It is recommended to use the custom option, \n'
                  'and example commands can be found in this code folder, in the file called custom_tracts.txt')
            print()
            tract_names = []
            finished = False
            defaults = None
            choice = None
            while finished is False:
                tract_name, defaults, choice = gentck(defaults, choice)
                tract_names.append(tract_name)
                check = input('Are you happy with the tract (y/n):  ')
                if check == 'y':
                    check_two = input('Would you like to create another tract (y/n)?:  ')
                    if check_two == 'n':
                        finished = True
                else:
                    print()
                    if len(defaults) == 3:
                        print(
                            f"Current step is {defaults[0]}, current angle is {defaults[1]} and current cutoff is {defaults[2]}.")
                    if len(defaults) == 4:
                        print(
                            f"Current step is {defaults[0]}, current angle is {defaults[1]}, current cutoff is {defaults[2]} and current tckedit number is {defaults[3]}.")
                    param_1 = input('Type in the step:  ')
                    param_2 = input('Type in the angle:  ')
                    param_3 = input('Type in the cutoff:  ')
                    param_4 = input('Type in the tckedit number if applicable, if not type in 0:  ')
                    defaults = [param_1, param_2, param_3, param_4]


        convert_tracts(file_paths['t1_mif'], 'debug')
        step += 1
        cont = input('Continue? (y/n): ')

    if step == 12 and cont.lower() == 'y':
        convert_tracts(file_paths['t1_mif'], 'debug')
        _, is_cont, registered = registration('debug')
        file_paths["registered"].append(registered)
        cont = is_cont
        step += 1

    if step == 13 and cont.lower() == 'y':
        print()
        print("Creating objects step")
        print()
        template_file = file_paths['template_file']
        t1_nii = file_paths['t1_nii']

        current_dir = os.getcwd()
        nii_dir = f"{current_dir}/mrtrix3_files/nifti/"
        overlay_dir = f"{current_dir}/mrtrix3_files/overlays/"
        final_dir = f"{current_dir}/mrtrix3_files/volumes/"

        relevant_dcm = pydicom.dcmread(template_file)
        data_dicom = relevant_dcm.pixel_array
        pixel_values_dicom = data_dicom.flatten()
        max_value = max(pixel_values_dicom)
        nii_dir = f"{current_dir}/mrtrix3_files/nifti/"

        used_indices = set()

        while True:
            paths_to_convert = [p for p in os.listdir(nii_dir) if p.endswith('.nii.gz')]
            available_indices = [i for i in range(len(paths_to_convert)) if i not in used_indices]

            if not available_indices:
                print("No more tracts left to convert.")
                break

            print('Available tracts to convert to DICOMs:')
            for idx in available_indices:
                print(f"{idx + 1}. {paths_to_convert[idx]}")
            print()

            # Select tract
            select = input("Please type in the number of the tract you would like to convert:  ").strip()
            if not select.isdigit() or (int(select) - 1) not in available_indices:
                print("Invalid selection. Try again.\n")
                continue

            idx = int(select) - 1
            used_indices.add(idx)

            thresh_reg_tract = os.path.join(nii_dir, paths_to_convert[idx])
            file_paths["registered"].append(thresh_reg_tract)

            tract_name_pre = thresh_reg_tract.split('_NORM_registered')[0]
            tract_name = os.path.basename(tract_name_pre)

            # Define overlay output files
            binarised_object = os.path.join(overlay_dir, f"{tract_name}_binarised_object.nii.gz")
            t1_object = os.path.join(overlay_dir, f"{tract_name}_t1_object.nii.gz")
            t1_hole = os.path.join(overlay_dir, f"{tract_name}_t1_hole.nii.gz")
            binarised_skew = os.path.join(overlay_dir, f"{tract_name}_binary_skew.nii.gz")
            t1_dicom_range = os.path.join(overlay_dir, f"{tract_name}_t1_dicom_range.nii.gz")
            object_dicom_range = os.path.join(overlay_dir, f"{tract_name}_object_dicom_range.nii.gz")
            t1_burned = os.path.join(overlay_dir, f"{tract_name}_t1_burned.nii.gz")
            t1_burned_final = os.path.join(overlay_dir, f"{tract_name}_t1_burned_final.nii.gz")

            # Process image
            norm_nii(thresh_reg_tract, binarised_object, 0, 1)
            modified_file = skew(binarised_object, 10)
            nib.save(modified_file, binarised_skew)

            run(f"fslmaths {t1_nii} -mul {binarised_object} {t1_object}")
            run(f"fslmaths {t1_nii} -sub {t1_object} {t1_hole}")

            nii_data = nib.load(t1_hole).get_fdata()
            max_hole = np.max(nii_data)
            norm_num = 60 / max_hole

            run(f"fslmaths {t1_hole} -mul {norm_num} {t1_dicom_range}")
            run(f"fslmaths {binarised_skew} -mul {max_value - 60} {object_dicom_range}")
            run(f"fslmaths {t1_dicom_range} -add {object_dicom_range} {t1_burned}")

            mirror_nifti(t1_burned, t1_burned_final)

            # Inner loop for tuning DICOM
            object_path = os.path.join(final_dir, f"Brainlab_Object_{tract_name}.dcm")

            while True:
                print("\nDicom creation. Open the resultant dicom in Volumes and adjust if necessary.\n")
                wind_factor = input('Type in the window factor (default = 0.5): ').strip() or "0.5"
                max_factor = input('Type in the max factor (default = 0.66): ').strip() or "0.66"

                create_brainlab_object(tract_name, t1_burned_final, template_file, object_path, float(max_factor),
                                       float(wind_factor))

                check = input('Is the dicom file flipped? (y/n): ').strip().lower()
                if check == 'y':
                    create_brainlab_object(tract_name, t1_burned, template_file, object_path, float(max_factor),
                                           float(wind_factor))

                happy = input('Is the dicom contrast sufficient? (y/n): ').strip().lower()
                if happy == 'y':
                    copy_directory(f"{os.getcwd()}/mrtrix3_files", f"{diff_data_dir}/Processed")
                    break  # Done with DICOM tuning

            # Ask if user wants to process another
            print()
            happy_overall = input('Do you want to create another object? (y/n): ').strip().lower()
            print()
            if happy_overall == 'n':
                print("Finished.")
                break

main()
            # elif len(file_paths["registered"]) == 1:
            #     thresh_reg_tract = file_paths["registered"][0]
            #     tract_name_pre = thresh_reg_tract.split('_NORM_registered')[0]
            #     tract_name = tract_name_pre.split('/')[-1]
            # else:
            #     print()
            #     print('------')
            #     print()
            #     print('Available tracts to convert to dicoms are:')
            #     for idx, i in enumerate(file_paths["registered"]):
            #         print(f"{idx+1}. {i}")
            #     print()
            #     select = input("Please type in the number of the tract you would like to convert:  ")
            #     thresh_reg_tract = file_paths["registered"][int(select)-1]
            #     tract_name_pre = thresh_reg_tract.split('_NORM_registered')[0]
            #     tract_name = tract_name_pre.split('/')[-1]




