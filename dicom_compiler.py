import os
import pydicom
import numpy as np

# Load all DICOM images in a directory

def compress(folder_path, output):

    dicom_files = os.listdir(folder_path)
    dicom_images = [pydicom.read_file(os.path.join(folder_path, f)) for f in dicom_files]

    # Sort the images by their ImagePositionPatient attribute
    dicom_images.sort(key=lambda x: float(x.ImagePositionPatient[2]))

    # Extract the image pixel data from each DICOM image
    image_shape = dicom_images[0].pixel_array.shape
    volume_data = np.zeros((len(dicom_images), image_shape[0], image_shape[1]), dtype=np.float32)
    for i, dicom in enumerate(dicom_images):
        volume_data[i,:,:] = dicom.pixel_array

    # Resample the images if necessary

    # Create a 3D array to store the volume data
    volume_shape = (len(dicom_images),) + image_shape
    volume = np.zeros(volume_shape, dtype=np.float32)

    # Fill the volume array with the pixel data from each image
    for i, dicom in enumerate(dicom_images):
        # Get the image position and pixel spacing from the DICOM headers
        image_position = np.array([float(val) for val in dicom.ImagePositionPatient])
        pixel_spacing = np.array([float(val) for val in dicom.PixelSpacing])
        # Calculate the x and y indices for the image in the volume
        xy_indices = ((image_position[:2] - image_position[0]) / pixel_spacing).astype(int)
        # Fill the volume with the pixel data from the image
        volume[i, xy_indices[0]:xy_indices[0]+image_shape[0], xy_indices[1]:xy_indices[1]+image_shape[1]] = dicom.pixel_array
        
        
    # Load the first DICOM image in the volume
    first_dicom = pydicom.dcmread(os.path.join(folder_path, dicom_files[0]))

    # Create a new DICOM object with the appropriate attributes for the volume data
    new_file = pydicom.dataset.FileDataset(output, {}, file_meta=first_dicom.file_meta, preamble=b"\0" * 128)
    new_file.Modality = first_dicom.Modality
    new_file.PatientID = first_dicom.PatientID
    new_file.StudyInstanceUID = first_dicom.StudyInstanceUID
    new_file.SeriesInstanceUID = first_dicom.SeriesInstanceUID
    new_file.SOPInstanceUID = pydicom.uid.generate_uid()
    new_file.SamplesPerPixel = first_dicom.SamplesPerPixel
    new_file.PhotometricInterpretation = first_dicom.PhotometricInterpretation
    new_file.PixelRepresentation = first_dicom.PixelRepresentation
    new_file.BitsAllocated = first_dicom.BitsAllocated
    new_file.BitsStored = first_dicom.BitsStored
    new_file.HighBit = first_dicom.HighBit
    new_file.PixelSpacing = first_dicom.PixelSpacing
    new_file.ImagePositionPatient = first_dicom.ImagePositionPatient
    new_file.ImageOrientationPatient = first_dicom.ImageOrientationPatient
    new_file.Rows, new_file.Columns = volume.shape[1], volume.shape[2]

    # Copy the pixel data from the volume array to the new DICOM object
    new_file.PixelData = volume.tobytes()

    # Save the new file
    pydicom.filewriter.dcmwrite(output, new_file)

