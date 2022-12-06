#!/bin/sh
set -x

#---------------------------------------------------
#--Fanglin Yang, April 2013
#  create daily mean stats from VSDB database for 
#  making longterm verification graphics.
#---------------------------------------------------

export years=${1:-${years:-2013}}
export yeare=${2:-${yeare:-2013}}
export mdlist=${3:-${mdlist:-"gfs"}}
export fcstcycle=${4:-${cyclist:-"00"}}


#----------------------------------------------------------------------
sorcdir=${sorcdir:-/gpfs/dell2/emc/modeling/noscrub/Fanglin.Yang/vrfygfs/longterm/long_vsdb}
machine=WCOSS_D      
machine=$(echo $machine|tr '[a-z]' '[A-Z]')
set -a;. $sorcdir/setup_envs.sh $machine
if [ $? -ne 0 -o $rc -gt 0 ]; then exit; fi
set -x

export execdir=${execdir:-/gpfs/dell6/ptmp/$USER/longterm}  
export vsdbhome=/gpfs/dell2/emc/modeling/noscrub/Fanglin.Yang/VRFY/vsdb
export vsdbsave=/gpfs/dell2/emc/modeling/noscrub/Fanglin.Yang/vrfygfs/vsdb_data
export doftp="NO"

export sfcvsdb="NO"         
export makemap="NO"         
export vlength=384         

#--------------------------------------------------
#export mdlist=${mdlist:-"gfs ecm cmc fno cdas ukm jma cfsr"}
for model in $mdlist; do
#--------------------------------------------------

#if [ $model = "gfs" ]; then
# export fcstcycle=${cyclist:-"00 06 12 18"}
#elif [ $model = "cdas" -o $model = "cfsr" ]; then
# export fcstcycle=${cyclist:-"00"}
#else
# export fcstcycle=${cyclist:-"00 12"}
#fi

#--------------------------------------------------
year=$years
while [ $year -le $yeare ]; do
for cyc in $fcstcycle ; do
#--------------------------------------------------

  export vhrlist="${cyc}"    ;#force vrfy to be done every 24 hours strating from cycle time
  export fcycle="${cyc}"
  export mdlist="${model}"
  export vsdblist="${vsdbsave}"    
  export DATEST=${year}0101                               
  export DATEND=${year}1231 
  export rundir=$execdir/${model}/$fcycle/${year}

  ${vsdbhome}/verify_exp_step2.sh


sleep 600

  savebin=${sorcdir}/daily/$fcycle/$model
  mkdir -p $savebin

## save pres files
  for area in G2PNA G2 G2NHX  G2SHX G2TRO ; do
  for var in WIND HGT T U V ; do
   filein=${rundir}/${area}/pres/${var}/${var}_${area}_${year}0101${year}1231.bin
   fileout=${var}_${area}_${model}${fcycle}Z${year}.bin
   ctlin=${rundir}/${area}/pres/${var}/${var}_${area}_${year}0101${year}1231.ctl
   ctlout=${var}_${area}_${model}${fcycle}Z.ctl

    nsleep=0; tsleep=120;   msleep=150   
    while test ! -s $filein -a $nsleep -lt $msleep;do
      sleep $tsleep
      nsleep=`expr $nsleep + 1`
    done

    if [ -s $filein ]; then 
     cp $filein  ${savebin}/$fileout
     if [ ! -s ${savebin}/$ctlout ]; then cp $ctlin  ${savebin}/$ctlout ;fi
    fi
  done
  done


## save anom files
  for area in G2 G2NHX  G2SHX G2TRO G2PNA; do

    filestatus=${rundir}/${area}/anom/HGT/HGT_P250_${area}_${year}0101${year}1231.bin
    nsleep=0; tsleep=120;   msleep=150   
    while test ! -s $filestatus -a $nsleep -lt $msleep;do
      sleep $tsleep
      nsleep=`expr $nsleep + 1`
    done

  for var in HGT T U V WIND PMSL; do
   for lev in P1000 P850 P700 P500 P250 MSL; do
    filein=${rundir}/${area}/anom/${var}/${var}_${lev}_${area}_${year}0101${year}1231.bin
    fileout=${var}_${lev}_${area}_${model}${fcycle}Z${year}.bin 
    ctlin=${rundir}/${area}/anom/${var}/${var}_${lev}_${area}_${year}0101${year}1231.ctl
    ctlout=${var}_${lev}_${area}_${model}${fcycle}Z.ctl 
    if [ -s $filein ]; then 
     cp $filein  ${savebin}/$fileout
     if [ ! -s ${savebin}/$ctlout ]; then cp $ctlin  ${savebin}/$ctlout ;fi
    fi
   done
  done
  done


done    ;#done fcycle 
year=`expr $year + 1 `
done    ;#done year
done    ;#done model


exit




