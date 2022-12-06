import os
import datetime
import numpy as np

np.set_printoptions(suppress=True)

sorcdir = '/lfs/h2/emc/vpppg/save/emc.vpppg/verification/global/long_term_stats/long_term_archive'

#-- VSDB, 2008 to 2020  
macold = os.path.join(sorcdir, 'legacy_vsdb')

modlist = ['gfs', 'ecm', 'cmc', 'fno', 'ukm', 'cdas', 'cfsr', 'jma']
varlist = ['AC_HGT','AC_WIND', 'AC_T', 'AC_U', 'AC_V',
           'RMS_HGT','RMS_WIND', 'RMS_T', 'RMS_U', 'RMS_V']
filecount = 0
for var in varlist:
    for mdl in modlist:
        if mdl == 'gfs':
            cyclist = ['00', '06', '12', '18']
        elif mdl in ['cdas', 'cfsr']:
            cyclist = ['00']
        else:
            cyclist = ['00','12']
        for cyc in cyclist:
            inf_old = os.path.join(macold, var+mdl+cyc+'Z_mean.txt')
            x = np.loadtxt(inf_old, dtype='str', comments=' ------', delimiter='\n', skiprows=1)
