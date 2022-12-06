import os
import datetime
import dateutil
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.gridspec as gridspec
#pd.plotting.deregister_matplotlib_converters()
pd.plotting.register_matplotlib_converters()
import plot_title as plot_title
import plot_util as plot_util

start_YYYYmm_in = os.environ['start_YYYYmm']
end_YYYYmm = os.environ['end_YYYYmm']
working_dir = os.environ['working_dir']
#start_YYYYmm_in = '199601'
#end_YYYYmm = '202105'
#working_dir = ('/gpfs/dell2/'+os.environ['USER']
#               +'/long_term_stats_update_2021'+end_YYYYmm[-2:])

# Set long term stats directory
long_term_stats_dir = ('/lfs/h2/emc/vpppg/save/emc.vpppg/verification'
                       +'/global/long_term_stats/long_term_archive')
long_term_archive = os.path.join(long_term_stats_dir, 'long_term', 'monthly_means')

# Set up plotting groups dictionary
plot_model_groups_vars_dict = {
    'all_models/HGT/00Z': {
        'model_list': ['gfs', 'ecm', 'cmc', 'fno', 'ukm', 'cdas'],
        'model_plot_name_list': ['gfs', 'ecm', 'cmc', 'fno', 'ukm', 'cdas'],
        'level_list': ['P1000', 'P500'],
        'vx_mask_list': ['NHX', 'SHX'],
        'stat_list': ['acc', 'bias', 'rmse']
    },
    'all_models/UGRD_VGRD/00Z': {
        'model_list': ['gfs', 'ecm', 'cmc', 'fno', 'ukm', 'cfsr'],
        'model_plot_name_list': ['gfs', 'ecm', 'cmc', 'fno', 'ukm', 'cfsr'],
        'level_list': ['P850', 'P200'],
        'vx_mask_list': ['TRO'],
        'stat_list': ['bias', 'rmse']
    },
    'gfs_ecm/HGT/00Z': {
        'model_list': ['ecm', 'gfs'],
        'model_plot_name_list': ['ecm', 'gfs'],
        'level_list': ['P1000', 'P500'],
        'vx_mask_list': ['NHX', 'SHX'],
        'stat_list': ['acc', 'bias', 'rmse']
    },
    'gfs_ecm/UGRD_VGRD/00Z': {
        'model_list': ['ecm', 'gfs'],
        'model_plot_name_list': ['ecm', 'gfs'],
        'level_list': ['P850', 'P200'],
        'vx_mask_list': ['TRO'],
        'stat_list': ['bias', 'rmse']
    },
    'gfs_4cycles/HGT': {
        'model_list': ['gfs/00Z', 'gfs/06Z', 'gfs/12Z', 'gfs/18Z'],
        'model_plot_name_list': ['gfs_00Z', 'gfs_06Z', 'gfs_12Z', 'gfs_18Z'],
        'level_list': ['P1000', 'P500'],
        'vx_mask_list': ['NHX', 'SHX'],
        'stat_list': ['acc', 'bias', 'rmse']
    },
    'gfs_4cycles/UGRD_VGRD': {
        'model_list': ['gfs/00Z', 'gfs/06Z', 'gfs/12Z', 'gfs/18Z'],
        'model_plot_name_list': ['gfs_00Z', 'gfs_06Z', 'gfs_12Z', 'gfs_18Z'],
        'level_list': ['P850', 'P200'],
        'vx_mask_list': ['TRO'],
        'stat_list': ['bias', 'rmse']
    }
}

# Set expected file columns
expected_file_columns = [
    'SYS', 'YEAR', 'MONTH', 'DAY0', 'DAY1', 'DAY2', 'DAY3', 'DAY4',
    'DAY5', 'DAY6', 'DAY7', 'DAY8', 'DAY9', 'DAY10', 'DAY11', 'DAY12',
    'DAY13', 'DAY14', 'DAY15', 'DAY16'
] 

