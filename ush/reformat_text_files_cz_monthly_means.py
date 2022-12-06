import os
import datetime
import numpy as np

np.set_printoptions(suppress=True)

sorcdir = '/lfs/h2/emc/vpppg/save/emc.vpppg/verification/global/long_term_stats/long_term_archive'
 
#-- Caplan_Zhu, 1996 to 2012            
cz_dir = os.path.join(sorcdir, 'legacy_caplan_zhu')
cz_start_year = 1996
cz_end_year = 2013

combined_dir = os.path.join(sorcdir, 'long_term', 'monthly_means')

modlist = ['gfs', 'ecm', 'cmc', 'fno', 'ukm', 'cdas']
varlist = ['HGT','WIND']

cz_dict = {
    'HGT': {
        'stat_list': ["HGT AC Wave1-3    ", "HGT AC Wave4-9    ","HGT AC Wave10-20  ","HGT AC Wave1-20   ",
                      "HGT RMSE          ", "HGT Error         ","HGT RMSEC         ","HGT ERRORC        "],
        'level_list': ["1000 hpa", "500 hpa "],
        'reg_list': ["NH      ", "SH      "]
    },
    'WIND': {
        'stat_list': ["U   AC Wave1-3    ", "U   AC Wave4-9    ","U   AC Wave10-20  ","U   AC Wave1-20   ",
                      "U   RMSE          ", "U   Error         ","U   RMSEC         ","U   ERRORC        ",
                      "V   AC Wave1-3    ", "V   AC Wave4-9    ","V   AC Wave10-20  ","V   AC Wave1-20   ",
                      "V   RMSE          ", "V   Error         ","V   RMSEC         ","V   ERRORC        ",
                      "SPD AC Wave1-3    ", "SPD AC Wave4-9    ","SPD AC Wave10-20  ","SPD AC Wave1-20   ",
                      "SPD RMSE          ", "SPD Error         ","SPD RMSEC         ","SPD ERRORC        ",
                      "UV  AC Wave1-3    ", "UV  AC Wave4-9    ","UV  AC Wave10-20  ","UV  AC Wave1-20   ",
                      "UV  RMSE          ", "UV  Error         ","UV  RMSEC         ","UV  ERRORC        "],
        'level_list': ["850 hPa ", "200 hPa "],
        'reg_list': ["Tropics "]
    }
}

file_header_list = [
    'SYS', 'YEAR', 'MONTH', 'DAY0', 'DAY1', 'DAY2', 'DAY3', 'DAY4',
    'DAY5', 'DAY6', 'DAY7', 'DAY8', 'DAY9', 'DAY10', 'DAY11', 'DAY12',
    'DAY13', 'DAY14', 'DAY15', 'DAY16'
]

for var in varlist:
    var_cz_dict = cz_dict[var]
    for mdl in modlist:
        if mdl == 'gfs':
            cyclist = ['00', '06', '12', '18']
        else:
            cyclist = ['00','12']
        for cyc in cyclist:
            new_legacy_archive = os.path.join(combined_dir, mdl, cyc+'Z')
            if not os.path.exists(new_legacy_archive):
                os.makedirs(new_legacy_archive)
            if mdl == 'gfs':
                cz_file = os.path.join(cz_dir, var+'s'+cyc+'Z_mean.txt')
            if mdl == 'ecm':
                cz_file = os.path.join(cz_dir, var+'e'+cyc+'Z_mean.txt')
            if mdl == 'cmc':
                cz_file = os.path.join(cz_dir, var+'m'+cyc+'Z_mean.txt')
            if mdl == 'fno':
                cz_file = os.path.join(cz_dir, var+'n'+cyc+'Z_mean.txt')
            if mdl == 'ukm':
                cz_file = os.path.join(cz_dir, var+'k'+cyc+'Z_mean.txt')
            if mdl == 'cdas':
                cz_file = os.path.join(cz_dir, var+'c'+cyc+'Z_mean.txt')
            print(cz_file)
            cz_file_data = np.loadtxt(cz_file, dtype='str', delimiter='\n')
            for stat in var_cz_dict['stat_list']:
                for level in var_cz_dict['level_list']:
                    for reg in var_cz_dict['reg_list']:
                        print(stat+' '+level+' '+reg)
                        line_num = 0
                        match = False
                        for cz_line in cz_file_data:
                            if stat+reg+level in cz_line:
                                stat_level_reg_line = cz_line
                                stat_level_reg_line_num = line_num
                                match = True
                            line_num+=1
                        if match:
                            print("Match for "+stat+reg+level)
                            reformat_file_name = os.path.join(
                                new_legacy_archive, 
                                'caplan_zhu_'+stat.replace(' ', '')+'_'
                                +level.replace(' ', '')+'_'
                                +reg.replace(' ', '')+'.txt'
                            )
                            print(reformat_file_name)
                            stat_level_reg_start_line = stat_level_reg_line_num-2
                            stat_level_reg_end_line =  (
                                stat_level_reg_line_num+6
                                +(cz_end_year-cz_start_year+1)
                                +((cz_end_year-cz_start_year+1)*12)
                            )
                            stat_level_reg_section = cz_file_data[
                                stat_level_reg_start_line:stat_level_reg_end_line
                            ]
                            stat_level_reg_annual_mean = stat_level_reg_section[
                                6:(cz_end_year-cz_start_year+7)
                             ]
                            stat_level_reg_monthly_mean = stat_level_reg_section[
                                (cz_end_year-cz_start_year+9):
                            ]
                            with open(reformat_file_name, 'w') as reformat_file:
                                reformat_file.write(' '.join(file_header_list)+'\n')
                                for monthly_mean_line in stat_level_reg_monthly_mean:
                                    monthly_mean_line_split = monthly_mean_line.split()
                                    if len(monthly_mean_line_split) > 0:
                                        if int(monthly_mean_line_split[1]) < 10:
                                            monthly_mean_line_split[1] = '0'+monthly_mean_line_split[1]
                                        new_line = 'CZ '+' '.join(monthly_mean_line_split)
                                        reformat_file.write(new_line.replace('-999.900', 'NA')+'\n')
                            del stat_level_reg_line, stat_level_reg_line_num
                            del stat_level_reg_start_line, stat_level_reg_end_line
                            del stat_level_reg_section
                            del stat_level_reg_annual_mean, stat_level_reg_monthly_mean
                        else:
                            print("No match for "+stat+reg+level)
                            exit()
