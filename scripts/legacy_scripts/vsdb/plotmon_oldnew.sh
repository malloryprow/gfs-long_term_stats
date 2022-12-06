#!/bin/ksh
set -x

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#  Compare stats between the legacy Pete-Zhu scores and the new VSDB-based scores 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
export sorcdir=/global/save/Fanglin.Yang/vrfygfs/longterm/legacy
export sorcdirx=/global/save/Fanglin.Yang/vrfygfs/longterm/long_vsdb

export sdate=${sdate:-01jan1996}
export edate=${edate:-31dec2012}
export sdat1=${sdat1:-01jan2012}                 ;#for computing last year average
export cyc=${cyc:-"00"}                          ;#forecast cycle
years=${years:-`echo $sdate |cut -c 6-9`}
yeare=${yeare:-`echo $edate |cut -c 6-9`}
#------------------------------------------------------------------


export HGTplot="YES"
export WINDplot="YES"
export ftpdir=${ftpdir:-/home/people/emc/www/htdocs/gmb/STATS_vsdb/oldnew/map}
export doftp=${doftp:-"YES"}        ;#ftp daily maps to web site

export mdlist="GFS ECM CDAS"                                   ;#models for line plots
export mdlist2d="GFS ECM CDAS"                                 ;#models for 2D map plots

export fdays=${fdays:-"1 2 3 4 5 6 7 8"}         ;#forecast day
export waves=${waves:-"120"}                     ;#wave numbers for anomaly correlations
export levsz=${levsz:-"500 1000"}                ;#levels for HGT
export levsw=${levsw:-"850 200"}                 ;#levels for tropical wind
export smth=${smth:-0}                           ;#number of months used for computing running mean
export xlon2d=11                                 ;#forecast days+1 to show on 2D and dieoff maps 


export datadir=${sorcdir}/monthly
export datadirx=${sorcdirx}/monthly
export rundir=/stmp/$LOGNAME/oldnew
mkdir -p $rundir; cd $rundir; rm *.gs *.png

###################################################################################
###################################################################################

#-- create  grads ctl files for line plots
#--old
k=0
for model in $mdlist; do
  k=`expr $k + 1 `
  if [ $model = "GFS"  ]; then export mdls="s"; fi
  if [ $model = "ECM"  ]; then export mdls="e"; fi
  if [ $model = "UKM"  ]; then export mdls="k"; fi
  if [ $model = "CMC"  ]; then export mdls="m"; fi
  if [ $model = "FNO"  ]; then export mdls="n"; fi
  if [ $model = "CDAS" ]; then export mdls="c"; fi
  export ctlHGT${k}=${datadir}/HGT${mdls}${cyc}Z_month.ctl
  export ctlWIND${k}=${datadir}/WIND${mdls}${cyc}Z_month.ctl
done

#--new
for model in $mdlist; do
  k=`expr $k + 1 `
  if [ $model = "GFS"  ]; then export mdls="gfs"; fi
  if [ $model = "ECM"  ]; then export mdls="ecm"; fi
  if [ $model = "UKM"  ]; then export mdls="ukm"; fi
  if [ $model = "CMC"  ]; then export mdls="cmc"; fi
  if [ $model = "FNO"  ]; then export mdls="fno"; fi
  if [ $model = "CDAS" ]; then export mdls="cdas"; fi
  export ctlHGT${k}=${datadirx}/AC_HGT${mdls}${cyc}Z_month.ctl
  export ctlWIND${k}=${datadirx}/RMS_WIND${mdls}${cyc}Z_month.ctl
done

export nmd=`echo $mdlist | wc -w`          ;#count number of models
export nmdx=`expr $nmd \* 2 `                                           
set -A mdname none $mdlist $mdlist
export smth2=`expr $smth \/ 2 `

#-- create  grads ctl files for 2D and dieoff maps
#--old
k=0
for model in $mdlist2d; do
  k=`expr $k + 1 `
  if [ $model = "GFS"  ]; then export mdls="s"; fi
  if [ $model = "ECM"  ]; then export mdls="e"; fi
  if [ $model = "UKM"  ]; then export mdls="k"; fi
  if [ $model = "CMC"  ]; then export mdls="m"; fi
  if [ $model = "FNO"  ]; then export mdls="n"; fi
  if [ $model = "CDAS" ]; then export mdls="c"; fi
  export ctl2dHGT${k}=${datadir}/HGT${mdls}${cyc}Z_month.ctl
  export ctl2dWIND${k}=${datadir}/WIND${mdls}${cyc}Z_month.ctl
done

#--new
for model in $mdlist2d; do
  k=`expr $k + 1 `
  if [ $model = "GFS"  ]; then export mdls="gfs"; fi
  if [ $model = "ECM"  ]; then export mdls="ecm"; fi
  if [ $model = "UKM"  ]; then export mdls="ukm"; fi
  if [ $model = "CMC"  ]; then export mdls="cmc"; fi
  if [ $model = "FNO"  ]; then export mdls="fno"; fi
  if [ $model = "CDAS" ]; then export mdls="cdas"; fi
  export ctl2dHGT${k}=${datadirx}/AC_HGT${mdls}${cyc}Z_month.ctl
  export ctl2dWIND${k}=${datadirx}/RMS_WIND${mdls}${cyc}Z_month.ctl

done
export nmd2d=`echo $mdlist2d | wc -w`          ;#count number of models on 2D and dieoff maps
export nmd2dx=`expr $nmd2d \* 2 `                                           
set -A mdname2d none $mdlist2d $mdlist2d


#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
if [ $HGTplot = "YES" ]; then

# time series of anomaly correlations, rmse and bias of geopotential 
# height at 1000hPa and 500hPa in the NH and SH, $smth running mean 
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
for area in NH SH; do
 if [ $area = "NH" ]; then ylat=1 ; ylatx=2; fi
 if [ $area = "SH" ]; then ylat=2 ; ylatx=3; fi
for lev in $levsz; do
#-----------------------------------------------------------------------

#...................................
for wav in $waves; do
 if [ $wav = "13" ];   then export wave="1-3"  ; fi
 if [ $wav = "49" ];   then export wave="4-9"  ; fi
 if [ $wav = "1020" ]; then export wave="10-20"  ; fi
 if [ $wav = "120" ];  then export wave="1-20"  ; fi
#...................................

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# line plots of time series
for day in $fdays; do
export xlon=`expr $day + 1 `
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
cat >acz_wave${wav}_${area}${lev}mb_day${day}.gs <<EOF1 
'reinit'; 'set font 1'
              'open ${ctlHGT1}';  mdc.1=${mdname[1]}
if($nmdx >1); 'open ${ctlHGT2}';  mdc.2=${mdname[2]} ;endif
if($nmdx >2); 'open ${ctlHGT3}';  mdc.3=${mdname[3]} ;endif
if($nmdx >3); 'open ${ctlHGT4}';  mdc.4=${mdname[4]} ;endif
if($nmdx >4); 'open ${ctlHGT5}';  mdc.5=${mdname[5]} ;endif
if($nmdx >5); 'open ${ctlHGT6}';  mdc.6=${mdname[6]} ;endif
if($nmdx >6); 'open ${ctlHGT7}';  mdc.7=${mdname[7]} ;endif
if($nmdx >7); 'open ${ctlHGT8}';  mdc.8=${mdname[8]} ;endif