def create_merged_dataset(var, level, vx_mask, model_list, valid_hour, stat,
                          all_YYYYmm_dt_list):
    print("-> Reading data and creating merged dataset")
    # Merge dates
    vsdb_start_YYYYmm = '200801'
    metplus_start_YYYYmm = '202101'
    vsdb_start_YYYYmm_dt = datetime.datetime.strptime(vsdb_start_YYYYmm,
                                                      '%Y%m')
    metplus_start_YYYYmm_dt = datetime.datetime.strptime(metplus_start_YYYYmm,
                                                         '%Y%m')
    # Create YYYYmm string list
    all_YYYYmm_list = []
    for YYYYmm_dt in all_YYYYmm_dt_list:
        all_YYYYmm_list.append(f"{YYYYmm_dt:%Y%m}")
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
        if valid_hour == '':
            long_term_model_hour_dir = os.path.join(long_term_archive, model)
        else:
            long_term_model_hour_dir = os.path.join(long_term_archive, model,
                                                    valid_hour)
        cz_file_name = os.path.join(long_term_model_hour_dir,
                                    'caplan_zhu_'+cz_var_stat+'_'+cz_level+'_'
                                    +cz_vx_mask+'.txt')
        vsdb_file_name = os.path.join(long_term_model_hour_dir,
                                      'vsdb_'+vsdb_stat+'_'+vsdb_var+'_'
                                      +level+'_G2'+vx_mask+'.txt')
        metplus_file_name = os.path.join(long_term_model_hour_dir,
                                         'metplus_'+stat.upper()+'_'+var+'_'
                                         +level+'_'+vx_mask+'.txt')
        print(cz_file_name)
        print(vsdb_file_name)
        print(metplus_file_name)
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
            [[model], all_YYYYmm_list],names=['model', 'YYYYmm']
        )
        merged_df = pd.DataFrame(index=model_merged_index,
                                 columns=expected_file_columns)
        for YYYYmm_dt in all_YYYYmm_dt_list:
            YYYYmm_dt_idx = all_YYYYmm_dt_list.index(YYYYmm_dt)
            YYYYmm = all_YYYYmm_list[YYYYmm_dt_idx]
            if YYYYmm_dt < vsdb_start_YYYYmm_dt:
                YYYYmm_df = cz_df
                df_name = 'CZ'
            elif YYYYmm_dt >= vsdb_start_YYYYmm_dt \
                    and YYYYmm_dt < metplus_start_YYYYmm_dt:
                YYYYmm_df = vsdb_df
                df_name = 'VSDB'
            elif YYYYmm_dt >= metplus_start_YYYYmm_dt:
                YYYYmm_df = metplus_df
                df_name = 'MP'
            YYYYmm_line = YYYYmm_df.loc[
                (YYYYmm_df['YEAR'] == YYYYmm[0:4])
                 & (YYYYmm_df['MONTH'] == YYYYmm[4:])
            ]
            if len(YYYYmm_line) == 0:
                merged_df.loc[(model,YYYYmm)] = (
                    [df_name, YYYYmm[0:4], YYYYmm[4:]] + (17*[np.nan])
                )
            else:
                merged_df.loc[(model,YYYYmm)] = YYYYmm_line.values
        if model_list.index(model) == 0:
            all_model_merged_df = merged_df
        else:
            all_model_merged_df = pd.concat([all_model_merged_df, merged_df])
    return all_model_merged_df

