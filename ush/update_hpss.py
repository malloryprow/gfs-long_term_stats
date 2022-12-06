import os
import subprocess

long_term_dir = ('/lfs/h2/emc/vpppg/save/emc.vpppg/verification/'
                 +'global/long_term_stats/long_term_archive/long_term')
os.chdir(long_term_dir)

hpss_dir = '/NCEPDEV/emc-global/5year/emc.verif/global/archive/long_term_stats'
hpss_tar = os.path.join(hpss_dir, 'long_term')

mean_dir_list = ['annual_means', 'monthly_means']
for mean_dir in mean_dir_list:
    model_dir_list = os.listdir(os.path.join(os.getcwd(), mean_dir))
    for model_dir in model_dir_list:
        hour_dir_list = os.listdir(os.path.join(os.getcwd(), mean_dir,
                                                model_dir))
        for hour_dir in hour_dir_list:
            mean_model_hour_dir = os.path.join(os.getcwd(), mean_dir,
                                               model_dir, hour_dir)
            hpss_mean_model_hour_tar = (hpss_tar+'_'+mean_dir+'_'
                                        +model_dir+'_'+hour_dir+'.tar')
            print(mean_model_hour_dir)
            print(hpss_mean_model_hour_tar)
            ps = subprocess.Popen('htar -cvf '+hpss_mean_model_hour_tar+' '
                                  +mean_model_hour_dir+'/*',
                                  shell=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, encoding='UTF-8')
            print(ps.communicate()[0])
