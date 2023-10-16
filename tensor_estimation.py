from Bash2PythonFuncs import run
import os

def tensor_estimation(pt_dir, DWI_shell, debug):
        
        pt_dir = f"{pt_dir}Processed/"
        mask_final = f"{pt_dir}6_mask/mask_final.nii.gz"
        mask_mif = f"{pt_dir}6_mask/mask_final.mif"
        mr_conv_3_cmd = f"mrconvert {mask_final} {mask_mif}"
        run(mr_conv_3_cmd)

        response_wm = f"{pt_dir}5_response/response_wm.txt"
        response_gm = f"{pt_dir}5_response/response_gm.txt"
        response_csf = f"{pt_dir}5_response/response_csf.txt"
        response_voxels = f"{pt_dir}5_response/response_voxels.mif"
        

        """TENSOR ESTIMATION"""

        upsample_out = f"{pt_dir}4_eddy/dwi_eddy_upsamp.mif"
        dwi_tensor = f"{pt_dir}7_tensor/dwi_tensor.mif"
        fa_tensor = f"{pt_dir}7_tensor/fa.mif"
        ev_tensor = f"{pt_dir}7_tensor/ev.mif"
        fa_nii = f"{pt_dir}7_tensor/fa.nii.gz"

        if not os.path.exists(dwi_tensor):
            print("Step 7: Tensor estimation")
            dwi2tensor_cmd = f"dwi2tensor {upsample_out} {dwi_tensor} -mask {mask_mif}"
            tens2metr_cmd = f"tensor2metric -mask {mask_mif} -fa {fa_tensor} -vector {ev_tensor} {dwi_tensor}"
            conv_fa = f"mrconvert {fa_tensor} {fa_nii}"
            run(dwi2tensor_cmd)
            run(tens2metr_cmd)
            run(conv_fa)
            
            
        if debug == 'debug':
            print("DEBUG STEP: Check the FA and EV maps")
            mrview_tensor = f"mrview -load {fa_tensor} -interpolation 0 -load {ev_tensor} -interpolation 0 -odf.load_tensor {dwi_tensor}"
            run(mrview_tensor)


        wm_fod = f"{pt_dir}8_msmt/wm_fod.mif"
        wm_fod_int = f"{pt_dir}8_msmt/wm_fod_int.mif"
        csf_fod = f"{pt_dir}8_msmt/csf_fod.mif"
        gm_fod = f"{pt_dir}8_msmt/gm_fod.mif"
        tissue_vf = f"{pt_dir}8_msmt/tissue_vf.mif"

        # Perform multi shell multi tissue constrained spherical deconvolution
        if DWI_shell.lower() == 'n':
            print("Single shell data")
            dwi2fod_cmd = f"dwi2fod msmt_csd -mask {mask_mif} {upsample_out} {response_wm} {wm_fod} {response_csf} {csf_fod} "
            run(dwi2fod_cmd)
        elif DWI_shell.lower() == 'y':
            print("Multi-shell data")
            dwi2fod_cmd = f"dwi2fod msmt_csd -mask {mask_mif} {upsample_out} {response_wm} {wm_fod} {response_gm} {gm_fod} {response_csf} {csf_fod} "
            run(dwi2fod_cmd)
            mrconv_cmd = f"mrconvert {wm_fod} {wm_fod_int} -coord 3 0"
            run(mrconv_cmd)
            mrcat_cmd = f"mrcat {csf_fod} {gm_fod} {wm_fod_int} {tissue_vf}"
            run(mrcat_cmd)
            if debug == 'debug':
                mrview_cmd = f"mrview -mode 2 -load {tissue_vf} -interpolation 0"
                run(mrview_cmd)

