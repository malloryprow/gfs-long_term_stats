import os
import datetime
import dateutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
#pd.plotting.deregister_matplotlib_converters()
pd.plotting.register_matplotlib_converters()
import plot_title as plot_title
import plot_util as plot_util

start_YYYY = '1989'
end_YYYY = os.environ['YYYY']
working_dir = os.environ['working_dir']
#end_YYYY = '2020'
#working_dir = ('/lfs/h2/emc/stmp/'+os.environ['USER']
#               +'/long_term_stats_update/long_term_plots')

# Set long term stats directory
long_term_stats_dir = ('/lfs/h2/emc/vpppg/save/emc.vpppg/verification'
                       +'/global/long_term_stats')
long_term_archive = os.path.join(long_term_stats_dir, 'long_term', 'annual_means')

# Set up useful forecast days output directory
useful_fcst_days_output_dir = os.path.join(
    working_dir, 'plots_annual_means_useful_fcst_days'
)
if not os.path.exists(useful_fcst_days_output_dir):
    os.makedirs(useful_fcst_days_output_dir)

# Set up information
model_list = ['gfs']
hour_list = ['00']
vx_mask_list = ['NHX']
level_list = ['P500']
acc_threshs = np.array([0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95])
cz_start_YYYY = 1996
vsdb_start_YYYY = 2008
metplus_start_YYYY = 2021
all_YYYY_dt_list = list(
    dateutil.rrule.rrule(
        dateutil.rrule.YEARLY,
        dtstart=dateutil.parser.parse(start_YYYY+'0101T000000'),
        until=dateutil.parser.parse(end_YYYY+'0101T000000')
    )
)
all_YYYY_list = []
for YYYY_dt in all_YYYY_dt_list:
    all_YYYY_list.append(f"{YYYY_dt:%Y}")

# Plot Settings
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.titlepad'] = 10
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['axes.labelpad'] = 10
plt.rcParams['axes.formatter.useoffset'] = False
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['xtick.major.pad'] = 10
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['ytick.major.pad'] = 10
plt.rcParams['figure.subplot.left'] = 0.1
plt.rcParams['figure.subplot.right'] = 0.95
plt.rcParams['figure.subplot.top'] = 0.85
plt.rcParams['figure.subplot.bottom'] = 0.15
plt.rcParams['legend.handletextpad'] = 0.25
plt.rcParams['legend.handlelength'] = 1.25
plt.rcParams['legend.borderaxespad'] = 0
plt.rcParams['legend.columnspacing'] = 1.0
plt.rcParams['legend.frameon'] = False
x_figsize, y_figsize = 14, 7
legend_bbox_x, legend_bbox_y = 0.5, 0.05
legend_fontsize = 13
legend_loc = 'center'
legend_ncol = 8
title_loc = 'center'
noaa_logo_path, nws_logo_path = plot_util.get_logo_paths()
noaa_logo_img_array = matplotlib.image.imread(noaa_logo_path)
noaa_logo_xpixel_loc = x_figsize*plt.rcParams['figure.dpi']*0.1
noaa_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.865
noaa_logo_alpha = 0.5
nws_logo_img_array = matplotlib.image.imread(nws_logo_path)
nws_logo_xpixel_loc = x_figsize*plt.rcParams['figure.dpi']*0.9
nws_logo_ypixel_loc = y_figsize*plt.rcParams['figure.dpi']*0.865
nws_logo_alpha = 0.5
models_plot_colors_dict = {
    'gfs': '#000000',
    'ecm': '#FB2020',
    'cmc': '#00DC00',
    'fno': '#1E3CFF',
    'ukm': '#E69F00'
}
acc_threshs_plot_colors_dict = {
    '0.6': '#000000',
    '0.65': '#FB2020',
    '0.7': '#00DC00',
    '0.75': '#1E3CFF',
    '0.8': '#E69F00',
    '0.85': '#00C8C8',
    '0.9': '#A0E632',
    '0.95': '#A000C8',
}

