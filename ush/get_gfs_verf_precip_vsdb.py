import os
import datetime

start_date = '20220101'
end_date = '20220601'

HTAR = 'htar'
start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')

date_dt = start_date_dt
while date_dt <= end_date_dt:
    hpss_tar_dir = os.path.join('/NCEPPROD', 'hpssprod', 'runhistory',
                                'rh'+date_dt.strftime('%Y'),
                                date_dt.strftime('%Y%m'),
                                date_dt.strftime('%Y%m%d'))
    hpss_tar = os.path.join(hpss_tar_dir , 'com_verf_precip_v4.5_precip.'
                            +date_dt.strftime('%Y%m%d')+'.tar')
    print(hpss_tar)
    os.system(HTAR+' -xvf '+hpss_tar+' gfs/gfs_'+date_dt.strftime('%Y%m%d')+'.vsdb')
    date_dt = date_dt + datetime.timedelta(days=1)
