import os
from functions import run

current_dir = os.getcwd()

"""CHANGE FA (NOT EVERYTIME)"""


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
    sides = ["L", "R"]
    defaults = ["1.75", "45", "0.05", "1000"]
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/SLF_{sides[1]}.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-AF_{sides[0]}.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {current_dir}/mrtrix3_files/rois/AF_{sides[0]}.mif -include {current_dir}/mrtrix3_files/rois/SLF_{sides[0]}.mif -include {current_dir}/mrtrix3_files/rois/BROCA_{sides[0]}.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}"
        cmd_2 = f"tckedit {output_file} {current_dir}/mrtrix3_files/tracts/mrtrix3-AF-EX.tck -exclude {current_dir}/mrtrix3_files/rois/AF_exclude.mif"
        cmd_3 = f"tckedit {output_file} {current_dir}/mrtrix3_files/tracts/mrtrix3-AF-EX_{defaults[3]}.tck -exclude {current_dir}/mrtrix3_files/rois/AF_exclude.mif -number {defaults[3]}"
        run(cmd)
        run(cmd_2)
        run(cmd_3)
        filepaths.append(output_file)
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/SLF_{sides[0]}.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-AF_{sides[1]}.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {current_dir}/mrtrix3_files/rois/AF_{sides[1]}.mif -include {current_dir}/mrtrix3_files/rois/SLF_{sides[1]}.mif -include {current_dir}/mrtrix3_files/rois/BROCA_{sides[1]}.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}"
        cmd_2 = f"tckedit {output_file} {current_dir}/mrtrix3_files/tracts/mrtrix3-AF-EX.tck -exclude {current_dir}/mrtrix3_files/rois/AF_exclude.mif"
        cmd_3 = f"tckedit {output_file} {current_dir}/mrtrix3_files/tracts/mrtrix3-AF-EX_{defaults[3]}.tck -exclude {current_dir}/mrtrix3_files/rois/AF_exclude.mif -number {defaults[3]}"
        run(cmd)
        run(cmd_2)
        run(cmd_3)
        filepaths.append(output_file)
    return filepaths

def process_mha():
    """Generate MHA tracts."""
    filepaths = []
    sides = ["L", "R"]
    defaults = ["1", "45", "0.1"]
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/{sides[1]}_Ped.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-MHA_{sides[1]}.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -include {current_dir}/mrtrix3_files/rois/{sides[1]}_Ped.mif -seed_image {current_dir}/mrtrix3_files/rois/{sides[0]}HandM1.mif -include {current_dir}/mrtrix3_files/rois/{sides[1]}_Cap.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}"
        run(cmd)
        filepaths.append(output_file)
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/{sides[0]}_Ped.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-MHA_{sides[0]}.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -include {current_dir}/mrtrix3_files/rois/{sides[0]}_Ped.mif -seed_image {current_dir}/mrtrix3_files/rois/{sides[1]}HandM1.mif -include {current_dir}/mrtrix3_files/rois/{sides[0]}_Cap.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}"
        run(cmd)
        filepaths.append(output_file)
    return filepaths


def process_sha():
    """Generate SHA tracts."""
    filepaths = []
    sides = ["L", "R"]
    defaults = ["1", "45", "0.1"]
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/SHA_{sides[1]}.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-MHA_{sides[1]}.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {current_dir}/mrtrix3_files/rois/{sides[1]}HandS1.mif -include {current_dir}/mrtrix3_files/rois/{sides[0]}_Thal.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}"
        run(cmd)
        filepaths.append(output_file)
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/SHA_{sides[0]}.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-MHA_{sides[0]}.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {current_dir}/mrtrix3_files/rois/{sides[0]}HandS1.mif -include {current_dir}/mrtrix3_files/rois/{sides[1]}_Thal.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}"
        run(cmd)
        filepaths.append(output_file)
    return filepaths

def process_lip_motor():
    """Generate Lip Motor tracts."""
    filepaths = []
    sides = ["L", "R"]
    defaults = ["1", "45", "0.1", "1000"]
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/{sides[0]}-Ped.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-{sides[1]}_Lip.tck"
        output_edit_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-{sides[1]}_Lip_1000.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -include {current_dir}/mrtrix3_files/rois/{sides[0]}-Ped.mif -seed_image {current_dir}/mrtrix3_files/rois/LipM1.mif -include {current_dir}/mrtrix3_files/rois/{sides[0]}-Cap.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional -force"
        cmd_2 = f"tckedit {output_file} {output_edit_file} -number {defaults[3]}"
        run(cmd)
        run(cmd_2)
        filepaths.append(output_file)
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/{sides[1]}-Ped.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-{sides[0]}_Lip.tck"
        output_edit_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-{sides[0]}_Lip_1000.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -include {current_dir}/mrtrix3_files/rois/{sides[1]}-Ped.mif -seed_image {current_dir}/mrtrix3_files/rois/LipM1.mif -include {current_dir}/mrtrix3_files/rois/{sides[1]}-Cap.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional -force"
        cmd_2 = f"tckedit {output_file} {output_edit_file} -number {defaults[3]}"
        run(cmd)
        run(cmd_2)
        filepaths.append(output_file)


    return filepaths