def create_plots(all_model_merged_df, var, level, vx_mask, model_list,
                 model_plot_name_list, valid_hour, stat,
                 all_YYYYmm_dt_list, forecast_days, running_mean, run_length,
                 output_dir):
    print("-> Creating Plots")
    all_model_running_mean_df = pd.DataFrame(
        index=all_model_merged_df.index,
        columns=all_model_merged_df.columns[3:3+len(forecast_days)]
    )
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
    ymesh, xmesh = np.meshgrid(all_YYYYmm_dt_list, forecast_days)
    YYYYmm = f"{all_YYYYmm_dt_list[-1]:%Y%m}"
    # Make time series plots for each forecast day
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
    plt.rcParams['figure.subplot.top'] = 0.925
    plt.rcParams['figure.subplot.bottom'] = 0.075
    plt.rcParams['legend.handletextpad'] = 0.25
    plt.rcParams['legend.handlelength'] = 1.25
    plt.rcParams['legend.borderaxespad'] = 0
    plt.rcParams['legend.columnspacing'] = 1.0
    plt.rcParams['legend.frameon'] = False
    x_figsize, y_figsize = 14, 14
    legend_bbox_x, legend_bbox_y = 0.5, 0.05
    legend_fontsize = 15
    legend_loc = 'center'
    title_loc = 'center'
    noaa_logo_xpixel_loc = (x_figsize*plt.rcParams['figure.dpi']*0.1)
    noaa_logo_ypixel_loc = (y_figsize*plt.rcParams['figure.dpi']*0.9325)
    noaa_logo_alpha = 0.5
    nws_logo_xpixel_loc = (x_figsize*plt.rcParams['figure.dpi']*0.9)
    nws_logo_ypixel_loc = (y_figsize*plt.rcParams['figure.dpi']*0.9325)
    nws_logo_alpha = 0.5
    for forecast_day in forecast_days:
        stat_min_max_dict = {
            'ax1_stat_min': np.ma.masked_invalid(np.nan),
            'ax1_stat_max': np.ma.masked_invalid(np.nan),
            'ax2_stat_min': np.ma.masked_invalid(np.nan),
            'ax2_stat_max': np.ma.masked_invalid(np.nan)
        }
        forecast_day_all_model_merged_df = (
            all_model_merged_df.loc[:]['DAY'+str(forecast_day)]
        )
        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=(x_figsize, y_figsize),
            sharex=True
        )
        ax1.grid(True)
        ax1.set_xlim([all_YYYYmm_dt_list[0], all_YYYYmm_dt_list[-1]])
        ax1.set_xticks(all_YYYYmm_dt_list[::24])
        ax1.xaxis.set_major_formatter(md.DateFormatter('%Y'))
        ax1.xaxis.set_minor_locator(md.MonthLocator())
        ax1.set_ylabel(str(running_mean)+' Month Running Mean')
        ax2.grid(True)
        ax2.set_xlim([all_YYYYmm_dt_list[0], all_YYYYmm_dt_list[-1]])
        ax2.set_xticks(all_YYYYmm_dt_list[::24])
        ax2.xaxis.set_major_formatter(md.DateFormatter('%Y'))
        ax2.xaxis.set_minor_locator(md.MonthLocator())
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Difference')
        ax2.set_title('Difference from '+model_plot_name_list[0], loc='left')
        for model in model_list:
            model_plot_name = model_plot_name_list[model_list.index(model)]
            model_monthly_mean_values = (
                forecast_day_all_model_merged_df.loc[model].values
            )
            masked_model_monthly_mean_values = np.ma.masked_invalid(
                np.array(model_monthly_mean_values, dtype=float)
            )
            model_running_mean_values = (
                np.ones_like(model_monthly_mean_values) * np.nan
            )
            for m in range(len(masked_model_monthly_mean_values)):
                start = m-int(running_mean/2)
                end = m+int(running_mean/2)
                if start >= 0 and end < len(model_monthly_mean_values):
                    if np.ma.count_masked(
                            masked_model_monthly_mean_values[start:end+1]
                    ) == 0:
                        model_running_mean_values[m] = (
                            masked_model_monthly_mean_values[start:end+1] \
                            .mean()
                        )
            all_model_running_mean_df['DAY'+str(forecast_day)].loc[model] = (
                model_running_mean_values
            )
            masked_model_running_mean_values = np.ma.masked_invalid(
                np.array(model_running_mean_values, dtype=float)
            )
            all_YYYYmm_dt_list_rm_mask = np.ma.array(
                all_YYYYmm_dt_list,
                mask=np.ma.getmaskarray(masked_model_running_mean_values)
            )
            count_for_mean = (
                len(masked_model_running_mean_values[-13:])
                -np.ma.count_masked(masked_model_running_mean_values[-13:])
            )
            count = (
                len(masked_model_running_mean_values)
                -np.ma.count_masked(masked_model_running_mean_values)
            )
            if count != 0:
                if count_for_mean != 0:
                    if np.abs(masked_model_running_mean_values[-13:].mean()) \
                           >= 10:
                        mean_for_label = round(
                           masked_model_running_mean_values[-13:].mean(), 2
                        )
                        mean_for_label = f"{mean_for_label:.2f}"
                    else:
                        mean_for_label = round(
                            masked_model_running_mean_values[-13:].mean(), 3
                        )
                        mean_for_label = f"{mean_for_label:.3f}"
                else:
                    mean_for_label = '--'
                ax1.plot_date(
                    all_YYYYmm_dt_list_rm_mask,
                    masked_model_running_mean_values,
                    color=models_plot_colors_dict[model],
                    linestyle='solid', linewidth=2,
                    marker=None, markersize=0,
                    zorder=((len(model_list)-model_list.index(model))+4),
                    label=model_plot_name+' '+str(mean_for_label)
                )
                if masked_model_running_mean_values.min() \
                        < stat_min_max_dict['ax1_stat_min'] \
                        or np.ma.is_masked(stat_min_max_dict['ax1_stat_min']):
                    stat_min_max_dict['ax1_stat_min'] = (
                        masked_model_running_mean_values.min()
                    )
                if masked_model_running_mean_values.max() > \
                        stat_min_max_dict['ax1_stat_max'] \
                        or np.ma.is_masked(stat_min_max_dict['ax1_stat_max']):
                    stat_min_max_dict['ax1_stat_max'] = (
                        masked_model_running_mean_values.max()
                    )
            if model == model_list[0]:
                masked_model1_running_mean_values = (
                    masked_model_running_mean_values
                )
                ax2.plot_date(
                    all_YYYYmm_dt_list, np.zeros_like(all_YYYYmm_dt_list),
                    color=models_plot_colors_dict[model],
                    linestyle='solid', linewidth=2,
                    marker=None, markersize=0,
                    zorder=((len(model_list)-model_list.index(model))+4)
                )
            all_YYYYmm_dt_list_rm_diff_mask = np.ma.array(
                all_YYYYmm_dt_list,
                mask=np.ma.getmaskarray(
                    masked_model_running_mean_values
                    -masked_model1_running_mean_values)
            )
            ax2.plot_date(
                all_YYYYmm_dt_list_rm_diff_mask,
                (masked_model_running_mean_values
                 -masked_model1_running_mean_values),
                color=models_plot_colors_dict[model],
                linestyle='solid', linewidth=2,
                marker=None, markersize=0,
                zorder=((len(model_list)-model_list.index(model))+4)
            )
            if (masked_model_running_mean_values
                    -masked_model1_running_mean_values).min() \
                    < stat_min_max_dict['ax2_stat_min'] \
                    or np.ma.is_masked(stat_min_max_dict['ax2_stat_min']):
                stat_min_max_dict['ax2_stat_min'] = (
                    masked_model_running_mean_values
                    -masked_model1_running_mean_values
                ).min()
            if (masked_model_running_mean_values
                    -masked_model1_running_mean_values).max() \
                    > stat_min_max_dict['ax2_stat_max'] \
                    or np.ma.is_masked(stat_min_max_dict['ax2_stat_max']):
                stat_min_max_dict['ax2_stat_max'] = (
                    masked_model_running_mean_values
                    -masked_model1_running_mean_values
                ).max()
        subplot_num = 1
        for ax in fig.get_axes():
            stat_min = stat_min_max_dict['ax'+str(subplot_num)+'_stat_min']
            stat_max = stat_min_max_dict['ax'+str(subplot_num)+'_stat_max']
            preset_y_axis_tick_min = ax.get_yticks()[0]
            preset_y_axis_tick_max = ax.get_yticks()[-1]
            preset_y_axis_tick_inc = (ax.get_yticks()[1]-ax.get_yticks()[0])
            if stat == 'acc' and subplot_num == 1:
                y_axis_tick_inc = 0.1
            else:
                y_axis_tick_inc = preset_y_axis_tick_inc
            if np.ma.is_masked(stat_min):
                y_axis_min = preset_y_axis_tick_min
            else:
                if stat == 'acc' and subplot_num == 1:
                    y_axis_min = (round(stat_min,1)-y_axis_tick_inc)
                else:
                    y_axis_min = preset_y_axis_tick_min
            while y_axis_min > stat_min:
                y_axis_min = y_axis_min - y_axis_tick_inc
            if np.ma.is_masked(stat_max):
                y_axis_max = preset_y_axis_tick_max
            else:
                if stat == 'acc' and subplot_num == 1:
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
            if subplot_num == 1:
                stat_min1 = stat_min
                y_axis_min1 = y_axis_min
                y_axis_max1 = y_axis_max
                y_axis_tick_inc1 = y_axis_tick_inc
            subplot_num+=1
        var_info_title = plot_title.get_var_info_title(var, level)
        vx_mask_title = plot_title.get_vx_mask_title(vx_mask)
        forecast_lead_title = plot_title.get_lead_title(str(forecast_day*24))
        if valid_hour == '':
            ax1.set_title(
                stat_title+'\n'
                +var_info_title+', '+vx_mask_title+'\n'
                +'valid '+f"{all_YYYYmm_dt_list[0]:%b%Y}"+'-'
                +f"{all_YYYYmm_dt_list[-1]:%b%Y}"+', '
                +forecast_lead_title+',\n'
                +str(running_mean)+' Month Running Mean', loc=title_loc
            )
        else:
            ax1.set_title(
                stat_title+'\n'
                +var_info_title+', '+vx_mask_title+'\n'
                +'valid '+f"{all_YYYYmm_dt_list[0]:%b%Y}"+'-'
                +f"{all_YYYYmm_dt_list[-1]:%b%Y}"+' '+valid_hour+', '
                +forecast_lead_title+',\n'
                +str(running_mean)+' Month Running Mean', loc=title_loc
            )
        fig.figimage(
            noaa_logo_img_array, noaa_logo_xpixel_loc,
            noaa_logo_ypixel_loc, zorder=1, alpha=noaa_logo_alpha
        )
        fig.figimage(
            nws_logo_img_array, nws_logo_xpixel_loc,
            nws_logo_ypixel_loc, zorder=1, alpha=nws_logo_alpha
        )
        ax.text(
            0.5, 0.09,
            all_YYYYmm_dt_list[-13:][0].strftime('%b%Y')+'-'
            +all_YYYYmm_dt_list[-13:][-1].strftime('%b%Y')+' Mean',
            fontsize=16, ha='center', va='center', transform=ax1.transAxes
        )
        if len(ax.lines) != 0:
            legend = ax1.legend(
                bbox_to_anchor=(legend_bbox_x, legend_bbox_y),
                loc=legend_loc, ncol=len(model_list), fontsize=legend_fontsize
            )
            plt.draw()
            legend_box = (
                legend.get_window_extent().inverse_transformed(ax1.transData)
            )
            if stat_min1 < legend_box.y1:
                while stat_min1 < legend_box.y1:
                    y_axis_min1 = y_axis_min1 - y_axis_tick_inc1
                    ax1.set_yticks(
                        np.arange(y_axis_min1,
                                  y_axis_max1+y_axis_tick_inc1,
                                  y_axis_tick_inc1)
                    )
                    ax1.set_ylim([y_axis_min1, y_axis_max1])
                    legend = ax1.legend(
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
                model_group+'_'+stat+'_'+var+'_'+level
                +'_fday'+str(forecast_day)+'_G002'+vx_mask
                +'_'+run_length+'.png'
            )
        else:
            savefig_name = os.path.join(
                output_dir,
                model_group+'_'+stat+'_valid'+valid_hour+'_'+var+'_'+level
                +'_fday'+str(forecast_day)+'_G002'+vx_mask
                +'_'+run_length+'.png'
            )
        print(savefig_name)
        plt.savefig(savefig_name)
        plt.close()
    # Make lead-year plots
    plt.rcParams['font.weight'] = 'bold'
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.titlepad'] = 5
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.labelpad'] = 10
    plt.rcParams['axes.formatter.useoffset'] = False
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['xtick.major.pad'] = 5
    plt.rcParams['ytick.major.pad'] = 5
    plt.rcParams['ytick.labelsize'] = 14
    plt.rcParams['figure.subplot.left'] = 0.1
    plt.rcParams['figure.subplot.right'] = 0.95
    plt.rcParams['figure.titleweight'] = 'bold'
    plt.rcParams['figure.titlesize'] = 16
    if stat == 'acc':
        cmap = plt.cm.BuPu_r
        cmap_diff_original = plt.cm.bwr_r
    elif stat == 'bias':
        cmap_original = plt.cm.PiYG_r
        colors = cmap_original(
            np.append(np.linspace(0,0.3,10), np.linspace(0.7,1,10))
        )
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
            'cmap_bias', colors
        )
        cmap_diff_original = plt.cm.bwr
    elif stat == 'rmse':
        cmap = plt.cm.BuPu_r
        cmap_diff_original = plt.cm.bwr
    else:
        cmap = plt.cm.BuPu_r
        cmap_diff_original = plt.cm.bwr
    colors_diff = cmap_diff_original(
        np.append(np.linspace(0,0.425,10), np.linspace(0.575,1,10))
    )
    cmap_diff = matplotlib.colors.LinearSegmentedColormap.from_list(
        'cmap_diff', colors_diff
    )
    nsubplots = len(model_list)
    if nsubplots == 1:
        x_figsize, y_figsize = 14, 7
        row, col = 1, 1
        hspace, wspace = 0, 0
        bottom, top = 0.175, 0.825
        suptitle_y_loc = 0.92125
        noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.865
        nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.865
        cbar_bottom = 0.06
        cbar_height = 0.02
    elif nsubplots == 2:
        x_figsize, y_figsize = 14, 7
        row, col = 1, 2
        hspace, wspace = 0, 0.1
        bottom, top = 0.175, 0.825
        suptitle_y_loc = 0.92125
        noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.865
        nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.865
        cbar_bottom = 0.06
        cbar_height = 0.02
    elif nsubplots > 2 and nsubplots <= 4:
        x_figsize, y_figsize = 14, 14
        row, col = 2, 2
        hspace, wspace = 0.15, 0.1
        bottom, top = 0.125, 0.9
        suptitle_y_loc = 0.9605
        noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
        nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
        cbar_bottom = 0.03
        cbar_height = 0.02
    elif nsubplots > 4 and nsubplots <= 6:
        x_figsize, y_figsize = 14, 14
        row, col = 3, 2
        hspace, wspace = 0.15, 0.1
        bottom, top = 0.125, 0.9
        suptitle_y_loc = 0.9605
        noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
        nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
        cbar_bottom = 0.03
        cbar_height = 0.02
    elif nsubplots > 6 and nsubplots <= 8:
        x_figsize, y_figsize = 14, 14
        row, col = 4, 2
        hspace, wspace = 0.175, 0.1
        bottom, top = 0.125, 0.9
        suptitle_y_loc = 0.9605
        noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
        nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
        cbar_bottom = 0.03
        cbar_height = 0.02
    elif nsubplots > 8 and nsubplots <= 10:
        x_figsize, y_figsize = 14, 14
        row, col = 5, 2
        hspace, wspace = 0.225, 0.1
        bottom, top = 0.125, 0.9
        suptitle_y_loc = 0.9605
        noaa_logo_x_scale, noaa_logo_y_scale = 0.1, 0.9325
        nws_logo_x_scale, nws_logo_y_scale = 0.9, 0.9325
        cbar_bottom = 0.03
        cbar_height = 0.02
    else:
        print('Too many subplots selected, max. is 10')
        exit(1)
    suptitle_x_loc = (
        plt.rcParams['figure.subplot.left']+plt.rcParams['figure.subplot.right']
    )/2.
    fig = plt.figure(figsize=(x_figsize, y_figsize))
    gs = gridspec.GridSpec(
        row, col,
        bottom = bottom, top = top,
        hspace = hspace, wspace = wspace,
    )
    noaa_logo_xpixel_loc = (
        x_figsize * plt.rcParams['figure.dpi'] * noaa_logo_x_scale
    )
    noaa_logo_ypixel_loc = (
        y_figsize * plt.rcParams['figure.dpi'] * noaa_logo_y_scale
    )
    nws_logo_xpixel_loc = (
        x_figsize * plt.rcParams['figure.dpi'] * nws_logo_x_scale
    )
    nws_logo_ypixel_loc = (
        y_figsize * plt.rcParams['figure.dpi'] * nws_logo_y_scale
    )
    subplot_num = 0
    while subplot_num < nsubplots:
        ax = plt.subplot(gs[subplot_num])
        ax.grid(True)
        ax.set_xticks(forecast_days)
        ax.set_xticklabels(forecast_days)
        ax.set_xlim([forecast_days[0], forecast_days[-1]])
        if ax.is_last_row() \
                or (nsubplots % 2 != 0 and subplot_num == nsubplots -1):
            ax.set_xlabel('Forecast Day')
        else:
            plt.setp(ax.get_xticklabels(), visible=False)
        ax.set_ylim([all_YYYYmm_dt_list[0], all_YYYYmm_dt_list[-1]])
        ax.set_yticks(all_YYYYmm_dt_list[::24])
        ax.yaxis.set_major_formatter(md.DateFormatter('%Y'))
        if ax.is_first_col():
            ax.set_ylabel('Year')
        else:
            plt.setp(ax.get_yticklabels(), visible=False)
        subplot_num+=1
    get_clevels = True
    make_colorbar = False
    for model in model_list:
        model_plot_name = model_plot_name_list[model_list.index(model)]
        model_running_mean = np.ma.masked_invalid(
            all_model_running_mean_df.loc[model].to_numpy(dtype=float).T
        )
        model_idx = model_list.index(model)
        ax = plt.subplot(gs[model_idx])
        if model_idx == 0:
            ax.set_title(model_plot_name, loc='left')
            model1_plot_name = model_plot_name
            model1_running_mean = model_running_mean
            if not model1_running_mean.mask.all():
                if stat in ['acc', 'bias', 'rmse']:
                    if stat == 'acc':
                        levels = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                                           0.7, 0.8, 0.9, 0.95, 0.99, 1])
                    elif stat == 'bias':
                        if np.max(np.abs(model1_running_mean)) > 100:
                            spacing = 2.25
                        elif np.max(np.abs(model1_running_mean)) > 10:
                            spacing = 2
                        else:
                            spacing = 1.75
                        levels = plot_util.get_clevels(
                            model1_running_mean, spacing
                        ) 
                    elif stat == 'rmse':
                        cmax = np.nanmax(model1_running_mean)
                        steps = 12
                        dx = 1.0 / (steps-1)
                        if cmax > 100:
                            spacing = 2.25
                        elif cmax > 10:
                            spacing = 2
                        else:
                            spacing = 1.75
                        levels = np.array(
                            [0+(i*dx)**spacing*cmax for i in range(steps)],
                            dtype=float
                        )
                    CF1 = ax.contourf(xmesh, ymesh, model1_running_mean,
                                      levels=levels, cmap=cmap, extend='both')
                else:
                    CF1 = ax.contourf(xmesh, ymesh, model1_running_mean,
                                      cmap=cmap, extend='both')
                C1 = ax.contour(xmesh, ymesh, model1_running_mean,
                                levels=CF1.levels, colors='k', linewidths=1.0)
                C1_labels_list = []
                for clevel in C1.levels:
                    if str(clevel).split('.')[1] == '0':
                        C1_labels_list.append(str(int(clevel)))
                    else:
                        C1_labels_list.append(str(round(clevel,3)).rstrip('0'))
                fmt = {}
                for lev, label in zip(C1.levels, C1_labels_list):
                    fmt[lev] = label
                ax.clabel(C1, C1.levels, fmt=fmt, inline=True, fontsize=12.5)
        else:
            ax.set_title(model_plot_name+'-'+model1_plot_name, loc='left')
            model_model1_diff = model_running_mean - model1_running_mean
            if not model_model1_diff.mask.all():
                if get_clevels:
                    if stat in ['acc']:
                        clevels_diff = np.array(
                            [-0.5, -0.4, -0.3, -0.2, -0.1, -0.05,
                             0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
                        )
                    else:
                        clevels_diff = plot_util.get_clevels(model_model1_diff,
                                                             1.25)
                    CF2 = ax.contourf(
                        xmesh, ymesh, model_model1_diff,
                        levels=clevels_diff, cmap=cmap_diff,
                        locator=matplotlib.ticker.MaxNLocator(symmetric=True),
                        extend='both'
                    )
                    get_clevels = False
                    make_colorbar = True
                    colorbar_CF = CF2
                    colorbar_CF_ticks = CF2.levels
                    colorbar_label = 'Difference'
                else:
                    CF = ax.contourf(
                        xmesh, ymesh, model_model1_diff,
                        levels=CF2.levels, cmap=cmap_diff,
                        locator=matplotlib.ticker.MaxNLocator(symmetric=True),
                        extend='both'
                    )
    var_info_title = plot_title.get_var_info_title(var, level)
    vx_mask_title = plot_title.get_vx_mask_title(vx_mask)
    if valid_hour == '':
        fig.suptitle(
            stat_title+'\n'
            +var_info_title+', '+vx_mask_title+'\n'
            +'valid '+f"{all_YYYYmm_dt_list[0]:%b%Y}"+'-'
            +f"{all_YYYYmm_dt_list[-1]:%b%Y}"+'\n'
            +str(running_mean)+' Month Running Mean',
            x=suptitle_x_loc, y=suptitle_y_loc,
            horizontalalignment=title_loc, verticalalignment=title_loc
        )
    else:
        fig.suptitle(
            stat_title+'\n'
            +var_info_title+', '+vx_mask_title+'\n'
            +'valid '+f"{all_YYYYmm_dt_list[0]:%b%Y}"+'-'
            +f"{all_YYYYmm_dt_list[-1]:%b%Y}"+' '+valid_hour+'\n'
            +str(running_mean)+' Month Running Mean',
            x=suptitle_x_loc, y=suptitle_y_loc,
            horizontalalignment=title_loc, verticalalignment=title_loc
        )
    noaa_img = fig.figimage(
        noaa_logo_img_array, noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
        zorder=1, alpha=noaa_logo_alpha
    )
    nws_img = fig.figimage(
        nws_logo_img_array, nws_logo_xpixel_loc, nws_logo_ypixel_loc,
        zorder=1, alpha=nws_logo_alpha
    )
    plt.subplots_adjust(
        left = noaa_img.get_extent()[1] \
            /(plt.rcParams['figure.dpi']*x_figsize),
        right = nws_img.get_extent()[0] \
            /(plt.rcParams['figure.dpi']*x_figsize)
    )
    if make_colorbar:
        cbar_left =(
            noaa_img.get_extent()[1]/
            (plt.rcParams['figure.dpi']*x_figsize)
        )
        cbar_width = (              
            nws_img.get_extent()[0]
            /(plt.rcParams['figure.dpi']*x_figsize)
            - noaa_img.get_extent()[1]
            /(plt.rcParams['figure.dpi']*x_figsize)
        )
        cax = fig.add_axes(
            [cbar_left, cbar_bottom, cbar_width, cbar_height]
        )
        cbar = fig.colorbar(
            colorbar_CF, cax = cax,
            orientation = 'horizontal',
            ticks = colorbar_CF_ticks
        )
        cbar.ax.set_xlabel(colorbar_label, labelpad = 0)
        cbar.ax.xaxis.set_tick_params(pad=0)
        cbar_tick_labels_list = []
        for tick in cbar.get_ticks():
            if str(tick).split('.')[1] == '0':
                cbar_tick_labels_list.append(str(int(tick)))
            else:
                cbar_tick_labels_list.append(str(round(tick,3)).rstrip('0'))
        cbar.ax.set_xticklabels(cbar_tick_labels_list)
    if valid_hour == '':
        savefig_name = os.path.join(
            output_dir,
            model_group+'_'+stat+'_'+var+'_'+level
            +'_leadyear_G002'+vx_mask+'_'+run_length+'.png'
        )
    else:
        savefig_name = os.path.join(
            output_dir,
            model_group+'_'+stat+'_valid'+valid_hour+'_'+var+'_'+level
            +'_leadyear_G002'+vx_mask+'_'+run_length+'.png'
        )
    print(savefig_name)
    plt.savefig(savefig_name)
    plt.clf()
    plt.close('all')
    # Make annual mean plots
    if nsubplots == 1:
        x_legend, y_legend, legend_factor = 0.925, 0.8275, 0.025
        legend_fontsize = 12
    elif nsubplots == 2:
        x_legend, y_legend, legend_factor = 0.925, 0.8275, 0.025
        legend_fontsize = 12
    elif nsubplots > 2 and nsubplots <= 4:
        x_legend, y_legend, legend_factor = 0.95, 0.9, 0.02
        legend_fontsize = 18
    elif nsubplots > 4 and nsubplots <= 6:
        x_legend, y_legend, legend_factor = 0.95, 0.9, 0.02
        legend_fontsize = 18
    elif nsubplots > 6 and nsubplots <= 8:
        x_legend, y_legend, legend_factor = 0.95, 0.9, 0.02
        legend_fontsize = 18
    elif nsubplots > 8 and nsubplots <= 10:
        x_legend, y_legend, legend_factor = 0.95, 0.9, 0.02
        legend_fontsize = 18
    else:
        print('Too many subplots selected, max. is 10')
        exit(1)

    stat_min = np.ma.masked_invalid(np.nan)
    stat_max = np.ma.masked_invalid(np.nan)
    cmap_colors = plt.cm.get_cmap('viridis_r')
    fig = plt.figure(figsize=(x_figsize, y_figsize))
    gs = gridspec.GridSpec(
        row, col,
        bottom = bottom, top = top,
        hspace = hspace, wspace = wspace,
    )
    for model in model_list:
        model_plot_name = model_plot_name_list[model_list.index(model)]
        model_idx = model_list.index(model)
        ax = plt.subplot(gs[model_idx])
        ax.set_title(model_plot_name, loc='left')
        model_groupby_year = (
            all_model_merged_df.loc[model].groupby('YEAR')
        )
        base_year = all_model_merged_df['YEAR'].iloc[0]
        if model == model_list[0]:
            years_plot_colors_dict = {}
            cmap_color_inc = int(cmap_colors.N/len(model_groupby_year)-1)
            for year, model_year_df in model_groupby_year:
                if year == YYYYmm[0:4]:
                    years_plot_colors_dict[year] = '#000000'
                else:
                    years_plot_colors_dict[year] = matplotlib.colors.rgb2hex(
                        cmap_colors(
                            (int(year)-int(base_year))*cmap_color_inc
                        )
                    )
        for year, model_year_df in model_groupby_year:
            model_year_forecast_day_mean_values = (
                model_year_df.iloc[:,3:3+len(forecast_days)] \
                .astype('float').mean().values
            )
            masked_model_year_forecast_day_mean_values = np.ma.masked_invalid(
                model_year_forecast_day_mean_values
            )
            forecast_days_mask = np.ma.array(
                forecast_days,
                mask=np.ma.getmaskarray(
                    masked_model_year_forecast_day_mean_values
                )
            )
            ax.plot(
                forecast_days_mask,
                masked_model_year_forecast_day_mean_values,
                color=years_plot_colors_dict[year],
                linestyle='solid', linewidth=2,
                marker=None, markersize=0,
            )
            if masked_model_year_forecast_day_mean_values.min() < stat_min \
                    or np.ma.is_masked(stat_min):
                stat_min = masked_model_year_forecast_day_mean_values.min()
            if masked_model_year_forecast_day_mean_values.max()  > stat_max \
                    or np.ma.is_masked(stat_max):
                stat_max = masked_model_year_forecast_day_mean_values.max()
    preset_y_axis_tick_min = ax.get_yticks()[0]
    preset_y_axis_tick_max = ax.get_yticks()[-1]
    preset_y_axis_tick_inc = ax.get_yticks()[1]- ax.get_yticks()[0]
    if stat == 'acc':
        y_axis_tick_inc = 0.1
    else:
        y_axis_tick_inc = preset_y_axis_tick_inc
    if np.ma.is_masked(stat_min):
        y_axis_min = preset_y_axis_tick_min
    else:
        if stat == 'acc':
            y_axis_min = (round(stat_min,1) - y_axis_tick_inc)
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
            y_axis_max = preset_y_axis_tick_max + y_axis_tick_inc
            while y_axis_max < stat_max:
                y_axis_max = y_axis_max + y_axis_tick_inc
    y_ticks = np.arange(y_axis_min,
                        y_axis_max+y_axis_tick_inc,
                        y_axis_tick_inc)
    subplot_num = 0
    while subplot_num < nsubplots:
        ax = plt.subplot(gs[subplot_num])
        ax.grid(True)
        ax.set_xticks(forecast_days)
        ax.set_xticklabels(forecast_days)
        ax.set_xlim([forecast_days[0], forecast_days[-1]])
        if ax.is_last_row() or (nsubplots % 2 != 0 \
                and subplot_num == nsubplots -1):
            ax.set_xlabel('Forecast Day')
        else:
            plt.setp(ax.get_xticklabels(), visible=False)
        ax.set_yticks(y_ticks)
        ax.set_ylim([y_axis_min, y_axis_max])
        if ax.is_first_col():
            ax.set_ylabel('Mean')
        else:
            plt.setp(ax.get_yticklabels(), visible=False)
        subplot_num+=1
    var_info_title = plot_title.get_var_info_title(var, level)
    vx_mask_title = plot_title.get_vx_mask_title(vx_mask)
    if valid_hour == '':
        fig.suptitle(
            stat_title+'\n'
            +var_info_title+', '+vx_mask_title+'\n'
            +'valid '+f"{all_YYYYmm_dt_list[0]:%b%Y}"+'-'
            +f"{all_YYYYmm_dt_list[-1]:%b%Y}",
            x=suptitle_x_loc, y=suptitle_y_loc,
            horizontalalignment=title_loc, verticalalignment=title_loc
        )
    else:
        fig.suptitle(
            stat_title+'\n'
            +var_info_title+', '+vx_mask_title+'\n'
            +'valid '+f"{all_YYYYmm_dt_list[0]:%b%Y}"+'-'
            +f"{all_YYYYmm_dt_list[-1]:%b%Y}"+' '+valid_hour,
            x=suptitle_x_loc, y=suptitle_y_loc,
            horizontalalignment=title_loc, verticalalignment=title_loc
        )
    noaa_img = fig.figimage(
        noaa_logo_img_array, noaa_logo_xpixel_loc, noaa_logo_ypixel_loc,
        zorder=1, alpha=noaa_logo_alpha
    )
    nws_img = fig.figimage(
        nws_logo_img_array, nws_logo_xpixel_loc, nws_logo_ypixel_loc,
        zorder=1, alpha=nws_logo_alpha
    )
    plt.subplots_adjust(
        left = noaa_img.get_extent()[1] \
            /(plt.rcParams['figure.dpi']*x_figsize),
        right = nws_img.get_extent()[0] \
            /(plt.rcParams['figure.dpi']*x_figsize)
    )
    for year in list(years_plot_colors_dict.keys()):
        plt.text(
            x_legend, y_legend-((int(year)-int(base_year))
                                 *legend_factor),
            year, fontsize=legend_fontsize, ha='center', va='top',
            color=years_plot_colors_dict[year],
            transform=fig.transFigure
        )
    if valid_hour == '':
        savefig_name = os.path.join(
            output_dir,
            model_group+'_'+stat+'_'+var+'_'+level
            +'_annualmeans_'+'G002'+vx_mask+'_'+run_length+'.png'
        )    
    else:
        savefig_name = os.path.join(
            output_dir,
            model_group+'_'+stat+'_valid'+valid_hour+'_'+var+'_'+level
            +'_annualmeans_'+'G002'+vx_mask+'_'+run_length+'.png'
        )
    print(savefig_name)
    plt.savefig(savefig_name)
    plt.clf()
    plt.close('all')

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
        working_dir, 'plots_monthly_means_'
        +plot_model_group_var.replace('/', '_')
    )
    if not os.path.exists(model_group_var_output_dir):
        os.makedirs(model_group_var_output_dir)
    print("")
    print("Output: "+model_group_var_output_dir)
    print("\n")
    # Set up dates
    if model_group == 'gfs_4cycles':
        start_YYYYmm = '200301'
    elif model_group == 'all_models' and var == 'UGRD_VGRD':
        start_YYYYmm = '201001'
    else:
        start_YYYYmm = start_YYYYmm_in
    all_YYYYmm_dt_list = list(
        dateutil.rrule.rrule(
            dateutil.rrule.MONTHLY,
            dtstart=dateutil.parser.parse(start_YYYYmm+'01T000000'),
            until=dateutil.parser.parse(end_YYYYmm+'01T000000')
        )
    )
    # Loop over run length, level, vx_mask, stat
    for run_length in ['allyears', 'past10years']:
        if run_length == 'allyears':
            run_length_running_mean = 3
            run_length_YYYYmm_dt_list = all_YYYYmm_dt_list
        elif run_length == 'past10years':
            run_length_running_mean = 1
            run_length_YYYYmm_dt_list = (
                all_YYYYmm_dt_list[len(all_YYYYmm_dt_list)-121:]
            )
        for level in level_list:
            for vx_mask in vx_mask_list:
                for stat in stat_list:
                    print("---> "+run_length+" "+level+" "+vx_mask+" "+stat)
                    model_group_var_merged_df = create_merged_dataset(
                        var, level, vx_mask, model_list, valid_hour, stat,
                        run_length_YYYYmm_dt_list
                    )
                    forecast_days = np.arange(0,11,1)
                    create_plots(model_group_var_merged_df, var, level,
                                 vx_mask, model_list, model_plot_name_list,
                                 valid_hour, stat, run_length_YYYYmm_dt_list,
                                 forecast_days, run_length_running_mean,
                                 run_length, model_group_var_output_dir)
