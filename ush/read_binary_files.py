import os
import datetime
import numpy as np

np.set_printoptions(suppress=True)

sorcdir = '/lfs/h2/emc/vpppg/save/emc.vpppg/verification/global/long_term_stats/long_term_archive'
execdir = '/lfs/h2/emc/ptmp/'+os.environ['USER']+'/longterm'
 
print("OUTPUT: "+execdir)

if not os.path.exists(execdir):
   os.makedirs(execdir)

today = datetime.datetime.today()
yyyymmdd = f"{today:%Y%m%d}"
yeare = int(yyyymmdd[0:4])
yy = int(yyyymmdd[0:4])
mm = int(yyyymmdd[4:6])
dd = int(yyyymmdd[6:])

mm1 = mm - 1
if mm1 == 0:
    yeare = yeare - 1
    mm1 = 12

## compute monthly means
#${sorcdir}/monthly_ac.sh
#${sorcdir}/monthly_rms.sh

#------------------------------------
# determine map time stamps               
#------------------------------------
## maps start from sdate and end at edate
mlist = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
dlist = ['31', '28', '31', '30', '31', '30', '31', '31', '30', '31', '30', '31']
years = '1996'
sdate = '01jan'+years
year1 = yeare - 1
sdat1 = '01'+mlist[mm]+str(year1)
edate = dlist[mm1]+mlist[mm1]+str(yeare)

###############################################################
#################################
##useful forecast day plots
# ${sorcdir}/graph_ac_fcstday.sh
#################################
yyyymmc = f"{today:%Y%m}"
yyyymm = datetime.datetime.strftime(
    datetime.datetime.strptime(yyyymmc+'0100', '%Y%m%d%H')
    - datetime.timedelta(hours=24), '%Y%m'
)
if 'yeare' not in globals():
    yeare = yyyymm[0:4]
if 'mone' not in globals():
   if 'mm1' in globals():
       mone = mm1
   else:
       mone = yyyym[4:6]
modlist = ['gfs', 'ecm', 'cmc', 'fno', 'ukm']
cyclist = ['00','12']

#--vsdb-based monthly AC, 2008 to the present
macnew = os.path.join(sorcdir, 'legacy_vsdb')            
#--vsdb-based monthly AC, 1996 to 2012            
macold = os.path.join(sorcdir, 'legacy_caplan_zhu')

#--web serve for display graphics
#export webhost=emcrzdm.ncep.noaa.gov
#export webhostid=wx24fy
#export ftpdir=/home/people/emc/www/htdocs/gmb/STATS_vsdb/longterm/fdayac
#export doftp=YES

rundir = os.path.join(sorcdir, 'usefulfcst')

#half of running mean length
nsm = 6
#running mean length
nsm2 = 2*nsm+1

