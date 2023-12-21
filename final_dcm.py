import nibabel as nib
import numpy as np
import pydicom
import random
import string
import os


def create_brainlab_object(tract_name, nifti_file_path, reference_dicom_path, output_dicom_path, max_factor, wind_factor):

    if '.' in tract_name:
        tract_part = os.path.basename(tract_name)
        tract = tract_part.split('.')[0]
    else:
        tract = tract_name

    # Load NIfTI file for pixel array
    nifti_data = nib.load(nifti_file_path)
    nifti_data = nib.as_closest_canonical(nifti_data)
    nifti_pixel_array = nifti_data.get_fdata()

    # Update pixel data with rescaled NIfTI pixel array
    dicom_file = pydicom.dcmread(reference_dicom_path, force=True)

    max_value = int(np.max(dicom_file.pixel_array)*max_factor)
    max_value = 1024

    # Flatten the NIfTI pixel array
    nifti_pixel_array_flat = nifti_pixel_array.flatten(order='K')
    max_flat = np.max(nifti_pixel_array_flat)
    nifti_pixel_array_flat[nifti_pixel_array_flat == max_flat] *= 2

    nifti_pixel_array_rescaled = (
        (nifti_pixel_array_flat - np.min(nifti_pixel_array_flat)) /
        (np.max(nifti_pixel_array_flat) - np.min(nifti_pixel_array_flat)) * max_value
    )

    nifti_pixel_array_rescaled = nifti_pixel_array_rescaled.astype(np.uint16)

    # Ensure correct byte order (little-endian)
    nifti_pixel_array_rescaled = nifti_pixel_array_rescaled.byteswap()


    # Convert to bytes with 'C' order
    nifti_pixel_data_bytes = nifti_pixel_array_rescaled.tobytes(order='C')
    dicom_file.PixelData = nifti_pixel_data_bytes
    dicom_pixel_array = dicom_file.pixel_array
    flipped_pixel_array = np.flip(dicom_pixel_array, axis=2)
    dicom_file.PixelData = flipped_pixel_array.tobytes()

    dicom_file.BitsStored = 16
    dicom_file.BitsAllocated = 16
    dicom_file.HighBit = 15

    # Set the correct Transfer Syntax UID
    trans_type = dicom_file.file_meta.TransferSyntaxUID
    dicom_file.file_meta.TransferSyntaxUID = trans_type  # Explicit VR Little Endian

    # Set WindowCenter and WindowWidth based on the peak value
    dicom_file.WindowCenter = int(max_value*wind_factor)

    dicom_file.SeriesDescription = f"Brainlab_Object_{tract}"
    dicom_file.ProtocolName = f"Brainlab_Object_{tract}"
    dicom_file.InstitutionName = "Guy's and St Thomas'"
    dicom_file.StudyDescription = f"fMRI Motor {tract}"
    dicom_file.StudyInstanceUID = ''.join(random.choices(string.digits, k=8))
    dicom_file.SeriesInstanceUID = ''.join(random.choices(string.digits, k=8))
    dicom_file.StudyID = ''.join(random.choices(string.digits, k=8))

    # Save as a new DICOM file
    dicom_file.save_as(output_dicom_path)







