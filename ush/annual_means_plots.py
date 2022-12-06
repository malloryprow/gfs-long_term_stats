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

start_YYYY = '1984'
end_YYYY = os.environ['YYYY']
working_dir = os.environ['working_dir']
#end_YYYY = '2020'
#working_dir = ('/lfs/h2/emc/stmp/'+os.environ['USER']
#               +'/long_term_stats_update/long_term_plots')

# Set long term stats directory
long_term_stats_dir = ('/lfs/h2/emc/vpppg/save/emc.vpppg/verification'
                       +'/global/long_term_stats')
long_term_archive = os.path.join(long_term_stats_dir, 'long_term', 'annual_means')

# Set up plotting groups dictionary
plot_model_groups_vars_dict = {
    'all_models/HGT/00Z': {
        'model_list': ['gfs', 'ecm', 'cmc', 'fno', 'ukm', 'cdas', 'cfsr'],
        'model_plot_name_list': ['gfs', 'ecm', 'cmc', 'fno', 'ukm', 'cdas', 'cfsr'],
        'level_list': ['P500'],
        'vx_mask_list': ['NHX', 'SHX'],
        'stat_list': ['acc']
    },
    'gfs_ecm/HGT/00Z': {
        'model_list': ['gfs', 'ecm'],
        'model_plot_name_list': ['gfs', 'ecm'],
        'level_list': ['P500'],
        'vx_mask_list': ['NHX', 'SHX'],
        'stat_list': ['acc']
    },
    'gfs_cdas/HGT/00Z': {
        'model_list': ['gfs', 'cdas'],
        'model_plot_name_list': ['gfs', 'cdas'],
        'level_list': ['P500'],
        'vx_mask_list': ['NHX', 'SHX'],
        'stat_list': ['acc']
    },
}

# Set expected file columns
expected_file_columns = [
    'SYS', 'YEAR', 'DAY0', 'DAY1', 'DAY2', 'DAY3', 'DAY4',
    'DAY5', 'DAY6', 'DAY7', 'DAY8', 'DAY9', 'DAY10', 'DAY11', 'DAY12',
    'DAY13', 'DAY14', 'DAY15', 'DAY16'
] 