for mdl in modlist:
    for cyc in cyclist:
        inf_new = os.path.join(macnew, 'AC_HGT'+mdl+cyc+'Z_month.bin')
        if mdl == 'gfs':
            inf_old = os.path.join(macold, 'HGTs'+cyc+'Z_month.bin')
        if mdl == 'ecm':
            inf_old = os.path.join(macold, 'HGTe'+cyc+'Z_month.bin')
        if mdl == 'cmc':
            inf_old = os.path.join(macold, 'HGTm'+cyc+'Z_month.bin')
        if mdl == 'fno':
            inf_old = os.path.join(macold, 'HGTn'+cyc+'Z_month.bin')
        if mdl == 'ukm':
            inf_old = os.path.join(macold, 'HGTk'+cyc+'Z_month.bin')
        if mdl == 'cdas':
            inf_old = os.path.join(macold, 'HGTc'+cyc+'Z_month.bin')
        #### "creating" fcstday_${mdl}${cyc}Z.f fcstday_${mdl}${cyc}Z.exe
        yeare = yeare
        # number of forecast days, from 0 to nf-1
        nf = 17
        # months in a year
        nm = 12
        nsm = nsm
        nsm2 = nsm2
        ## legacy Caplan-Zhu monthly scores, 1996 to 2012
        yeare1 = 2012
        years1 = 1996
        ny1 = yeare1-years1+1
        # number of areas, NH and SH
        nreg1 = 2
        # number of layers, 1000hPa and 500hPa 
        nlev1 = 2
        # number of variables
        nvar1 = 8
        ## new vsdb-based scores, 2008 to the present
        years2 = 2008
        ny2 = yeare-years2+1
        # number of areas, G2 G2NHX G2SHX G2TRO G2PNA
        nreg2 = 5
        # number of layers, 1000 700 500 250
        nlev2 = 4
        # number of variables
        nvar2 = 3
        # monthly means for all variables in the source file
        var1 = np.empty((nf,nreg1,nlev1,nm,nvar1,ny1))
        var2 = np.empty((nf,nreg2,nlev2,nm,nvar2,ny2))
        ## merged HGT AC in the NH and SH, on 1000hPa and 500hPa
        # year start to merge
        yearm=2013
        ny = yeare-years1+1
        # number of areas, NH and SH
        nreg=2
        # number of layers, 1000hPa and 500hPa
        nlev=2
        # monthly means
        acz1 = np.empty((nf,nreg,nlev,nm,ny1))
        acz2 = np.empty((nf,nreg,nlev,nm,ny2))
        # mergered monthly means
        acz = np.empty((nf,nreg,nlev,nm,ny))
        # mergered annual means
        acz_ann = np.empty((nf,nreg,nlev,ny))
        regname = ['NH', 'SH']
        levname = ['P1000', 'P500']
        ## arrays for determining forecast days exceeding a certain AC value
        acs = 0.6
        ace = 0.95
        dac = 0.05
        # nac=(ace-acs)/dac+1.001 
        nac=8
        ## 13-month running means
        dayac = np.empty((nac,nreg,nlev,nm,ny))
        dayacsm = np.empty((nac,nreg,nlev,nm,ny))
        ## temporary arrays
        # critical ac that needs to be exceeded, from acs to ace
        acx = np.empty((nac))
        # monthly mean ac for a given month and region
        aczt = np.empty((nf))
        # derived exceeding days for a given ac
        dayt = np.empty((nac))
        # derived exceeding days for a given ac, 13-month running mean
        daytsm = np.empty((nac))
        # original forecast days, from 0 to 16
        days = np.empty((nf))
        tmpday = np.empty((ny*nm))
        tmpdaysm = np.empty((ny*nm))
        bad1 = -999.900
        bad = -99.9
        ## read from source data, and pick HGT AC in NH and SH and on 1000hPa and 500hPa 
        inf_old_array = np.append([0], np.fromfile(inf_old, dtype='>f4'))
        inf_new_array = np.append([0], np.fromfile(inf_new, dtype='>f4'))
        start_count = -36
        end_count = 0
        for jy in range(ny1):
            for mmm in range(nm):
                for n in range(nvar1):
                    for k in range(nlev1):
                        start_count = start_count + 36
                        end_count = end_count + 36
                        i_j = inf_old_array[2+start_count:end_count]
                        var1[:,0,k,mmm,n,jy] = i_j[0:17]
                        var1[:,1,k,mmm,n,jy] = i_j[17:]
                #NH, 1000hPa
                acz1[:,0,0,mmm,jy] = var1[:,0,0,mmm,3,jy]
                #NH, 500hPa
                acz1[:,0,1,mmm,jy] = var1[:,0,1,mmm,3,jy]
                #SH, 1000hPa
                acz1[:,1,0,mmm,jy] = var1[:,1,0,mmm,3,jy]
                #SH, 500hPa
                acz1[:,1,1,mmm,jy] = var1[:,1,1,mmm,3,jy]
        start_count = -87
        end_count = 0
        for jy in range(ny2):
            for mmm in range(nm):
                for n in range(nvar2):
                    for k in range(nlev2):
                        start_count = start_count + 87 
                        end_count = end_count + 87
                        i_j = inf_new_array[2+start_count:end_count]
                        var2[:,0,k,mmm,n,jy] = i_j[0:17]
                        var2[:,1,k,mmm,n,jy] = i_j[17:34]
                        var2[:,2,k,mmm,n,jy] = i_j[34:51]
                        var2[:,3,k,mmm,n,jy] = i_j[51:68]
                        var2[:,4,k,mmm,n,jy] = i_j[68:]
                #NH, 1000hPa
                acz2[:,0,0,mmm,jy] = var2[:,1,0,mmm,0,jy]
                #NH, 500hPa
                acz2[:,0,1,mmm,jy] = var2[:,1,2,mmm,0,jy]
                #SH, 1000hPa
                acz2[:,1,0,mmm,jy] = var2[:,2,0,mmm,0,jy]
                #SH, 500hPa
                acz2[:,1,1,mmm,jy] = var2[:,2,2,mmm,0,jy]
        ## merge
        for i in range(nf):
            for j in range(nreg):
                for k in range(nlev):
                    for mmm in range(nm):
                        for iy in range(years1,yearm):
                            jy = iy-years1
                            acz[i,j,k,mmm,jy] = acz1[i,j,k,mmm,jy]
                        for iy in range(yearm, yeare+1):
                            jy = iy-years1
                            jy2 = iy-years2
                            acz[i,j,k,mmm,jy] = acz2[i,j,k,mmm,jy2]
        ## compute annual mean
        for iy in range(years1, yeare+1):
            jy = iy-years1
            for k in range(nlev):
                for i in range(nf):
                    for j in range(nreg):
                        ngood = 0
                        xtmp = 0
                        for mmm in range(nm):
                            if acz[i,j,k,mmm,jy] >= 0:
                                xtmp = xtmp + acz[i,j,k,mmm,jy]
                                ngood = ngood + 1
                        if ngood >= 6:
                            acz_ann[i,j,k,jy] = xtmp/ngood
                        else:
                            acz_ann[i,j,k,jy] = -999.999
        ## determine the days at which forecast AC exceeding a certain value
        for nc in range(nac):
            # critical ac that needs to be exceeded
            acx[nc] = acs+(nc)*dac
        for i in range(nf):
            days[i] = i
        for j in range(nreg):
            for k in range(nlev):
                for jy in range(ny):
                    for mmm in range(nm):
                        ngood = 0
                        for i in range(nf):
                            aczt[i]=acz[i,j,k,mmm,jy]
                            if aczt[i] >= 0:
                                ngood = ngood + 1
                        for nc in range(nac):
                            dayt[nc] = -999.999
                        if ngood >= 6:
                            for nc in range(nac):
                                #i=nf,2,-1
                                for i in range(nf-1,1,-1):
                                    if (aczt[i] >= 0 and aczt[i-1] >= 0) and (acx[nc] < aczt[i-1] and acx[nc] >= aczt[i]):
                                        dayt[nc] = days[i-1]+(days[i]-days[i-1])/(aczt[i]-aczt[i-1])*(acx[nc]-aczt[i-1])
                        for nc in range(nac):
                            dayac[nc,j,k,mmm,jy] = dayt[nc]
                ## compute 13-month running mean
                for nc in range(nac):
                   for jy in range(ny):
                       for mmm in range(nm):
                           nym = (jy)*12+(mmm)
                           dayacsm[nc,j,k,mmm,jy] = -999.999  
                           tmpday[nym] = dayac[nc,j,k,mmm,jy]
                   for jy in range(ny):
                       for mmm in range(nm):
                           nym = (jy)*12+(mmm)
                           #print(str(nym)+' '+str(nsm)+' '+str(ny*nm-nsm))
                           if nym > nsm and nym < (ny*nm-nsm):
                               ssum = 0
                               nct = 0
                               for kk in range(nym-nsm,nym+nsm+1):
                                   if tmpday[kk] > 0:
                                       ssum = ssum + tmpday[kk]
                                       nct = nct + 1
                               if nct >= (nsm2-3):
                                   dayacsm[nc,j,k,mmm,jy] = ssum/nct
        for jy in range(ny):
            for mmm in range(nm):
               for k in range(nlev):
                   for j in range(nreg):
                       print(dayac[:,j,k,mmm,jy]) 
                       exit()
#################################
#################################
#################################
###############################################################

## longterm stats of AC, bias and RMSE
#${sorcdir}/graphmon_all.sh                         ;#since 1996. HGT
#${sorcdir}/graphmon_all_2008.sh                    ;#since 2008, WIND
#${sorcdir}/graphmon_gfsecm.sh
#${sorcdir}/graphmon_gfs4cyc.sh
