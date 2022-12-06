#!/bin/ksh
set -x

#-----------------------------------------------------------------------
#--Fanglin Yang, April 2013
# 1. Use monthly mean anomaly correlations to derive forecast days at which
#    forecast anomaly correlations exceed 0.6, 0.65, 0.7, ......, and 0.95 
# 2. Combine the legacy Caplan-Zhu monthly scores from 1996 to 2007 with 
#    the vsdb-based monthly scores from 2008 to the present.
# 3. The computation is made for HGT at 500mb and 1000hPa, and over the 
#    NH and SH, respectively.
# 4. make graphics and send to emcrzdm
#-----------------------------------------------------------------------

sorcdir=${sorcdir:-/global/save/Fanglin.Yang/vrfygfs/longterm/long_vsdb} 

yyyymmc=`date '+%Y%m'`
yyyymm=`/nwprod/util/exec/ndate -24 ${yyyymmc}0100 |cut -c 1-6`
export yeare=${yeare:-`echo $yyyymm |cut -c 1-4`}                  
export mone=${mm1:-`echo $yyyymm |cut -c 5-6` }                  

export modlist="gfs ecm cmc fno ukm "
export cyclist="00 12"   
#export modlist="gfs"
#export cyclist="00"   

#--vsdb-based monthly AC, 2008 to the present
export macnew=${sorcdir}/monthly             
#--vsdb-based monthly AC, 1996 to 2012            
export macold=${sorcdir}/legacy/monthly              

#--web serve for display graphics
export webhost=emcrzdm.ncep.noaa.gov
export webhostid=wx24fy
export ftpdir=/home/people/emc/www/htdocs/gmb/STATS_vsdb/longterm/fdayac
export doftp=YES

export rundir=${sorcdir}/usefulfcst             
mkdir -p $rundir
cd $rundir || exit 8


#---------------------------------------------
for mdl in  $modlist ; do
for cyc in $cyclist ; do

 inf_new=${macnew}/AC_HGT${mdl}${cyc}Z_month.bin
 if [ $mdl = "gfs" ]; then inf_old=${macold}/HGTs${cyc}Z_month.bin ;fi
 if [ $mdl = "ecm" ]; then inf_old=${macold}/HGTe${cyc}Z_month.bin ;fi
 if [ $mdl = "cmc" ]; then inf_old=${macold}/HGTm${cyc}Z_month.bin ;fi
 if [ $mdl = "fno" ]; then inf_old=${macold}/HGTn${cyc}Z_month.bin ;fi
 if [ $mdl = "ukm" ]; then inf_old=${macold}/HGTk${cyc}Z_month.bin ;fi
 if [ $mdl = "cdas" ]; then inf_old=${macold}/HGTc${cyc}Z_month.bin ;fi

#---------------------------------------------
nsm=6               ;#half of running mean length
nsm2=$((2*$nsm+1))  ;#running mean length

rm fcstday_${mdl}${cyc}Z.f fcstday_${mdl}${cyc}Z.exe
cat > fcstday_${mdl}${cyc}Z.f << EOF
      integer, parameter :: yeare=$yeare
      integer, parameter :: nf=17          !number of forecast days, from 0 to nf-1 
      integer, parameter :: nm=12          !months in a year               
      integer, parameter :: nsm=$nsm, nsm2=$nsm2                           

!---legacy Caplan-Zhu monthly scores, 1996 to 2012        
      integer, parameter :: yeare1=2012 
      integer, parameter :: years1=1996,ny1=yeare1-years1+1 
      integer, parameter :: nreg1=2    !number of areas, NH and SH
      integer, parameter :: nlev1=2    !number of layers, 1000hPa and 500hPa 
      integer, parameter :: nvar1=8    !number of variables                  

!---new vsdb-based scores, 2008 to the present
      integer, parameter :: years2=2008,ny2=yeare-years2+1 
      integer, parameter :: nreg2=5    !number of areas, G2 G2NHX G2SHX G2TRO G2PNA
      integer, parameter :: nlev2=4    !number of layers, 1000 700 500 250   
      integer, parameter :: nvar2=3    !number of variables                  