def process_optic_radiation():
    """Generate Optic Radiation tracts (OR_UNI) for both sides."""
    sides = ["L", "R"]
    defaults = ["1", "45", "0.1"]
    filepaths = []

    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/{sides[0]}_LGN.mif"):
        print("Drawing on LEFT side")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-{sides[0]}-OR_UNI.tck"
        cmd = (
            f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} "
            f"-seed_image {current_dir}/mrtrix3_files/rois/{sides[0]}_LGN.mif "
            f"-include {current_dir}/mrtrix3_files/rois/{sides[0]}-latCalc.mif "
            f"-include {current_dir}/mrtrix3_files/rois/{sides[0]}-latVentr.mif "
            f"-step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional"
        )
        run(cmd)
        filepaths.append(output_file)

    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/{sides[1]}_LGN.mif"):
        print("Drawing on RIGHT side")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-{sides[1]}-OR_UNI.tck"
        cmd = (
            f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} "
            f"-seed_image {current_dir}/mrtrix3_files/rois/{sides[1]}_LGN.mif "
            f"-include {current_dir}/mrtrix3_files/rois/{sides[1]}-latCalc.mif "
            f"-include {current_dir}/mrtrix3_files/rois/{sides[1]}-latVentr.mif "
            f"-step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional"
        )
        run(cmd)
        filepaths.append(output_file)
    return filepaths


def process_motor_foot():
    """Generate foot motor area tracts for both sides."""
    sides = ["R", "L"]
    file_suffixes = ["RF_MFO", "LF_MFO"]
    ped_suffixes = ["L_Ped", "R_Ped"]
    cap_suffixes = ["L_Cap", "R_Cap"]
    defaults = ["1", "45", "0.1", "1000"]
    filepaths = []

    # Process Right Foot Motor Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/{sides[0]}FootM1.mif"):
        print("Making Right foot motor area tracts")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-{file_suffixes[0]}.tck"
        output_edit_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-{file_suffixes[0]}_{defaults[3]}.tck"
        cmd = (
            f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} "
            f"-seed_image {current_dir}/mrtrix3_files/rois/{sides[0]}FootM1.mif "
            f"-include {current_dir}/mrtrix3_files/rois/{ped_suffixes[0]}.mif "
            f"-include {current_dir}/mrtrix3_files/rois/{cap_suffixes[0]}.mif "
            f"-step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional -force"
        )
        edit_cmd = f"tckedit {output_file} {output_edit_file} -number {defaults[3]}"
        run(cmd)
        run(edit_cmd)
        filepaths.append(output_file)

    # Process Left Foot Motor Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/{sides[1]}FootM1.mif"):
        print("Making Left foot motor area tracts")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-{file_suffixes[1]}.tck"
        output_edit_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-{file_suffixes[1]}_{defaults[3]}.tck"
        cmd = (
            f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} "
            f"-seed_image {current_dir}/mrtrix3_files/rois/{sides[1]}FootM1.mif "
            f"-include {current_dir}/mrtrix3_files/rois/{ped_suffixes[1]}.mif "
            f"-include {current_dir}/mrtrix3_files/rois/{cap_suffixes[1]}.mif "
            f"-step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional -force"
        )
        edit_cmd = f"tckedit {output_file} {output_edit_file} -number {defaults[3]}"
        run(cmd)
        run(edit_cmd)
        filepaths.append(output_file)

    return filepaths


def process_motor_face():
    """Generate face motor area tracts for both sides."""
    sides = ["R", "L"]
    file_suffixes = ["R_MFace", "L_MFace"]
    ped_suffixes = ["L_Ped", "R_Ped"]
    cap_suffixes = ["L_Cap", "R_Cap"]
    defaults = ["1", "45", "0.05"]
    filepaths = []

    # Process Right Face Motor Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/{sides[0]}FaceM1.mif"):
        print("Making Right Face Motor Area")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-{file_suffixes[0]}.tck"
        cmd = (
            f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} "
            f"-seed_image {current_dir}/mrtrix3_files/rois/{sides[0]}FaceM1.mif "
            f"-include {current_dir}/mrtrix3_files/rois/{ped_suffixes[0]}.mif "
            f"-include {current_dir}/mrtrix3_files/rois/{cap_suffixes[0]}.mif "
            f"-step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -force"
        )
        run(cmd)
        filepaths.append(output_file)

    # Process Left Face Motor Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/{sides[1]}FaceM1.mif"):
        print("Making Left Face Motor Area")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-{file_suffixes[1]}.tck"
        cmd = (
            f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} "
            f"-seed_image {current_dir}/mrtrix3_files/rois/{sides[1]}FaceM1.mif "
            f"-include {current_dir}/mrtrix3_files/rois/{ped_suffixes[1]}.mif "
            f"-include {current_dir}/mrtrix3_files/rois/{cap_suffixes[1]}.mif "
            f"-step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -force"
        )
        run(cmd)
        filepaths.append(output_file)

    return filepaths