*-- define line styles and model names 
* cst.1=1; cst.2=5; cst.3=3; cst.4=5; cst.5=5; cst.6=3; cst.7=5; cst.8=5
* cth.1=9; cth.2=4; cth.3=4; cth.4=4; cth.5=4; cth.6=4; cth.7=4; cth.8=4
* cma.1=0; cma.2=8; cma.3=6; cma.4=1; cma.5=2; cma.6=0; cma.7=3; cma.8=7
  cst.1=1; cst.2=1; cst.3=1; cst.4=1; cst.5=1; cst.6=1; cst.7=1; cst.8=1
  cth.1=9; cth.2=9; cth.3=5; cth.4=5; cth.5=5; cth.6=5; cth.7=5; cth.8=5
  cma.1=0; cma.2=0; cma.3=0; cma.4=0; cma.5=0; cma.6=0; cma.7=0; cma.8=0
  cco.1=1; cco.2=2; cco.3=3; cco.4=4; cco.5=8; cco.6=9; cco.7=5; cco.8=6

  'set x $xlon' 
  'set y $ylat' 
  'set lev $lev' 
  'set time $sdate $edate' 

   i=1
   while (i <= $nmd)
     'define var'%i'=ave(ac${wav}.'%i',t-${smth2},t+${smth2})'
     j=i+$nmd
     'define var'%j'=ave(cor.'%j'(y=${ylatx}),t-${smth2},t+${smth2})'
    i=i+1
   endwhile

  xwd=7.0; ywd=4.0; yy=ywd/16
  xmin=1.0; xmax=xmin+xwd; ymin=6.0; ymax=ymin+ywd
  xt=xmin+0.3; xt1=xt+0.5; xt2=xt1+0.1; yt=ymin ;*for legend  
  titlx=xmin+0.5*xwd;  titly=ymax+0.20                  ;*for tytle
  xlabx=xmin+0.5*xwd;  xlaby=ymin-0.60
  'set parea 'xmin' 'xmax' 'ymin' 'ymax

*--find maximum and minmum values
   cmax=0.1; cmin=1
   i=1
   while (i <= $nmdx)
    'set gxout stat'
    'd var'%i
    range=sublin(result,9); zmin=subwrd(range,5); zmax=subwrd(range,6)
    if(zmax > cmax); cmax=zmax; endif
    if(zmin < cmin); cmin=zmin; endif
   i=i+1
   endwhile
   dist=cmax-cmin; cmin=cmin-0.6*dist; cmax=1.2*cmax        
   if (cmin < -1); cmin=-1; endif
   if (cmax > 1.0); cmax=1.0; endif
   cmin=substr(cmin,1,3); cmax=substr(cmax,1,3); cint=0.1
   say 'cmin cmax cint 'cmin' 'cmax' 'cint

   i=1
   while (i <= $nmdx)
    'set gxout stat'  ;* first compute last-year means and count good data numbers
    'set time $sdat1 $edate' 
    'd var'%i
    ln=sublin(result,11); wd=subwrd(ln,2); a=substr(wd,1,5)
    ln=sublin(result,7); wd=subwrd(ln,8); b=substr(wd,1,5)
    if ( b>0 )
      'set strsiz 0.13 0.13'; yt=yt+yy
      'set line 'cco.i' 'cst.i' 11'; 'draw line 'xt' 'yt' 'xt1' 'yt
      'set string 'cco.i' bl 6'
      if(i=1)
        'draw string 'xt2' 'yt' 'mdc.i '  'a  '  last 1yr Avg'
      else
       if (i<=$nmd)
        'draw string 'xt2' 'yt' 'mdc.i '  'a  
       else
        'draw string 'xt2' 'yt' VSDB_'mdc.i '  'a  
       endif
      endif

      'set time $sdate $edate' 
      'set gxout line'
      'set display color white'; 'set missconn on';     'set grads off'; 'set grid on'
      'set xlopts 1 6 0.14'
      if( $nmd >= 1); 'set xlopts 1 6 0.0';endif
      'set ylopts 1 6 0.14'; 'set clopts 1 6 0.0'
      'set cstyle 'cst.i; 'set cthick 'cth.i; 'set cmark 'cma.i; 'set ccolor 'cco.i
      'set vrange 'cmin' 'cmax; 'set ylint 'cint
*     'set xlint $xtick'
      'd var'%i
     endif
   i=i+1
   endwhile

  'set string 1 bc 7'
  'set strsiz 0.16 0.16'
* 'draw string 'titlx' 'titly' ${area} HGT AC: ${lev}hPa Day${day}, ${smth}-Mon Mean'
  'draw string 'titlx' 'titly' ${area} HGT AC: ${lev}hPa Day${day}'
  'set string 1 bl 3'
  'set strsiz 0.09 0.09'


*---------------------------------------------------------
if ($nmd >= 1); then
*---------------------------------------------------------
* plot AC difference between others and the first
  ymin=ymin-4; ymax=ymin+4
  'set parea 'xmin' 'xmax' 'ymin' 'ymax
  xlabx=xmin+0.45*xwd;  xlaby=ymin-0.60

*--find maximum and minmum values to determine y-axis labels
 cmax=-1.0; cmin=1.0
 i=1
 while (i <= $nmd)
  j=i+${nmd}
  'set gxout stat'
  'd var'%i     ;* number of records
  ln=sublin(result,11); wd=subwrd(ln,2); a=substr(wd,1,3)
  if ( a>0 )
    'set gxout stat'
    'd 100*(var'%j'-var'%i')/var'%i 
    range=sublin(result,9); zmin=subwrd(range,5); zmax=subwrd(range,6) 
    if(zmax > cmax); cmax=zmax; endif 
    if(zmin < cmin); cmin=zmin; endif 
   endif 
 i=i+1 
 endwhile 
 dist=cmax-cmin 
 if (dist = 0); dist=1; endif 
 cmin=cmin-0.01*dist; cmax=cmax+0.01*dist 
 cmin=substr(cmin,1,6); cmax=substr(cmax,1,6) 
 cintp=10*substr(dist/40,1,4) 
 if (cintp = 0); cintp=10*substr(dist/40,1,5); endif 
 if (cintp = 0); cintp=10*substr(dist/40,1,6); endif
 i=1
 while (i <= $nmd)
  j=i+${nmd}
  'set gxout stat'
  'd var'%i     ;* number of records
  ln=sublin(result,11); wd=subwrd(ln,2); a=substr(wd,1,3)
  if ( a>0 )
     'set gxout line'
     'set mproj off'
     'set display color white'; 'set missconn on';     'set grads off'; 'set grid on'
     'set xlopts 1 6 0.14'
     'set ylopts 1 6 0.14'; 'set clopts 1 6 0.0'
     'set vrange 'cmin' 'cmax; 'set ylint 'cintp; 'set xlint 48'
     'set cstyle 'cst.i; 'set cthick 'cth.i; 'set cmark 'cma.i; 'set ccolor 'cco.i
     if(i=1); 'set cstyle 1'; 'set cthick 1'; 'set cmark 0'; 'set ccolor 1'; endif
    'd 100*(var'%j'-var'%i')/var'%i 
*   'd var'%j'-var'%i 
  endif
 i=i+1
 endwhile

 'set string 1 bl 6'
 'set strsiz 0.14 0.14'
 'draw string 'xmin+0.2' 'ymax-0.4' Percent Difference'
*---------------------------------------------------------
endif            
*---------------------------------------------------------

 'set strsiz 0.15 0.15'
 'draw string 'xlabx' 'xlaby' Verification Date'
 'printim acz_wave${wav}_${area}${lev}mb_day${day}.png png x800 y800'
 'set vpage off'
'quit'
EOF1
grads -bcp "acz_wave${wav}_${area}${lev}mb_day${day}.gs"
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
done  ;# end of days
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# 2D maps of HGT AC varying with forecast days 
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
cat >acz_wave${wav}_${area}${lev}mb_alldays.gs <<EOF1 
'reinit'; 'set font 1'
'run /u/wx24fy/bin/grads/white.gs'
                'open ${ctl2dHGT1}'; mdc.1=${mdname2d[1]}