!--monthly means for all variables in the source file
      real*4 :: var1(nf,nreg1,nlev1,nm,nvar1,ny1)
      real*4 :: var2(nf,nreg2,nlev2,nm,nvar2,ny2)

!--merged HGT AC in the NH and SH, on 1000hPa and 500hPa
      integer, parameter :: yearm=2013         !year start to merge
      integer, parameter :: ny=yeare-years1+1 
      integer, parameter :: nreg=2             !number of areas, NH and SH
      integer, parameter :: nlev=2             !number of layers, 1000hPa and 500hPa 
      real*4 :: acz1(nf,nreg,nlev,nm,ny1)      !monthly means
      real*4 :: acz2(nf,nreg,nlev,nm,ny2)      !monthly means
      real*4 :: acz(nf,nreg,nlev,nm,ny)        !mergered monthly means
      real*4 :: acz_ann(nf,nreg,nlev,ny)       !mergered annual means
      character*5 :: regname(2),levname(2)
      data regname/"NH","SH"/, levname/"P1000","P500"/

!--arrays for determining forecast days exceeding a certain AC value
      real*4,  parameter :: acs=0.6, ace=0.95, dac=0.05
      integer, parameter :: nac=8      !!nac=(ace-acs)/dac+1.001        
      real*4 :: dayac(nac,nreg,nlev,nm,ny)
      real*4 :: dayacsm(nac,nreg,nlev,nm,ny)    !!13-month running means 

!--temporary arrays
      real*4 :: acx(nac)    !critical ac that needs to be exceeded, from acs to ace
      real*4 :: aczt(nf)    !monthly mean ac for a given month and region 
      real*4 :: dayt(nac)   !derived exceeding days for a given ac 
      real*4 :: daytsm(nac) !derived exceeding days for a given ac, 13-month running mean 
      real*4 :: days(nf)    !original forecast days, from 0 to 16
      real*4 :: tmpday(ny*nm),tmpdaysm(ny*nm) 
!--
      character*300 :: infile1, infile2
      data bad1/-999.900/, bad/-99.9/


!------------------------------------------------------------------------------------------------------
!------------------------------------------------------------------------------------------------------
!---read from source data, and pick HGT AC in NH and SH and on 1000hPa and 500hPa 
      infile1="${inf_old}"
      infile2="${inf_new}"
      open(10,file=infile1,form="unformatted",status="unknown")
      open(20,file=infile2,form="unformatted",status="unknown")

      do 100 jy=1,ny1        
      do 100 mm=1,nm
       do n=1,nvar1
       do k=1,nlev1
         read(10) ((var1(i,j,k,mm,n,jy),i=1,nf),j=1,nreg1)
         do i=1,nf
         do j=1,nreg1
          if (var1(i,j,k,mm,n,jy).eq.bad1) var1(i,j,k,mm,n,jy)=bad
         enddo
         enddo
       enddo
       enddo
       do i=1,nf
        acz1(i,1,1,mm,jy)=var1(i,1,1,mm,4,jy)  !NH, 1000hPa
        acz1(i,1,2,mm,jy)=var1(i,1,2,mm,4,jy)  !NH, 500hPa
        acz1(i,2,1,mm,jy)=var1(i,2,1,mm,4,jy)  !SH, 1000hPa
        acz1(i,2,2,mm,jy)=var1(i,2,2,mm,4,jy)  !SH, 500hPa
       enddo
 100  continue

      do 200 jy=1,ny2       
      do 200 mm=1,nm
       do n=1,nvar2
       do k=1,nlev2
         read(20) ((var2(i,j,k,mm,n,jy),i=1,nf),j=1,nreg2)
       enddo
       enddo
       do i=1,nf
        acz2(i,1,1,mm,jy)=var2(i,2,1,mm,1,jy)  !NH, 1000hPa
        acz2(i,1,2,mm,jy)=var2(i,2,3,mm,1,jy)  !NH, 500hPa
        acz2(i,2,1,mm,jy)=var2(i,3,1,mm,1,jy)  !SH, 1000hPa
        acz2(i,2,2,mm,jy)=var2(i,3,3,mm,1,jy)  !SH, 500hPa
       enddo
 200  continue

