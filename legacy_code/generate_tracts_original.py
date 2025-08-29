import os
from functions import run

current_dir = os.getcwd()


def cmd_check(cmd):
    print('-----------')
    print('Command is:')
    print(cmd)
    print()
    check = input('Do you need to edit this command?  (y/n)')
    if check.lower() != 'y':
        run(cmd)
    else:
        new_cmd = input('Please type in the command you want to run:')
        cmd_check(new_cmd)


def gentck(defaults, choice):
    """Present tractography options and execute chosen operation."""
    print("\nTractography Options:")

    if choice is None:
        tract_options = {
            "1": "AF: Arcuate Fasciculus",
            "2": "MHA: Corticospinal Tract (Motor Hand Area)",
            "3": "SHA: Sensory Hand Area",
            "4": "Lip Motor Tract",
            "7": "Optic Radiation",
            "8": "Sensory Foot Area",
            "9": "MFO: Motor Foot Area",
            "f": "MFace: Motor Face Area",
            "c": "Custom",
            "s": "Skip",
        }
        for key, desc in tract_options.items():
            print(f"({key}) {desc}")

        while True:
            choice = input("Which tracts do you want to generate? ")
            if choice in tract_options:
                break
            print("Invalid choice. Please try again.")

    filepaths = []  # Ensure filepaths is always initialized
    if choice == "1":
        print("You chose AF (Arcuate Fasciculus)")
        filepaths, defaults = process_af(defaults)
    elif choice == "2":
        print("You chose MHA (Motor Hand Area)")
        filepaths, defaults = process_mha(defaults)
    elif choice == "3":
        print("You chose SHA (Sensory Hand Area)")
        filepaths, defaults = process_sha(defaults)
    elif choice == "4":
        print("You chose Lip Motor Tract")
        filepaths, defaults = process_lip_motor(defaults)
    elif choice == "7":
        print("You chose Optic Radiation")
        filepaths, defaults = process_optic_radiation(defaults)
    elif choice == "8":
        print("You chose Sensory Foot Area")
        filepaths, defaults = process_sensory_foot(defaults)
    elif choice == "9":
        print("You chose MFO (Motor Foot Area)")
        filepaths, defaults = process_motor_foot(defaults)
    elif choice in ["F", "f"]:
        print("You chose MFace (Motor Face Area)")
        filepaths, defaults = process_motor_face(defaults)
    elif choice in ["C", "c"]:
        print("You chose a custom tract with custom commands")
        filepaths, defaults = process_custom()
    elif choice in ["S", "s"]:
        print("Skipping tract generation.")
        return [], defaults  # Explicitly return an empty list and defaults

    if filepaths:
        print("\nGenerated tract files:")
        for path in filepaths:
            print(path)
            display_tract(path)
    else:
        print("No tracts were generated.")

    return filepaths, defaults, choice  # Ensure a consistent return value


def display_tract(tract_path):
    """Display the generated tract in mrview."""
    fa_tensor = f"{current_dir}/mrtrix3_files/fods/wm_fod.mif"
    print(f"Displaying tract: {tract_path}")
    run(f"mrview -mode 2 -load {fa_tensor} -interpolation 0 -tractography.load {tract_path}")


def process_af(defaults):
    """Generate AF tracts."""
    filepaths = []
    sides = ["L", "R"]
    force = ""
    if defaults is None:
        defaults = ["1", "45", "0.05", "500"]
    else:
        force = " -force"

    # Left AF
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/AF_{sides[0]}.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-AF.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {current_dir}/mrtrix3_files/rois/AF_{sides[0]}.mif -include {current_dir}/mrtrix3_files/rois/SLF_{sides[0]}.mif -include {current_dir}/mrtrix3_files/rois/BROCA_{sides[0]}.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -select {defaults[3]}{force}"
        run(cmd)
        filepaths.append(output_file)

    # Right AF
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/AF_{sides[1]}.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-AF_{sides[1]}.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {current_dir}/mrtrix3_files/rois/AF_{sides[1]}.mif -include {current_dir}/mrtrix3_files/rois/SLF_{sides[1]}.mif -include {current_dir}/mrtrix3_files/rois/BROCA_{sides[1]}.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}{force}"
        run(cmd)
        filepaths.append(output_file)

    return filepaths, defaults