if($nmd2dx >1); 'open ${ctl2dHGT2}'; mdc.2=${mdname2d[2]} ;endif
if($nmd2dx >2); 'open ${ctl2dHGT3}'; mdc.3=${mdname2d[3]} ;endif
if($nmd2dx >3); 'open ${ctl2dHGT4}'; mdc.4=${mdname2d[4]} ;endif
if($nmd2dx >4); 'open ${ctl2dHGT5}'; mdc.5=${mdname2d[5]} ;endif
if($nmd2dx >5); 'open ${ctl2dHGT6}'; mdc.6=${mdname2d[6]} ;endif
if($nmd2dx >6); 'open ${ctl2dHGT7}'; mdc.7=${mdname2d[7]} ;endif
if($nmd2dx >7); 'open ${ctl2dHGT8}'; mdc.8=${mdname2d[8]} ;endif

  'set x 1 $xlon2d' 
  'set y $ylat' 
  'set lev $lev' 
* 'set time $sdate $edate' 
  'set time 01jan2007 $edate' 

   i=1
   while (i <= $nmd2d)
     'define var'%i'=ave(ac${wav}.'%i',t-${smth2},t+${smth2})'
     j=i+$nmd2d
     'define var'%j'=ave(cor.'%j'(y=${ylatx}),t-${smth2},t+${smth2})'
    i=i+1
   endwhile

  nframe=$nmd2dx
  xmin0=1.2;  xgap=0.2;  xlen=6.0
  ymax0=10.0; ygap=-0.1; ylen=-6.0
  if($nmd2dx >1); xlen=3;  endif
                 nframe2=1;  nframe3=2 
  if($nmd2dx >2); nframe2=2;  nframe3=4; ylen=-4.2;endif
  if($nmd2dx >4); nframe2=3;  nframe3=6; ylen=-2.8;endif
  if($nmd2dx >6); nframe2=4;  nframe3=8; ylen=-2.1; endif
                                                                                                                    
  i=1
  while ( i <= nframe )
    icx=1; if (i > nframe2); icx=2; endif
    if (i > nframe3); icx=3; endif
    if (i > nframe4); icx=4; endif
    xmin=xmin0+(icx-1)*(xlen+xgap)
    xmax=xmin+xlen
    icy=i; if (i > nframe2); icy=i-nframe2; endif
    if (i > nframe3); icy=i-nframe3; endif
    if (i > nframe4); icy=i-nframe4; endif
    ymax=ymax0+(icy-1)*(ylen+ygap)
    ymin=ymax+ylen
    titlx=xmin+0.15
    titly=ymax-0.3
    'set parea 'xmin' 'xmax' 'ymin' 'ymax
                                                                                                                    
    'run /u/wx24fy/bin/grads/rgbset.gs'
    'set xlopts 1 4 0.0'
    'set ylopts 1 4 0.0'
      if($nmd2dx <=2)
        'set xlopts 1 4 0.11'
        if(i=1);'set ylopts 1 4 0.11';endif
      endif
      if($nmd2dx >2 & $nmd2dx <=4)
        if(i=2|i=$nmd2dx);'set xlopts 1 4 0.11';endif
        if(i<=2);'set ylopts 1 4 0.11';endif
      endif
      if($nmd2dx >4 & $nmd2dx <=6)
        if(i=3|i=$nmd2dx);'set xlopts 1 4 0.11';endif
        if(i<=3);'set ylopts 1 4 0.11';endif
      endif
      if($nmd2dx >=7)
        if(i=4|i=$nmd2dx);'set xlopts 1 4 0.11';endif
        if(i<=4);'set ylopts 1 4 0.11';endif
      endif
    'set clopts 1 4 0.08'
    'set grid on'
    'set mproj off'
    'set gxout shaded'
    'set grads off'
*   'set clevs   -0.03 -0.02 -0.01 -0.005 -0.001 -0.0005 0 0.0005 0.001 0.005 0.01 0.02 0.03'
    'set clevs   -0.3 -0.2 -0.1 -0.05 -0.01 -0.005 0 0.005 0.01 0.05 0.1 0.2 0.3'
*   'set rbcols 39   38   37   36    35    34    32 62   64   65   66   67   68 69'
    'set rbcols 69   67   66   65   64   62  32   34   35  36   37   39'
    if(i<=$nmd2d); 'set clevs    0.2 0.3 0.4 0.5 0.6 0.7 0.75 0.8 0.85 0.9 0.95 0.97 ' ;endif
    if(i<=$nmd2d); 'set rbcols 31  33  35  37  39  42  44   45   47   49  73  75   77';endif
    'set xlevs 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 '
    'set ylint 5'
    if(i<=$nmd2d);'d var'%i ;endif
    if(i>$nmd2d);
     j=i-$nmd2d
     'd var'%j' - var'%i 
    endif
*
    'set gxout contour'
    'set grads off'
    'set ccolor 1'
    'set clevs   -0.3 -0.2 -0.1 -0.05 -0.01 -0.005 0 0.005 0.01 0.05 0.1 0.2 0.3'
*   'set clevs   -0.03 -0.02 -0.01 -0.005 -0.001 -0.0005 0 0.0005 0.001 0.005 0.01 0.02 0.03'
     if(i<=$nmd2d); 'set clevs    0.2 0.3 0.4 0.5 0.6 0.7 0.75 0.8 0.85 0.9 0.95 0.97 0.99' ;endif
    'set clab forced'
    'set cstyle 1'
    if(i<=$nmd2d);'d var'%i ;endif
*   if(i>$nmd2d);
*    j=i-$nmd2d
*    'd var'%j' - var'%i 
*   endif
       
    'set string 1 bl 7'
    'set strsiz 0.14 0.14'
    if(i <= $nmd2d); 'draw string 'titlx' 'titly' 'mdc.i; endif
    if(i > $nmd2d); 'draw string 'titlx' 'titly' 'mdc.i' new-old '; endif
  i=i+1
  endwhile
       
  'set string 1 bc 6'
  'set strsiz 0.15 0.15'
* 'draw string 4.2 10.4  HGT AC: ${area} ${lev}hPa, ${smth}-Mon Mean'   
  'draw string 4.2 10.4  HGT AC: ${area} ${lev}hPa'   
  'set string 1 bc 5'
  'set strsiz 0.13 0.13'
  'set strsiz 0.15 0.15'
  if($nmd2d >2)
    'draw string 4.3 0.9 Forecast Day'
    'run /u/wx24fy/bin/grads/cbarn.gs 0.95 0 4.1 0.40'
   else
    'draw string 4.3 3.5 Forecast Day'
    'run /u/wx24fy/bin/grads/cbarn.gs 0.95 0 4.1 2.90'
   endif
       
  'printim acz_wave${wav}_${area}${lev}mb_alldays.png png x700 y700'
  'set vpage off'
'quit'
EOF1
grads -bcp "acz_wave${wav}_${area}${lev}mb_alldays.gs"
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#...................................
done  ;# end of AC wave
#...................................


#...................................
for vname in zrms zerr; do
 if [ $vname = "zrms" ]; then vnamex=rms; export des="RMSE" ; fi
 if [ $vname = "zerr" ]; then vnamex=bias; export des="Bias" ; fi
#...................................

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# line plots of time series
for day in $fdays; do
export xlon=`expr $day + 1 `
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
cat >${vname}_${area}${lev}mb_day${day}.gs <<EOF1 
'reinit'; 'set font 1'
             'open ${ctlHGT1}'; mdc.1=${mdname[1]}
if($nmdx >1); 'open ${ctlHGT2}'; mdc.2=${mdname[2]} ;endif
if($nmdx >2); 'open ${ctlHGT3}'; mdc.3=${mdname[3]} ;endif
if($nmdx >3); 'open ${ctlHGT4}'; mdc.4=${mdname[4]} ;endif
if($nmdx >4); 'open ${ctlHGT5}'; mdc.5=${mdname[5]} ;endif
if($nmdx >5); 'open ${ctlHGT6}'; mdc.6=${mdname[6]} ;endif
if($nmdx >6); 'open ${ctlHGT7}'; mdc.7=${mdname[7]} ;endif
if($nmdx >7); 'open ${ctlHGT8}'; mdc.8=${mdname[8]} ;endif