!--merge
      do 300 i=1,nf
      do 300 j=1,nreg
      do 300 k=1,nlev
      do 300 mm=1,nm
       do iy=years1,yearm-1
         jy=iy-years1+1
         acz(i,j,k,mm,jy)=acz1(i,j,k,mm,jy)
       enddo
       do iy=yearm,yeare  
         jy=iy-years1+1
         jy2=iy-years2+1
         acz(i,j,k,mm,jy)=acz2(i,j,k,mm,jy2)
       enddo
 300  continue
        

!------------------------------------------------------------------------------------------------------
!------------------------------------------------------------------------------------------------------
!--compute annual mean and write out monthly means and annuanl means in ASCII format 
      open(30,file="meanac_${mdl}${cyc}Z.txt",form="formatted",status="unknown")

      do 101 iy=years1,yeare
          jy=iy-years1+1
      do 101 k=1,nlev        ! vertical layers
      do 101 i=1,nf          ! forecasts days
      do 101 j=1,nreg        ! areas
        ngood=0
        xtmp=0
       do mm=1,nm      ! month 1-12
        if(acz(i,j,k,mm,jy).ne.bad) then
          xtmp=xtmp+acz(i,j,k,mm,jy)
          ngood=ngood+1
        endif
       enddo
       if(ngood.ge.6) then
          acz_ann(i,j,k,jy)=xtmp/ngood
       else
          acz_ann(i,j,k,jy)=bad
       endif
 101  continue

      write(30,*)"==================== $mdl ${cyc}Z-cycle Mean HGT AC ===================="
      do j=1,nreg
      do k=1,nlev  
       write(30,*)                        
       write(30,*)"---------------------------------------------------------------------"
       write(30,*)"        ",regname(j)," ",levname(k),"    for forecast days 0 ~ ",nf-1
       write(30,*)"---------------------------------------------------------------------"

       write(30,*)"--- Annual Means --"
       do iy=years1,yeare
          jy=iy-years1+1
         write(30,'(i4,4x,17f8.3)')iy, (acz_ann(i,j,k,jy),i=1,nf)
       enddo

       write(30,*)                        
       write(30,*)"--- Monthly Means --"
       do iy=years1,yeare
          jy=iy-years1+1
       do mm=1,12
         write(30,'(2i4,17f8.3)')iy, mm, (acz(i,j,k,mm,jy),i=1,nf)
       enddo
       enddo
      enddo
      enddo

!------------------------------------------------------------------------------------------------------
!------------------------------------------------------------------------------------------------------
!--determine the days at which forecast AC exceeding a certain value

      do nc=1,nac
       acx(nc)=acs+(nc-1)*dac   !critical ac that needs to be exceeded
      enddo
      do i=1,nf
       days(i)=i-1            !original forecast days, from 0 to 16
      enddo

      do 400 j=1,nreg
      do 400 k=1,nlev
!
      do 500 jy=1,ny              
      do 500 mm=1,nm

       ngood=0
       do i=1,nf
        aczt(i)=acz(i,j,k,mm,jy)
        if(aczt(i).ne.bad) ngood=ngood+1
       enddo

       do nc=1,nac 
        dayt(nc)=bad
       enddo

       if(ngood.ge.6) then
       do 550 nc=1,nac 
       do i=nf,2,-1
!!      if( (aczt(i).ne.bad .and. aczt(i-1).ne.bad) .and. acx(nc).lt.aczt(i-1) ) then   !extrapolation or interpolation          
        if( (aczt(i).ne.bad .and. aczt(i-1).ne.bad) .and. (acx(nc).lt.aczt(i-1) .and. acx(nc).ge.aczt(i)) ) then  !no extrapolation        
         dayt(nc)=days(i-1)+(days(i)-days(i-1))/(aczt(i)-aczt(i-1))*(acx(nc)-aczt(i-1))
         goto 550
        endif
       enddo
 550   continue
       endif
         
       do  nc=1,nac 
        dayac(nc,j,k,mm,jy)=dayt(nc)
       enddo
 500  continue