def process_mha(defaults):
    """Generate MHA tracts."""
    filepaths = []
    force = ""
    if defaults is None:
        defaults = ["1", "45", "0.05"]
    else:
        force = " -force"

    # Right Hand Motor Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/RHandM1.mif"):
        print("Making Right hand motor area tracts")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-RH_MHA.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -include {current_dir}/mrtrix3_files/rois/L-Ped.mif -seed_image {current_dir}/mrtrix3_files/rois/RHandM1.mif -include {current_dir}/mrtrix3_files/rois/L-Cap.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional{force}"
        run(cmd)
        filepaths.append(output_file)

    # Left Hand Motor Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/LHandM1.mif"):
        print("Making left hand motor area tracts")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-LH_MHA.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -include {current_dir}/mrtrix3_files/rois/R-Ped.mif -seed_image {current_dir}/mrtrix3_files/rois/LHandM1.mif -include {current_dir}/mrtrix3_files/rois/R-Cap.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional{force}"
        run(cmd)
        filepaths.append(output_file)

    return filepaths, defaults


def process_sha(defaults):
    """Generate SHA tracts."""
    filepaths = []
    force = ""
    if defaults is None:
        defaults = ["1", "45", "0.1"]
    else:
        force = " -force"

    # Right Hand Sensory Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/RHandS1.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-R-SHA.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {current_dir}/mrtrix3_files/rois/RHandS1.mif -include {current_dir}/mrtrix3_files/rois/L-Thal.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}{force}"
        run(cmd)
        filepaths.append(output_file)

    # Left Hand Sensory Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/LHandS1.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-L-SHA.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {current_dir}/mrtrix3_files/rois/LHandS1.mif -include {current_dir}/mrtrix3_files/rois/R-Thal.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}{force}"
        run(cmd)
        filepaths.append(output_file)

    return filepaths, defaults


def process_lip_motor(defaults):
    """Generate Lip Motor tracts."""
    filepaths = []
    force = ""
    if defaults is None:
        defaults = ["1", "45", "0.1"]
    else:
        force = " -force"

    # Lip Motor - Right side tract
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/LipM1.mif"):
        print("Making Right hand side tract of lips")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-R-Lip.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -include {current_dir}/mrtrix3_files/rois/L-Ped.mif -seed_image {current_dir}/mrtrix3_files/rois/LipM1.mif -include {current_dir}/mrtrix3_files/rois/L-Cap.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional{force}"
        run(cmd)
        filepaths.append(output_file)

        # Also create left side tract using same LipM1 ROI
        print("Making left hand side tract of lips")
        output_file_left = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-L-Lip.tck"
        cmd_left = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file_left} -include {current_dir}/mrtrix3_files/rois/R-Ped.mif -seed_image {current_dir}/mrtrix3_files/rois/LipM1.mif -include {current_dir}/mrtrix3_files/rois/R-Cap.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional{force}"
        run(cmd_left)
        filepaths.append(output_file_left)

    return filepaths, defaults


def process_optic_radiation(defaults):
    """Generate Optic Radiation tracts (OR_UNI) for both sides."""
    filepaths = []
    force = ""
    if defaults is None:
        defaults = ["1", "45", "0.05"]
    else:
        force = " -force"

    # Left Optic Radiation
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/L-LGN.mif"):
        print("Drawing on LEFT side")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-L-OR_UNI.tck"
        cmd = (
            f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} "
            f"-seed_image {current_dir}/mrtrix3_files/rois/L-LGN.mif "
            f"-include {current_dir}/mrtrix3_files/rois/L-latCalc.mif "
            f"-include {current_dir}/mrtrix3_files/rois/L-latVentr.mif "
            f"-step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional{force}"
        )
        run(cmd)
        filepaths.append(output_file)

    # Right Optic Radiation
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/R-LGN.mif"):
        print("Drawing on RIGHT side")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-R-OR_UNI.tck"
        cmd = (
            f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} "
            f"-seed_image {current_dir}/mrtrix3_files/rois/R-LGN.mif "
            f"-include {current_dir}/mrtrix3_files/rois/R-latCalc.mif "
            f"-include {current_dir}/mrtrix3_files/rois/R-latVentr.mif "
            f"-step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional{force}"
        )
        run(cmd)
        filepaths.append(output_file)
    return filepaths, defaults


