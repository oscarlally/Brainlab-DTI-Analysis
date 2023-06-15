import numpy as np
import pydicom
import os
import matplotlib.pyplot as plt


def final_dicom_conversion(dcm_directory, t1_dicom, output_file):

    def separate_images(pixel_data, rows, columns, bits_allocated, samples_per_pixel):
        image_size = rows * columns * bits_allocated // 8
        total_images = len(pixel_data) // image_size

        images = []
        for i in range(1):
            start_idx = i * image_size
            end_idx = start_idx + image_size
            image_bytes = pixel_data[start_idx:end_idx]

            if bits_allocated == 8:
                # For 8-bit data, use numpy to reshape the byte string into a 2D image array
                image_array = np.frombuffer(image_bytes, dtype=np.uint8).reshape((rows, columns))
            elif bits_allocated == 16:
                # For 16-bit data, use numpy to reshape the byte string into a 2D image array
                image_array = np.frombuffer(image_bytes, dtype=np.uint16).reshape((rows, columns))
            else:
                # Handle other bits_allocated values if necessary
                raise ValueError(f"Unsupported bits_allocated: {bits_allocated}")
            flipped_array = np.flipud(image_array)
            images.append(flipped_array.tobytes())

        return images

    filelist = []
    for i in os.listdir(dcm_directory):
        filelist.append(f"{os.path.split(dcm_directory)[0]}/{i}")

    filelist.sort()


    a = []

    for idx, i in enumerate(filelist):

        # Load DICOM file
        dicom_file = pydicom.dcmread(i)

        # Extract relevant DICOM header information
        rows = dicom_file.Rows
        columns = dicom_file.Columns
        bits_allocated = dicom_file.BitsAllocated
        samples_per_pixel = dicom_file.SamplesPerPixel

        # Separate images from pixel data
        pixel_data = dicom_file.PixelData
        images = separate_images(pixel_data, rows, columns, bits_allocated, samples_per_pixel)

        if idx == 0:

            a.append(images[0])

        else:

            a[0] = a[0] + images[0]


    dicom_file = pydicom.dcmread(t1_dicom)

    dicom_file.PixelData = a[0]

    dicom_file.save_as(output_file)





