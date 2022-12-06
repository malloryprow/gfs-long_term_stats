#!/bin/ksh
set -x

#--------------------------------------------------------------
#--Fanglin Yang, April 2013
#  derive monthly means of anomaly correlations from daily means
#--------------------------------------------------------------

export sorcdir=${sorcdir:-/global/save/Fanglin.Yang/vrfygfs/longterm/long_vsdb}
cd ${sorcdir}/monthly  ||exit 8

#  creatve monthly means based on daily stats
export dailysorc=${sorcdir}/daily                            

export yeare=${yeare:-2015}                  
export years=2008                  

export modlist=${modlist:-"gfs ecm cmc fno cdas ukm jma cfsr"}
export varlist=${varlist:-"HGT T U V WIND"}
nmod=`echo $modlist | wc -w`
nvar=`echo $varlist | wc -w`


reglist="G2 G2NHX G2SHX G2TRO G2PNA"
reglistc="'G2  ','G2NHX','G2SHX','G2TRO','G2PNA'"
nreg=`echo $reglist | wc -w`

#---------------------------------------------
for mdl in  $modlist ; do
 if [ $mdl = "gfs" ]; then
  cyclist="00 06 12 18"
 elif [ $mdl = "cdas" -o $mdl = "cfsr" ]; then
  cyclist="00"
 else
  cyclist="00 12"
 fi

for cyc in $cyclist ; do
for var in  $varlist ; do
#---------------------------------------------

if [ $var = "HGT" ]; then
 levlist="1000 700 500 250"
 levlistc="'P1000','P700 ','P500 ','P250 '"
else
 levlist="850 500 250"
 levlistc="'P850 ','P500 ','P250 '"
fi
nlev=`echo $levlist | wc -w`


rm month_ac.f
cat > month_ac.f << EOF
      integer, parameter :: years=$years, yeare=$yeare,ny=yeare-years+2 
      integer, parameter :: nd=366         !days in a year 
      integer, parameter :: nreg=$nreg         !number of areas
      integer, parameter :: nlev=$nlev     !number of layers 
      integer, parameter :: nf=17          !number of forecasts 
      integer, parameter :: nm=12          !months in a year               
      integer, parameter :: nst=4          !cor,rms,bias,bincor
      integer, parameter :: nst3=3         !cor,rms,bias
!--daily stats  
!     real*4 :: cor(nf,nreg,nlev,nd),rms(nf,nreg,nlev,nd)
!     real*4 :: bias(nf,nreg,nlev,nd),bincor(nf,nreg,nlev,nd)
      real*4 :: varday(nf,nreg,nlev,nd,nst)
!--monthly means
      real*4 :: varmon(nf,nreg,nlev,nm,nst3,ny)
!--annual means
      real*4 :: varyear(nf,nreg,nlev,nst3,ny)
!--
      character*5 :: stname(3),regname(nreg),levname(nlev)
      data stname /"AC   ", "RMSE ", "BIAS "/
      data regname/${reglistc}/                                      
      data levname/${levlistc}/             

      character*300 :: infile
      integer :: mday(nm)
      data mday/31,28,31,30,31,30,31,31,30,31,30,31/
      data bad/-99.9/
      logical leap
      character*4 yc

      open(10,file="AC_${var}${mdl}${cyc}Z_month.bin",form="unformatted",status="unknown")
      open(20,file="AC_${var}${mdl}${cyc}Z_mean.txt",form="formatted",status="unknown")
      varmon=bad    !initialize data
      varyear=bad   !initialize data

      do 1000 iy=years,yeare
       jy=iy-years+1
       leap=.false.
       if(mod(iy,4).eq.0) leap=.true.
       write(yc,'(i4)')iy

       do 50 j=1,nreg
       do 50 k=1,nlev
        ndayinyear=365
        if(leap) ndayinyear=366

        infile="../daily/${cyc}/${mdl}/${var}_"//trim(levname(k))//"_"//trim(regname(j))//"_${mdl}${cyc}Z"//yc//".bin" 
        open(1,iostat=iso,file=trim(infile),form="unformatted",status="old")
        if(iso.ne.0) goto 60 

        print*,trim(infile)        
        do m=1,ndayinyear
         do n=1,nst
           read(1) (varday(i,j,k,m,n),i=1,nf)
         enddo
        enddo
        goto 50
   60   continue
        print*,trim(infile), "  is missing"        
        do m=1,ndayinyear
         do n=1,nst
          do i=1,nf
            varday(i,j,k,m,n)=bad       
          enddo
         enddo
        enddo
   50  continue
   