!-------------------------------
!--compute 13-month running mean
      do 560 nc=1,nac 
       do jy=1,ny              
       do mm=1,nm
        nym=(jy-1)*12+mm
        dayacsm(nc,j,k,mm,jy)=bad     
        tmpday(nym)=dayac(nc,j,k,mm,jy)
       enddo
       enddo

       do jy=1,ny              
       do mm=1,nm
        nym=(jy-1)*12+mm
        if(nym.gt.nsm .and. nym.lt.(ny*nm-nsm) ) then
         sum=0; nct=0
         do kk=nym-nsm,nym+nsm 
         if(tmpday(kk).ne.bad) then
           sum=sum+tmpday(kk)
           nct=nct+1
         endif
         enddo
         if( nct.ge.nsm2-3)  dayacsm(nc,j,k,mm,jy)=sum/nct   !requires at least 10 points
        endif
       enddo
       enddo
 560  continue
 400  continue

      open(40,file="fcstday_${mdl}${cyc}Z.txt",form="formatted",status="unknown")
      open(41,file="fcstday_${mdl}${cyc}Z.bin",form="unformatted",status="unknown")

      write(40,*)"====== $mdl ${cyc}Z-cycle Forecast DAY Reaching a Given AC Value ======="
      do j=1,nreg
      do k=1,nlev  
       write(40,*)                        
       write(40,*)"---------------------------------------------------------------------"
       write(40,*)"        ",regname(j),"   ",levname(k)
       write(40,*)"Year Mon AC=0.60 AC=0.65 AC=0.70 AC=0.75 AC=0.80 AC=0.85 AC=0.90 AC=0.95"
       write(40,*)"---------------------------------------------------------------------"

       do iy=years1,yeare
          jy=iy-years1+1
       do mm=1,12
         write(40,'(2i4,10f8.2)')iy, mm, (dayac(i,j,k,mm,jy),i=1,nac)
       enddo
       enddo
      enddo
      enddo

      do iy=years1,yeare
          jy=iy-years1+1
      do mm=1,nm
        do k=1,nlev
         write(41) ((dayac(i,j,k,mm,jy),i=1,nac),j=1,nreg)
        enddo
        do k=1,nlev
         write(41) ((dayacsm(i,j,k,mm,jy),i=1,nac),j=1,nreg)
        enddo
      enddo
      enddo


      stop
      end
EOF
#----------------------------------------------------------------
        
#xlf90 -o fcstday_${mdl}${cyc}Z.exe fcstday_${mdl}${cyc}Z.f 
ifort -convert big_endian -FR -o fcstday_${mdl}${cyc}Z.exe fcstday_${mdl}${cyc}Z.f 
./fcstday_${mdl}${cyc}Z.exe

#----------------------------------------------------------------
nlev=2; nac=8
nmon=$(( 12*($yeare-1996+1) )) 
nmon6=$(( 12*($yeare-1996)+$mone-$nsm )) 

cat > fcstday_${mdl}${cyc}Z.ctl         << EOF
dset ^fcstday_${mdl}${cyc}Z.bin         
undef -99.9
options sequential
format big_endian
title forecast days reaching given critical AC values
title x-critical AC values: 0.60, 0.65, 0.70 ......0.95
title y regions: NH and SH
xdef $nac linear 0.60 0.05
ydef 2 linear 1 1
zdef 2 levels 1000 500 
tdef $nmon Linear jan1996 1mon
vars    2
fday 2 0  forecast days           
fdaysm 2 0  forecast days, 13-month running mean           
endvars
EOF

#---------------------------------------------
done   ;# cycles
done   ;# models
#---------------------------------------------


 
#==========================================
#==========================================
#==========================================
#--make graphics

export modlist=${modlist:-"gfs ecm cmc fno cdas ukm"}
export cyclist=${cyclist:-"00 12"}   

for reg in NH SH  ;  do
if [ $reg = "NH" ]; then yset=1 ; fi
if [ $reg = "SH" ]; then yset=2 ; fi

for cyc in $cyclist ; do
for lev in 1000 500 ; do


# ----- PLOT TYPE 1:  time series of forecast days for a single model at multiple AC values
for mdl in $modlist ; do
cat >fdayplot_${mdl}${cyc}Z_${reg}${lev}mb.gs <<EOF1 
'reinit'; 'set font 1'
'open fcstday_${mdl}${cyc}Z.ctl'

