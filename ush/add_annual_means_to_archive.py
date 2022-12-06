import os
import pandas as pd
import numpy as np

YYYY = os.environ['YYYY']

# Set long term stats directory
long_term_stats_dir = ('/lfs/h2/emc/vpppg/save/emc.vpppg/verification'
                       +'/global/long_term_stats')

model_list = ['gfs', 'cdas', 'ecm', 'ukm', 'cmc', 'fno', 'cfsr']
vx_mask_list = ['NHX', 'SHX']

# File header
file_header_list = [
    'SYS', 'YEAR', 'DAY0', 'DAY1', 'DAY2', 'DAY3', 'DAY4',
    'DAY5', 'DAY6', 'DAY7', 'DAY8', 'DAY9', 'DAY10', 'DAY11', 'DAY12',
    'DAY13', 'DAY14', 'DAY15', 'DAY16'
]

for model in model_list:
    for vx_mask in vx_mask_list:
        long_term_annual_mean_file_name = os.path.join(
            long_term_stats_dir, 'long_term_archive',
            'long_term', 'annual_means', model, '00Z',
            'metplus_ACC_HGT_P500_'+vx_mask+'.txt'
        )
        print(long_term_annual_mean_file_name)
        # Read long term annual mean file if it exists,
        # if not create and write header
        if not os.path.exists(long_term_annual_mean_file_name):
            with open(long_term_annual_mean_file_name, 'w') as \
                    long_term_annual_mean_file:
                long_term_annual_mean_file.write(
                    ' '.join(file_header_list)+'\n'
                )
        long_term_annual_mean_df = pd.read_table(
            long_term_annual_mean_file_name,
            delimiter=' ', dtype='str',
            skipinitialspace=True,
            keep_default_na=False
        )
        # Read in monthly mean file
        long_term_monthly_mean_file_name = os.path.join(
            long_term_stats_dir, 'long_term_archive',
            'long_term', 'monthly_means', model, '00Z',
            'metplus_ACC_HGT_P500_'+vx_mask+'.txt'
        )
        stat_annual_mean_line = ['MP', YYYY]
        if os.path.exists(long_term_monthly_mean_file_name):
            print(long_term_monthly_mean_file_name)
            long_term_monthly_mean_df = pd.read_table(
                long_term_monthly_mean_file_name,
                delimiter=' ', dtype='str', skipinitialspace=True,
                keep_default_na=False
            )
            YYYY_monthly_mean_df = (
                long_term_monthly_mean_df.groupby(['YEAR']).get_group(YYYY)
            )
            for forecast_day_header in file_header_list[2:]:
                forecast_day = forecast_day_header.replace('DAY', '')
                forecast_day_value_list = (
                    YYYY_monthly_mean_df[forecast_day_header].tolist()
                )
                forecast_day_value_list = list(
                    filter(lambda x: x!= 'NA', forecast_day_value_list)
                )
                if len(forecast_day_value_list) >= 6:
                    forecast_day_annual_mean = round(
                        np.mean(np.asarray(forecast_day_value_list,
                                           dtype=float))
                        ,3
                    )
                else:
                    forecast_day_annual_mean = 'NA'
                stat_annual_mean_line.append(str(forecast_day_annual_mean))
            # Write line into long term annual mean file
            # if empty write as first line, else check file
            # to see if annual mean already in there
            # if it is compare results to what is in file
            # if it isnt put annual mean in correct row
            compare_to_YYYY_list = []
            for index, row in long_term_annual_mean_df.iterrows():
                if int(row['YEAR']) < int(YYYY):
                    compare_to_YYYY_list.append('after')
                elif int(row['YEAR']) > int(YYYY):
                    compare_to_YYYY_list.append('before')
                elif int(row['YEAR']) == int(YYYY):
                    compare_to_YYYY_list.append('equal')
            # Empty file, write as first line
            if len(compare_to_YYYY_list) == 0:
                long_term_annual_mean_df.loc[0,:] = stat_annual_mean_line
                write_new_file = True
            # If YYYY in file, compare, replace if different
            elif 'equal' in compare_to_YYYY_list:
                if compare_to_YYYY_list.count('equal') == 1:
                    YYYY_long_term_annual_mean = long_term_annual_mean_df.loc[
                        (long_term_annual_mean_df['YEAR'] == YYYY)
                    ]
                    if not (stat_annual_mean_line == \
                            YYYY_long_term_annual_mean.values[0]).all():
                        YYYY_long_term_annual_mean_idx = (
                             YYYY_long_term_annual_mean.index
                        )[0]
                        long_term_annual_mean_df.loc[
                            YYYY_long_term_annual_mean_idx,:
                        ] = stat_annual_mean_line
                        write_new_file = True
                    else:
                        write_new_file = False
                else:
                    print("ERROR: "+YYYY+" in "
                          +long_term_annual_mean_file_name+" "
                          +str(compare_to_YYYY_list.count('equal'))+" times")
                    exit()
            # If YYYY before all, put annual mean as first line
            elif all(compare == 'before' for compare in compare_to_YYYY_list):
                long_term_annual_mean_df.loc[-1,:] = stat_annual_mean_line
                long_term_annual_mean_df.index = (
                    long_term_annual_mean_df.index+1
                )
                long_term_annual_mean_df = (
                    long_term_annual_mean_df.sort_index()
                )
                write_new_file = True
            # If YYYY after all, put annual mean as last line
            elif all(compare == 'after' for compare in compare_to_YYYY_list):
                long_term_annual_mean_df.loc[
                    long_term_annual_mean_df.index[-1]+1, :
                ] = stat_annual_mean_line
                write_new_file = True
            # Mix of before and after
            else:
                after_idx_list = [idx for idx,val in \
                                  enumerate(compare_to_YYYY_list) \
                                  if val=='after']
                before_idx_list = [idx for idx,val in \
                                   enumerate(compare_to_YYYY_list) \
                                   if val=='before']
                new_idxs = np.append(
                    np.array(after_idx_list),
                    np.array(before_idx_list)+1
                )
                long_term_annual_mean_df = (
                     long_term_annual_mean_df.rename(
                     index=dict(zip(before_idx_list,
                                    np.array(before_idx_list)+1))
                     )
                )
                min_before_idx = min(before_idx_list)
                long_term_annual_mean_df.loc[min_before_idx,:] = (
                    stat_annual_mean_line
                )
                long_term_annual_mean_df = (
                    long_term_annual_mean_df.sort_index()
                )
                write_new_file = True
            # Write new file
            if write_new_file:
                os.remove(long_term_annual_mean_file_name)
                long_term_annual_mean_df_string = (
                    long_term_annual_mean_df.to_string(
                        header=True, index=False,
                     )
                )
                with open(long_term_annual_mean_file_name, 'w') \
                        as long_term_annual_mean_file:
                    long_term_annual_mean_file.write(
                        long_term_annual_mean_df_string
                    )
        else:
            print(long_term_monthly_mean_file_name+" does not exist")
