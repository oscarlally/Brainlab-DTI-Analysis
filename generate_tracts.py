import os
from functions import run

current_dir = os.getcwd()

def gentck():
    """Present tractography options and execute chosen operation."""
    print("\nTractography Options:")
    tract_options = {
        "1": "AF: Arcuate Fasciculus",
        "2": "MHA: Corticospinal Tract (Motor Hand Area)",
        "3": "SHA: Sensory Hand Area",
        "4": "Lip Motor Tract",
        "7": "Optic Radiation",
        "9": "MFO: Motor Foot Area",
        "F": "MFace: Motor Face Area",
        "S": "Skip",
    }
    for key, desc in tract_options.items():
        print(f"({key}) {desc}")

    while True:
        choice = input("Which tracts do you want to generate? ")
        if choice in tract_options:
            break
        print("Invalid choice. Please try again.")

    if choice == "1":
        print("You chose AF (Arcuate Fasciculus)")
        filepaths = process_af()
    elif choice == "2":
        print("You chose MHA (Motor Hand Area)")
        filepaths = process_mha()
    elif choice == "3":
        print("You chose SHA (Sensory Hand Area)")
        filepaths = process_sha()
    elif choice == "4":
        print("You chose Lip Motor Tract")
        filepaths = process_lip_motor()
    elif choice == "7":
        print("You chose Optic Radiation")
        filepaths = process_optic_radiation()
    elif choice == "9":
        print("You chose MFO (Motor Foot Area)")
        filepaths = process_motor_foot()
    elif choice == "F":
        print("You chose MFace (Motor Face Area)")
        filepaths = process_motor_face()
    elif choice == "S":
        print("Skipping tract generation.")
        return

    if filepaths:
        print("\nGenerated tract files:")
        for path in filepaths:
            print(path)
            display_tract(path)
    else:
        print("No tracts were generated.")

def display_tract(tract_path):
    """Display the generated tract in mrview."""
    fa_tensor = f"{current_dir}/mrtrix3_files/fods/wm_fod.mif"
    print(f"Displaying tract: {tract_path}")
    run(f"mrview -mode 2 -load {fa_tensor} -interpolation 0 -tractography.load {tract_path}")

def process_af():
    """Generate AF tracts."""
    filepaths = []
    for side in ["L", "R"]:
        roi_file = f"{current_dir}/mrtrix3_files/rois/AF_{side}.mif"
        if os.path.isfile(roi_file):
            output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-AF_{side}.tck"
            print(f"Generating AF tracts for {side} hemisphere...")
            run(
                f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {roi_file} "
                f"-include {current_dir}/mrtrix3_files/rois/SLF_{side}.mif -include {current_dir}/mrtrix3_files/rois/BROCA_{side}.mif -step 1.75 -angle 45 -cutoff 0.05"
            )
            exclude_file = f"{current_dir}/mrtrix3_files/rois/AF_exclude.mif"
            if os.path.isfile(exclude_file):
                run(f"tckedit {output_file} {output_file.replace('.tck', '-EX.tck')} -exclude {exclude_file}")
            filepaths.append(output_file)
    return filepaths

def process_mha():
    """Generate MHA tracts."""
    filepaths = []
    for side in ["L", "R"]:
        roi_file = f"{current_dir}/mrtrix3_files/rois/MHA_{side}.mif"
        if os.path.isfile(roi_file):
            output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-MHA_{side}.tck"
            print(f"Generating MHA tracts for {side} hemisphere...")
            run(
                f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {roi_file} "
                f"-include {current_dir}/mrtrix3_files/rois/M1_{side}.mif -step 1.75 -angle 45 -cutoff 0.05"
            )
            filepaths.append(output_file)
    return filepaths

def process_sha():
    """Generate SHA tracts."""
    filepaths = []
    for side in ["L", "R"]:
        roi_file = f"{current_dir}/mrtrix3_files/rois/SHA_{side}.mif"
        if os.path.isfile(roi_file):
            output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-SHA_{side}.tck"
            print(f"Generating SHA tracts for {side} hemisphere...")
            run(
                f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {roi_file} "
                f"-include {current_dir}/mrtrix3_files/rois/S1_{side}.mif -step 1.75 -angle 45 -cutoff 0.05"
            )
            filepaths.append(output_file)
    return filepaths

def process_lip_motor():
    """Generate Lip Motor tracts."""
    filepaths = []
    for side in ["L", "R"]:
        roi_file = f"{current_dir}/mrtrix3_files/rois/LipMotor_{side}.mif"
        if os.path.isfile(roi_file):
            output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-LipMotor_{side}.tck"
            print(f"Generating Lip Motor tracts for {side} hemisphere...")
            run(
                f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {roi_file} "
                f"-include {current_dir}/mrtrix3_files/rois/PreMotor_{side}.mif -step 1.75 -angle 45 -cutoff 0.05"
            )
            filepaths.append(output_file)
    return filepaths

def process_optic_radiation():
    """Generate Optic Radiation tracts."""
    filepaths = []
    for side in ["L", "R"]:
        roi_file = f"{current_dir}/mrtrix3_files/rois/OpticRad_{side}.mif"
        if os.path.isfile(roi_file):
            output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-OpticRad_{side}.tck"
            print(f"Generating Optic Radiation tracts for {side} hemisphere...")
            run(
                f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {roi_file} "
                f"-include {current_dir}/mrtrix3_files/rois/LGN_{side}.mif -step 1.75 -angle 45 -cutoff 0.05"
            )
            filepaths.append(output_file)
    return filepaths

def process_motor_foot():
    """Generate Motor Foot tracts."""
    filepaths = []
    for side in ["L", "R"]:
        roi_file = f"{current_dir}/mrtrix3_files/rois/MFoot_{side}.mif"
        if os.path.isfile(roi_file):
            output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-MFoot_{side}.tck"
            print(f"Generating Motor Foot tracts for {side} hemisphere...")
            run(
                f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {roi_file} "
                f"-include {current_dir}/mrtrix3_files/rois/LegMotor_{side}.mif -step 1.75 -angle 45 -cutoff 0.05"
            )
            filepaths.append(output_file)
    return filepaths

def process_motor_face():
    """Generate Motor Face tracts."""
    filepaths = []
    for side in ["L", "R"]:
        roi_file = f"{current_dir}/mrtrix3_files/rois/MFace_{side}.mif"
        if os.path.isfile(roi_file):
            output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-MFace_{side}.tck"
            print(f"Generating Motor Face tracts for {side} hemisphere...")
            run(
                f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {roi_file} "
                f"-include {current_dir}/mrtrix3_files/rois/FaceMotor_{side}.mif -step 1.75 -angle 45 -cutoff 0.05"
            )
            filepaths.append(output_file)
    return filepaths