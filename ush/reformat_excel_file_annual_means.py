import os
import pandas as pd

sorcdir = '/lfs/h2/emc/vpppg/save/emc.vpppg/verification/global/long_term_stats/long_term_archive'

annual_dir = os.path.join(sorcdir, 'legacy_excel_spreadsheets')

file_header_list = [
    'SYS', 'YEAR', 'DAY0', 'DAY1', 'DAY2', 'DAY3', 'DAY4',
    'DAY5', 'DAY6', 'DAY7', 'DAY8', 'DAY9', 'DAY10', 'DAY11', 'DAY12',
    'DAY13', 'DAY14', 'DAY15', 'DAY16'
]
 
for vx_mask in ['NHX', 'SHX']:
    vx_mask_excel = os.path.join(annual_dir,
                               'annualscore_allmodel_data_only_'
                               +vx_mask+'.csv')
    print(vx_mask_excel)
    # Read in Excel file: contains Day 5 values only
    vx_mask_excel_df = pd.read_csv(vx_mask_excel,
                                   delimiter=',', dtype='str',
                                   skipinitialspace=True,
                                   keep_default_na=False)
    YYYY_list = vx_mask_excel_df.loc[:,'YYYY'].values
    for model in vx_mask_excel_df.columns[1:]:
        model_reformat_file_name = os.path.join(sorcdir, 'long_term',
                                                'annual_means', model.lower(),
                                                '00Z', 'excel_ACC_HGT_P500_'
                                                +vx_mask+'.txt')
        print(model_reformat_file_name)
        model_reformat_df = pd.DataFrame(index=vx_mask_excel_df.index,
                                         columns=file_header_list)
        model_reformat_df.loc[:,'SYS'] = 'EXCEL'
        model_reformat_df.loc[:,'YEAR'] = YYYY_list
        for forecast_day_header in file_header_list[2:]:
            if forecast_day_header != 'DAY5':
                model_reformat_df.loc[:,forecast_day_header] = 'NA'
            else:
                model_reformat_df.loc[:,forecast_day_header] = (
                    vx_mask_excel_df.loc[:, model].values
                )
        string_model_reformat_df = model_reformat_df.to_string(header=False,
                                                              index=False)
        with open(model_reformat_file_name, 'w') as reformat_file:
            reformat_file.write(' '.join(file_header_list)+'\n')
            reformat_file.write(string_model_reformat_df) 
