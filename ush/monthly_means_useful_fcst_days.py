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

start_YYYYmm = os.environ['start_YYYYmm']
end_YYYYmm = os.environ['end_YYYYmm']
working_dir = os.environ['working_dir']
#start_YYYYmm = '199601'
#end_YYYYmm = '202105'
#working_dir = ('/gpfs/dell2/'+os.environ['USER']
#               +'/long_term_stats_update_2021'+end_YYYYmm[-2:])

# Set long term stats directory
long_term_stats_dir = ('/lfs/h2/emc/vpppg/save/emc.vpppg/verification'
                       +'/global/long_term_stats/long_term_archive')
long_term_archive = os.path.join(long_term_stats_dir, 'long_term', 'monthly_means')

# Set up useful forecast days output directory
useful_fcst_days_output_dir = os.path.join(
    working_dir, 'plots_monthly_means_useful_fcst_days'
)
if not os.path.exists(useful_fcst_days_output_dir):
    os.makedirs(useful_fcst_days_output_dir)

# Set up information
model_list = ['gfs', 'ecm', 'cmc', 'fno', 'ukm']
hour_list = ['00','12']
vx_mask_list = ['NHX', 'SHX']
level_list = ['P1000', 'P500']
acc_threshs = np.array([0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95])
running_mean = 13
vsdb_start_YYYYmm = '200801'
metplus_start_YYYYmm = '202101'
all_YYYYmm_dt_list = list(
    dateutil.rrule.rrule(
        dateutil.rrule.MONTHLY,
        dtstart=dateutil.parser.parse(start_YYYYmm+'01T000000'),
        until=dateutil.parser.parse(end_YYYYmm+'01T000000')
    )
)
all_YYYYmm_list = []
for YYYYmm_dt in all_YYYYmm_dt_list:
    all_YYYYmm_list.append(f"{YYYYmm_dt:%Y%m}")

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
            # Set up specific threshold dataframes
            acc_thresh_06_monthly_mean_df = pd.DataFrame(
                index=model_list, columns=all_YYYYmm_list
            )
            acc_thresh_06_running_mean_df = pd.DataFrame(
                index=model_list, columns=all_YYYYmm_list
            )
            acc_thresh_08_monthly_mean_df = pd.DataFrame(
                index=model_list, columns=all_YYYYmm_list
            )
            acc_thresh_08_running_mean_df = pd.DataFrame(
                index=model_list, columns=all_YYYYmm_list
            )
            for model in model_list:
                long_term_model_hour_dir = os.path.join(long_term_archive,
                                                        model, hour+'Z')        
                # Read monthly mean files and put in dataframe
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
                # Merge dataframes
                merged_df = pd.DataFrame(index=all_YYYYmm_list,
                                         columns=vsdb_df.columns)
                for YYYYmm_dt in all_YYYYmm_dt_list:
                    YYYYmm_dt_idx = all_YYYYmm_dt_list.index(YYYYmm_dt)
                    YYYYmm = all_YYYYmm_list[YYYYmm_dt_idx]
                    if YYYYmm_dt < \
                            datetime.datetime.strptime(vsdb_start_YYYYmm,
                                                       '%Y%m'):
                        YYYYmm_df = caplan_zhu_df
                        df_name = 'CZ'
                    elif YYYYmm_dt >= \
                            datetime.datetime.strptime(vsdb_start_YYYYmm,
                                                       '%Y%m') \
                            and YYYYmm_dt < \
                            datetime.datetime.strptime(metplus_start_YYYYmm,
                                                      '%Y%m'):
                        YYYYmm_df = vsdb_df
                        df_name = 'VSDB'
                    elif YYYYmm_dt >= \
                            datetime.datetime.strptime(metplus_start_YYYYmm,
                                                       '%Y%m'):
                        YYYYmm_df = metplus_df
                        df_name = 'MP'
                    YYYYmm_line = YYYYmm_df.loc[
                        (YYYYmm_df['YEAR'] == YYYYmm[0:4])
                        & (YYYYmm_df['MONTH'] == YYYYmm[4:])
                    ]
                    if len(YYYYmm_line) == 0:
                         merged_df.loc[YYYYmm] = (
                             [df_name, YYYYmm[0:4], YYYYmm[4:]] + (17*[np.nan])
                         )
                    else:
                        merged_df.loc[YYYYmm] = YYYYmm_line.values
                # Get days at which forecast ACC exceeding a certain value
                acc_treshs_days_df = pd.DataFrame(index=all_YYYYmm_list,
                                                  columns=acc_threshs)
                for YYYYmm_dt in all_YYYYmm_dt_list:
                    YYYYmm_dt_idx = all_YYYYmm_dt_list.index(YYYYmm_dt)
                    YYYYmm = all_YYYYmm_list[YYYYmm_dt_idx]
                    masked_YYYYmm_fcst_days_values = np.ma.masked_invalid(
                        np.array(merged_df.loc[YYYYmm].values[3:],
                        dtype='float')
                    )
                    masked_fcst_days = np.ma.array(
                        np.arange(0,len(merged_df.loc[YYYYmm].values[3:]),1),
                        mask=np.ma.getmaskarray(
                            masked_YYYYmm_fcst_days_values
                        )
                    )
                    if len(masked_YYYYmm_fcst_days_values) \
                            - np.ma.count_masked(
                                masked_YYYYmm_fcst_days_values
                            ) >= 6:
                        compressed_YYYYmm_fcst_days_values = (
                            masked_YYYYmm_fcst_days_values.compressed()
                        )
                        compressed_fcst_days = masked_fcst_days.compressed()
                        for acc_thresh in acc_threshs:
                            acc_thresh_day = np.interp(
                                acc_thresh,
                                compressed_YYYYmm_fcst_days_values[::-1],
                                compressed_fcst_days[::-1],
                                left=np.nan, right=np.nan
                            )
                            acc_treshs_days_df.loc[YYYYmm, acc_thresh] = (
                                acc_thresh_day
                            )
                # Get runnning mean
                acc_treshs_days_rm_df = pd.DataFrame(index=all_YYYYmm_list,
                                                     columns=acc_threshs)
                for acc_thresh in acc_threshs:
                    acc_tresh_values = np.array(
                        acc_treshs_days_df.loc[:,acc_thresh] \
                        .values.ravel(), dtype='float'
                    )
                    for t in range(len(acc_tresh_values)):
                        if t >= int(running_mean/2) \
                                and (t < len(acc_tresh_values) \
                                     - int(running_mean/2)):
                            start = t-int(running_mean/2)
                            end = t+int(running_mean/2)
                            acc_tresh_values_start_end = (
                                np.ma.masked_invalid(
                                    acc_tresh_values[start:end+1]
                                )
                            )
                            if len(acc_tresh_values_start_end.compressed()) \
                                    >= 10:
                                acc_treshs_days_rm_df.loc[all_YYYYmm_list[t],
                                                          acc_thresh] = (
                                    np.ma.mean(acc_tresh_values_start_end)
                                )
                # Make plot for individual model
                fig, ax = plt.subplots(1,1,figsize=(x_figsize, y_figsize))
                ax.grid(True)
                ax.set_xlabel('Year')
                ax.set_xlim([all_YYYYmm_dt_list[0], all_YYYYmm_dt_list[-1]])
                ax.set_xticks(all_YYYYmm_dt_list[::24])
                ax.xaxis.set_major_formatter(md.DateFormatter('%Y'))
                ax.xaxis.set_minor_locator(md.MonthLocator())
                ax.set_ylabel('Forecast Day')
                ax.set_yticks(range(0,11,1))
                ax.set_ylim([0, 10])
                for acc_thresh in acc_threshs:
                    # Monthly Mean
                    acc_thresh_monthly_mean = np.ma.masked_invalid(
                        np.array(acc_treshs_days_df.loc[:,acc_thresh].values,
                                 dtype='float')
                    )
                    all_YYYYmm_dt_list_mm_mask = np.ma.array(
                        all_YYYYmm_dt_list,
                        mask=np.ma.getmaskarray(acc_thresh_monthly_mean)
                    )
                    ax.plot_date(
                        all_YYYYmm_dt_list_mm_mask, acc_thresh_monthly_mean,
                        color=acc_threshs_plot_colors_dict[str(acc_thresh)],
                        linestyle='dotted', linewidth=1,
                        marker=None, markersize=0,
                    )
                    # Running Mean
                    acc_thresh_running_mean = np.ma.masked_invalid(
                        np.array(acc_treshs_days_rm_df.loc[:,acc_thresh].values,
                                 dtype='float')
                    )
                    all_YYYYmm_dt_list_rm_mask = np.ma.array(
                        all_YYYYmm_dt_list,
                        mask=np.ma.getmaskarray(acc_thresh_running_mean)
                    )
                    ax.plot_date(
                        all_YYYYmm_dt_list_rm_mask, acc_thresh_running_mean,
                        color=acc_threshs_plot_colors_dict[str(acc_thresh)],
                        linestyle='solid', linewidth=2,
                        marker=None, markersize=0,
                        label='ACC='+str(acc_thresh)
                    )
                    if acc_thresh == 0.6:
                        acc_thresh_06_monthly_mean_df.loc[model,:] = (
                            acc_thresh_monthly_mean
                        )
                        acc_thresh_06_running_mean_df.loc[model,:] = (
                            acc_thresh_running_mean
                        )
                    if acc_thresh == 0.8:
                        acc_thresh_08_monthly_mean_df.loc[model,:] = (
                            acc_thresh_monthly_mean
                        )
                        acc_thresh_08_running_mean_df.loc[model,:] = (
                            acc_thresh_running_mean
                        )
                var_info_title = plot_title.get_var_info_title(
                    'HGT', level
                )
                vx_mask_title = plot_title.get_vx_mask_title(vx_mask)
                ax.set_title('Forecast Days Exceeding Given ACC Values\n'
                             +model.upper()+', '+var_info_title+', '
                             +vx_mask_title+'\n'
                             +'valid '+f"{all_YYYYmm_dt_list[0]:%b%Y}"+'-'
                             +f"{all_YYYYmm_dt_list[-1]:%b%Y}"+' '
                             +hour+'Z\n'
                             +'Dotted line: Monthly Mean, Solid Line: '
                             +str(running_mean)+' Month Running Mean',
                             loc=title_loc)
                fig.figimage(noaa_logo_img_array,
                             noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
                             zorder=1, alpha=noaa_logo_alpha)
                fig.figimage(nws_logo_img_array,
                             nws_logo_xpixel_loc, nws_logo_ypixel_loc,
                             zorder=1, alpha=nws_logo_alpha)
                if len(ax.lines) != 0:
                    legend = ax.legend(
                        bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                        loc=legend_loc, ncol=legend_ncol,
                        fontsize=legend_fontsize
                    )
                savefig_name = os.path.join(useful_fcst_days_output_dir,
                                            'useful_fcst_days_'+model+'_valid'
                                            +hour+'Z_HGT_'+level+'_G002'
                                            +vx_mask+'.png')
                print(savefig_name)
                plt.savefig(savefig_name)
                plt.close()
            # Make plot for 0.6 and 0.8 tresholds
            fig, ax = plt.subplots(1,1,figsize=(x_figsize, y_figsize))
            ax.grid(True)
            ax.set_xlabel('Year')
            ax.set_xlim([all_YYYYmm_dt_list[0], all_YYYYmm_dt_list[-1]])
            ax.set_xticks(all_YYYYmm_dt_list[::24])
            ax.xaxis.set_major_formatter(md.DateFormatter('%Y'))
            ax.xaxis.set_minor_locator(md.MonthLocator())
            ax.set_ylabel('Forecast Day')
            ax.set_yticks(range(0,11,1))
            ax.set_ylim([0, 10])
            for model in model_list:
                # ACC = 0.6, monthly mean
                model_thresh_06_monthly_mean = np.ma.masked_invalid(
                    np.array(acc_thresh_06_monthly_mean_df.loc[model,:].values,
                             dtype='float')
                ) 
                all_YYYYmm_dt_list_mm_06_mask = np.ma.array(
                    all_YYYYmm_dt_list,
                    mask=np.ma.getmaskarray(model_thresh_06_monthly_mean)
                )
                ax.plot_date(
                    all_YYYYmm_dt_list_mm_06_mask,
                    model_thresh_06_monthly_mean,
                    color=models_plot_colors_dict[model],
                    linestyle='dotted', linewidth=1,
                    marker=None, markersize=0,
                    zorder=((len(model_list)-model_list.index(model))+4)
                )
                # ACC = 0.6, running mean
                model_thresh_06_running_mean = np.ma.masked_invalid(
                    np.array(acc_thresh_06_running_mean_df.loc[model,:].values,
                             dtype='float')
                )
                all_YYYYmm_dt_list_rm_06_mask = np.ma.array(
                    all_YYYYmm_dt_list,
                    mask=np.ma.getmaskarray(model_thresh_06_running_mean)
                )
                ax.plot_date(
                    all_YYYYmm_dt_list_rm_06_mask,
                    model_thresh_06_running_mean,
                    color=models_plot_colors_dict[model],
                    linestyle='solid', linewidth=2,
                    marker=None, markersize=0,
                    zorder=((len(model_list)-model_list.index(model))+4)
                )
                # ACC = 0.8, monthly mean
                model_thresh_08_monthly_mean = np.ma.masked_invalid(
                    np.array(acc_thresh_08_monthly_mean_df.loc[model,:].values,
                             dtype='float')
                )
                all_YYYYmm_dt_list_mm_08_mask = np.ma.array(
                    all_YYYYmm_dt_list,
                    mask=np.ma.getmaskarray(model_thresh_08_monthly_mean)
                )
                ax.plot_date(
                    all_YYYYmm_dt_list_mm_08_mask,
                    model_thresh_08_monthly_mean,
                    color=models_plot_colors_dict[model],
                    linestyle='dotted', linewidth=1,
                    marker=None, markersize=0,
                    zorder=((len(model_list)-model_list.index(model))+4)
                )
                # ACC = 0.8, running mean
                model_thresh_08_running_mean = np.ma.masked_invalid(
                    np.array(acc_thresh_08_running_mean_df.loc[model,:].values,
                             dtype='float')
                )
                all_YYYYmm_dt_list_rm_08_mask = np.ma.array(
                    all_YYYYmm_dt_list,
                    mask=np.ma.getmaskarray(model_thresh_08_running_mean)
                )   
                ax.plot_date(
                    all_YYYYmm_dt_list_rm_08_mask,
                    model_thresh_08_running_mean,
                    color=models_plot_colors_dict[model],
                    linestyle='solid', linewidth=2,
                    marker=None, markersize=0,
                    label=model,
                    zorder=((len(model_list)-model_list.index(model))+4)
                )
            ax.text(1.01, 0.825, 'ACC=\n0.6', fontsize=11,
                    transform=ax.transAxes)
            ax.text(1.01, 0.625, 'ACC=\n0.8', fontsize=11,
                    transform=ax.transAxes)
            var_info_title = plot_title.get_var_info_title(
                'HGT', level
            )
            vx_mask_title = plot_title.get_vx_mask_title(vx_mask)
            ax.set_title('Forecast Days Exceeding ACC=0.6 and ACC=0.8\n'
                         +var_info_title+', '+vx_mask_title+'\n'
                         +'valid '+f"{all_YYYYmm_dt_list[0]:%b%Y}"+'-'
                         +f"{all_YYYYmm_dt_list[-1]:%b%Y}"+' '
                         +hour+'Z\n'
                         +'Dotted line: Monthly Mean, Solid Line: '
                         +str(running_mean)+' Month Running Mean',
                         loc=title_loc)
            fig.figimage(noaa_logo_img_array,
                         noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
                         zorder=1, alpha=noaa_logo_alpha)
            fig.figimage(nws_logo_img_array,
                         nws_logo_xpixel_loc, nws_logo_ypixel_loc,
                         zorder=1, alpha=nws_logo_alpha)
            if len(ax.lines) != 0:
                legend = ax.legend(
                    bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                    loc=legend_loc, ncol=len(model_list),
                    fontsize=legend_fontsize
                )
            savefig_name = os.path.join(useful_fcst_days_output_dir,
                                        'useful_fcst_days_all_models_valid'
                                        +hour+'Z_HGT_'+level+'_G002'
                                        +vx_mask+'.png')
            print(savefig_name)
            plt.savefig(savefig_name)
            plt.close()