!-- compute monthly means
      do 100 n=1,nst3     ! number of variables
      do 100 k=1,nlev     ! vertical layers
      do 100 i=1,nf       ! forecasts days 
      do 100 j=1,nreg     ! areas  
        nday=1
       do mm=1,nm      ! month 1-12
        iday=mday(mm)
        if(mm.eq.2 .and. leap) iday=29    !leap year
        ngood=0
        xtmp=0
       do ii=nday,nday+iday-1
        if(varday(i,j,k,ii,n).ne.bad) then
           xtmp=xtmp+varday(i,j,k,ii,n)
           ngood=ngood+1
        endif
       enddo
        if(ngood.ge.25)  then               !at least have 25 points in the month
         varmon(i,j,k,mm,n,jy)=xtmp/ngood
        else
         varmon(i,j,k,mm,n,jy)=bad
        endif
         nday=nday+iday
       enddo
  100 continue
       

 999  continue
      do mm=1,nm
       do n=1,nst3
        do k=1,nlev
         write(10) ((varmon(i,j,k,mm,n,jy),i=1,nf),j=1,nreg)
        enddo
       enddo
      enddo
      close(1)
 1000 continue

!-- add one more year for computing running mean, all default data
      do mm=1,nm
       do n=1,nst3
        do k=1,nlev
         write(10) ((varmon(i,j,k,mm,n,ny),i=1,nf),j=1,nreg)
        enddo
       enddo
      enddo


!-----------------
! compute annual means
      do 101 iy=years,yeare
          jy=iy-years+1
      do 101 n=1,nst3     ! number of variables
      do 101 k=1,nlev     ! vertical layers
      do 101 i=1,nf       ! forecasts days 
      do 101 j=1,nreg     ! areas
        ngood=0
        xtmp=0
       do mm=1,nm      ! month 1-12
        if(varmon(i,j,k,mm,n,jy).ne.bad) then
          xtmp=xtmp+varmon(i,j,k,mm,n,jy)
          ngood=ngood+1
        endif
       enddo
       if(ngood.ge.6) then
          varyear(i,j,k,n,jy)=xtmp/ngood
       else
          varyear(i,j,k,n,jy)=bad
       endif
 101  continue
        

!------------write monthly mean and annual means

      do n=1,nst3
      do j=1,nreg
      do k=1,nlev  
       write(20,*)
       write(20,*)"-------------------------------------------------------------------------------------"
       write(20,*)"---",stname(n)," ",regname(j)," ",levname(k),"--- for forecast days 0 ~ ",nf-1
       write(20,*)"-------------------------------------------------------------------------------------"

       write(20,*)"--- Annual Means --"
       do iy=years,yeare
          jy=iy-years+1
         write(20,'(3a,i5,2x,a,17f9.3)')stname(n),regname(j),levname(k), iy, "ANN", (varyear(i,j,k,n,jy),i=1,nf)
       enddo

       write(20,*)
       write(20,*)"--- Monthly Means --"
       do iy=years,yeare
          jy=iy-years+1
       do mm=1,12
         write(20,'(3a,2i5,17f9.3)')stname(n),regname(j),levname(k), iy, mm, (varmon(i,j,k,mm,n,jy),i=1,nf)
       enddo
       enddo

      enddo
      enddo
      enddo

      stop
      end
EOF
#----------------------------------------------------------------
        
#xlf90 -o month_ac.out month_ac.f 
ifort -convert big_endian -FR -o month_ac.out month_ac.f 
./month_ac.out


#----------------------------------------------------------------

cat > AC_${var}${mdl}${cyc}Z_month.ctl  << EOF
dset ^AC_${var}${mdl}${cyc}Z_month.bin
undef -99.9
options sequential
format big_endian
title monthly mean AC, RMSE abd Bias  
title x-fcsthr: 0-384 at 24hr interval .   
title y regions: $reglist                    
xdef 17 linear 0 1
ydef $nreg linear 1 1
zdef $nlev levels $levlist         
tdef 600 Linear 01jan${years} 1mon
vars    3
cor  $nlev 0  anomaly correlation   
rms  $nlev 0  rmse                    
bias $nlev 0  bias                       
endvars
EOF

#---------------------------------------------
done   ;# variables
done   ;# cycles
done   ;# models
#---------------------------------------------

exit

