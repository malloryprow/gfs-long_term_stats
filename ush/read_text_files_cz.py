import os
import datetime
import numpy as np

np.set_printoptions(suppress=True)

sorcdir = '/lfs/h2/emc/vpppg/save/emc.vpppg/verification/global/long_term_stats/long_term_archive'
 
#-- Caplan_Zhu, 1996 to 2012            
macold = os.path.join(sorcdir, 'legacy_caplan_zhu')

modlist = ['gfs', 'ecm', 'cmc', 'fno', 'ukm', 'cdas']
varlist = ['HGT','WIND']

for var in varlist:
    for mdl in modlist:
        if mdl == 'gfs':
            cyclist = ['00', '06', '12', '18']
        else:
            cyclist = ['00','12']
        for cyc in cyclist:
            if mdl == 'gfs':
                inf_old = os.path.join(macold, var+'s'+cyc+'Z_mean.txt')
            if mdl == 'ecm':
                inf_old = os.path.join(macold, var+'e'+cyc+'Z_mean.txt')
            if mdl == 'cmc':
                inf_old = os.path.join(macold, var+'m'+cyc+'Z_mean.txt')
            if mdl == 'fno':
                inf_old = os.path.join(macold, var+'n'+cyc+'Z_mean.txt')
            if mdl == 'ukm':
                inf_old = os.path.join(macold, var+'k'+cyc+'Z_mean.txt')
            if mdl == 'cdas':
                inf_old = os.path.join(macold, var+'c'+cyc+'Z_mean.txt')
            print(inf_old)
            x = np.loadtxt(inf_old, dtype='str', comments=' ------', delimiter='\n', skiprows=1)