*-- define line styles and model names 
* cst.1=1; cst.2=5; cst.3=3; cst.4=5; cst.5=5; cst.6=3; cst.7=5; cst.8=5
* cth.1=9; cth.2=4; cth.3=4; cth.4=4; cth.5=4; cth.6=4; cth.7=4; cth.8=4
* cma.1=0; cma.2=8; cma.3=6; cma.4=1; cma.5=2; cma.6=0; cma.7=3; cma.8=7
  cst.1=1; cst.2=1; cst.3=1; cst.4=1; cst.5=1; cst.6=1; cst.7=1; cst.8=1
  cth.1=9; cth.2=9; cth.3=5; cth.4=5; cth.5=5; cth.6=5; cth.7=5; cth.8=5
  cma.1=0; cma.2=0; cma.3=0; cma.4=0; cma.5=0; cma.6=0; cma.7=0; cma.8=0
  cco.1=1; cco.2=2; cco.3=3; cco.4=4; cco.5=8; cco.6=9; cco.7=5; cco.8=6

  'set x $xlon' 
  'set y $ylat' 
  'set lev $lev' 
  'set time $sdate $edate' 

   i=1
   while (i <= $nmd)
     'define var'%i'=ave(${vname}.'%i',t-${smth2},t+${smth2})'
     j=i+$nmd
     'define var'%j'=ave(${vnamex}.'%j'(y=${ylatx}),t-${smth2},t+${smth2})'
    i=i+1
   endwhile

  xwd=7.0; ywd=4.0; yy=ywd/16
  xmin=1.0; xmax=xmin+xwd; ymin=6.0; ymax=ymin+ywd
  xt=xmin+0.3; xt1=xt+0.5; xt2=xt1+0.1; yt=ymin ;*for legend  
  titlx=xmin+0.5*xwd;  titly=ymax+0.20                  ;*for tytle
  xlabx=xmin+0.5*xwd;  xlaby=ymin-0.60
  'set parea 'xmin' 'xmax' 'ymin' 'ymax

*--find maximum and minmum values
   cmax=-10000; cmin=10000
   i=1
   while (i <= $nmdx)
    'set gxout stat'
    'd var'%i
    range=sublin(result,9); zmin=subwrd(range,5); zmax=subwrd(range,6)
    if(zmax > cmax & zmax < 1000 ); cmax=zmax; endif
    if(zmin < cmin & zmin > -1000 ); cmin=zmin; endif
   i=i+1
   endwhile
   dist=cmax-cmin; cmin=cmin-0.6*dist; cmax=cmax+0.2*dist
   cmin=substr(cmin,1,6); cmax=substr(cmax,1,6); cint=10*substr((cmax-cmin)/100,1,4)
   if (cint = 0); cint=substr((cmax-cmin)/10,1,4); endif
   if (cint = 0); cint=0.1*substr((cmax-cmin),1,4); endif
   if (cint = 0); cint=0.01*substr((cmax-cmin)*10,1,4); endif
   say 'cmin cmax cint 'cmin' 'cmax' 'cint

   i=1
   while (i <= $nmdx)
    'set gxout stat'  ;* first compute last-year means and count good data numbers
    'set time $sdat1 $edate' 
    'd var'%i
    ln=sublin(result,11); wd=subwrd(ln,2); a=substr(wd,1,5)
    ln=sublin(result,7); wd=subwrd(ln,8); b=substr(wd,1,5)
    if ( b>0 )
      'set strsiz 0.13 0.13'; yt=yt+yy
      'set line 'cco.i' 'cst.i' 11'; 'draw line 'xt' 'yt' 'xt1' 'yt
      'set string 'cco.i' bl 6'
      if(i=1)
        'draw string 'xt2' 'yt' 'mdc.i '  'a  '  Last 1yr Avg'
      else
       if (i<=$nmd)
        'draw string 'xt2' 'yt' 'mdc.i '  'a  
       else
        'draw string 'xt2' 'yt' VSDB_'mdc.i '  'a  
       endif
      endif

      'set time $sdate $edate' 
      'set gxout line'
      'set display color white'; 'set missconn on';     'set grads off'; 'set grid on'
      'set xlopts 1 6 0.14'
      if( $nmdx > 1); 'set xlopts 1 6 0.0'; endif
      'set ylopts 1 6 0.14'; 'set clopts 1 6 0.0'
      'set cstyle 'cst.i; 'set cthick 'cth.i; 'set cmark 'cma.i; 'set ccolor 'cco.i
      'set vrange 'cmin' 'cmax; 'set ylint 'cint
*     'set xlint $xtick'
      'd var'%i
     endif
   i=i+1
   endwhile

  'set string 1 bc 7'
  'set strsiz 0.16 0.16'
* 'draw string 'titlx' 'titly' ${area} HGT ${des}: ${lev}hPa Day${day}, ${smth}-Mon Mean'
  'draw string 'titlx' 'titly' ${area} HGT ${des}: ${lev}hPa Day${day}'
  'set string 1 bl 3'
  'set strsiz 0.09 0.09'

*---------------------------------------------------------
if ($nmd > 1 & $vname = zrms ); then
*---------------------------------------------------------
* plot  difference between others and the first
  ymin=ymin-4; ymax=ymin+4
  'set parea 'xmin' 'xmax' 'ymin' 'ymax
  xlabx=xmin+0.45*xwd;  xlaby=ymin-0.60

*--find maximum and minmum values to determine y-axis labels
 cmax=-10000; cmin=10000
 i=1
 while (i <= $nmd)
  j=i+${nmd}
  'set gxout stat'
  'd var'%i     ;* number of records
  ln=sublin(result,11); wd=subwrd(ln,2); a=substr(wd,1,3)
  if ( a>0 )
    'set gxout stat'
*   'd var'%j'-var'%i
    'd 100*(var'%j'-var'%i')/var'%i 
    range=sublin(result,9); zmin=subwrd(range,5); zmax=subwrd(range,6)
    if(zmax > cmax); cmax=zmax; endif
    if(zmin < cmin); cmin=zmin; endif
  endif
 i=i+1
 endwhile
 dist=cmax-cmin
 if (dist = 0); dist=1; endif
 cmin=cmin-0.01*dist; cmax=cmax+0.01*dist
 cmin=substr(cmin,1,6); cmax=substr(cmax,1,6)
 cintp=10*substr(dist/40,1,4)
 if (cintp = 0); cintp=10*substr(dist/40,1,5); endif
 if (cintp = 0); cintp=10*substr(dist/40,1,6); endif

 i=1
 while (i <= $nmd)
  j=i+${nmd}
  'set gxout stat'
  'd var'%i     ;* number of records
  ln=sublin(result,11); wd=subwrd(ln,2); a=substr(wd,1,3)
  if ( a>0 )
     'set gxout line'
     'set mproj off'
     'set display color white'; 'set missconn on';     'set grads off'; 'set grid on'
     'set xlopts 1 6 0.14'
     'set ylopts 1 6 0.14'; 'set clopts 1 6 0.0'
     'set vrange 'cmin' 'cmax; 'set ylint 'cintp
     'set cstyle 'cst.i; 'set cthick 'cth.i; 'set cmark 'cma.i; 'set ccolor 'cco.i
     if(i=1); 'set cstyle 1'; 'set cthick 1'; 'set cmark 0'; 'set ccolor 1'; endif
    'd 100*(var'%j'-var'%i')/var'%i 
*   'd var'%j'-var'%i
  endif
 i=i+1
 endwhile

 'set string 1 bl 6'
 'set strsiz 0.14 0.14'
 'draw string 'xmin+0.2' 'ymax-0.4'  Percent Difference'
*---------------------------------------------------------
endif            
*---------------------------------------------------------


  'set strsiz 0.15 0.15'
  'draw string 'xlabx' 'xlaby' Verification Date'

  'printim ${vname}_${area}${lev}mb_day${day}.png png x800 y800'
  'set vpage off'