*-- define line styles and model names 
  cst.1=1; cst.2=1; cst.3=1; cst.4=1; cst.5=1; cst.6=1; cst.7=1; cst.8=1; cst.9=1; cst.10=1
  cth.1=5; cth.2=5; cth.3=5; cth.4=5; cth.5=5; cth.6=5; cth.7=5; cth.8=5; cth.9=5; cth.10=5
  cma.1=2; cma.2=3; cma.3=5; cma.4=6; cma.5=7; cma.6=8; cma.7=9; cma.8=10; cma.9=11; cma.10=12
  cco.1=1; cco.2=2; cco.3=3; cco.4=4; cco.5=8; cco.6=5; cco.7=10; cco.8=9; cco.9=6; cco.10=7
*------------------------
  'set x 1' 
  'set t 1 $nmon '               
  'set y $yset ' 
  'set lev $lev ' 

*critical AC values
  mdc.1="AC=0.60"
  mdc.2="AC=0.65"
  mdc.3="AC=0.70"
  mdc.4="AC=0.75"
  mdc.5="AC=0.80"
  mdc.6="AC=0.85"  
  mdc.7="AC=0.90"
  mdc.8="AC=0.95"  

**model name
  if ( $mdl = gfs ); mdname=GFS ; endif
  if ( $mdl = ecm ); mdname=ECMWF ; endif
  if ( $mdl = ukm ); mdname=UKMO ; endif
  if ( $mdl = fno ); mdname=FNOMC ; endif
  if ( $mdl = cmc ); mdname=CMC ; endif
  if ( $mdl = cfsr ); mdname=CFSR ; endif
  if ( $mdl = cdas ); mdname=CDAS ; endif

  xwd=9.0; ywd=7.0; yy=ywd/16; xx=xwd/5
  xmin=1.0; xmax=xmin+xwd; ymin=0.7; ymax=ymin+ywd
  titlx=xmin+0.5*xwd;  titly=ymax+0.45                  ;*for tytle
  titlx2=xmin+0.5*xwd;  titly2=ymax+0.20                ;*for tytle
  xlabx=xmin+0.45*xwd;  xlaby=ymin-0.60
  'set parea 'xmin' 'xmax' 'ymin' 'ymax

   i=1
   while (i <= $nac)
    'set gxout stat'  ;* first compute means and count good data numbers
    'd fdaysm(x='%i')'
    ln=sublin(result,11); wd=subwrd(ln,2); a=substr(wd,1,5)
    ln=sublin(result,7); wd=subwrd(ln,8); b=substr(wd,1,3)
      if( i <=4); yt=ymin+0.5;endif
      if( i >4);  yt=ymin+0.15; endif
      if(i=1|i=5); xt=1.0 ; endif                                          
        xt=xt+xx; xt1=xt+0.4; xt2=xt1+0.1; xtm=xt+0.20
        'set strsiz 0.17 0.17'
        'set line 'cco.i' 'cst.i' 11'; 'draw line 'xt' 'yt' 'xt1' 'yt
        'set string 'cco.i' bl 6';     'draw string 'xt2' 'yt' 'mdc.i
*       'draw mark 'cma.i' 'xtm' 'yt' 0.1'

    if ( b>0 )
      'set gxout line'
      'set display color white'; 'set missconn off';     'set grads off'; 'set grid on'
      'set xlopts 1 6 0.14';     'set ylopts 1 6 0.14'; 'set clopts 1 6 0.0'
      'set vrange 1 9.5'; 'set ylint 1'
      'set xlint 1'
      'set cstyle 3'; 'set cmark 0'; 'set cthick 1'; 'set ccolor 'cco.i    
*     'set cstyle 3'; 'set cmark 0'; 'set cthick 1'; 'set ccolor 15'    
      'd fday(x='%i')'
