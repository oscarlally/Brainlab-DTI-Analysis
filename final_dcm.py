import numpy as np
import pydicom
import os


def final_dicom_conversion(dcm_directory, t1_dicom, output_file, max_value):

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
            

    dicom_file = pydicom.dcmread(t1_dicom, force=True)
    
    dicom_file.PixelData = a[0]

    dicom_file.save_as(output_file)
    

    def contrast_stretching(pixel_array):
        min_value = pixel_array.min()
        max_value = pixel_array.max()

        # Calculate the contrast stretching mapping
        pixel_values = (pixel_array - min_value) * (max_value - 1) / (max_value - min_value)
        pixel_values = np.clip(pixel_values, 0, max_value - 1)
        pixel_values = pixel_values.astype(np.uint16)

        return pixel_values

    def histogram_equalization(pixel_array):
        # Calculate the cumulative distribution function
        hist, bin_edges = np.histogram(pixel_array.flatten(), bins=range(0, 4096))
        cdf = hist.cumsum()

        # Normalize the cdf
        cdf_normalized = (cdf - cdf.min()) * float(max_value - 1) / (cdf.max() - cdf.min())

        # Use linear interpolation to map the pixel values
        pixel_values = np.interp(pixel_array.flatten(), bin_edges[:-1], cdf_normalized)
        pixel_values = np.clip(pixel_values, 0, max_value - 1)
        pixel_values = pixel_values.astype(np.uint16)

        return pixel_values.reshape(pixel_array.shape)

    def rescale_dicom_image(dicom_file_path):
        # Read the DICOM image
        dicom_dataset = pydicom.dcmread(dicom_file_path)

        # Get the pixel data as a NumPy array
        pixel_array = dicom_dataset.pixel_array.astype(float)

        # Check if the maximum pixel value is greater than the desired maximum
        if pixel_array.max() > max_value:
            # Apply contrast stretching to rescale the pixel values
            stretched_pixel_array = contrast_stretching(pixel_array)

            # Apply histogram equalization to the stretched pixel values
            scaled_pixel_array = histogram_equalization(stretched_pixel_array)

            # Update the pixel data in the DICOM dataset
            dicom_dataset.PixelData = scaled_pixel_array.tobytes()

            # Update the window width and window center
            dicom_dataset.WindowWidth = max_value
            dicom_dataset.WindowCenter = max_value / 2

            # Save the modified DICOM dataset back to a new file
            new_dicom_file_path = output_file
            dicom_dataset.save_as(new_dicom_file_path)
            print()
            print("Analysis completed")

        else:
            print()
            print("No rescaling needed. Maximum pixel value is not greater than the desired maximum.")
            print("Analysis completed")

    rescale_dicom_image(output_file)