'quit'
EOF1
grads -bcp "${vname}_${area}${lev}mb_day${day}.gs"
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
done   ;#end day
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# 2D maps of HGT RMSE or BIAS varying with forecast days 
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
cat >${vname}_${area}${lev}mb_alldays.gs <<EOF1 
'reinit'; 'set font 1'
'run /u/wx24fy/bin/grads/white.gs'
               'open ${ctl2dHGT1}'; mdc.1=${mdname2d[1]}
if($nmd2dx >1); 'open ${ctl2dHGT2}'; mdc.2=${mdname2d[2]} ;endif
if($nmd2dx >2); 'open ${ctl2dHGT3}'; mdc.3=${mdname2d[3]} ;endif
if($nmd2dx >3); 'open ${ctl2dHGT4}'; mdc.4=${mdname2d[4]} ;endif
if($nmd2dx >4); 'open ${ctl2dHGT5}'; mdc.5=${mdname2d[5]} ;endif
if($nmd2dx >5); 'open ${ctl2dHGT6}'; mdc.6=${mdname2d[6]} ;endif
if($nmd2dx >6); 'open ${ctl2dHGT7}'; mdc.7=${mdname2d[7]} ;endif
if($nmd2dx >7); 'open ${ctl2dHGT8}'; mdc.8=${mdname2d[8]} ;endif

  'set x 1 $xlon2d' 
  'set y $ylat' 
  'set lev $lev' 
* 'set time $sdate $edate' 
  'set time 01jan2007 $edate' 

   i=1
   while (i <= $nmd2d)
     'define var'%i'=ave(${vname}.'%i',t-${smth2},t+${smth2})'
     j=i+$nmd
     'define var'%j'=ave(${vnamex}.'%j'(y=${ylatx}),t-${smth2},t+${smth2})'
    i=i+1
   endwhile

*--find maximum and minmum values for first total field map
   cmax=-10000000.0; cmin=10000000.0
   i=1
*  while (i <= $nmd2d)
    'set gxout stat'
    'd var'%i
    range=sublin(result,9); zmin=subwrd(range,5); zmax=subwrd(range,6)
    if(zmax > cmax); cmax=zmax; endif
    if(zmin < cmin); cmin=zmin; endif
*  i=i+1
*  endwhile
   dist=cmax-cmin; cmin=cmin; cmax=cmax+0.1*dist
   cmin=substr(cmin,1,5); cmax=substr(cmax,1,5); cint=10*substr((cmax-cmin)/100,1,4)
   if (cint = 0); cint=substr((cmax-cmin)/10,1,4); endif
   if (cint = 0); cint=0.1*substr((cmax-cmin),1,4); endif
   if (cint = 0); cint=0.01*substr((cmax-cmin)*10,1,4); endif
   say 'cmin cmax cint 'cmin' 'cmax' 'cint
    bb1=cmin; bb2=cmin+cint; bb3=bb2+cint; bb4=bb3+cint; bb5=bb4+cint; bb6=bb5+cint
    bb7=bb6+cint; bb8=bb7+cint; bb9=bb8+cint; bb10=bb9+cint; bb11=bb10+cint

*--find maximum and minmum values for difference map
   cmax=-10000000.0; cmin=10000000.0
   i=1
   while (i <= $nmd2d)
    j=i+$nmd2d
    'set gxout stat'
    'd var'%j'-var'%i
    range=sublin(result,9); zmin=subwrd(range,5); zmax=subwrd(range,6)
    if(zmax > cmax); cmax=zmax; endif
    if(zmin < cmin); cmin=zmin; endif
   i=i+1
   endwhile
   dist=cmax-cmin; cmin=cmin; cmax=cmax+0.1*dist
   cmin=substr(cmin,1,6); cmax=substr(cmax,1,6);
   cintm=10*substr(cmin/50,1,4)
     if (cintm = 0); cintm=substr(cmin/5,1,4); endif
     if (cintm = 0); cintm=0.2*substr(cmin,1,4); endif
     if (cintm = 0); cintm=0.02*substr(cmin*10,1,4); endif
     if (cintm = 0); cintm=0.002*substr(cmin*100,1,4); endif
   cm1=cintm; cm2=cm1+cintm; cm3=cm2+cintm; cm4=cm3+cintm; cm5=cm4+cintm
              cm6=cm5+cintm; cm7=cm6+cintm; cm8=cm7+cintm; cm9=cm8+cintm
   cintp=10*substr(cmax/50,1,4)
     if (cintp = 0); cintp=substr(cmax/5,1,4); endif
     if (cintp = 0); cintp=0.2*substr(cmax,1,4); endif
     if (cintp = 0); cintp=0.02*substr(cmax*10,1,4); endif
     if (cintp = 0); cintp=0.002*substr(cmax*100,1,4); endif
   cp1=cintp; cp2=cp1+cintp; cp3=cp2+cintp; cp4=cp3+cintp; cp5=cp4+cintp
              cp6=cp5+cintp; cp7=cp6+cintp; cp8=cp7+cintp; cp9=cp8+cintp
   say 'cmin cmax cintm cintp 'cmin' 'cmax' 'cintm' 'cintp


  nframe=$nmd2dx
  xmin0=1.2;  xgap=0.2;  xlen=6.0
  ymax0=10.0; ygap=-0.1; ylen=-6.0
  if($nmd2dx >1); xlen=3;  endif
                 nframe2=1;  nframe3=2 
  if($nmd2dx >2); nframe2=2;  nframe3=4; ylen=-4.2;endif
  if($nmd2dx >4); nframe2=3;  nframe3=6; ylen=-2.8;endif
  if($nmd2dx >6); nframe2=4;  nframe3=8; ylen=-2.1; endif
                                                                                                                    

  i=1
  while ( i <= nframe )
  'set gxout stat'  ;*count good data numbers
  'd var'%i
  ln=sublin(result,7); wd=subwrd(ln,8); b=substr(wd,1,3)
  if ( b>0 )
    icx=1; if (i > nframe2); icx=2; endif
    if (i > nframe3); icx=3; endif
    if (i > nframe4); icx=4; endif
    xmin=xmin0+(icx-1)*(xlen+xgap)
    xmax=xmin+xlen
    icy=i; if (i > nframe2); icy=i-nframe2; endif
    if (i > nframe3); icy=i-nframe3; endif
    if (i > nframe4); icy=i-nframe4; endif
    ymax=ymax0+(icy-1)*(ylen+ygap)
    ymin=ymax+ylen
    titlx=xmin+0.15
    titly=ymax-0.3
    'set parea 'xmin' 'xmax' 'ymin' 'ymax

    'run /u/wx24fy/bin/grads/rgbset.gs'
    'set xlopts 1 4 0.0'
    'set ylopts 1 4 0.0'
      if($nmd2d <=2)
        'set xlopts 1 4 0.11'
        if(i=1);'set ylopts 1 4 0.11';endif
      endif
      if($nmd2dx >2 & $nmd2dx <=4)
        if(i=2|i=$nmd2dx);'set xlopts 1 4 0.11';endif
        if(i<=2);'set ylopts 1 4 0.11';endif
      endif
      if($nmd2dx >4 & $nmd2dx <=6)
        if(i=3|i=$nmd2dx);'set xlopts 1 4 0.11';endif
        if(i<=3);'set ylopts 1 4 0.11';endif
      endif
      if($nmd2dx >=7)
        if(i=4|i=$nmd2dx);'set xlopts 1 4 0.11';endif
        if(i<=4);'set ylopts 1 4 0.11';endif
      endif
    'set clopts 1 4 0.09'
    'set grid on'
    'set zlog on'
    'set mproj off'

    'set gxout shaded'
    'set grads off'
    'set clevs   'cm5' 'cm4' 'cm3' 'cm2' 'cm1' 0 'cp1' 'cp2' 'cp3' 'cp4' 'cp5
    'set rbcols 39    37    36   35    34    32 62   64    65   66     67   69'
    if(i<=$nmd2d);'set clevs   'bb1' 'bb2' 'bb3' 'bb4' 'bb5' 'bb6' 'bb7' 'bb8' 'bb9' 'bb10' 'bb11 ;endif
    if(i<=$nmd2d);'set rbcols 41   42    43    44    45   46  47  48    49   55     56   57';endif
    'set xlint 1'
    if(i<=$nmd2d);'d var'%i ;endif
    if(i>$nmd2d)
      j=i-$nmd2d
      'd var'%j '- var'%i 
    endif