def create_merged_dataset(var, level, vx_mask, model_list, valid_hour, stat,
                          all_YYYY_dt_list):
    print("-> Reading data and creating merged dataset")
    # Merge dates
    cz_start_YYYY = '1996'
    vsdb_start_YYYY = '2008'
    metplus_start_YYYY = '2021'
    # Create YYYY string list
    all_YYYY_list = []
    for YYYY_dt in all_YYYY_dt_list:
        all_YYYY_list.append(f"{YYYY_dt:%Y}")
    # Adjustments for Czplan-Zhu files
    if var == 'HGT':
        cz_level = level.replace('P', '')+'hpa'
        if stat == 'acc':
            cz_var_stat = 'HGTACWave1-20'
        elif stat == 'bias':
            cz_var_stat = 'HGTError'
        elif stat == 'rmse':
            cz_var_stat = 'HGTRMSE'
    elif var == 'UGRD_VGRD':
        cz_level = level.replace('P', '')+'hPa'
        if stat == 'acc':
            cz_var_stat = 'UVACWave1-20'
        elif stat == 'bias':
            cz_var_stat = 'SPDError'
        elif stat == 'rmse':
            cz_var_stat = 'UVRMSE'
    else:
        cz_level = level
        cz_var_stat = var+stat
    if vx_mask in ['NHX', 'SHX']:
        cz_vx_mask = vx_mask[0:2]
    elif vx_mask == 'TRO':
        cz_vx_mask = 'Tropics'
    else:
        cz_vx_mask = vx_mask
    # Adjustments for VSDB files
    if var == 'HGT':
        vsdb_var = 'HGT'
    elif var == 'UGRD_VGRD':
        vsdb_var = 'WIND'
    else:
        vsdb_var = var
    if stat == 'acc':
        vsdb_stat = 'AC'
    elif stat in ['bias', 'rmse']:
        vsdb_stat = stat.upper()
    else:
        vsdb_stat = stat
    # Get individual model files paths and put in dataframe 
    for model in model_list:
        print(model)
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
        if valid_hour == '':
            long_term_model_hour_dir = os.path.join(long_term_archive, model)
        else:
            long_term_model_hour_dir = os.path.join(long_term_archive, model,
                                                    valid_hour)
        excel_file_name = os.path.join(long_term_model_hour_dir,
                                       'excel_'+stat.upper()+'_'+var+'_'
                                        +level+'_'+vx_mask+'.txt')
        cz_file_name = os.path.join(long_term_model_hour_dir,
                                    'caplan_zhu_'+cz_var_stat+'_'+cz_level+'_'
                                    +cz_vx_mask+'.txt')
        vsdb_file_name = os.path.join(long_term_model_hour_dir,
                                      'vsdb_'+vsdb_stat+'_'+vsdb_var+'_'
                                      +level+'_G2'+vx_mask+'.txt')
        metplus_file_name = os.path.join(long_term_model_hour_dir,
                                         'metplus_'+stat.upper()+'_'+var+'_'
                                         +level+'_'+vx_mask+'.txt')
        print(excel_file_name)
        print(cz_file_name)
        print(vsdb_file_name)
        print(metplus_file_name)
        if os.path.exists(excel_file_name):
            excel_df = pd.read_table(excel_file_name, delimiter=' ', dtype='str',
                                     skipinitialspace=True)
        else:
            excel_df = pd.DataFrame(columns=expected_file_columns)
        if os.path.exists(cz_file_name):
            cz_df = pd.read_table(cz_file_name, delimiter=' ', dtype='str',
                                  skipinitialspace=True)
        else:
            cz_df = pd.DataFrame(columns=expected_file_columns)
        if os.path.exists(vsdb_file_name): 
            vsdb_df = pd.read_table(vsdb_file_name, delimiter=' ', dtype='str',
                                    skipinitialspace=True)
        else:
            vsdb_df = pd.DataFrame(columns=expected_file_columns)
        if os.path.exists(metplus_file_name):
            metplus_df = pd.read_table(metplus_file_name, delimiter=' ',
                                       dtype='str', skipinitialspace=True)
        else:
            metplus_df = pd.DataFrame(columns=expected_file_columns)
        # Merge dataframes
        model_merged_index = pd.MultiIndex.from_product(
            [[model], all_YYYY_list],names=['model', 'YYYY']
        )
        merged_df = pd.DataFrame(index=model_merged_index,
                                 columns=expected_file_columns)
        # Initialize merged_df DAY5 to excel_df DAY5
        excel_df_end_idx = 2020-int(end_YYYY)
        merged_df.loc[:,'DAY5'].iloc[:excel_df_end_idx] = (
            excel_df.loc[:,'DAY5'].values
        )
        merged_df.loc[:,'SYS'].iloc[:excel_df_end_idx] = (
            excel_df.loc[:,'SYS'].values
        )
        for YYYY in all_YYYY_list:
            if int(YYYY) >= cz_start_YYYY \
                    and int(YYYY) < vsdb_start_YYYY:
                YYYY_df = cz_df
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
                merged_df.loc[(model,YYYY)] = (
                    [df_name, YYYY] + (17*[np.nan])
                )
            else:
                merged_df.loc[(model,YYYY)] = YYYY_line.values
        #print(np.asarray(excel_df.loc[:,'DAY5'].values, dtype=float)
        #      -np.asarray(merged_df.loc[:,'DAY5'].values, dtype=float))
        if model_list.index(model) == 0:
            all_model_merged_df = merged_df
        else:
            all_model_merged_df = pd.concat([all_model_merged_df, merged_df])
    return all_model_merged_df

