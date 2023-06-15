#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 15/02/2023
@author: oscarlally
"""


import os
import subprocess
import signal
import numpy as np
import itertools
import shutil
from shutil import rmtree
import re



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
        
        
def find_karawun(pid, base_dir):
    x = 0
    for root, subdirs, files in os.walk(base_dir):
        for d in subdirs:
            if d == pid:
                x += 1
                return os.path.join(root, d)
    if x == 0:
        print('Please retype in package')
        new_pid = input()
        find_dir(new_pid, base_dir)


class TimeoutException(Exception):
    pass
    
    
def rem_dir(pt_dir):
    isExist = os.path.exists(f"{pt_dir}Processed/1_convert/")
    if isExist == True:
        remove = input('There is already data here.  Would you like to remove it? (y/n): ')
        if remove.lower() == 'y':
            rmtree(f"{pt_dir}Processed/")
            os.makedirs(f"{pt_dir}Processed/")
        else:
            pass
    else:
        os.makedirs(f"{pt_dir}Processed/", exist_ok=True)
        return 1
    os.chdir(f"{pt_dir}Processed/")
    
    

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
        print("The application is not in your user directory or your local directory. Please move it to either of these directories")



def fsl_path_finder(dir_1, dir_2):
    a = find_app('miniconda3', dir_1, dir_2)
    b = f"{a}/lib"
    c = find_dir('site_packages', b)
    return f"{c}/fsl"
    
    
    

def get_bvalue_folders():
    bvalue_folders = [f.path for f in os.scandir(os.getcwd()) if f.is_dir()]
    for idx, i in enumerate(bvalue_folders):
        bvalue_folders[idx] = f"{i}/"
    for idx, i in enumerate(bvalue_folders):
        if 'Processed' in i:
            del bvalue_folders[idx]
    return bvalue_folders

    
    
def run(cmd):
    current_dir = os.getcwd()
    home_dir = os.path.expanduser("~")
    functions_path = find_app('mrtrix3', '/usr/local/', home_dir)
    functions_path = f"{functions_path}/bin"
    os.chdir(functions_path)
    process = subprocess.run(cmd.split())
    os.chdir(current_dir)
    
   
   
def run_fsl(cmd, pt_dir):
    home_dir = os.path.expanduser("~")
    functions_path = find_app('fsl', '/usr/local/', home_dir)
    functions_path = f"{functions_path}/bin"
    os.chdir(functions_path)
    if 'extracted_b0' in cmd:
        output_file = 'extracted_b0.txt'
    else:
        output_file = 'object.txt'
    output_dir = f"{pt_dir}Processed/13_misc/"
    current_dir = os.getcwd()
    with open(f"{output_dir}{output_file}", 'w') as f:
        process = subprocess.run(cmd.split(), stdout=f, stderr=subprocess.STDOUT)
    with open(f"{output_dir}{output_file}", 'r') as f:
        output = f.read()
    

def BC(*arg):
    current_dir = os.getcwd()
    home_dir = os.path.expanduser("~")
    functions_path = find_app('mrtrix3', '/usr/local/', home_dir)
    functions_path = f"{functions_path}/bin"
    os.chdir(functions_path)
    cmd = ''
    for i in arg:
        if type(i) == list:
            for j in i:
                cmd += f"{j} "
        else:
            cmd += f"{i} "
    process = subprocess.Popen(cmd.split())
    process.wait()
    os.chdir(current_dir)


def run_norm(cmd):
    process = subprocess.run(cmd.split())
    
    

def create_files(*arg):
    for i in arg:
        f = open(i, 'w')
        


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




def test_image(convert_files, test_file):
    test_bval = input('b-value: ')
    a = []
    for i in convert_files:
        if test_bval in i:
            a.append(i)
    if len(a) != 0:
        output = f"{a[0]}"
        b_volumes = get_volumes(output)
        test_file.append(a[0])
        test_file.append(output)
        return b_volumes, test_bval
    else:
        print(f"b{test_bval} not in dataset.  Please select another b-value")
        test_image(convert_files, test_file)
        return None, None




def masking(pt_id, pt_dir, dwi_cmd, mr_conv_1_cmd, mr_conv_2_cmd, debug):
    
    current_dir = os.getcwd()
    run(dwi_cmd)
    run(mr_conv_1_cmd)
    run(mr_conv_2_cmd)

    b0_extract_nii = f"{os.getcwd()}/extracted_b0.nii"
    moved_b0_extract_nii = f"{pt_dir}Processed/11_nifti/extracted_b0.nii"
    b0_upsamp = f"{os.getcwd()}/b0_upsamp.nii.gz"
    b0_upsamp_mask = f"{os.getcwd()}/b0_upsamp_mask.nii.gz"
    shutil.copy(b0_extract_nii, moved_b0_extract_nii)
    
    g = input("g-value vertical gradient in fractional intensity threshold (-1->1); default=0; positive values give larger brain outline at bottom, smaller at top: ")
    f = input("f-value fractional intensity threshold (0->1); default=0.5; smaller values give larger brain outline estimates: ")
    
    bet_cmd = f"bet {b0_extract_nii} {b0_upsamp} -n -m -f {f} -g {g}"
    run(bet_cmd)
    
    if debug == 'debug':
    
        print('Check if the mask has worked.  If it has not, re-run this script and skip to masking, or run the check_mask function in the mask.py file')
        fsleyes_path = os.environ.get('FSLDIR')
        fsleyes_path = f"{fsleyes_path}/bin/"
        os.chdir(fsleyes_path)
        fsl_cmd = f"fsleyes {b0_extract_nii} {b0_upsamp_mask}"
        subprocess.run(fsl_cmd.split())
        os.chdir(current_dir)

        
    os.rename(f"{os.getcwd()}/b0_upsamp_mask.nii.gz", f"{os.getcwd()}/mask_final.nii.gz")
    with open('mask_params.txt', 'a') as f:
        f.write(f"For the mask for patient {pt_id} the g-value is {g} and f-value is {g}")
     
    
    

def zero_test(file_1, file_2):
    with open(f"{file_1}", 'r') as f1, open(f"{file_2}", 'r') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
    result = [line for line in lines1 if line not in lines2]
    print(result)
    if len(result) > 4:
        print()
        print('The headers are not the same')
        print()
        return 0
    else:
        print()
        print('The headers are identical')
        print()
        return 1
        

    
def get_volumes(mif_image):
    
    cmd = f"mrinfo -size {mif_image}"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)

    if result.returncode == 0:
        pass
    else:
        print(f"Error: {result.stderr.strip()}")
        
    output = result.stdout
    volumes = int(output.split(' ')[-1])
        
    return volumes

  
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
   
   
    
def convert_tracts(pt_dir, debug):

    nii_dir = f"{pt_dir}Processed/11_nifti/"
    tract_dir = f"{pt_dir}Processed/9_tract/"
    fa_tensor = f"{pt_dir}Processed/7_tensor/fa.mif"
    
    mif_orig_filepath = f"{pt_dir}Processed/1_convert/"
    mif_orig_files = os.listdir(mif_orig_filepath)
    for i in mif_orig_files:
        if 't1' in i.lower():
            t1_file = f"{mif_orig_filepath}{i}"

    
    tract_files = os.listdir(tract_dir)
    for i in tract_files:
        if '.tck' in i:
            file = f"{tract_dir}{i}"
            mif_file = f"{tract_dir}{i.split('.')[0]}.mif"
            norm_file = f"{tract_dir}{i.split('.')[0]}_NORM.mif"
            tck_to_mif = f"tckmap -template {fa_tensor} {file} {mif_file}"
            run(tck_to_mif)
            N_tracts = get_counts(file)
            run(f"mrcalc {mif_file} {N_tracts} -div {norm_file}")
            if debug == 'debug':
                mrview_cmd = f"mrview -mode 2 -load {t1_file} -interpolation 0 -overlay.load {norm_file} -comments 0"
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


def get_transform_matrix(nii_list):

    trans_cmd = f"flirt -in {nii_list[1]} -ref {nii_list[0]} -o transform"
    result = subprocess.run(trans_cmd.split(), capture_output=True, text=True)
    std_output = result.stdout
    last_four_lines = std_output.split('\n')[-6:-2]
    trans_list = []
    for i in last_four_lines:
        trans_list.append(i.split())
    trans = list(itertools.chain(*trans_list))
    trans = list(map(float, trans))
    
    transform = np.array(trans).reshape((4, 4))
    
    return transform, std_output
    
    

def register(pt_dir, object):

    nii_dir = f"{pt_dir}Processed/11_nifti/"
    misc_dir = f"{pt_dir}Processed/13_misc/"
    b0_extract_nii = f"{nii_dir}extracted_b0.nii"
    t1_bet_nii = f"{nii_dir}t1_bet_mask.nii.gz"
    

    objects = []
    names = []
    for i in os.listdir(nii_dir):
        if 'NORM' in i:
            objects.append(f"{nii_dir}{i}")
            names.append(i)
    
    if len(objects) > 1:
        for idx, i in enumerate(objects):
            if object.lower() in i.lower():
                object_nii = i
                object_name = names[idx]
    else:
        object_nii = objects[0]
        object_name = names[0].split('.')[0]
        
        
    registered_object = f"{nii_dir}{object_name}_registered.nii.gz"
    
    fslhd_cmd_1 = f"fslhd {b0_extract_nii}"
    fslhd_cmd_2 = f"fslhd {object_nii}"


    run_fsl(fslhd_cmd_1, pt_dir)
    run_fsl(fslhd_cmd_2, pt_dir)

    identical = zero_test(f"{misc_dir}extracted_b0.txt", f"{misc_dir}object.txt")
        
    #1. register the dwi to T1 and get transform
    trans_cmd_1 = f"flirt -in {b0_extract_nii} -ref {t1_bet_nii} -out {nii_dir}outvol.nii -omat {misc_dir}transform.mat -dof 6"
    run(trans_cmd_1)
    #2. apply transform to object
    trans_cmd_2 = f"flirt -in {object_nii} -ref {t1_bet_nii} -out {registered_object} -init {misc_dir}transform.mat -applyxfm"
    run(trans_cmd_2)

    if identical == 0:
        return 0, registered_object
    else:
        return 1, registered_object
        
        





def karawun_run(pt_dir, dicom_template, nifti_filename, dcm_dir, t1_nii):
    current_dir = os.getcwd()
    fa_tensor = f"{pt_dir}Processed/7_tensor/fa.nii.gz"
    
    print("WARNING: This function assumes that you have python 3.8 and that it is saved in the standard location. If you do not, please download python3.8 from https://www.python.org/downloads/release/python-380/. You also need to have downloaded the python package karawun using python3.8.  If you have not done so, add python3.8 to your system path and run the command python3.8 -m pip install karawun.")
    
    base_dir_pre = find_karawun('3.8', '/Library/')
    base_dir = find_karawun('site-packages', base_dir_pre)
    karawun_dir = find_karawun('karawun', base_dir)
    os.chdir(karawun_dir)
    #importTractography --dicom-template path/to/a/dicom --nifti T1.nii.gz fa.nii.gz --tract-files left_cst.tck right_cst.tck --output-dir path/to/output/folder
    #importTractography --dicom-template path/to/a/dicom --nifti T1.nii.gz fa.nii.gz --tract-files left_cst.tck right_cst.tck --label-files lesion.nii.gz white_matter.nii.gz  --output-dir path/to/output/folder

    conversion_cmd = f"importTractography --dicom-template {dicom_template} --nifti {nifti_filename} {fa_tensor} --output-dir {dcm_dir}"
    subprocess.run(conversion_cmd.split())
    
    tract_files = f"--tract-files left_cst.tck right_cst.tck"
    label_files = f"--label-files lesion.nii.gz white_matter.nii.gz"
    label_cmd = f"importTractography --dicom-template {dicom_template} --nifti {t1_nii} {fa_tensor} {tract_files}  {label_files}   --output-dir {dcm_dir}"
    
    
    os.chdir(current_dir)
