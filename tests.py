from Bash2PythonFuncs import zero_test, karawun_run, register, run, norm_nii, skew, get_pixel_range
from final_dcm import create_brainlab_object
import pydicom
import nibabel as nib
import numpy as np
import pydicom
import os
import subprocess


"""After masking"""
pt_dir = '/Users/oscarlally/Desktop/CCL/1414/raw/'
template_file = ['/Users/oscarlally/Desktop/CCL/1414/raw/T1/AL-SUHAIB_Fatem.MR.fMRI_Language.5.1.2022.10.28.11.22.14.582.70899209.dcm']

relevant_dcm = pydicom.dcmread(template_file[0])
data_dicom = relevant_dcm.pixel_array
pixel_values_dicom = data_dicom.flatten()
max_value = max(pixel_values_dicom)

test = '/Users/oscarlally/Documents/GitHub/Brainlab-DTI-Analysis/template'

nii_dir = f"{pt_dir}Processed/11_nifti/"
overlay_dir = f"{pt_dir}Processed/12_overlays/"
final_dir = f"{pt_dir}Processed/14_volume/"

binarised_object = f"{overlay_dir}binarised_object.nii.gz"
t1_object = f"{overlay_dir}t1_object.nii.gz"
t1_hole = f"{overlay_dir}t1_hole.nii.gz"
binarised_skew = f"{overlay_dir}binary_skew.nii.gz"
t1_dicom_range = f"{overlay_dir}t1_dicom_range.nii.gz"
object_dicom_range = f"{overlay_dir}object_dicom_range.nii.gz"
t1_burned_pre = f"{overlay_dir}t1_burned_pre.nii.gz"
t1_burned = f"{overlay_dir}t1_burned.nii.gz"
registered = f"{pt_dir}Processed/11_nifti/OR_exclude_5000_NORM_registered.nii.gz"

print()

for i in os.listdir(nii_dir):
    if 't1.nii' in i:
        t1_nii = f"{nii_dir}{i}"

min0, max0 = get_pixel_range(t1_nii)
print('t1 nii')
print(min0, max0)
print()

min1, max1 = get_pixel_range(registered)
print('registered')
print(min1, max1)
print()

norm_nii(registered, binarised_object, 0, 1)

min2, max2 = get_pixel_range(binarised_object)
print('binarised')
print(min2, max2)
print()


modified_file = skew(binarised_object, 10)
nib.save(modified_file, f"{binarised_skew}")


mult_cmd = f"fslmaths {t1_nii} -mul {binarised_object} {t1_object}"
sub_cmd = f"fslmaths {t1_nii} -sub {t1_object} {t1_hole}"


run(mult_cmd)
run(sub_cmd)


min3, max3 = get_pixel_range(binarised_skew)
print('skew')
print(min3, max3)
print()


nifti_file = nib.load(f"{t1_hole}")
nii_data = nifti_file.get_fdata()
max_hole = np.max(nii_data)
norm_num = 60 / max_hole


mult_2_cmd = f"fslmaths {t1_hole} -mul {norm_num} {t1_dicom_range}"
mult_3_cmd = f"fslmaths {binarised_skew} -mul {max_value-60} {object_dicom_range}"
add_cmd = f"fslmaths {t1_dicom_range} -add {object_dicom_range} {t1_burned}"

run(mult_2_cmd)

min4, max4 = get_pixel_range(t1_dicom_range)
print('t1 dicom range')
print(min4, max4)
print()


run(mult_3_cmd)

min5, max5 = get_pixel_range(object_dicom_range)
print('object_range')
print(min5, max5)
print()

run(add_cmd)

min6, max6 = get_pixel_range(t1_burned_pre)
print('t1 burned_pre')
print(min6, max6)


print()
min7, max7 = get_pixel_range(t1_burned)
print('t1 burned ')
print(min7, max7)

object_path = f"{final_dir}Brainlab_Object.dcm"

while True:
    print()
    print("Dicom creation.  Please open the resultant dicomes in the 14/volume folder and play around with the parameters as necessary.")
    print()
    wind_factor = input('Type in the maximum factor (default = 0.5): ')
    print()
    max_factor = input('Type in the window factor (default = 0.66: ')
    print()
    create_brainlab_object(t1_burned, template_file[0], object_path, float(max_factor), float(wind_factor))
    print()

    happy = input('Is the dicom contrast sufficient? (y/n): ')

    if happy.lower() == 'y':
        break

