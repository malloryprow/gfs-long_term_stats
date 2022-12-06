import os
import datetime
import pandas as pd
import numpy as np
import math

start_date = '20200101'
end_date = '20201231'
annual_mean_gfs_precip_dir = (
    '/lfs/h2/emc/vpppg/save/emc.vpppg/verification/global/long_term_stats'
    +'long_term_archive/precip'
)
gfs_precip_vsdb_dir = os.path.join(annual_mean_gfs_precip_dir,
                                   'verf_precip_vsdb', 'gfs')
fhr_list = ['24', '48', '72'] 
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')

def nint(x):
    y = math.floor(x + 0.5)
    a = int(y)
    if np.abs(a-y) > 0.3:
        a = a+1
    return a

file_name_dict = {
    'gfs.ets.1in.txt': {
        'STAT': 'FHO>1.0',
        'PARAM': 'APCP/24',
        'V_RGN': 'G212/RFC',
        'LEVEL': 'SFC'
    },
    'gfs.ets.2in.txt': {
        'STAT': 'FHO>2.0',
        'PARAM': 'APCP/24',
        'V_RGN': 'G212/RFC',
        'LEVEL': 'SFC'
    },
    'gfs.ets.3in.txt': {
        'STAT': 'FHO>3.0',
        'PARAM': 'APCP/24',
        'V_RGN': 'G212/RFC',
        'LEVEL': 'SFC'
    },
    'gfs.ets.pt25in.txt': {
        'STAT': 'FHO>.25',
        'PARAM': 'APCP/24',
        'V_RGN': 'G212/RFC',
        'LEVEL': 'SFC'
    },
    'gfs.fss24.10mm.62km.txt': {
        'STAT': 'FSS<062',
        'PARAM': 'APCP/24>010.0',
        'V_RGN': 'G240/CNS',
        'LEVEL': 'SFC'       
    },
    'gfs.fss24.25mm.62km.txt': {
        'STAT': 'FSS<062',
        'PARAM': 'APCP/24>025.0',
        'V_RGN': 'G240/CNS',
        'LEVEL': 'SFC'
    }
}