*
    'set gxout contour'
    'set grads off'
    'set ccolor 1'
    'set clevs   'cm5' 'cm4' 'cm3' 'cm2' 'cm1' 0 'cp1' 'cp2' 'cp3' 'cp4' 'cp5
    if(i<=$nmd2d);'set clevs   'bb1' 'bb2' 'bb3' 'bb4' 'bb5' 'bb6' 'bb7' 'bb8' 'bb9' 'bb10' 'bb11 ;endif
*   'set clab on'
    if(i=1);'set clab forced';endif
    'set cstyle 3'
    if(i<=$nmd2d);'d var'%i ;endif

    'set string 1 bl 7'
    'set strsiz 0.16 0.16'
    if(i<=$nmd2d);'draw string 'titlx' 'titly' 'mdc.i ;endif
    if(i>$nmd2d);'draw string 'titlx' 'titly' 'mdc.i 'new-old'; endif
  endif
  i=i+1
  endwhile

  'set string 1 bc 6'
  'set strsiz 0.14 0.14'
* 'draw string 4.5 10.35  ${area} ${lev}hPa HGT ${des}, ${smth}-Mon Mean'
  'draw string 4.5 10.35  ${area} ${lev}hPa HGT ${des}'
  'set string 1 bc 4'
  'set strsiz 0.14 0.14'
  'set strsiz 0.15 0.15'
  if($nmd2d >2)
    'draw string 4.3 0.9 Forecast Day'
    'run /u/wx24fy/bin/grads/cbarn.gs 0.95 0 4.1 0.40'
   else
    'draw string 4.3 3.5 Forecast Day'
    'run /u/wx24fy/bin/grads/cbarn.gs 0.95 0 4.1 2.90'
   endif
       
  'printim ${vname}_${area}${lev}mb_alldays.png png x700 y700'
  'set vpage off'
'quit'
EOF1
grads -bcp "${vname}_${area}${lev}mb_alldays.gs"        
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#...................................
done   ;#end vname
#...................................

#-----------------------------------------------------------------------
done   ;#end lev
done   ;#end area
#-----------------------------------------------------------------------
fi
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------







#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
if [ $WINDplot = "YES" ]; then

##for tropics
ylatx=4  

# time series of tropical wind rmse at 850hPa and 200hPa, $smth running mean 
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
for lev in $levsw; do
#-----------------------------------------------------------------------

#...................................
for vname in  wrms serr; do
 if [ $vname = "urms" ]; then export vnamex=rms; des="U Wind RMSE" ; fi
 if [ $vname = "vrms" ]; then export vnamex=rms; des="V Wind RMSE" ; fi
 if [ $vname = "srms" ]; then export vnamex=rms; des="Wind Speed RMSE" ; fi
 if [ $vname = "wrms" ]; then export vnamex=rms; des="Vector Wind RMSE" ; fi
 if [ $vname = "uerr" ]; then export vnamex=bias; des="U Wind Bias" ; fi
 if [ $vname = "verr" ]; then export vnamex=bias; des="V Wind Bias" ; fi
 if [ $vname = "serr" ]; then export vnamex=bias; des="Wind Speed Bias" ; fi
 if [ $vname = "werr" ]; then export des="Vector Wind Bias" ; fi
#...................................

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# line plots of time series
for day in $fdays; do
export xlon=`expr $day + 1 `
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
cat >${vname}_${lev}mb_day${day}.gs <<EOF1 
'reinit'; 'set font 1'
             'open ${ctlWIND1}'; mdc.1=${mdname[1]}
if($nmdx >1); 'open ${ctlWIND2}'; mdc.2=${mdname[2]} ;endif
if($nmdx >2); 'open ${ctlWIND3}'; mdc.3=${mdname[3]} ;endif
if($nmdx >3); 'open ${ctlWIND4}'; mdc.4=${mdname[4]} ;endif
if($nmdx >4); 'open ${ctlWIND5}'; mdc.5=${mdname[5]} ;endif
if($nmdx >5); 'open ${ctlWIND6}'; mdc.6=${mdname[6]} ;endif
if($nmdx >6); 'open ${ctlWIND7}'; mdc.7=${mdname[7]} ;endif
if($nmdx >7); 'open ${ctlWIND8}'; mdc.8=${mdname[8]} ;endif

*-- define line styles and model names 
* cst.1=1; cst.2=5; cst.3=3; cst.4=5; cst.5=5; cst.6=3; cst.7=5; cst.8=5
* cth.1=9; cth.2=4; cth.3=4; cth.4=4; cth.5=4; cth.6=4; cth.7=4; cth.8=4
* cma.1=0; cma.2=8; cma.3=6; cma.4=1; cma.5=2; cma.6=0; cma.7=3; cma.8=7
  cst.1=1; cst.2=1; cst.3=1; cst.4=1; cst.5=1; cst.6=1; cst.7=1; cst.8=1
  cth.1=9; cth.2=9; cth.3=5; cth.4=5; cth.5=5; cth.6=5; cth.7=5; cth.8=5
  cma.1=0; cma.2=0; cma.3=0; cma.4=0; cma.5=0; cma.6=0; cma.7=0; cma.8=0
  cco.1=1; cco.2=2; cco.3=3; cco.4=4; cco.5=8; cco.6=9; cco.7=5; cco.8=6

  'set x $xlon' 
  'set y 1' 
  'set lev $lev' 
  'set time $sdate $edate' 

   i=1
   while (i <= $nmd)
     'define var'%i'=ave(${vname}.'%i',t-${smth2},t+${smth2})'
     j=i+$nmd
     'define var'%j'=ave(${vnamex}.'%j'(y=${ylatx}),t-${smth2},t+${smth2})'
    i=i+1
   endwhile

  xwd=7.0; ywd=4.0; yy=ywd/16
  xmin=1.0; xmax=xmin+xwd; ymin=6.0; ymax=ymin+ywd
  xt=xmin+0.3; xt1=xt+0.5; xt2=xt1+0.1; yt=ymin ;*for legend  
  titlx=xmin+0.5*xwd;  titly=ymax+0.20                  ;*for tytle
  xlabx=xmin+0.5*xwd;  xlaby=ymin-0.60
  'set parea 'xmin' 'xmax' 'ymin' 'ymax

