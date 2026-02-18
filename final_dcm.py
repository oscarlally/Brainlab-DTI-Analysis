from datetime import datetime
import nibabel as nib
import numpy as np
import pydicom
from pydicom.uid import generate_uid
import random
import string


def create_brainlab_object(tract, nifti_file_path, reference_dicom_path, output_dicom_path):

    # Load NIfTI and reorient to canonical RAS+
    nifti_data = nib.load(nifti_file_path)
    nifti_data = nib.as_closest_canonical(nifti_data)
    nifti_pixel_array = nifti_data.get_fdata()

    dicom_file = pydicom.dcmread(reference_dicom_path, force=True)
    nifti_zyx = np.transpose(nifti_pixel_array, (2, 1, 0))
    nifti_zyx = np.flip(nifti_zyx, axis=(0, 2))

    vmin, vmax = nifti_zyx.min(), nifti_zyx.max()
    if vmax == vmin:
        rescaled = np.zeros_like(nifti_zyx, dtype='<u2')
    else:
        scaled = (nifti_zyx - vmin) / (vmax - vmin)
        rescaled = (scaled * 255).astype('<u2')

    dicom_shape = dicom_file.pixel_array.shape
    if rescaled.shape != dicom_shape:
        raise ValueError(
            f"Shape mismatch after transpose: NIfTI {rescaled.shape} vs DICOM {dicom_shape}. "
            f"Check that the NIfTI and reference DICOM are from the same acquisition."
        )

    dicom_file.PixelData = rescaled.tobytes()
    dicom_file.BitsStored = 16
    dicom_file.BitsAllocated = 16
    dicom_file.HighBit = 15
    dicom_file.PixelRepresentation = 0

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%Y%m%d%H%M%S')
    series_time = current_datetime.strftime('%H%M%S')

    dicom_file.SeriesDescription = f"Brainlab_Object_{tract}"
    dicom_file.ProtocolName = f"Brainlab_Object_{tract}"
    dicom_file.InstitutionName = "Guy's and St Thomas'"
    dicom_file.StudyDescription = f"{tract}"
    dicom_file.AcquisitionDateTime = formatted_datetime
    dicom_file.ContentTime = f"{series_time}.000000"

    dicom_file.StudyInstanceUID = generate_uid()
    dicom_file.SeriesInstanceUID = generate_uid()
    dicom_file.StudyID = ''.join(random.choices(string.digits, k=8))

    dicom_file.save_as(output_dicom_path)

    print(f"NIfTI original shape:   {nifti_pixel_array.shape}  (X, Y, Z)")
    print(f"After transpose+flip:   {rescaled.shape}  (Z, Y, X)")
    print(f"DICOM expected shape:   {dicom_shape}")
    print(f"Rescaled dtype:         {rescaled.dtype}")
