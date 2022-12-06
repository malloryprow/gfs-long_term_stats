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

start_YYYY = '2002'
end_YYYY = '2020'
working_dir = ('/lfs/h2/emc/stmp/'+os.environ['USER']
               +'/long_term_precip/long_term_plots')

# Set long term stats directory
long_term_stats_dir = ('/lfs/h2/emc/vpppg/save/emc.vpppg/verification'
                       +'/global/long_term_stats')
long_term_archive = os.path.join(long_term_stats_dir, 'precip')

# Set up useful forecast days output directory
gfs_precip_output_dir = os.path.join(
    working_dir, 'plots_annual_means_gfs_precip'
)
if not os.path.exists(gfs_precip_output_dir):
    os.makedirs(gfs_precip_output_dir)

# Set up information
stat_threshold_dict = {
    'ets': ['0.25in', '1in', '2in', '3in'],
    'fss': ['10mm', '25mm']
}
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
years = np.asarray(all_YYYY_list, dtype=float)

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
fhr_plot_colors_dict = {
    '24': '#FB2020',
    '48': '#00DC00',
    '72': '#1E3CFF'
}

# Make plots
for stat_threshold in list(stat_threshold_dict.keys()):
    stat = stat_threshold
    threshold_list = stat_threshold_dict[stat]
    for threshold in threshold_list:
        if stat == 'ets':  
            stat_threshold_file_name = os.path.join(
                long_term_archive, 'gfs.'+stat+'.'+threshold+'.txt'
            )
            stat_threshold_file_name = stat_threshold_file_name.replace(
                '0.', 'pt'
            )
        elif stat == 'fss':
           stat_threshold_file_name = os.path.join(
                long_term_archive, 'gfs.'+stat+'24.'+threshold+'.62km.txt'
           )
        fig, ax = plt.subplots(1,1,figsize=(x_figsize, y_figsize))
        ax.grid(True)
        ax.set_xlabel('Year')
        ax.set_xlim([years[0], years[-1]])
        ax.set_xticks(years[::2])
        if stat == 'ets':
            ax.set_ylabel('Equitable Threat Score')
            ax.set_yticks(np.arange(0,0.6,0.05))
            ax.set_ylim([0, 0.55])
        elif stat == 'fss':
            ax.set_ylabel('Fraction Skill Score')
            ax.set_yticks(np.arange(0,1.1,0.1))
            ax.set_ylim([0, 1.0])
        if os.path.exists(stat_threshold_file_name):
            # Read in file
            stat_threshold_df = pd.read_table(
                stat_threshold_file_name, delimiter=' ',
                skipinitialspace=True
            )
            stat_threshold_df_years = np.asarray(
                stat_threshold_df['YEAR'], dtype=float
            )
            stat_threshold_df_fhr24 = np.asarray(
                stat_threshold_df['FHR24'], dtype=float
            )
            stat_threshold_df_fhr48 = np.asarray(
                stat_threshold_df['FHR48'], dtype=float
            )
            stat_threshold_df_fhr72 = np.asarray(
                stat_threshold_df['FHR72'], dtype=float
            )
            ax.plot(
                stat_threshold_df_years,
                stat_threshold_df_fhr24,
                color=fhr_plot_colors_dict['24'],
                linestyle='solid', linewidth=2,
                marker=None, markersize=0,
                label='forecast hour 24'
            )
            ax.plot(
                stat_threshold_df_years,
                stat_threshold_df_fhr48,
                color=fhr_plot_colors_dict['48'],
                linestyle='solid', linewidth=2,
                marker=None, markersize=0,
                label='forecast hour 48'
            )
            ax.plot(
                stat_threshold_df_years,
                stat_threshold_df_fhr72,
                color=fhr_plot_colors_dict['72'],
                linestyle='solid', linewidth=2,
                marker=None, markersize=0,
                label='forecast hour 72'
            )
        if stat == 'ets':
            ax.set_title('GFS Annual Mean Equitable Threat Score\n'
                         +'24 hour Accumulated Precipitation >'+threshold
                         +' over CONUS\n')
        elif stat == 'fss':
             ax.set_title('GFS Annual Mean Fraction Skill Score '
                          +'(62 km Neighborhood)\n'
                          +'24 hour Accumulated Precipitation >'+threshold
                          +' over CONUS\n')
        legend = ax.legend(bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                                           loc=legend_loc, ncol=legend_ncol,
                                           fontsize=legend_fontsize)
        fig.figimage(noaa_logo_img_array,
                     noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
                     zorder=1, alpha=noaa_logo_alpha)
        fig.figimage(nws_logo_img_array,
                     nws_logo_xpixel_loc, nws_logo_ypixel_loc,
                     zorder=1, alpha=nws_logo_alpha)
        savefig_name = os.path.join(gfs_precip_output_dir,
                                    'annual_gfs_precip_'+stat+'_'
                                    +threshold+'.png')
        print(savefig_name)
        plt.savefig(savefig_name)
        plt.close()
