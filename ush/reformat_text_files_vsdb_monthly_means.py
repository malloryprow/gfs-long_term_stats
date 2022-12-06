import os
import datetime
import numpy as np

np.set_printoptions(suppress=True)

sorcdir = '/lfs/h2/emc/vpppg/save/emc.vpppg/verification/global/long_term_stats/long_term_archive'

#-- VSDB, 2008 to 2020  
vsdb_dir = os.path.join(sorcdir, 'legacy_vsdb')
vsdb_start_year = 2008
vsdb_end_year = 2021

combined_dir = os.path.join(sorcdir, 'long_term', 'monthly_means')

modlist = ['gfs', 'ecm', 'cmc', 'fno', 'ukm', 'cdas', 'cfsr', 'jma']
varlist = ['AC_HGT','AC_WIND', 'AC_T', 'AC_U', 'AC_V',
           'RMS_HGT','RMS_WIND', 'RMS_T', 'RMS_U', 'RMS_V']

vsdb_dict = {
    'AC_HGT': {
        'stat_list': ["AC   "],
        'level_list': ["P1000", "P700 ", "P500 ", "P250 "],
        'reg_list': ["G2   ", "G2NHX", "G2SHX", "G2TRO", "G2PNA"]
    },
    'AC_WIND': {
        'stat_list': ["AC   "],
        'level_list': ["P850 ", "P500 ", "P250 "],
        'reg_list': ["G2   ", "G2NHX", "G2SHX", "G2TRO", "G2PNA"]
    },
    'AC_T': {
        'stat_list': ["AC   "],
        'level_list': ["P850 ", "P500 ", "P250 "],
        'reg_list': ["G2   ", "G2NHX", "G2SHX", "G2TRO", "G2PNA"]
    },
    'AC_U': {
        'stat_list': ["AC   "],
        'level_list': ["P850 ", "P500 ", "P250 "],
        'reg_list': ["G2   ", "G2NHX", "G2SHX", "G2TRO", "G2PNA"]
    },
    'AC_V': {
        'stat_list': ["AC   "],
        'level_list': ["P850 ", "P500 ", "P250 "],
        'reg_list': ["G2   ", "G2NHX", "G2SHX", "G2TRO", "G2PNA"]
    },
    'RMS_HGT': {
        'stat_list': ["PCOR ", "RMSE ", "BIAS "],
        'level_list': ["P1000", "P850", "P500", "P300", "P200", "P100", "P20"],
        'reg_list': ["G2   ", "G2NHX", "G2SHX", "G2TRO", "G2PNA"]
    },
    'RMS_WIND': {
        'stat_list': ["PCOR ", "RMSE ", "BIAS "],
        'level_list': ["P1000", "P850", "P500", "P300", "P200", "P100", "P20"],
        'reg_list': ["G2   ", "G2NHX", "G2SHX", "G2TRO", "G2PNA"]
    },
    'RMS_T': {
        'stat_list': ["PCOR ", "RMSE ", "BIAS "],
        'level_list': ["P1000", "P850", "P500", "P300", "P200", "P100", "P20"],
        'reg_list': ["G2   ", "G2NHX", "G2SHX", "G2TRO", "G2PNA"]
    },
    'RMS_U': {
        'stat_list': ["PCOR ", "RMSE ", "BIAS "],
        'level_list': ["P1000", "P850", "P500", "P300", "P200", "P100", "P20"],
        'reg_list': ["G2   ", "G2NHX", "G2SHX", "G2TRO", "G2PNA"]
    },
    'RMS_V': {
        'stat_list': ["PCOR ", "RMSE ", "BIAS "],
        'level_list': ["P1000", "P850", "P500", "P300", "P200", "P100", "P20"],
        'reg_list': ["G2   ", "G2NHX", "G2SHX", "G2TRO", "G2PNA"]
    }
}

file_header_list = [
    'SYS', 'YEAR', 'MONTH', 'DAY0', 'DAY1', 'DAY2', 'DAY3', 'DAY4',
    'DAY5', 'DAY6', 'DAY7', 'DAY8', 'DAY9', 'DAY10', 'DAY11', 'DAY12',
    'DAY13', 'DAY14', 'DAY15', 'DAY16'
]