def create_plots(all_model_merged_df, var, level, vx_mask, model_list,
                 model_plot_name_list, valid_hour, stat,
                 all_YYYY_dt_list, forecast_days, output_dir):
    print("-> Creating Plots")
    # Common plot settings
    noaa_logo_path, nws_logo_path = plot_util.get_logo_paths()
    noaa_logo_img_array = matplotlib.image.imread(noaa_logo_path)
    nws_logo_img_array = matplotlib.image.imread(nws_logo_path)
    models_plot_colors_dict = {
        'gfs': '#000000',
        'gfs/00Z': '#000000',
        'gfs/06Z': '#E00707',
        'gfs/12Z': '#039437',
        'gfs/18Z': '#441EFF',
        'ecm': '#FB2020',
        'cmc': '#00DC00',
        'fno': '#1E3CFF',
        'ukm': '#E69F00',
        'cfsr': '#56B4E9',
        'cdas': '#8400C8'
    }
    if stat == 'acc':
        stat_title = 'Anomaly Correlation Coefficient'
    elif stat == 'bias':
        stat_title = stat.title()
    elif stat == 'rmse':
        stat_title = 'Root Mean Square Error'
    YYYY = f"{all_YYYY_dt_list[-1]:%Y}"
    # Make time series plots for each forecast day
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.titlepad'] = 15
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
    legend_ncol = 4
    title_loc = 'center'
    noaa_logo_xpixel_loc = (x_figsize*plt.rcParams['figure.dpi']*0.1)
    noaa_logo_ypixel_loc = (y_figsize*plt.rcParams['figure.dpi']*0.865)
    noaa_logo_alpha = 0.5
    nws_logo_xpixel_loc = (x_figsize*plt.rcParams['figure.dpi']*0.9)
    nws_logo_ypixel_loc = (y_figsize*plt.rcParams['figure.dpi']*0.865)
    nws_logo_alpha = 0.5
    for forecast_day in forecast_days:
        stat_min = np.ma.masked_invalid(np.nan)
        stat_max = np.ma.masked_invalid(np.nan)
        forecast_day_all_model_merged_df = (
            all_model_merged_df.loc[:]['DAY'+str(forecast_day)]
        )
        fig, ax = plt.subplots(
            1, 1, figsize=(x_figsize, y_figsize),
        )
        ax.grid(True)
        ax.set_xlabel('Year')
        ax.set_xlim([all_YYYY_dt_list[0], all_YYYY_dt_list[-1]])
        ax.set_xticks(all_YYYY_dt_list[::4])
        ax.xaxis.set_major_formatter(md.DateFormatter('%Y'))
        ax.set_ylabel(stat_title)
        for model in model_list:
            model_plot_name = model_plot_name_list[model_list.index(model)]
            model_annual_mean_values = (
                forecast_day_all_model_merged_df.loc[model].values
            )
            masked_model_annual_mean_values = np.ma.masked_invalid(
                np.array(model_annual_mean_values, dtype=float)
            )
            count = (
                len(masked_model_annual_mean_values)
                -np.ma.count_masked(masked_model_annual_mean_values)
            )
            all_YYYY_dt_list_mask =  np.ma.array(
                all_YYYY_dt_list,
                mask=np.ma.getmaskarray(masked_model_annual_mean_values)
            )
            if model == 'gfs':
                model_linewidth = 3
            else:
                model_linewidth = 2
            if count != 0:
                ax.plot_date(
                    all_YYYY_dt_list_mask,
                    masked_model_annual_mean_values,
                    color=models_plot_colors_dict[model],
                    linestyle='solid', linewidth=model_linewidth,
                    marker=None, markersize=0,
                    zorder=((len(model_list)-model_list.index(model))+4),
                    label=model_plot_name
                )
                if masked_model_annual_mean_values.min() < stat_min \
                        or np.ma.is_masked(stat_min):
                    stat_min = masked_model_annual_mean_values.min()
                if masked_model_annual_mean_values.max() > stat_max \
                        or np.ma.is_masked(stat_max):
                    stat_max = masked_model_annual_mean_values.max()
        preset_y_axis_tick_min = ax.get_yticks()[0]
        preset_y_axis_tick_max = ax.get_yticks()[-1]
        preset_y_axis_tick_inc = (ax.get_yticks()[1]-ax.get_yticks()[0])
        if stat == 'acc':
            y_axis_tick_inc = 0.1
        else:
            y_axis_tick_inc = preset_y_axis_tick_inc
        if np.ma.is_masked(stat_min):
            y_axis_min = preset_y_axis_tick_min
        else:
            if stat == 'acc':
                y_axis_min = (round(stat_min,1)-y_axis_tick_inc)
            else:
                y_axis_min = preset_y_axis_tick_min
        while y_axis_min > stat_min:
            y_axis_min = y_axis_min - y_axis_tick_inc
        if np.ma.is_masked(stat_max):
            y_axis_max = preset_y_axis_tick_max
        else:
            if stat == 'acc':
                y_axis_max = 1
            else:
                y_axis_max = (preset_y_axis_tick_max+y_axis_tick_inc)
        while y_axis_max < stat_max:
            y_axis_max = y_axis_max + y_axis_tick_inc
        ax.set_yticks(
            np.arange(y_axis_min,
                      y_axis_max+y_axis_tick_inc,
                      y_axis_tick_inc)
        )
        ax.set_ylim([y_axis_min, y_axis_max])
        if stat_max >= ax.get_ylim()[1]:
            while stat_max >= ax.get_ylim()[1]:
                y_axis_max = y_axis_max + y_axis_tick_inc
                ax.set_yticks(
                    np.arange(y_axis_min,
                              y_axis_max+y_axis_tick_inc,
                              y_axis_tick_inc)
                )
        ax.set_ylim([y_axis_min, y_axis_max])
        if stat_min <= ax.get_ylim()[0]:
            while stat_min <= ax.get_ylim()[0]:
                y_axis_min = y_axis_min - y_axis_tick_inc
                ax.set_yticks(
                    np.arange(y_axis_min,
                              y_axis_max+y_axis_tick_inc,
                              y_axis_tick_inc)
                )
        ax.set_ylim([y_axis_min, y_axis_max])
        var_info_title = plot_title.get_var_info_title(var, level)
        vx_mask_title = plot_title.get_vx_mask_title(vx_mask)
        forecast_lead_title = plot_title.get_lead_title(str(forecast_day*24))
        ax.set_title(
            stat_title+'\n'
            +var_info_title+', '+vx_mask_title+'\n'+' '
            'Annual Means, '
            +forecast_lead_title, loc=title_loc
        )
        fig.figimage(
            noaa_logo_img_array, noaa_logo_xpixel_loc,
            noaa_logo_ypixel_loc, zorder=1, alpha=noaa_logo_alpha
        )
        fig.figimage(
            nws_logo_img_array, nws_logo_xpixel_loc,
            nws_logo_ypixel_loc, zorder=1, alpha=nws_logo_alpha
        )
        if len(ax.lines) != 0:
            legend = ax.legend(
                bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                loc=legend_loc, ncol=len(model_list), fontsize=legend_fontsize
            )
            plt.draw()
            legend_box = (
                legend.get_window_extent().inverse_transformed(ax.transData)
            )
            if stat_min < legend_box.y1:
                while stat_min < legend_box.y1:
                    y_axis_min = y_axis_min - y_axis_tick_inc
                    ax.set_yticks(
                        np.arange(y_axis_min,
                                  y_axis_max+y_axis_tick_inc,
                                  y_axis_tick_inc)
                    )
                    ax.set_ylim([y_axis_min, y_axis_max])
                    legend = ax.legend(
                        bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                        loc=legend_loc, ncol=len(model_list),
                        fontsize=legend_fontsize
                    )
                    plt.draw()
                    legend_box = (
                        legend.get_window_extent() \
                        .inverse_transformed(ax1.transData)
                    )
        if valid_hour == '':
            savefig_name = os.path.join(
                output_dir,
                'annual_'+model_group+'_'+stat+'_'+var+'_'+level
                +'_fday'+str(forecast_day)+'_G002'+vx_mask+'.png'
            )
        else:
            savefig_name = os.path.join(
                output_dir,
                'annual_'+model_group+'_'+stat+'_valid'+valid_hour+'_'
                +var+'_'+level+'_fday'+str(forecast_day)+'_G002'
                +vx_mask+'.png'
            )
        print(savefig_name)
        plt.savefig(savefig_name)
        plt.close()