*--find maximum and minmum values
   cmax=-10000; cmin=10000
   i=1
   while (i <= $nmdx)
    'set gxout stat'
    'd var'%i
    range=sublin(result,9); zmin=subwrd(range,5); zmax=subwrd(range,6)
    if(zmax > cmax & zmax < 1000 ); cmax=zmax; endif
    if(zmin < cmin & zmin > -1000 ); cmin=zmin; endif
   i=i+1
   endwhile
   dist=cmax-cmin; cmin=cmin-0.5*dist; cmax=cmax+0.2*dist
   cmin=substr(cmin,1,6); cmax=substr(cmax,1,6); cint=10*substr((cmax-cmin)/100,1,4)
   if (cint = 0); cint=substr((cmax-cmin)/10,1,4); endif
   if (cint = 0); cint=0.1*substr((cmax-cmin),1,4); endif
   if (cint = 0); cint=0.01*substr((cmax-cmin)*10,1,4); endif
   say 'cmin cmax cint 'cmin' 'cmax' 'cint

   i=1
   while (i <= $nmdx)
    'set gxout stat'  ;* first compute last-year means and count good data numbers
    'set time $sdat1 $edate' 
    'd var'%i
    ln=sublin(result,11); wd=subwrd(ln,2); a=substr(wd,1,5)
    ln=sublin(result,7); wd=subwrd(ln,8); b=substr(wd,1,5)
    if ( b>0 )
      'set strsiz 0.13 0.13'; yt=yt+yy
      'set line 'cco.i' 'cst.i' 11'; 'draw line 'xt' 'yt' 'xt1' 'yt
      'set string 'cco.i' bl 6'
      if(i=1)
        'draw string 'xt2' 'yt' 'mdc.i '  'a  '  Last 1yr Avg'
      else
       if (i<=$nmd)
        'draw string 'xt2' 'yt' 'mdc.i '  'a  
       else
        'draw string 'xt2' 'yt' VSDB_'mdc.i '  'a  
       endif
      endif

      'set time $sdate $edate' 
      'set gxout line'
      'set display color white'; 'set missconn on';     'set grads off'; 'set grid on'
      'set xlopts 1 6 0.14'
      if( $nmdx > 1); 'set xlopts 1 6 0.0'; endif
      'set ylopts 1 6 0.14'; 'set clopts 1 6 0.0'
      'set cstyle 'cst.i; 'set cthick 'cth.i; 'set cmark 'cma.i; 'set ccolor 'cco.i
      'set vrange 'cmin' 'cmax; 'set ylint 'cint
*     'set xlint $xtick'
      'd var'%i
     endif
   i=i+1
   endwhile

  'set string 1 bc 7'
  'set strsiz 0.14 0.14'
* 'draw string 'titlx' 'titly' Tropic ${des}: ${lev}hPa Day${day}, ${smth}-Mon Mean'
  'draw string 'titlx' 'titly' Tropic ${des}: ${lev}hPa Day${day}'
  'set string 1 bl 3'
  'set strsiz 0.09 0.09'


*---------------------------------------------------------
if ($nmdx > 1); then
if ( $vname = wrms ); do
*---------------------------------------------------------
* plot  difference between others and the first
  ymin=ymin-4; ymax=ymin+4
  'set parea 'xmin' 'xmax' 'ymin' 'ymax
  xlabx=xmin+0.45*xwd;  xlaby=ymin-0.60

*--find maximum and minmum values to determine y-axis labels
 cmax=-10000; cmin=10000
 i=1
 while (i <= $nmd)
  j=i+$nmd
  'set gxout stat'
  'd var'%i     ;* number of records
  ln=sublin(result,11); wd=subwrd(ln,2); a=substr(wd,1,3)
  if ( a>0 )
    'set gxout stat'
    'd var'%j'-var'%i
    range=sublin(result,9); zmin=subwrd(range,5); zmax=subwrd(range,6)
    if(zmax > cmax); cmax=zmax; endif
    if(zmin < cmin); cmin=zmin; endif
  endif
 i=i+1
 endwhile
 dist=cmax-cmin
 if (dist = 0); dist=1; endif
 cmin=cmin-0.01*dist; cmax=cmax+0.01*dist
 cmin=substr(cmin,1,6); cmax=substr(cmax,1,6)
 cintp=10*substr(dist/40,1,4)
 if (cintp = 0); cintp=10*substr(dist/40,1,5); endif
 if (cintp = 0); cintp=10*substr(dist/40,1,6); endif

 i=1
 while (i <= $nmd)
  j=i+$nmd
  'set gxout stat'
  'd var'%i     ;* number of records
  ln=sublin(result,11); wd=subwrd(ln,2); a=substr(wd,1,3)
  if ( a>0 )
     'set gxout line'
     'set mproj off'
     'set display color white'; 'set missconn on';     'set grads off'; 'set grid on'
     'set xlopts 1 6 0.14'
     'set ylopts 1 6 0.14'; 'set clopts 1 6 0.0'
     'set vrange 'cmin' 'cmax; 'set ylint 'cintp
     'set cstyle 'cst.i; 'set cthick 'cth.i; 'set cmark 'cma.i; 'set ccolor 'cco.i
     if(i=1); 'set cstyle 1'; 'set cthick 1'; 'set cmark 0'; 'set ccolor 1'; endif
    'd var'%j'-var'%i
  endif
 i=i+1
 endwhile

 'set string 1 bl 6'
 'set strsiz 0.14 0.14'
 'draw string 'xmin+0.2' 'ymax-0.4' Difference'
*---------------------------------------------------------
endif            
endif            
*---------------------------------------------------------


  'set strsiz 0.14 0.14'
  'draw string 'xlabx' 'xlaby' Verification Date'

  'printim ${vname}_${lev}mb_day${day}.png png x800 y800'
  'set vpage off'
'quit'
EOF1
grads -bcp "${vname}_${lev}mb_day${day}.gs"

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
done   ;#end day
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# 2D maps of tropical wind RMSE and Bias  varying with forecast days 
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
cat >${vname}_${lev}mb_alldays.gs <<EOF1 
'reinit'; 'set font 1'
'run /u/wx24fy/bin/grads/white.gs'
               'open ${ctl2dWIND1}'; mdc.1=${mdname2d[1]}
if($nmd2dx >1); 'open ${ctl2dWIND2}'; mdc.2=${mdname2d[2]} ;endif
if($nmd2dx >2); 'open ${ctl2dWIND3}'; mdc.3=${mdname2d[3]} ;endif
if($nmd2dx >3); 'open ${ctl2dWIND4}'; mdc.4=${mdname2d[4]} ;endif
if($nmd2dx >4); 'open ${ctl2dWIND5}'; mdc.5=${mdname2d[5]} ;endif
if($nmd2dx >5); 'open ${ctl2dWIND6}'; mdc.6=${mdname2d[6]} ;endif
if($nmd2dx >6); 'open ${ctl2dWIND7}'; mdc.7=${mdname2d[7]} ;endif
if($nmd2dx >7); 'open ${ctl2dWIND8}'; mdc.8=${mdname2d[8]} ;endif

  'set x 1 $xlon2d' 
  'set y 1' 
  'set lev $lev' 
* 'set time $sdate $edate' 
  'set time 01jan2007 $edate' 

   i=1
   while (i <= $nmd2d)
     'define var'%i'=ave(${vname}.'%i',t-${smth2},t+${smth2})'
     j=i+$nmd
     'define var'%j'=ave(${vnamex}.'%j'(y=${ylatx}),t-${smth2},t+${smth2})'
    i=i+1
   endwhile

*--find maximum and minmum values for first total field map
   cmax=-10000000.0; cmin=10000000.0
   i=1
*  while (i <= $nmd2d)
    'set gxout stat'
    'd var'%i
    range=sublin(result,9); zmin=subwrd(range,5); zmax=subwrd(range,6)
    if(zmax > cmax); cmax=zmax; endif
    if(zmin < cmin); cmin=zmin; endif
*  i=i+1
*  endwhile
   dist=cmax-cmin; cmin=cmin; cmax=cmax+0.1*dist
   cmin=substr(cmin,1,5); cmax=substr(cmax,1,5); cint=10*substr((cmax-cmin)/100,1,4)
   if (cint = 0); cint=substr((cmax-cmin)/10,1,4); endif
   if (cint = 0); cint=0.1*substr((cmax-cmin),1,4); endif
   if (cint = 0); cint=0.01*substr((cmax-cmin)*10,1,4); endif
   say 'cmin cmax cint 'cmin' 'cmax' 'cint
    bb1=cmin; bb2=cmin+cint; bb3=bb2+cint; bb4=bb3+cint; bb5=bb4+cint; bb6=bb5+cint
    bb7=bb6+cint; bb8=bb7+cint; bb9=bb8+cint; bb10=bb9+cint; bb11=bb10+cint

