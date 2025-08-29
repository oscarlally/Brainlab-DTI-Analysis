from functions import get_full_file_names


diff_data_dir = "/Users/oscarlally/Desktop/CCL/170124638"

for i in get_full_file_names(diff_data_dir):
    print(i)