# Make plots for groupings
for plot_model_group_var in list(plot_model_groups_vars_dict.keys()):
    print("-----> "+plot_model_group_var)
    plot_model_group_var_dict = plot_model_groups_vars_dict[plot_model_group_var]
    if len(plot_model_group_var.split('/')) == 3:
        model_group = plot_model_group_var.split('/')[0]
        var = plot_model_group_var.split('/')[1]
        valid_hour = plot_model_group_var.split('/')[2]
    if len(plot_model_group_var.split('/')) == 2:
        model_group = plot_model_group_var.split('/')[0]
        var = plot_model_group_var.split('/')[1]
        valid_hour = ''
    for mgv_setting in list(plot_model_group_var_dict.keys()):
       print(mgv_setting+": "+', '.join(plot_model_group_var_dict[mgv_setting]))
    model_list = plot_model_group_var_dict['model_list']
    model_plot_name_list = plot_model_group_var_dict['model_plot_name_list']
    level_list = plot_model_group_var_dict['level_list']
    vx_mask_list = plot_model_group_var_dict['vx_mask_list']
    stat_list = plot_model_group_var_dict['stat_list']
    # Set up model group var output directory
    model_group_var_output_dir = os.path.join(
        working_dir, 'plots_annual_means_'
        +plot_model_group_var.replace('/', '_')
    )
    if not os.path.exists(model_group_var_output_dir):
        os.makedirs(model_group_var_output_dir)
    print("")
    print("Output: "+model_group_var_output_dir)
    print("\n")
    # Set up dates
    all_YYYY_dt_list = list(
        dateutil.rrule.rrule(
            dateutil.rrule.YEARLY,
            dtstart=dateutil.parser.parse(start_YYYY+'0101T000000'),
            until=dateutil.parser.parse(end_YYYY+'0101T000000')
        )
    )
    # Loop over level, vx_mask, stat
    for level in level_list:
        for vx_mask in vx_mask_list:
            for stat in stat_list:
                print("---> "+level+" "+vx_mask+" "+stat)
                model_group_var_merged_df = create_merged_dataset(
                    var, level, vx_mask, model_list, valid_hour, stat,
                    all_YYYY_dt_list
                )
                forecast_days = np.arange(5,6,1)
                create_plots(model_group_var_merged_df, var, level, vx_mask,
                             model_list, model_plot_name_list, valid_hour,
                             stat, all_YYYY_dt_list, forecast_days,
                             model_group_var_output_dir)