# Make plots
for hour in hour_list:
    for level in level_list:
        caplan_zhu_level = level.replace('P', '')+'hpa'
        for vx_mask in vx_mask_list:
            for model in model_list:
                long_term_model_hour_dir = os.path.join(long_term_archive,
                                                        model, hour+'Z')        
                # Read annual mean files and put in dataframe
                caplan_zhu_vx_mask = vx_mask[0:2]  
                caplan_zhu_file_name = os.path.join(
                    long_term_model_hour_dir,
                    'caplan_zhu_HGTACWave1-20_'
                    +caplan_zhu_level+'_'
                    +caplan_zhu_vx_mask+'.txt'
                )
                vsdb_file_name = os.path.join(
                    long_term_model_hour_dir,
                    'vsdb_AC_HGT_'+level+'_G2'+vx_mask+'.txt'
                )
                metplus_file_name = os.path.join(
                    long_term_model_hour_dir,
                    'metplus_ACC_HGT_'+level+'_'+vx_mask+'.txt'
                )
                caplan_zhu_df = pd.read_table(
                    caplan_zhu_file_name, delimiter=' ', dtype='str',
                    skipinitialspace=True
                )
                vsdb_df = pd.read_table(
                    vsdb_file_name, delimiter=' ', dtype='str',
                    skipinitialspace=True
                )
                metplus_df = pd.read_table(
                    metplus_file_name, delimiter=' ', dtype='str',
                    skipinitialspace=True
                )
                # Merge dates
                if model == 'ukm':
                    cz_start_YYYY = 1997
                elif model == 'fno':
                    cz_start_YYYY = 1998
                elif model == 'cfsr':
                    cz_start_YYYY = 9999
                else:
                    cz_start_YYYY = 1996
                vsdb_start_YYYY = 2008
                metplus_start_YYYY = 2021
                # Merge dataframes
                merged_df = pd.DataFrame(index=all_YYYY_list,
                                         columns=vsdb_df.columns)
                for YYYY in all_YYYY_list:
                    if int(YYYY) >= cz_start_YYYY \
                            and int(YYYY) < vsdb_start_YYYY:
                        YYYY_df = caplan_zhu_df
                        df_name = 'CZ'
                    elif int(YYYY) >= vsdb_start_YYYY \
                            and int(YYYY) < metplus_start_YYYY:
                        YYYY_df = vsdb_df
                        df_name = 'VSDB'
                    elif int(YYYY) >= metplus_start_YYYY:
                        YYYY_df = metplus_df
                        df_name = 'MP'
                    else:
                        continue
                    YYYY_line = YYYY_df.loc[
                        (YYYY_df['YEAR'] == YYYY)
                    ]
                    if len(YYYY_line) == 0:
                         merged_df.loc[YYYY] = (
                             [df_name, YYYY] + (17*[np.nan])
                         )
                    else:
                        merged_df.loc[YYYY] = YYYY_line.values
                # Get days at which forecast ACC exceeding a certain value
                acc_treshs_days_df = pd.DataFrame(index=all_YYYY_list,
                                                  columns=acc_threshs)
                for YYYY in all_YYYY_list:
                    masked_YYYY_fcst_days_values = np.ma.masked_invalid(
                        np.array(merged_df.loc[YYYY].values[2:],
                        dtype='float')
                    )
                    masked_fcst_days = np.ma.array(
                        np.arange(0,len(merged_df.loc[YYYY].values[2:]),1),
                        mask=np.ma.getmaskarray(
                            masked_YYYY_fcst_days_values
                        )
                    )
                    if len(masked_YYYY_fcst_days_values) \
                            - np.ma.count_masked(
                                masked_YYYY_fcst_days_values
                            ) >= 6:
                        compressed_YYYY_fcst_days_values = (
                            masked_YYYY_fcst_days_values.compressed()
                        )
                        compressed_fcst_days = masked_fcst_days.compressed()
                        for acc_thresh in acc_threshs:
                            acc_thresh_day = np.interp(
                                acc_thresh,
                                compressed_YYYY_fcst_days_values[::-1],
                                compressed_fcst_days[::-1],
                                left=np.nan, right=np.nan
                            )
                            acc_treshs_days_df.loc[YYYY, acc_thresh] = (
                                acc_thresh_day
                            )
                if model == 'gfs' and level == 'P500' \
                        and vx_mask == 'NHX' and hour == '00': 
                     # Read in excel spreadsheet for 0.6 threshold
                     # and fill NaNs
                     excel_file_name = os.path.join(
                         long_term_model_hour_dir,
                         'excel_usefulfcstdays_ACC06_HGT_'
                         +level+'_'+vx_mask+'.txt'
                     )
                     excel_df = pd.read_table(
                         excel_file_name, delimiter=' ',
                         skipinitialspace=True
                     )
                     #print(excel_df['DAY'].values - acc_treshs_days_df[0.60].values)
                     for year in acc_treshs_days_df.index:
                         if np.isnan(acc_treshs_days_df.loc[year,0.6]):
                             if int(year) in excel_df['YEAR'].values:
                                 year_excel_df = excel_df.loc[
                                     (excel_df['YEAR'] == int(year))
                                 ]
                                 acc_treshs_days_df.loc[year,0.6] = (
                                     year_excel_df['DAY'].values[0]
                                 )
                # Make bar graph for 0.6 threshold
                acc06_days = acc_treshs_days_df.loc[:,0.6].values
                years = np.asarray(all_YYYY_list, dtype=float)
                fig, ax = plt.subplots(1,1,figsize=(x_figsize, y_figsize))
                ax.grid(True)
                ax.set_xlabel('Year')
                ax.set_xlim([years[0], years[-1]])
                ax.set_xticks(years[::2])
                ax.set_ylabel('Forecast Day')
                ax.set_yticks(range(0,11,1))
                ax.set_ylim([0, 10])
                ax.bar(years, acc06_days)
                var_info_title = plot_title.get_var_info_title(
                    'HGT', level
                )
                vx_mask_title = plot_title.get_vx_mask_title(vx_mask)
                ax.set_title('Day At Which GFS Forecast Loses Useful Skill '
                             +'(Anomaly Correlation Coefficient=0.6)\n'
                             +var_info_title+', '+vx_mask_title+'\n'
                             +'Annual Means')
                fig.figimage(noaa_logo_img_array,
                             noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
                             zorder=1, alpha=noaa_logo_alpha)
                fig.figimage(nws_logo_img_array,
                             nws_logo_xpixel_loc, nws_logo_ypixel_loc,
                             zorder=1, alpha=nws_logo_alpha)
                savefig_name = os.path.join(useful_fcst_days_output_dir,
                                            'annual_useful_fcst_days_acc06_'
                                            +model+'_valid'+hour+'Z_HGT_'
                                            +level+'_G002'+vx_mask+'.png')
                print(savefig_name)
                plt.savefig(savefig_name)
                plt.close()