*     'set cstyle 'cst.i; 'set cmark 'cma.i; 'set cthick 'cth.i ; 'set ccolor 'cco.i 
      'set cstyle 'cst.i; 'set cmark 0'; 'set cthick 18' ; 'set ccolor 'cco.i 
      'd fdaysm(x='%i')'
    endif
   i=i+1
   endwhile

  'set string 1 bc 7'
  'set strsiz 0.16 0.16'
  'draw string 'titlx' 'titly' Forecast Days Exceeding Given ACs: '%mdname ' $reg ${lev}hPa HGT'
  'set strsiz 0.14 0.14'
  'draw string 'titlx2' 'titly2'  Dotted line: monthly mean; Bold line: ${nsm2}-mon Running Mean'
  'set string 1 bc 7'
  'set strsiz 0.15 0.15'
  'draw string 'xlabx' 'xlaby' Year'
  'draw ylab Forecast Days'          

  'printim fdayplot_${mdl}${cyc}Z_${reg}${lev}mb.png x900 y600'
  'set vpage off'
'quit'
EOF1
#-------------------------------------------------------
grads -bcl "run fdayplot_${mdl}${cyc}Z_${reg}${lev}mb.gs"
done
#-------End of PLOT1------------------------------------               


# ----- PLOT TYPE 2:  time series of forecast days reaching AC=0.6 and AC=0.8, all models           
cat >fdayplot_all${cyc}Z_${reg}${lev}mb.gs <<EOF1 
'reinit'; 'set font 1'
'open fcstday_gfs${cyc}Z.ctl'
'open fcstday_ecm${cyc}Z.ctl'
'open fcstday_ukm${cyc}Z.ctl'
'open fcstday_fno${cyc}Z.ctl'
'open fcstday_cmc${cyc}Z.ctl'

*-- define line styles and model names 
  cst.1=1; cst.2=1; cst.3=1; cst.4=1; cst.5=1; cst.6=1; cst.7=1; cst.8=1; cst.9=1; cst.10=1
  cth.1=18; cth.2=18; cth.3=18; cth.4=18; cth.5=18; cth.6=18; cth.7=18; cth.8=18; cth.9=18; cth.10=18
  cma.1=2; cma.2=3; cma.3=5; cma.4=6; cma.5=7; cma.6=8; cma.7=9; cma.8=10; cma.9=11; cma.10=12
  cco.1=1; cco.2=2; cco.3=3; cco.4=4; cco.5=8; cco.6=5; cco.7=10; cco.8=9; cco.9=6; cco.10=7
*------------------------
  'set x 1' 
  'set t 1 $nmon '               
  'set y $yset ' 
  'set lev $lev ' 

**model name       
  mdc.1="GFS"
  mdc.2="ECMWF"    
  mdc.3="UKMO"    
  mdc.4="FNOMC"  
  mdc.5="CMC"      
  mdc.6="CFSR"      

  xwd=9.0; ywd=7.0; yy=ywd/16; xx=xwd/6
  xmin=1.0; xmax=xmin+xwd; ymin=0.7; ymax=ymin+ywd
  titlx=xmin+0.5*xwd;  titly=ymax+0.45                  ;*for tytle
  titlx2=xmin+0.5*xwd;  titly2=ymax+0.20                ;*for tytle
  xlabx=xmin+0.45*xwd;  xlaby=ymin-0.60
  'set parea 'xmin' 'xmax' 'ymin' 'ymax

   i=1
   while (i <= 5)

**for AC=0.6
    'set gxout stat'   
    'd fdaysm.'%i'(x=1)'  
    ln=sublin(result,11); wd=subwrd(ln,2); a=substr(wd,1,5)
    ln=sublin(result,7); wd=subwrd(ln,8); b=substr(wd,1,3)
        yt=ymin+0.3 
        if(i=1); xt=0.1 ; endif                                          
        xt=xt+xx; xt1=xt+0.4; xt2=xt1+0.1; xtm=xt+0.20
        'set strsiz 0.15 0.15'
        'set line 'cco.i' 'cst.i' 11'; 'draw line 'xt' 'yt' 'xt1' 'yt
        'set string 'cco.i' bl 6';     'draw string 'xt2' 'yt' 'mdc.i
*       'draw mark 'cma.i' 'xtm' 'yt' 0.1'

    if ( b>0 )
      'set gxout line'
      'set display color white'; 'set missconn off';     'set grads off'; 'set grid on'
      'set xlopts 1 6 0.14';     'set ylopts 1 6 0.14'; 'set clopts 1 6 0.0'
      'set vrange 2 10'; 'set ylint 1'
      'set xlint 1'
      'set cstyle 3'; 'set cmark 0'; 'set cthick 1'; 'set ccolor 'cco.i    
