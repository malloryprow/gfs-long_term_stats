import os
import glob

working_dir = os.environ['working_dir']
webhost = os.environ['webhost']
webhostid = os.environ['webhostid']
webdir = os.environ['webdir']
YYYYmm = os.environ['YYYYmm']

# Copy monthly mean long term plots
os.system('scp '+os.path.join(working_dir,'plots_monthly_means_*', '*')+' '
          +webhostid+'@'+webhost+':'+webdir+'/monthly_long_term/images/.')

# Copy annual mean long term plots
if len(glob.glob(os.path.join(working_dir,'plots_annual_means_*', '*'))) != 0:
    os.system('scp '+os.path.join(working_dir,'plots_annual_means_*', '*')+' '
              +webhostid+'@'+webhost+':'+webdir+'/annual_long_term/images/.')

# Copy monthly 500 hPa HGT NHX plots to archive
ops_webdir = ('/home/people/emc/www/htdocs/users/verification/'
              +'global/gfs/ops/grid2grid_all_models/acc_archive/images')
hr_list = ['00', '12']
fhr_list = ['00', '24', '48', '72', '96', '120', '144',
            '168', '192', '216', '240', 'mean']
for hr in hr_list:
    all_models_hr_output_dir = os.path.join(
        working_dir, 'verif_global_monthly_mean_all_models_'+hr+'Z'
    )
    if os.path.exists(all_models_hr_output_dir):
        all_models_hr_HGT_NHX_output_dir = glob.glob(
            os.path.join(all_models_hr_output_dir, 'tmp',
                         'verif_global.*', 'grid2grid_step2', 'metplus_output',
                         'plot_by_VALID', 'make_plots', 'SAL1L2_HGT_NHX',
                         'grid2grid', 'anom', 'images')
        )[0]
        for fhr in fhr_list:
            all_models_hr_HGT_NHX_fhr_img = os.path.join(
                all_models_hr_HGT_NHX_output_dir,
                'acc_valid'+hr+'Z_HGT_P500_fhr'+fhr+'_G002NHX.png' 
            )
            all_models_hr_HGT_NHX_fhr_archive_img = os.path.join(
                ops_webdir,
                'acc_valid'+hr+'Z_HGT_P500_fhr'+fhr+'_G002NHX_'+YYYYmm+'.png'
            )
            if os.path.exists(all_models_hr_HGT_NHX_fhr_img):
                os.system('scp '+all_models_hr_HGT_NHX_fhr_img+' '
                          +webhostid+'@'+webhost+':'
                          +all_models_hr_HGT_NHX_fhr_archive_img)
