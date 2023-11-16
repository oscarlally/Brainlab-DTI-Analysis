import nibabel as nib
import numpy as np
import pydicom

nii_path = '/Users/oscarlally/Desktop/CCL/twelth/raw/Processed/12_overlays/t1_burned.nii.gz'
ref_path = '/Users/oscarlally/Desktop/CCL/twelth/raw/T1/SCARD_Philip_He.MR.fMRI_Motor.5.1.2023.10.18.12.29.30.477.17582223.dcm'
output_path = '/Users/oscarlally/Desktop/tests/new_dicom_file.dcm'

def create_brainlab_object(nifti_file_path, reference_dicom_path, output_dicom_path, max_factor, wind_factor):

    # Load NIfTI file for pixel array
    nifti_data = nib.load(nifti_file_path)
    nifti_pixel_array = nifti_data.get_fdata()

    # Update pixel data with rescaled NIfTI pixel array
    dicom_file = pydicom.dcmread(reference_dicom_path, force=True)
    max_value = int(np.max(dicom_file.pixel_array)*max_factor)

    # Flatten the NIfTI pixel array
    nifti_pixel_array_flat = nifti_pixel_array.flatten(order='K')
    max_value = np.max(nifti_pixel_array_flat)
    arr_max_doubled = nifti_pixel_array_flat.copy()
    nifti_pixel_array_flat[nifti_pixel_array_flat == max_value] *= 2

    nifti_pixel_array_rescaled = (
        (nifti_pixel_array_flat - np.min(nifti_pixel_array_flat)) /
        (np.max(nifti_pixel_array_flat) - np.min(nifti_pixel_array_flat)) * max_value
    )

    # bincount = list(np.bincount(nifti_pixel_array_rescaled.astype(np.int16)))
    # middle = find_balance_point(bincount)

    nifti_pixel_array_rescaled = nifti_pixel_array_rescaled.astype(np.uint16)

    # Ensure correct byte order (little-endian)
    nifti_pixel_array_rescaled = nifti_pixel_array_rescaled.byteswap()

    # Convert to bytes with 'C' order
    nifti_pixel_data_bytes = nifti_pixel_array_rescaled.tobytes(order='C')

    # Set the correct data type
    dicom_file.BitsStored = 16
    dicom_file.BitsAllocated = 16
    dicom_file.HighBit = 15

    # Set the correct Transfer Syntax UID
    trans_type = dicom_file.file_meta.TransferSyntaxUID
    dicom_file.file_meta.TransferSyntaxUID = trans_type  # Explicit VR Little Endian

    # Update the PixelData attribute
    dicom_file.PixelData = nifti_pixel_data_bytes

    dicom_file.PatientName = 'Anon'

    # Set WindowCenter and WindowWidth based on the peak value
    dicom_file.WindowCenter = int(max_value*wind_factor)

    # Save as a new DICOM file
    dicom_file.save_as(output_dicom_path)


create_brainlab_object(nii_path, ref_path, output_path, 0.5, 0.66)





