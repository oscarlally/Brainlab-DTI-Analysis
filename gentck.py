import os
import subprocess
from Bash2PythonFuncs import run, find_dir, convert_tracts


def gentck(pt_dir, debug):

    GREEN='\e[0;32m'
    RED='\e[0;31m'
    NC='\e[0m'

    processed_path = f"{pt_dir}Processed"
    roi_list = ['AF_L.mif',
                'AF_R.mif',
                'SLF_L.mif',
                'SLF_R.mif',
                'BROCA_L.mif',
                'BROCA_R.mif',
                'AF_exclude.mif',
                'RHandM1.mif',
                'LHandM1.mif',
                'L-ped.mif',
                'R-ped.mif',
                'RhandS1.mif',
                'LhandS1.mif',
                'R_Thal.mif',
                'L_Thal.mif',
                'L-LGN.mif',
                'R-LGN.mif',
                'L-latCalc.mif',
                'R-latCalc.mif',
                'L-latVentr',
                'R-latVentr',
                'OR_exclude.mif']


    while True:
    
        choice = input('Do you need to draw ROIs? If so, please save in the 10_ROI folder in the patient processed directory (y/n). ')
        print('Please save the ROI under the following names for the script to be able to find them')
        for i in roi_list:
            print(i)

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
            

    
    message = "Generating tracks, see choices below"
    message = "\033[32m" + message + "\033[0m"
    command = "echo {}".format(message)
    subprocess.run(command, shell=True)
    

    print('(1) AF: To generate Arcuate Fasciculus tracts requires Broca SLF and AF ROIs ')
    print('(2) CorticoSpinal Tract (CST) MHA: Motor hand area (seed) with cerebral peduncles waypoint requires RhandM1 or LhandM1')
    print('(3) CST SHA: Sensory hand area (seed) to thalamus requires ShandS1 or RhandS1')
    print('(4) CST Motor lip area (seed) with cerebral peduncles waypoint')
    print('(5) CST Sensory lip area (seed) to the thalamus')
    print('(6) CST Sensory motor foot area (seed) to the cerebral peduncles waypoint')
    print('(7) Optic Radiation: Uses LGN, Lat Ventr and Lat Calc as seeds/waypoints')
    print('(8) OTHER: Other tract not listed here')
    print('(s) SKIP')
    
    
    
    fa = f"{processed_path}/7_tensor/fa.mif"
    wm_fod = f"{processed_path}/8_msmt/wm_fod.mif"
    af_tck = f"{processed_path}/9_tract/mrtrix3-AF.tck"
    af_tck_r = f"{processed_path}/9_tract/mrtrix3-AF_R.tck"
    af_tck_ex = f"{processed_path}/9_tract/mrtrix3-AF-EX.tck"
    af_tck_ex_r = f"{processed_path}/9_tract/mrtrix3-AF-EX_R.tck"
    mha_r_tck = f"{processed_path}/9_tract/mrtrix3-RH_MHA.tck"
    mha_l_tck = f"{processed_path}/9_tract/mrtrix3-LH_MHA.tck"
    af_l = f"{processed_path}/10_ROI/AF_L.mif"
    af_r = f"{processed_path}/10_ROI/AF_R.mif"
    slf_l = f"{processed_path}/10_ROI/SLF_L.mif"
    slf_r = f"{processed_path}/10_ROI/SLF_R.mif"
    broca_l = f"{processed_path}/10_ROI/BROCA_L.mif"
    broca_r = f"{processed_path}/10_ROI/BROCA_R.mif"
    af_exclude = f"{processed_path}/10_ROI/AF_exclude.mif"
    rhm1 = f"{processed_path}/10_ROI/RHandM1.mif"
    lhm1 = f"{processed_path}/10_ROI/LHandM1.mif"
    lped = f"{processed_path}/10_ROI/L-ped.mif"
    rped = f"{processed_path}/10_ROI/R-ped.mif"
    rhs1 = f"{processed_path}/10_ROI/RhandS1.mif"
    rsha_tck = f"{processed_path}/9_tract/mrtrix3-R-SHA.tck"
    lhs1 = f"{processed_path}/10_ROI/LhandS1.mif"
    lsha_tck = f"{processed_path}/9_tract/mrtrix3-L-SHA.tck"
    r_thal = f"{processed_path}/10_ROI/R_Thal.mif"
    l_thal = f"{processed_path}/10_ROI/L_Thal.mif"
    llgn = f"{processed_path}/10_ROI/L-LGN.mif"
    rlgn = f"{processed_path}/10_ROI/R-LGN.mif"
    llc = f"{processed_path}/10_ROI/L-latCalc.mif"
    rlc = f"{processed_path}/10_ROI/R-latCalc.mif"
    llv = f"{processed_path}/10_ROI/L-latVentr.mif"
    rlv = f"{processed_path}/10_ROI/R-latVentr.mif"
    OR_exclude = f"{processed_path}/10_ROI/OR_exclude.mif"
    luni_tck = f"{processed_path}/9_tract/mrtrix3-L-LGN_EX_UNI.tck"
    runi_tck = f"{processed_path}/9_tract/mrtrix3-R-LGN_EX_UNI.tck"
    
    

    tract_choice = input("Which tracts do you want to generate? Please type in the number or s for skip. ")
    
    gen_tracks = []
    
    if tract_choice == '1':
    
        message = "You have chosen AF"
        message = "\033[35m" + message + "\033[0m"
        command = "echo {}".format(message)
        subprocess.run(command, shell=True)
        
        if os.path.isfile(f"{processed_path}/10_ROI/AF_L.mif"):
            run("tckgen {wm_fod} {af_tck} -seed_image {af_l} -include {slf_l} -include {broca_l} -step 1.75 -angle 45 -cutoff 0.05")
            run("tckedit {af_tck} {af_tck_ex} -exclude {af_exclude}")
            run("mrview -mode 2 -load {fa} -interpolation 0 -tractography.load {af_tck} -tractography.load {af_tck_ex} -comments 0")
            gen_tracks.append(af_tck, af_tck_ex)
        if os.path.isfile(f"{processed_path}/10_ROI/AF_R.mif"):
            run("tckgen {wm_fod} {af_tck_r} -seed_image {af_r} -include {slf_r} -include {broca_r} -step 1.75 -angle 45 -cutoff 0.05")
            run("tckedit {af_tck} {af_tck_ex_r} -exclude {af_exclude}")
            run("mrview -mode 2 -load {fa} -interpolation 0 -tractography.load 9_tract/mrtrix3")
            gen_tracks.append(af_tck, af_tck_ex_r)



    elif tract_choice == '2':
    
        message = "You have chosen MHA"
        message = "\033[35m" + message + "\033[0m"
        command = "echo {}".format(message)
        subprocess.run(command, shell=True)
        
        if os.path.isfile(f"{processed_path}/10_ROI/RHandM1.mif"):
            print("Making Right hand motor area tracts")
            run("tckgen {wm_fod} {mha_r_tck} -seed_image {rhm1} -include {lped} -step 1.75 -angle 45 -cutoff 0.05 -seed_unidirectional -force")
            run("mrview -mode 2 -load {fa} -interpolation 0 -tractography.load {mha_r_tck}")
            gen_tracks.append(mha_r_tck)

        if os.path.isfile(f"{processed_path}/10_ROI/LHandM1.mif"):
            print("Making left hand motor area tracts")
            run("tckgen {wm_fod} {mha_l_tck} -seed_image {lhm_1} -include {rped} -step 1.75 -angle 45 -cutoff 0.05 -seed_unidirectional -force")
            run("mrview -mode 2 -load {fa} -interpolation 0 -tractography.load 9_tract/{mha_l_tck}")
            gen_tracks.append(mha_l_tck)
            
            
    elif tract_choice =='3':
        
        message = "You have chosen Sensory hand area"
        message = "\033[35m" + message + "\033[0m"
        command = "echo {}".format(message)
        subprocess.run(command, shell=True)

        print("If RhandS1 or LhandS1 exist, making tracks will be attempted")

        if os.path.isfile(rhs1):
            run("tckgen {wm_fod} {rsha_tck} -seed_image {rhs1} -include {l_thal} -step 1.75 -angle 45 -cutoff 0.05")
            run("mrview -mode 2 -load {fa} -interpolation 0 -tractography.load {rsha_tck} -comments 0")
            gen_tracks.append(rsha_tck)

        if os.path.isfile("10_ROI/LhandS1.mif"):
            run("tckgen {wm_fod} {lsha_tck} -seed_image {lhs1} -include {r_thal} -step 1.75 -angle 45 -cutoff 0.05")
            run("mrview -mode 2 -load {fa} -interpolation 0 -tractography.load {lsha_tck} -comments 0")
            gen_tracks.append(lsha_tck)


    elif tract_choice == '7':

        message = "You have chosen optic radiation"
        message = "\033[35m" + message + "\033[0m"
        command = "echo {}".format(message)
        subprocess.run(command, shell=True)
        
        print("If R_LGN or L-LGN exist, making tracts will be attempted")
        
        if os.path.isfile(llgn):
            print("Drawing on LEFT side")
            run("tckgen {wm_fod} {llgn} -seed_image {llgn} -include {llc} -include {llv} -step 1.75 -angle 45 -cutoff 0.05")
            run("tckedit {luni_tck} -exclude {OR_exclude} -seed_unidirectional")
            run("mrview -mode 2 -load {fa} -interpolation 0 -tractography.load {llgn} -comments 0")
            gen_tracks.append(luni_tck)

        if os.path.isfile(rlgn):
            run("tckgen {wm_fod} {rlgn} -seed_image {rlgn} -include {rlc} -include {rlv} -step 1.75 -angle 45 -cutoff 0.05")
            run("tckedit {runi_tck} -exclude {OR_exclude} -seed_unidirectional")
            run("mrview -mode 2 -load {fa} -interpolation 0 -tractography.load {rlgn} -comments 0")
            gen_tracks.append(runi_tck)


    elif tract_choice.lower() == 's':
        print("Process skipped")
        
        
    else:
        message = "Invalid response, exiting code"
        message = "\033[31m" + message + "\033[0m"
        command = "echo {}".format(message)
        subprocess.run(command, shell=True)
      
    convert_tracts(pt_dir, debug)
        
    return gen_tracks



    
    
    
