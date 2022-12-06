#!/bin/ksh
set -x

# Fanglin Yang, April 2013
# submit jobs at the beginning of each month to 
# 1. compute monthly mean scores
# 2. make plots for display at emcrzdm.ncep.noaa.gov

export sorcdir=/gpfs/dell2/emc/modeling/noscrub/Fanglin.Yang/vrfygfs/longterm/long_vsdb
export execdir=/gpfs/dell6/ptmp/$USER/longterm                     
cd $sorcdir || exit
chmod u+x *.sh */*.sh
mkdir -p $execdir

yyyymmdd=`date '+%Y%m%d'`
export yeare=` echo $yyyymmdd | cut -c1-4 `
export yy=` echo $yyyymmdd | cut -c1-4 `
export mm=` echo $yyyymmdd | cut -c5-6 `
export dd=` echo $yyyymmdd | cut -c7-8 `

export mm1=`expr $mm - 1 `          
if [ $mm1 -eq 0 ]; then 
  export yeare=`expr $yeare - 1 ` 
  export mm1=12
fi


## compute monthly means
${sorcdir}/monthly_ac.sh                  
${sorcdir}/monthly_rms.sh                  


#------------------------------------
# determine map time stamps               
#------------------------------------
## maps start from sdate and end at edate
set -A mlist none jan feb mar apr may jun jul aug sep oct nov dec
set -A dlist none 31 28 31 30 31 30 31 31 30 31 30 31
export years=1996
export sdate=01jan${years}
export year1=`expr $yeare - 1 ` 
export sdat1=01${mlist[$mm]}${year1}
export edate=${dlist[$mm1]}${mlist[$mm1]}${yeare}

##useful forecast day plots
${sorcdir}/graph_ac_fcstday.sh

## longterm stats of AC, bias and RMSE
${sorcdir}/graphmon_all.sh                         ;#since 1996. HGT
${sorcdir}/graphmon_all_2008.sh                    ;#since 2008, WIND
${sorcdir}/graphmon_gfsecm.sh
${sorcdir}/graphmon_gfs4cyc.sh


exit



