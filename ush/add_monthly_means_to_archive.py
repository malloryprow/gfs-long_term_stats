import os
import numpy as np
import datetime
import calendar
import glob
import pandas as pd

YYYYmm = os.environ['YYYYmm']
working_dir = os.environ['working_dir']

# Set long term stats directory
long_term_stats_dir = ('/lfs/h2/emc/vpppg/save/emc.vpppg/verification'
                       +'/global/long_term_stats')

# Set information
model_info_dict = {
    'gfs': {
        'obs_name': 'gfs_anl',
        'hour_list': ['00', '06', '12', '18']
    },
    'ecm': {
        'obs_name': 'ecm_f00',
        'hour_list': ['00', '12']
    },
    'cmc': {
        'obs_name': 'cmc_f00',
        'hour_list': ['00', '12']
    },
    'fno': {
        'obs_name': 'fno_f00',
        'hour_list': ['00', '12']
    },
    'cdas': {
        'obs_name': 'cdas_f00',
        'hour_list': ['00']
    },
    'ukm': {
        'obs_name': 'ukm_f00',
        'hour_list': ['00', '12']
    },
    'jma': {
        'obs_name': 'jma_f00',
        'hour_list': ['00', '12']
    },
    'cfsr': {
        'obs_name': 'cfsr_anl',
        'hour_list': ['00']
    }
}

# Set statistics information
var_list = ['HGT', 'TMP', 'UGRD', 'VGRD', 'UGRD_VGRD']
vx_mask_list = ['G002', 'NHX', 'SHX', 'TRO', 'PNA']
stat_dict = {'anom': ['acc'],
             'pres': ['bias', 'rmse']}

# File header
file_header_list = [
    'SYS', 'YEAR', 'MONTH', 'DAY0', 'DAY1', 'DAY2', 'DAY3', 'DAY4',
    'DAY5', 'DAY6', 'DAY7', 'DAY8', 'DAY9', 'DAY10', 'DAY11', 'DAY12',
    'DAY13', 'DAY14', 'DAY15', 'DAY16'
]

# Set month start and end dates
start_date_dt = datetime.datetime.strptime(YYYYmm+'01', '%Y%m%d')
end_date_dt = datetime.datetime.strptime(
    YYYYmm+str(calendar.monthrange(int(YYYYmm[0:4]), int(YYYYmm[4:]))[1]),
    '%Y%m%d'
)
expected_dates_dt = np.arange(start_date_dt,
                              end_date_dt+datetime.timedelta(days=1),
                              datetime.timedelta(days=1)) \
                              .astype(datetime.datetime)