for file_name in file_name_dict:
    annual_mean_gfs_precip_file_name = os.path.join(
        annual_mean_gfs_precip_dir, file_name
    )
    print(annual_mean_gfs_precip_file_name)
    file_name_verif_settings_dict = file_name_dict[file_name]
    date_dt = start_date_dt
    total24, total48, total72 = 0, 0, 0
    fbs24, fbs48, fbs72 = 0, 0, 0
    sumf24, sumf48, sumf72 = 0, 0, 0
    sumo24, sumo48, sumo72 = 0, 0, 0
    a24, b24, c24, d24 = 0, 0, 0, 0
    a48, b48, c48, d48 = 0, 0, 0, 0
    a72, b72, c72, d72 = 0, 0, 0, 0
    while date_dt <= end_date_dt:    
        date_vsdb_file = os.path.join(
            gfs_precip_vsdb_dir,
            'gfs_'+date_dt.strftime('%Y%m%d')+'.vsdb'
        )
        date_stat_values = np.nan * np.ones(3)
        if os.path.exists(date_vsdb_file):
            date_vsdb_df = pd.read_table(
                date_vsdb_file, delimiter=' ',
                skipinitialspace=True, dtype=str,
                header=None, names=[
                    'VERSION', 'MODEL', 'FHR', 'VALID',
                    'OBS', 'V_RGN', 'STAT', 'PARAM', 'LEVEL',
                    'EQUALS', 'A', 'B', 'C', 'D', 'E', 'F'
                ]
            )
            file_name_verif_settings_date_vsdb_df = date_vsdb_df
            for file_name_verif_setting in file_name_verif_settings_dict:
                file_name_verif_setting_value = (
                    file_name_verif_settings_dict[file_name_verif_setting]
                )
                file_name_verif_settings_date_vsdb_df = (
                    file_name_verif_settings_date_vsdb_df.loc[
                        file_name_verif_settings_date_vsdb_df \
                        [file_name_verif_setting]
                        == file_name_verif_setting_value
                    ]
                )
            for fhr in fhr_list:
                if 'fss' in file_name:
                    fhr_setting = '0'+fhr
                else:
                    fhr_setting = fhr
                fhr_file_name_verif_settings_date_vsdb_df = (
                    file_name_verif_settings_date_vsdb_df.loc[
                        file_name_verif_settings_date_vsdb_df['FHR']
                        == fhr_setting
                    ]
                )
                if len(fhr_file_name_verif_settings_date_vsdb_df) == 1:
                    if fhr == '24':
                        total24 = total24 + float(
                            fhr_file_name_verif_settings_date_vsdb_df['A'] \
                            .values[0]
                        )
                    elif fhr == '48':
                        total48 = total48 + float(
                            fhr_file_name_verif_settings_date_vsdb_df['A'] \
                            .values[0]
                        )
                    elif fhr == '72':
                        total72 = total72 + float(
                            fhr_file_name_verif_settings_date_vsdb_df['A'] \
                            .values[0]
                        ) 
                    if 'fss' in file_name:
                        if fhr == '24':
                            fbs24 = fbs24 + float(
                                fhr_file_name_verif_settings_date_vsdb_df['B'] \
                                .values[0]
                            )
                            sumf24 = sumf24 + float(
                                fhr_file_name_verif_settings_date_vsdb_df['C'] \
                                .values[0]
                            )
                            sumo24 = sumo24 + float(
                                fhr_file_name_verif_settings_date_vsdb_df['D'] \
                               .values[0]
                            )
                        elif fhr == '48':
                            fbs48 = fbs48 + float(
                                fhr_file_name_verif_settings_date_vsdb_df['B'] \
                                .values[0]
                            )
                            sumf48 = sumf48 + float(
                                fhr_file_name_verif_settings_date_vsdb_df['C'] \
                                .values[0]
                            )
                            sumo48 = sumo48 + float(
                                fhr_file_name_verif_settings_date_vsdb_df['D'] \
                                .values[0]
                            )
                        elif fhr == '72':
                            fbs72 = fbs72 + float(
                                fhr_file_name_verif_settings_date_vsdb_df['B'] \
                                .values[0]
                            )
                            sumf72 = sumf72 + float(
                                fhr_file_name_verif_settings_date_vsdb_df['C'] \
                                .values[0]
                            )
                            sumo72 = sumo72 + float(
                                fhr_file_name_verif_settings_date_vsdb_df['D'] \
                                .values[0]
                           )
                    else:
                        if fhr == '24':
                            fy24 = nint(
                                float(
                                    fhr_file_name_verif_settings_date_vsdb_df['A'] \
                                    .values[0]
                                )
                                *float(fhr_file_name_verif_settings_date_vsdb_df['B'] \
                                       .values[0])
                            )
                            oy24 = nint(
                                float(
                                    fhr_file_name_verif_settings_date_vsdb_df['A'] \
                                    .values[0]
                                )
                                *float(fhr_file_name_verif_settings_date_vsdb_df['D'] \
                                       .values[0])
                            )
                            fy_oy24 = nint(
                                float(
                                    fhr_file_name_verif_settings_date_vsdb_df['A'] \
                                    .values[0]
                                )
                                *float(fhr_file_name_verif_settings_date_vsdb_df['C'] \
                                       .values[0])
                            )
                            fy_on24 = fy24 - fy_oy24
                            fn_oy24 = oy24 - fy_oy24
                            a24 = a24 + fy_oy24
                            b24 = b24 + fy_on24
                            c24 = c24 + fn_oy24
                        elif fhr == '48':
                            fy48 = nint(
                                float(
                                    fhr_file_name_verif_settings_date_vsdb_df['A'] \
                                    .values[0]
                                )
                                *float(fhr_file_name_verif_settings_date_vsdb_df['B'] \
                                       .values[0])
                            )
                            oy48 = nint(
                                float(
                                    fhr_file_name_verif_settings_date_vsdb_df['A'] \
                                    .values[0]
                                )
                                *float(fhr_file_name_verif_settings_date_vsdb_df['D'] \
                                       .values[0])
                            )
                            fy_oy48 = nint(
                                float(
                                    fhr_file_name_verif_settings_date_vsdb_df['A'] \
                                    .values[0]
                                )
                                *float(fhr_file_name_verif_settings_date_vsdb_df['C'] \
                                       .values[0])
                            )
                            fy_on48 = fy48 - fy_oy48
                            fn_oy48 = oy48 - fy_oy48
                            a48 = a48 + fy_oy48
                            b48 = b48 + fy_on48
                            c48 = c48 + fn_oy48
                        elif fhr == '72':
                            fy72 = nint(
                                float(
                                    fhr_file_name_verif_settings_date_vsdb_df['A'] \
                                    .values[0]
                                )
                                *float(fhr_file_name_verif_settings_date_vsdb_df['B'] \
                                       .values[0])
                            )
                            oy72 = nint(
                                float(
                                    fhr_file_name_verif_settings_date_vsdb_df['A'] \
                                    .values[0]
                                )
                                *float(fhr_file_name_verif_settings_date_vsdb_df['D'] \
                                       .values[0])
                            )
                            fy_oy72 = nint(
                                float(
                                    fhr_file_name_verif_settings_date_vsdb_df['A'] \
                                    .values[0]
                                )
                                *float(fhr_file_name_verif_settings_date_vsdb_df['C'] \
                                       .values[0])
                            )
                            fy_on72 = fy72 - fy_oy72
                            fn_oy72 = oy72 - fy_oy72
                            a72 = a72 + fy_oy72
                            b72 = b72 + fy_on72
                            c72 = c72 + fn_oy72
        #else:
        #    print("No "+date_vsdb_file)
        date_dt = date_dt + datetime.timedelta(days=1)
    if 'fss' in file_name:
        value24 = 1 - (fbs24/(sumf24+sumo24))
        value48 = 1 - (fbs48/(sumf48+sumo48))
        value72 = 1 - (fbs72/(sumf72+sumo72))
    elif 'ets' in file_name:
        q24 = ((a24+b24)*(a24+c24))/total24
        value24 = (a24-q24)/(a24+b24+c24-q24)
        q48 = ((a48+b48)*(a48+c48))/total48
        value48 = (a48-q48)/(a48+b48+c48-q48)
        q72 = ((a72+b72)*(a72+c72))/total72
        value72 = (a72-q72)/(a72+b72+c72-q72)
    print("{:.5e}".format(value24).replace('e', 'E')
          +' '+"{:.5e}".format(value48).replace('e', 'E')
          +' '+"{:.5e}".format(value72).replace('e', 'E'))
    print("\n\n")