for var in varlist:
    var_vsdb_dict = vsdb_dict[var]
    for mdl in modlist:
        if mdl == 'gfs':
            cyclist = ['00', '06', '12', '18']
        elif mdl in ['cdas', 'cfsr']:
            cyclist = ['00']
        else:
            cyclist = ['00','12']
        for cyc in cyclist:
            new_legacy_archive = os.path.join(combined_dir, mdl, cyc+'Z')
            if not os.path.exists(new_legacy_archive):
                os.makedirs(new_legacy_archive)
            vsdb_file = os.path.join(vsdb_dir, var+mdl+cyc+'Z_mean.txt')
            print(vsdb_file)
            vsdb_file_data = np.loadtxt(vsdb_file, dtype='str', delimiter='\n')
            for stat in var_vsdb_dict['stat_list']:
                for level in var_vsdb_dict['level_list']:
                    for reg in var_vsdb_dict['reg_list']:
                        line_num = 0
                        match = False
                        for vsdb_line in vsdb_file_data:
                            if stat+' '+reg+' '+level in vsdb_line:
                                stat_level_reg_line = vsdb_line
                                stat_level_reg_line_num = line_num
                                match = True
                            line_num+=1
                        if match:
                            print("Match for "+stat+' '+reg+' '+level)
                            var_name = var.split('_')[1]
                            reformat_file_name = os.path.join(
                                new_legacy_archive,
                                'vsdb_'+stat.replace(' ', '')+'_'
                                +var_name+'_'
                                +level.replace(' ', '')+'_'
                                +reg.replace(' ', '')+'.txt'
                            )
                            print(reformat_file_name)
                            stat_level_reg_start_line = stat_level_reg_line_num-2
                            if mdl == 'ecm' and cyc == '12' and var == 'RMS_WIND':
                                stat_level_reg_end_line =  (
                                    stat_level_reg_line_num+6
                                    +(2018-vsdb_start_year+1)
                                    +((2018-vsdb_start_year+1)*12)
                                )
                                stat_level_reg_section = vsdb_file_data[
                                    stat_level_reg_start_line:stat_level_reg_end_line
                                ]
                                stat_level_reg_annual_mean = stat_level_reg_section[
                                   6:(2018-vsdb_start_year+7)
                                ]
                                stat_level_reg_monthly_mean = stat_level_reg_section[
                                    (2018-vsdb_start_year+9):
                                ]
                            elif mdl == 'cmc' and cyc == '12' and var == 'RMS_U':
                                stat_level_reg_end_line =  (
                                    stat_level_reg_line_num+6
                                    +(2019-vsdb_start_year+1)
                                    +((2019-vsdb_start_year+1)*12)
                                )
                                stat_level_reg_section = vsdb_file_data[
                                    stat_level_reg_start_line:stat_level_reg_end_line
                                ]
                                stat_level_reg_annual_mean = stat_level_reg_section[
                                   6:(2019-vsdb_start_year+7)
                                ]
                                stat_level_reg_monthly_mean = stat_level_reg_section[
                                    (2019-vsdb_start_year+9):
                                ]
                            else:
                                stat_level_reg_end_line =  (
                                    stat_level_reg_line_num+6
                                    +(vsdb_end_year-vsdb_start_year+1)
                                    +((vsdb_end_year-vsdb_start_year+1)*12)
                                )
                                stat_level_reg_section = vsdb_file_data[
                                    stat_level_reg_start_line:stat_level_reg_end_line
                                ]
                                stat_level_reg_annual_mean = stat_level_reg_section[
                                   6:(vsdb_end_year-vsdb_start_year+7)
                                ]
                                stat_level_reg_monthly_mean = stat_level_reg_section[
                                    (vsdb_end_year-vsdb_start_year+9):
                                ]
                            with open(reformat_file_name, 'w') as reformat_file:
                                reformat_file.write(' '.join(file_header_list)+'\n')
                                for monthly_mean_line in stat_level_reg_monthly_mean:
                                    replaced_monthly_mean_line = (
                                        monthly_mean_line.replace(stat,'') \
                                        .replace(level, '').replace(reg, '')
                                    )
                                    replaced_monthly_mean_line_split = replaced_monthly_mean_line.split()
                                    if len(replaced_monthly_mean_line_split) > 0:
                                        if int(replaced_monthly_mean_line_split[1]) < 10:
                                            replaced_monthly_mean_line_split[1] = '0'+replaced_monthly_mean_line_split[1]
                                        new_line = ('VSDB '+' '.join(replaced_monthly_mean_line_split))
                                        reformat_file.write(new_line.replace('-99.900', 'NA')+'\n')
                            del stat_level_reg_line, stat_level_reg_line_num
                            del stat_level_reg_start_line, stat_level_reg_end_line
                            del stat_level_reg_section
                            del stat_level_reg_annual_mean, stat_level_reg_monthly_mean
                        else:
                            print("No match for "+stat+' '+reg+' '+level)
                            exit()
