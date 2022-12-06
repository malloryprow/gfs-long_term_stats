#!/bin/sh
set -x

# submit jobs at the beginning of each month to 
# 1. assemble daily scores from /global/shared/stat
# 2. compute monthly mean scores
# 3. make plots for display at emcrzdm.ncep.noaa.gov

export sorcdir=/global/save/Fanglin.Yang/vrfygfs/longterm/legacy
cd $sorcdir || exit
chmod u+x *.sh */*.sh

export years=1996
yyyymmdd=`date '+%Y%m%d'`
export yeare=` echo $yyyymmdd | cut -c1-4 `
export yy=` echo $yyyymmdd | cut -c1-4 `
export mm=` echo $yyyymmdd | cut -c5-6 `

batch=${batch:-yes}
if [ $batch = no ]; then exit; fi

#------------------------------------
# Submit job for next monthly stats
#------------------------------------
export mx=`expr $mm + 1 `
if [ $mx -eq 13 ]; then
 export mx=1
 export yy=`expr $yy + 1 `
fi
if [ $mx -lt 10 ]; then mx=0$mx; fi
job=longterm_legacy.sh
                                                                                     
/u/Fanglin.Yang/bin sub  -a GFS-T2O -q dev -p 1/1/S -t 02:59:00 \
    -r 1024/1 -w ${yy}${mx}021300 -j $job \
    -o $sorcdir/longterm_legacy.out $sorcdir/$job


#------------------------------------
# gather data 
#------------------------------------
for cycle in 00 12; do
export cyc=$cycle

## assemble daily scores
${sorcdir}/daily/readvrfy_cdas.sh
export mdlist="s e k m n"
${sorcdir}/daily/readvrfy_afjan2000.sh


## compute monthly means
export mdlist="s e k m n c"
${sorcdir}/monthly/month_HGT.sh    
${sorcdir}/monthly/month_WIND.sh    
done


## only for GFS 
for cycle in 06 18; do
export cyc=$cycle

## assemble daily scores
export mdlist="s"
${sorcdir}/daily/readvrfy_afjan2000.sh

## compute monthly means
export mdlist="s"
${sorcdir}/monthly/month_HGT.sh    
${sorcdir}/monthly/month_WIND.sh    
done

#------------------------------------
# determine map time stamps               
#------------------------------------
## maps start from sdate and end at edate
set -A mlist none jan feb mar apr may jun jul aug sep oct nov dec
set -A dlist none 31 28 31 30 31 30 31 31 30 31 30 31
export sdate=01jan${years}
export year1=`expr $yeare - 1 ` 
export sdat1=01${mlist[$mm]}${year1}
export mm1=`expr $mm - 1 `          
if [ $mm1 -eq 0 ]; then 
  export yeare=`expr $yeare - 1 ` 
  export mm1=12
fi
export edate=${dlist[$mm1]}${mlist[$mm1]}${yeare}


exit
## make plots for 00Z stats
export cyc=00
${sorcdir}/plotmon_all.sh           
${sorcdir}/plotmon_gfsecm.sh           


## make plots for GFS 4 cycles 
${sorcdir}/plotmon_gfs4cyc.sh

exit



