from Bash2PythonFuncs import run, convert_tracts
from roi_tck import roi_list, tck_list
from tkinter import ttk
import subprocess
import tkinter as tk

def gentck(pt_dir, debug):

    gen_tracks = []
    processed_path = f"{pt_dir}Processed"

    while True:

        print()
        for i in roi_list:
            print(i)
        print()
        choice = input(
            'Do you need to draw ROIs? If so, please save in the 9_ROI folder in the patient Processed directory with one of the filenames above (y/n). ')
        print('Please save the ROI under the following names for the script to be able to find them')

        if choice.lower() == 'y':
            subprocess.run('echo -e "Opening mrview"', shell=True)
            message = "Step 8: Draw ROIs"
            message = "\033[32m" + message + "\033[0m"
            command = "echo {}".format(message)
            subprocess.run(command, shell=True)

            # step size should be 0.5xvoxelsize (currently set to 1)
            fa = f"{processed_path}/7_tensor/fa.mif"
            ev = f"{processed_path}/7_tensor/ev.mif"
            dwi_tensor = f"{pt_dir}7_tensor/dwi_tensor.mif"

            view_cmd = f"mrview -mode 2 -load {fa} -interpolation 0 -load {ev} -interpolation 0 -comments 0"
            run(view_cmd)

            break
        elif choice.lower() == 'n':
            print('Continue with analysis using ROIs already generated')
            break
        else:
            message = "Invalid response"
            message = "\033[31m" + message + "\033[0m"
            command = "echo {}".format(message)
            subprocess.run(command, shell=True)

    print()
    print()
    message = "Generating tracks, please fill out the form."
    print(message)

    wm_fod = f"{processed_path}/8_msmt/wm_fod.mif"
    fa = f"{processed_path}/7_tensor/fa.mif"
    ev = f"{processed_path}/7_tensor/ev.mif"
    dwi_tensor = f"{pt_dir}7_tensor/dwi_tensor.mif"

    if debug == 'debug':
        view_cmd = f"mrview -mode 2 -load {fa} -interpolation 0 -load {ev} -interpolation 0 -comments 0"
        run(view_cmd)

    cmd_1 = None
    cmd_2 = None
    cmd_3 = None
    cmd_4 = None
    cmd_5 = None
    cmd_6 = None
    cmd_7 = None
    cmd_8 = None
    cmd_9 = None
    exclude_cmd = None
    stream_cmd = None
    view_cmd = None
    tract_select = None

    def run_command():
        nonlocal cmd_1
        nonlocal cmd_2
        nonlocal cmd_3
        nonlocal cmd_4
        nonlocal cmd_5
        nonlocal cmd_6
        nonlocal cmd_7
        nonlocal cmd_8
        nonlocal cmd_9
        nonlocal exclude_cmd
        nonlocal stream_cmd
        nonlocal view_cmd
        nonlocal tract_select

        roi_path = f"{processed_path}/9_ROI/"
        fa = f"{processed_path}/7_tensor/fa.mif"
        ev = f"{processed_path}/7_tensor/ev.mif"
        tract = f"{processed_path}/10_tract/{tract_combo.get()}"
        tract_select = tract_combo.get()
        seed_image = f"{roi_path}{seed_image_combo.get()}"
        include_1 = include_1_combo.get()
        include_2 = include_2_combo.get()
        step = str(step_var.get())
        angle = str(angle_var.get())
        cutoff = str(cutoff_var.get())
        seed = f"{seed_combo.get()}"
        exclude_1 = exclude_1_combo.get()
        exclude_2 = exclude_2_combo.get()
        streamlines = str(streamlines_var.get())
        map = map_combo.get().lower()

        cmd_1 = f"tckgen {wm_fod} {tract} "
        cmd_2 = f"-seed_image {seed_image} "

        if f"{include_1}" != '':
            cmd_3 = f"-include {roi_path}{include_1} "
        else:
            cmd_3 = ''
        if f"{include_2}" != '':
            cmd_3 = f"-include {roi_path}{include_2} "
        else:
            cmd_4 = ''
        if f"{step}" != '':
            cmd_5 = f"-step {step} "
        else:
            cmd_5 = ''
        if f"{angle}" != '':
            cmd_6 = f"-angle {angle} "
        else:
            cmd_6 = ''
        if f"{cutoff}" != '':
            cmd_7 = f"-cutoff {cutoff} "
        else:
            cmd_7 = ''
        if f"{seed}" != '':
            cmd_8 = f"seed_{seed.lower()}"
        else:
            cmd_8 = ''
        if f"{exclude_1}" != '':
            cmd_9 = f"-exclude {roi_path}{exclude_1}"
        else:
            cmd_9 = ''
        if f"{exclude_2}" != '':
            cmd_10 = f"-exclude {roi_path}{exclude_2}"
        else:
            cmd_10 = ''
        if f"{streamlines}" != '':
            cmd_11 = f"-number {streamlines}"
        else:
            cmd_11 = ''
        if cmd_11 != '':
            stream_cmd = f"tckedit {tract} {tract.replace('.', f'_{streamlines}.')} {cmd_11}"
        else:
            stream_cmd = ''
        """Can add the diffusion as well just for display"""
        view_cmd = f"mrview -mode 2 -load {eval(map)} -interpolation 0 -tractography.load {tract} -comments 0"

        gen_tracks.append(f"{tract.replace('.', f'_{streamlines}.')}")
        root.destroy()

    roi_list.append('None')
    root = tk.Tk()
    root.title("Select 'None' or type N/A if not included")

    tract_label = ttk.Label(root, text="Tract:")
    tract_values = tck_list
    tract_combo = ttk.Combobox(root, values=tract_values)

    seed_image_label = ttk.Label(root, text="Seed Image:")
    seed_image_values = roi_list
    seed_image_combo = ttk.Combobox(root, values=seed_image_values)

    include_1_label = ttk.Label(root, text="Include 1:")
    include_1_values = roi_list
    include_1_combo = ttk.Combobox(root, values=include_1_values)

    include_2_label = ttk.Label(root, text="Include 2:")
    include_2_values = roi_list
    include_2_combo = ttk.Combobox(root, values=include_2_values)

    step_label = ttk.Label(root, text="Step:")
    step_var = tk.StringVar()  # Use tk.StringVar()
    step_entry = ttk.Entry(root, textvariable=step_var)

    angle_label = ttk.Label(root, text="Angle:")
    angle_var = tk.StringVar()  # Use tk.StringVar()
    angle_entry = ttk.Entry(root, textvariable=angle_var)

    cutoff_label = ttk.Label(root, text="Cutoff:")
    cutoff_var = tk.StringVar()
    cutoff_entry = ttk.Entry(root, textvariable=cutoff_var)

    seed_label = ttk.Label(root, text="Seed Direction:")
    seed_values = ['Unidirectional', 'None']
    seed_combo = ttk.Combobox(root, values=seed_values)

    exclude_1_label = ttk.Label(root, text="Exclude:")
    exclude_1_values = roi_list
    exclude_1_combo = ttk.Combobox(root, values=exclude_1_values)

    exclude_2_label = ttk.Label(root, text="Exclude:")
    exclude_2_values = roi_list
    exclude_2_combo = ttk.Combobox(root, values=exclude_2_values)

    streamlines_label = ttk.Label(root, text="Streamlines:")
    streamlines_var = tk.StringVar()  # Use tk.StringVar()
    streamlines_entry = ttk.Entry(root, textvariable=streamlines_var)

    map_label = ttk.Label(root, text="FA or EV map:")
    map_values = ['FA', 'EV']
    map_combo = ttk.Combobox(root, values=map_values)

    run_button = ttk.Button(root, text="Run Command", command=run_command)

    # Place labels and input fields in the window
    tract_label.grid(row=0, column=0)
    tract_combo.grid(row=0, column=1)
    seed_image_label.grid(row=1, column=0)
    seed_image_combo.grid(row=1, column=1)
    include_1_label.grid(row=2, column=0)
    include_1_combo.grid(row=2, column=1)
    include_2_label.grid(row=3, column=0)
    include_2_combo.grid(row=3, column=1)
    step_label.grid(row=4, column=0)
    step_entry.grid(row=4, column=1)
    angle_label.grid(row=5, column=0)
    angle_entry.grid(row=5, column=1)
    cutoff_label.grid(row=6, column=0)
    cutoff_entry.grid(row=6, column=1)
    seed_label.grid(row=7, column=0)
    seed_combo.grid(row=7, column=1)
    exclude_1_label.grid(row=8, column=0)
    exclude_1_combo.grid(row=8, column=1)
    exclude_2_label.grid(row=9, column=0)
    exclude_2_combo.grid(row=9, column=1)
    streamlines_label.grid(row=10, column=0)
    streamlines_entry.grid(row=10, column=1)
    map_label.grid(row=11, column=0)
    map_combo.grid(row=11, column=1)
    run_button.grid(row=12, columnspan=2)

    root.mainloop()

    main_cmd = ''

    print(cmd_3)

    for i in range(1, 9):
        if i == 1:
            main_cmd = eval(f"cmd_{i}")
        else:
            if eval(f"cmd_{i}") != '':
                main_cmd = main_cmd + eval(f"cmd_{i}")

    print(main_cmd)

    run(main_cmd)

    if cmd_9 != '':

        run(exclude_cmd)

    if stream_cmd != '':

        run(stream_cmd)

    if debug == 'debug':

        run(view_cmd)

    convert_tracts(pt_dir, debug)

    return tract_select


