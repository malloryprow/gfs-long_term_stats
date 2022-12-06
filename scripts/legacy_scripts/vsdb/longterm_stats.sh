#!/bin/ksh
set -x

# Fanglin Yang, April 2013
# submit jobs at the beginning of each month to 
# compute daily scores using VSDB data base     

export sorcdir=/gpfs/dell2/emc/modeling/noscrub/Fanglin.Yang/vrfygfs/longterm/long_vsdb
export execdir=/gpfs/dell6/ptmp/$USER/longterm
export SUB=/u/Fanglin.Yang/bin/sub_wcoss_d
export NDATE=/gpfs/dell1/nco/ops/nwprod/prod_util.v1.1.4/exec/ips/ndate
export QUEUE=dev_shared
export ACCOUNT=GFS-DEV


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


#------------------------------------
# Submit job for next monthly stats
#------------------------------------
#export mx=`expr $mm + 1 `
#if [ $mx -eq 13 ]; then
# export mx=1
# export yy=`expr $yy + 1 `
#fi
#if [ $mx -lt 10 ]; then mx=0$mx; fi
#job=longterm_stats.sh
#$SUB  -a $ACCOUNT -q $QUEUE -p 1/1/S -r 1024/1 -t 02:59:00 \
#    -w ${yy}${mx}020600 -j longstats -o $sorcdir/longterm_stats.out $sorcdir/$job


#----------------------------------------------
# get daily data for the current year and month
# submit jobs for one model one cycle at a time
rtime=`date -u '+%Y%m%d%H'`
rtime=`$NDATE +1 $rtime `
#----------------------------------------------

for model in gfs ecm cmc fno cdas ukm jma cfsr; do
 if [ $model = "gfs" ]; then
  cycles="00 06 12 18"
 elif [ $model = "cdas" -o $model = "cfsr" ]; then
  export cycles="00"
 else
  export cycles="00 12"
 fi
for cyc in $cycles ; do
 export mdlist="$model"
 export cyclist="$cyc"
 export years=$yeare
 listvar=sorcdir,execdir,years,yeare,mdlist,cyclist
    $SUB  -e $listvar -a $ACCOUNT -q $QUEUE -p 1/1/S -r 1024/1 -t 06:00:00 \
    -w ${rtime} -j long_$mdlist$cyclist \
    -o $execdir/long_$mdlist$cyclist.out \
    ${sorcdir}/vsdb_daily.sh  
done
 rtime=`$NDATE +1 $rtime`
done
#------------------------------------



#-----------------------
# submit jobs to compute monthly means and 
# make graphics to run next day

rtime=`$NDATE +24 $(date -u '+%Y%m%d%H') `

job=longterm_plots.sh
$SUB  -a $ACCOUNT -q $QUEUE -p 1/1/S -r 1024/1 -t 06:00:00 \
    -w $rtime  -j longplot  -o $sorcdir/longterm_plots.out $sorcdir/$job



exit