# Read files from running EMC_verif-global and write to monthly mean file
for model in list(model_info_dict.keys()):
    model_obs_name = model_info_dict[model]['obs_name']
    model_hour_list = model_info_dict[model]['hour_list']
    for hour in model_hour_list:
        model_hour_base_dir = os.path.join(
            working_dir, 'verif_global_monthly_mean_'+model+'_'+hour+'Z'
        )
        model_hour_plot_by_dir = glob.glob(
            os.path.join(model_hour_base_dir, 'tmp', 'verif_global.*',
                         'grid2grid_step2', 'metplus_output', 'plot_by_VALID')
        )[0]
        for stat_type in list(stat_dict.keys()):
            stat_list = stat_dict[stat_type]
            for var in var_list:
                if stat_type == 'anom':
                    if var == 'HGT':
                        level_list = ['P1000', 'P700', 'P500', 'P250']
                    else:
                        level_list = ['P850', 'P500', 'P250']
                    if var == 'UGRD_VGRD':
                       line_type = 'VAL1L2'
                    else:
                       line_type = 'SAL1L2'
                elif stat_type == 'pres':
                    level_list = ['P1000', 'P850', 'P500',
                                  'P200', 'P100', 'P20']
                    if var == 'UGRD_VGRD':
                       line_type = 'VL1L2'
                    else:
                       line_type = 'SL1L2'
                for level in level_list:
                    for vx_mask in vx_mask_list:
                        for stat in stat_list:
                            long_term_monthly_mean_file_name = os.path.join(
                                long_term_stats_dir, 'long_term_archive',
                                'long_term', 'monthly_means', model, hour+'Z',
                                'metplus_'+stat.upper()+'_'+var+'_'+level+'_'
                                +vx_mask+'.txt'
                            )
                            print(long_term_monthly_mean_file_name)
                            # Read long term monthly mean file if it exists,
                            # if not create and write header
                            if not os.path.exists(
                                    long_term_monthly_mean_file_name
                                    ):
                                with open(long_term_monthly_mean_file_name,
                                          'w') \
                                        as long_term_monthly_mean_file:
                                    long_term_monthly_mean_file.write(
                                        ' '.join(file_header_list)+'\n'
                                    )
                            long_term_monthly_mean_df = pd.read_table(
                                long_term_monthly_mean_file_name,
                                delimiter=' ', dtype='str',
                                skipinitialspace=True,
                                keep_default_na=False
                            )
                            stat_monthly_mean_line = [
                                'MP', YYYYmm[0:4], YYYYmm[4:]
                            ]
                            # Read EMC_verif-global monthly mean files
                            emc_verif_global_mean_file_name_check1 = (
                                os.path.join(
                                    model_hour_plot_by_dir, 'make_plots',
                                    var+'_'+vx_mask, 'grid2grid',
                                    stat_type, 'data',
                                    'valid'+f"{expected_dates_dt[0]:%Y%m%d}"
                                    +'to'+f"{expected_dates_dt[-1]:%Y%m%d}"+'_'
                                    +'valid'+hour+'0000to'+hour+'0000Z_'
                                    +'init'+hour+'0000to'+hour+'0000Z',
                                    model+'_'+stat+'_fcst'
                                    +var+level+'_obs'+var+level
                                    +'_interpNEAREST_'
                                    +'region'+vx_mask+'_LEAD_MEAN.txt'
                               )
                            )
                            emc_verif_global_mean_file_name_check2 = (
                                os.path.join(
                                    model_hour_plot_by_dir, 'make_plots',
                                    line_type+'_'+var+'_'+vx_mask,
                                    'grid2grid', stat_type, 'data',
                                    stat+'_'+model+'_'+model_obs_name+'_'
                                    +'valid'+f"{expected_dates_dt[0]:%Y%m%d}"
                                    +'to'+f"{expected_dates_dt[-1]:%Y%m%d}"+'_'
                                    +'valid'+hour+'00to'+hour+'00Z_'
                                    +'init'+hour+'00to'+hour+'00Z_'
                                    +'fcst_lead_avgs_fcst'+var+level+'_'
                                    +'obs'+var+level+'_vxmask'+vx_mask
                                    +'.txt'
                                )
                            )
                            if os.path.exists(
                                    emc_verif_global_mean_file_name_check1
                                    ):
                                emc_verif_global_mean_file_name = (
                                    emc_verif_global_mean_file_name_check1
                                )
                            elif os.path.exists(
                                    emc_verif_global_mean_file_name_check2
                                    ):
                                emc_verif_global_mean_file_name = (
                                    emc_verif_global_mean_file_name_check2
                                )
                            else:
                                print("ERROR: "
                                      +emc_verif_global_mean_file_name_check1
                                      +" and "
                                      +emc_verif_global_mean_file_name_check2
                                      +" do not exist")
                                continue
                            print(emc_verif_global_mean_file_name)
                            emc_verif_global_mean_df = pd.read_table(
                                emc_verif_global_mean_file_name,
                                delimiter=' ', dtype='str',
                                names = ['FORECAST_HOUR', 'VALUE']
                            )
                            emc_verif_global_mean_forecast_hour_list = []
                            for fhr \
                                    in emc_verif_global_mean_df \
                                    ['FORECAST_HOUR'].values:
                                emc_verif_global_mean_forecast_hour_list \
                                    .append(
                                        fhr.replace('0000', '')
                                )
                            emc_verif_global_mean_forecast_hours = np.array(
                                emc_verif_global_mean_forecast_hour_list,
                                dtype=int
                            )
                            emc_verif_global_mean_value_list = (
                                emc_verif_global_mean_df['VALUE'] \
                                .values
                            )
                            # Match EMC_verif-global data to forecast day
                            for forecast_day_header in file_header_list[3:]:
                                forecast_day = int(
                                    forecast_day_header.replace('DAY', '')
                                )
                                forecast_hour = forecast_day * 24
                                matched_idx_list = np.where(
                                    emc_verif_global_mean_forecast_hours \
                                    == forecast_hour
                                )[0]
                                if len(matched_idx_list) != 1:
                                    print("ERROR: Could not find single match to "
                                          +"forceast day "+str(forecast_day))
                                    forecast_hour_monthly_mean = 'NA'
                                else:
                                    if emc_verif_global_mean_value_list[
                                            matched_idx_list[0]
                                            ] == '--':
                                        forecast_hour_monthly_mean = 'NA'
                                    else:
                                        forecast_hour_monthly_mean = round(
                                            float(
                                                emc_verif_global_mean_value_list \
                                                [matched_idx_list[0]]
                                            )
                                        , 3)
                                # Check stat file for at least 25 days
                                emc_verif_global_stat_file_name_check1 = (
                                    os.path.join(
                                        model_hour_plot_by_dir, 'stat_analysis',
                                        var+'_'+vx_mask, 'grid2grid',
                                        stat_type, model,
                                        'valid'+f"{expected_dates_dt[0]:%Y%m%d}"
                                        +'to'
                                        +f"{expected_dates_dt[-1]:%Y%m%d}"+'_'
                                        +'valid'+hour+'0000to'+hour+'0000Z_'
                                        +'init'+hour+'0000to'+hour+'0000Z',
                                        model+'_'+
                                        'f'+str(forecast_hour).zfill(2)+'_'
                                        +'fcst'+var+level+'_obs'+var+level+'_'
                                        +'interpNEAREST_region'+vx_mask+'.stat'
                                    )
                                )
                                emc_verif_global_stat_file_name_check2 = (
                                    os.path.join(
                                        model_hour_plot_by_dir, 'stat_analysis',
                                        line_type+'_'+var+'_'+vx_mask,
                                        'grid2grid', stat_type,
                                        model+'_'+model_obs_name+'_'
                                        +'valid'+f"{expected_dates_dt[0]:%Y%m%d}"
                                        +'to'
                                        +f"{expected_dates_dt[-1]:%Y%m%d}"+'_'
                                        +'valid'+hour+'00to'+hour+'00Z_'
                                        +'init'+hour+'00to'+hour+'00Z_'
                                        +'fcst_lead'
                                        +str(forecast_hour).zfill(2)+'0000_'
                                        +'fcst'+var+level+'_obs'+var+level+'_'
                                        +'vxmask'+vx_mask+'_dump_row'
                                        +'.stat'
                                    )
                                )
                                if os.path.exists(
                                        emc_verif_global_stat_file_name_check1
                                        ):
                                    # minus 1 for header
                                    ndays = len(open(
                                        emc_verif_global_stat_file_name_check1
                                    ).read().splitlines()) - 1
                                elif os.path.exists(
                                        emc_verif_global_stat_file_name_check2
                                        ):
                                    # minus 1 for header
                                    ndays = len(open(
                                        emc_verif_global_stat_file_name_check2
                                    ).read().splitlines()) - 1
                                else:
                                    print(
                                        "ERROR: "
                                        +emc_verif_global_stat_file_name_check1
                                        +" and "
                                        +emc_verif_global_stat_file_name_check2
                                        +" do not exist"
                                    )
                                    ndays = 0
                                if ndays < 25:
                                    forecast_hour_monthly_mean = 'NA'
                                stat_monthly_mean_line.append(
                                    str(forecast_hour_monthly_mean)
                                )
                            # Write line into long term monthly mean file
                            # if empty write as first line, else check file
                            # to see if monthly mean already in there
                            # if it is compare results to what is in file
                            # if it isnt put monthly mean in correct row
                            compare_to_YYYYmm_list = []
                            for index, row \
                                    in long_term_monthly_mean_df.iterrows():
                                row_date_dt = datetime.datetime.strptime(
                                    row['YEAR']+row['MONTH']+'01','%Y%m%d'
                                )
                                if row_date_dt < start_date_dt:
                                    compare_to_YYYYmm_list.append('after')
                                elif row_date_dt > start_date_dt:
                                    compare_to_YYYYmm_list.append('before')
                                elif row_date_dt == start_date_dt:
                                    compare_to_YYYYmm_list.append('equal')
                            # Empty file, write as first line
                            if len(compare_to_YYYYmm_list) == 0:
                                long_term_monthly_mean_df.loc[0,:] = (
                                    stat_monthly_mean_line
                                )
                                write_new_file = True
                            # If YYYYmm in file, compare, replace if different
                            elif 'equal' in compare_to_YYYYmm_list:
                                if compare_to_YYYYmm_list.count('equal') == 1:
                                    YYYYmm_long_term_monthly_mean = (
                                        long_term_monthly_mean_df.loc[
                                            (long_term_monthly_mean_df \
                                             ['YEAR'] == YYYYmm[0:4]) \
                                            & (long_term_monthly_mean_df \
                                               ['MONTH'] == YYYYmm[4:])
                                        ]
                                    )
                                    if not (stat_monthly_mean_line == \
                                            YYYYmm_long_term_monthly_mean \
                                            .values[0]).all():
                                        YYYYmm_long_term_monthly_mean_idx = (
                                            YYYYmm_long_term_monthly_mean.index
                                        )[0]
                                        long_term_monthly_mean_df.loc[
                                            YYYYmm_long_term_monthly_mean_idx,:
                                        ] = stat_monthly_mean_line
                                        write_new_file = True
                                    else:
                                        write_new_file = False
                                else:
                                    print("ERROR: "+YYYYmm+" in "
                                          +long_term_monthly_mean_file_name+" "
                                          +str(
                                              compare_to_YYYYmm_list.count('equal')
                                          )+" times")
                                    exit()
                            # If YYYYmm before all, put monthly mean as first line
                            elif all(compare == 'before'
                                   for compare in compare_to_YYYYmm_list):
                                long_term_monthly_mean_df.loc[-1,:] = (
                                    stat_monthly_mean_line
                                )
                                long_term_monthly_mean_df.index = (
                                    long_term_monthly_mean_df.index+1
                                )
                                long_term_monthly_mean_df = (
                                    long_term_monthly_mean_df.sort_index()
                                )
                                write_new_file = True
                            # If YYYYmm after all, put monthly mean as last line
                            elif all(compare == 'after'
                                   for compare in compare_to_YYYYmm_list):
                                long_term_monthly_mean_df.loc[
                                    long_term_monthly_mean_df.index[-1]+1, :
                                ] = stat_monthly_mean_line
                                write_new_file = True
                            # Mix of before and after
                            else:
                                after_idx_list = [
                                    idx for idx,val in \
                                    enumerate(compare_to_YYYYmm_list) \
                                    if val=='after'
                                ]
                                before_idx_list = [
                                    idx for idx,val in \
                                    enumerate(compare_to_YYYYmm_list) \
                                    if val=='before'
                                ]
                                new_idxs = np.append(
                                    np.array(after_idx_list),
                                    np.array(before_idx_list)+1
                                )
                                long_term_monthly_mean_df = (
                                    long_term_monthly_mean_df.rename(
                                        index=dict(
                                            zip(before_idx_list,
                                                np.array(before_idx_list)+1)
                                        )
                                    )
                                )
                                min_before_idx = min(before_idx_list)
                                long_term_monthly_mean_df.loc[
                                    min_before_idx,:
                                ] = stat_monthly_mean_line
                                long_term_monthly_mean_df = (
                                    long_term_monthly_mean_df.sort_index()
                                )
                                write_new_file = True
                            # Write new file
                            if write_new_file:
                                os.remove(long_term_monthly_mean_file_name)
                                long_term_monthly_mean_df_string = (
                                    long_term_monthly_mean_df.to_string(
                                        header=True, index=False,
                                    )
                                )
                                with open(long_term_monthly_mean_file_name,
                                          'w') \
                                        as long_term_monthly_mean_file:
                                    long_term_monthly_mean_file.write(
                                        long_term_monthly_mean_df_string
                                    )