*--find maximum and minmum values for difference map
   cmax=-10000000.0; cmin=10000000.0
   i=1
   while (i <= $nmd2d)
    j=i+$nmd2d
    'set gxout stat'
    'd var'%j'-var'%i
    range=sublin(result,9); zmin=subwrd(range,5); zmax=subwrd(range,6)
    if(zmax > cmax); cmax=zmax; endif
    if(zmin < cmin); cmin=zmin; endif
   i=i+1
   endwhile
   dist=cmax-cmin; cmin=cmin; cmax=cmax+0.1*dist
   cmin=substr(cmin,1,6); cmax=substr(cmax,1,6);
   cintm=10*substr(cmin/50,1,4)
     if (cintm = 0); cintm=substr(cmin/5,1,4); endif
     if (cintm = 0); cintm=0.2*substr(cmin,1,4); endif
     if (cintm = 0); cintm=0.02*substr(cmin*10,1,4); endif
     if (cintm = 0); cintm=0.002*substr(cmin*100,1,4); endif
   cm1=cintm; cm2=cm1+cintm; cm3=cm2+cintm; cm4=cm3+cintm; cm5=cm4+cintm
              cm6=cm5+cintm; cm7=cm6+cintm; cm8=cm7+cintm; cm9=cm8+cintm
   cintp=10*substr(cmax/50,1,4)
     if (cintp = 0); cintp=substr(cmax/5,1,4); endif
     if (cintp = 0); cintp=0.2*substr(cmax,1,4); endif
     if (cintp = 0); cintp=0.02*substr(cmax*10,1,4); endif
     if (cintp = 0); cintp=0.002*substr(cmax*100,1,4); endif
   cp1=cintp; cp2=cp1+cintp; cp3=cp2+cintp; cp4=cp3+cintp; cp5=cp4+cintp
              cp6=cp5+cintp; cp7=cp6+cintp; cp8=cp7+cintp; cp9=cp8+cintp
   say 'cmin cmax cintm cintp 'cmin' 'cmax' 'cintm' 'cintp


  nframe=$nmd2dx
  xmin0=1.2;  xgap=0.2;  xlen=6.0
  ymax0=10.0; ygap=-0.1; ylen=-6.0
  if($nmd2dx >1); xlen=3;  endif
                 nframe2=1;  nframe3=2 
  if($nmd2dx >2); nframe2=2;  nframe3=4; ylen=-4.2;endif
  if($nmd2dx >4); nframe2=3;  nframe3=6; ylen=-2.8;endif
  if($nmd2dx >6); nframe2=4;  nframe3=8; ylen=-2.1; endif
                                                                                                                    

  i=1
  while ( i <= nframe )
  'set gxout stat'  ;*count good data numbers
  'd var'%i
  ln=sublin(result,7); wd=subwrd(ln,8); b=substr(wd,1,3)
  if ( b>0 )
    icx=1; if (i > nframe2); icx=2; endif
    if (i > nframe3); icx=3; endif
    if (i > nframe4); icx=4; endif
    xmin=xmin0+(icx-1)*(xlen+xgap)
    xmax=xmin+xlen
    icy=i; if (i > nframe2); icy=i-nframe2; endif
    if (i > nframe3); icy=i-nframe3; endif
    if (i > nframe4); icy=i-nframe4; endif
    ymax=ymax0+(icy-1)*(ylen+ygap)
    ymin=ymax+ylen
    titlx=xmin+0.15
    titly=ymax-0.3
    'set parea 'xmin' 'xmax' 'ymin' 'ymax

    'run /u/wx24fy/bin/grads/rgbset.gs'
    'set xlopts 1 4 0.0'
    'set ylopts 1 4 0.0'
      if($nmd2dx <=2)
        'set xlopts 1 4 0.11'
        if(i=1);'set ylopts 1 4 0.11';endif
      endif
      if($nmd2dx >2 & $nmd2dx <=4)
        if(i=2|i=$nmd2dx);'set xlopts 1 4 0.11';endif
        if(i<=2);'set ylopts 1 4 0.11';endif
      endif
      if($nmd2dx >4 & $nmd2dx <=6)
        if(i=3|i=$nmd2dx);'set xlopts 1 4 0.11';endif
        if(i<=3);'set ylopts 1 4 0.11';endif
      endif
      if($nmd2dx >=7)
        if(i=4|i=$nmd2dx);'set xlopts 1 4 0.11';endif
        if(i<=4);'set ylopts 1 4 0.11';endif
      endif
    'set clopts 1 4 0.09'
    'set grid on'
    'set zlog on'
    'set mproj off'

    'set gxout shaded'
    'set grads off'
    'set clevs   'cm5' 'cm4' 'cm3' 'cm2' 'cm1' 0 'cp1' 'cp2' 'cp3' 'cp4' 'cp5
    'set rbcols 39    37    36   35    34    32 62   64    65   66     67   69'
    if(i<=$nmd2d);'set clevs   'bb1' 'bb2' 'bb3' 'bb4' 'bb5' 'bb6' 'bb7' 'bb8' 'bb9' 'bb10' 'bb11 ;endif
    if(i<=$nmd2d);'set rbcols 41   42    43    44    45   46  47  48    49   55     56   57';endif
    'set xlint 1'
    if(i<=$nmd2d);'d var'%i ;endif
    if(i>$nmd2d)
      j=i-$nmd2d
      'd var'%j '- var'%i
    endif
*
    'set gxout contour'
    'set grads off'
    'set ccolor 1'
    'set clevs   'cm5' 'cm4' 'cm3' 'cm2' 'cm1' 0 'cp1' 'cp2' 'cp3' 'cp4' 'cp5
    if(i<=$nmd2d);'set clevs   'bb1' 'bb2' 'bb3' 'bb4' 'bb5' 'bb6' 'bb7' 'bb8' 'bb9' 'bb10' 'bb11 ;endif
*   'set clab on'
    if(i=1);'set clab forced';endif
    'set cstyle 3'
    if(i<=$nmd2d);'d var'%i ;endif
*   if(i>$nmd2d)
*     j=i-$nmd2d
*     'd var'%j '- var'%i
*   endif

    'set string 1 bl 7'
    'set strsiz 0.16 0.16'
    if(i<=$nmd2d);'draw string 'titlx' 'titly' 'mdc.i ;endif
    if(i>$nmd2d);'draw string 'titlx' 'titly' 'mdc.i ' new-old'; endif
  endif
  i=i+1
  endwhile

  'set string 1 bc 6'
  'set strsiz 0.14 0.14'
* 'draw string 4.5 10.35  Tropic ${lev}hPa ${des}, ${smth}-Mon Mean'
  'draw string 4.5 10.35  Tropic ${lev}hPa ${des}'
  'set string 1 bc 4'
  'set strsiz 0.14 0.14'
  'set strsiz 0.15 0.15'
  if($nmd2d >2)
    'draw string 4.3 0.9 Forecast Day'
    'run /u/wx24fy/bin/grads/cbarn.gs 0.95 0 4.1 0.40'
   else
    'draw string 4.3 3.5 Forecast Day'
    'run /u/wx24fy/bin/grads/cbarn.gs 0.95 0 4.1 2.90'
   endif
       
  'printim ${vname}_${lev}mb_alldays.png png x700 y700'
  'set vpage off'
'quit'
EOF1
grads -bcp "${vname}_${lev}mb_alldays.gs"        
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^




#...................................
done   ;#end vname
#...................................
#-----------------------------------------------------------------------
done   ;#end lev
#-----------------------------------------------------------------------
fi
#-----------------------------------------------------------------------



if [ $doftp = "YES" ]; then
cat << EOF >ftpin
  binary
  prompt
  cd $ftpdir
    mput *.png
  quit
EOF
ftp -i -v emcrzdm.ncep.noaa.gov <ftpin
fi

exit