def process_sensory_foot(defaults):
    """Generate sensory foot area tracts for both sides."""
    filepaths = []
    force = ""
    if defaults is None:
        defaults = ["1", "45", "0.1"]
    else:
        force = " -force"

    # Right Foot Sensory Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/RFootS1.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-R-SFO.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {current_dir}/mrtrix3_files/rois/RFootS1.mif -include {current_dir}/mrtrix3_files/rois/L-Thal.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}{force}"
        run(cmd)
        filepaths.append(output_file)

    # Left Foot Sensory Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/LFootS1.mif"):
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-L-SFO.tck"
        cmd = f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} -seed_image {current_dir}/mrtrix3_files/rois/LFootS1.mif -include {current_dir}/mrtrix3_files/rois/R-Thal.mif -step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}{force}"
        run(cmd)
        filepaths.append(output_file)

    return filepaths, defaults


def process_motor_foot(defaults):
    """Generate foot motor area tracts for both sides."""
    filepaths = []
    force = ""
    if defaults is None:
        defaults = ["1", "45", "0.1"]
    else:
        force = " -force"

    # Right Foot Motor Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/RFootM1.mif"):
        print("Making Right foot motor area tracts")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-RF_MFO.tck"
        cmd = (
            f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} "
            f"-seed_image {current_dir}/mrtrix3_files/rois/RFootM1.mif "
            f"-include {current_dir}/mrtrix3_files/rois/L-Ped.mif "
            f"-include {current_dir}/mrtrix3_files/rois/L-Cap.mif "
            f"-step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional{force}"
        )
        run(cmd)
        filepaths.append(output_file)

    # Left Foot Motor Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/LFootM1.mif"):
        print("Making left foot motor area tracts")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-LF_MFO.tck"
        cmd = (
            f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} "
            f"-seed_image {current_dir}/mrtrix3_files/rois/LFootM1.mif "
            f"-include {current_dir}/mrtrix3_files/rois/R-Ped.mif "
            f"-include {current_dir}/mrtrix3_files/rois/R-Cap.mif "
            f"-step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]} -seed_unidirectional{force}"
        )
        run(cmd)
        filepaths.append(output_file)

    return filepaths, defaults


def process_motor_face(defaults):
    """Generate face motor area tracts for both sides."""
    filepaths = []
    force = ""
    if defaults is None:
        defaults = ["1", "45", "0.05"]
    else:
        force = " -force"

    # Right Face Motor Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/RFaceM1.mif"):
        print("Making Right Face Motor Area")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-R_MFace.tck"
        cmd = (
            f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} "
            f"-seed_image {current_dir}/mrtrix3_files/rois/RFaceM1.mif "
            f"-include {current_dir}/mrtrix3_files/rois/L-Ped.mif "
            f"-include {current_dir}/mrtrix3_files/rois/L-Cap.mif "
            f"-step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}{force}"
        )
        run(cmd)
        filepaths.append(output_file)

    # Left Face Motor Area
    if os.path.isfile(f"{current_dir}/mrtrix3_files/rois/LFaceM1.mif"):
        print("Making left face motor area")
        output_file = f"{current_dir}/mrtrix3_files/tracts/mrtrix3-L_MFace.tck"
        cmd = (
            f"tckgen {current_dir}/mrtrix3_files/fods/wm_fod.mif {output_file} "
            f"-seed_image {current_dir}/mrtrix3_files/rois/LFaceM1.mif "
            f"-include {current_dir}/mrtrix3_files/rois/R-Ped.mif "
            f"-include {current_dir}/mrtrix3_files/rois/R-Cap.mif "
            f"-step {defaults[0]} -angle {defaults[1]} -cutoff {defaults[2]}{force}"
        )
        run(cmd)
        filepaths.append(output_file)

    return filepaths, defaults


def process_custom():
    finished = False
    print('---------------------------')
    print('Preparing for custom tracts')
    print()

    while finished is False:
        cmd = input('Please type the command you want to run:  ')
        run(cmd)
        a = cmd.split(' ')
        tract_output = [element for element in a if '.tck' in element]
        check = input('Would you like to run another command?:  ')
        if check == 'n':
            finished = True
    return tract_output, None