*     'set cstyle 1'; 'set cmark 0'; 'set cthick 1'; 'set ccolor 15'    
      'd fday.'%i'(x=1)'  
      'set cstyle 'cst.i; 'set cmark 0'; 'set cthick 'cth.i ; 'set ccolor 'cco.i 
      'd fdaysm.'%i'(x=1)'  
    endif

**for AC=0.8
    'set gxout stat'   
    'd fdaysm.'%i'(x=5)'  
    ln=sublin(result,11); wd=subwrd(ln,2); a=substr(wd,1,5)
    ln=sublin(result,7); wd=subwrd(ln,8); b=substr(wd,1,3)
*       yt=ymin+0.1 
*       if(i=1); xt=1.0 ; endif                                          
*       xt=xt+xx; xt1=xt+0.4; xt2=xt1+0.1; xtm=xt+0.20
*       'set strsiz 0.15 0.15'
*       'set line 'cco.i' 'cst.i' 11'; 'draw line 'xt' 'yt' 'xt1' 'yt
*       'set string 'cco.i' bl 6';     'draw string 'xt2' 'yt' 'mdc.i
*       'draw mark 'cma.i' 'xtm' 'yt' 0.1'

    if ( b>0 )
      'set gxout line'
      'set display color white'; 'set missconn off';     'set grads off'; 'set grid on'
      'set xlopts 1 6 0.14';     'set ylopts 1 6 0.14'; 'set clopts 1 6 0.0'
      'set vrange 2 10'; 'set ylint 1'
      'set xlint 1'
      'set cstyle 3'; 'set cmark 0'; 'set cthick 1'; 'set ccolor 'cco.i    
*     'set cstyle 1'; 'set cmark 0'; 'set cthick 1'; 'set ccolor 15'    
      'd fday.'%i'(x=5)'  
      'set cstyle 'cst.i; 'set cmark 0'; 'set cthick 'cth.i ; 'set ccolor 'cco.i 
      'd fdaysm.'%i'(x=5)'  
    endif

   i=i+1
   endwhile

  'set string 1 bc 10'
  'set strsiz 0.20 0.20'
  'draw string 3 5.5 AC=0.6'
  'draw string 8 2.6 AC=0.8'

  'set string 1 bc 7'
  'set strsiz 0.16 0.16'
  'draw string 'titlx' 'titly' Forecast Days Exceeding AC=0.6 and AC=0.8: $reg ${lev}hPa HGT'
  'set strsiz 0.14 0.14'
  'draw string 'titlx2' 'titly2'  Dotted line: monthly mean; Bold line: ${nsm2}-mon Running Mean'
  'set string 1 bc 7'
  'set strsiz 0.15 0.15'
  'draw string 'xlabx' 'xlaby' Year'
  'draw ylab Forecast Days'          

  'printim fdayplot_all${cyc}Z_${reg}${lev}mb.png x900 y600'
  'set vpage off'
'quit'
EOF1
#-------------------------------------------------------
grads -bcl "run fdayplot_all${cyc}Z_${reg}${lev}mb.gs"
#-------End of PLOT2------------------------------------               


done
done
done
#-----------------------------------------------------------------


#----------------------------------------
if [ $doftp = "YES" ]; then
cat >ftpin <<EOF
  binary
  promt
  cd $ftpdir
    mput fdayplot*.png           
    mput fcstday*.txt           
  quit
EOF
 sftp  ${webhostid}@${webhost} <ftpin
#-------------
if [ $? -ne 0 ]; then 
cat <<EOF >ftpcard.sh
#!/bin/ksh
set -x
 sftp  ${webhostid}@${webhost} <ftpin
EOF
 chmod u+x $rundir/ftpcard.sh
 /u/Fanglin.Yang/bin/sub -a GFS-DEV -q transfer -g g01 -p 1/1/S -t 0:30:00 -r 64/1 $rundir/ftpcard.sh
fi
#-------------
fi
#----------------------------------------

exit
