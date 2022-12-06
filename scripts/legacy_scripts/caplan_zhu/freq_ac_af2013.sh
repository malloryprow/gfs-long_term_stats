#!/bin/sh
set -x

#------------------------------------------------------------
#--frequency distribution of HGT AC scores
#--new vsdb-based data on and after 2013
#------------------------------------------------------------
curdir=`pwd`
export dailydata=/global/save/Fanglin.Yang/vrfygfs/longterm/long_vsdb/daily

###########################################################
for model in s e k m c; do
  if [ $model = s ]; then mdname=gfs ;fi
  if [ $model = e ]; then mdname=ecm ;fi
  if [ $model = k ]; then mdname=ukm ;fi
  if [ $model = m ]; then mdname=cmc ;fi
  if [ $model = c ]; then mdname=cdas ;fi
for yyyy in 2013; do
###########################################################

cyc=00    ;# forecast cycle to be vefified: 00Z, 06Z, 12Z, 18Z
ndays=365 ;# days in a year
fday=17   ;# forecast length (gfs default=16, 384 hours) including f00 fcst


fileina1=${dailydata}/${cyc}/${mdname}/HGT_P1000_G2NHX_${mdname}${cyc}Z${yyyy}.bin
fileina2=${dailydata}/${cyc}/${mdname}/HGT_P1000_G2SHX_${mdname}${cyc}Z${yyyy}.bin
fileinb1=${dailydata}/${cyc}/${mdname}/HGT_P500_G2NHX_${mdname}${cyc}Z${yyyy}.bin
fileinb2=${dailydata}/${cyc}/${mdname}/HGT_P500_G2SHX_${mdname}${cyc}Z${yyyy}.bin
fileout=HGT${model}${cyc}Z_${yyyy}

#------------------------------------------------------------
rm conv_freq.f conv_freq.x tmp.txt
cat >conv_freq.f <<EOF
!
      integer, parameter :: nday=${ndays}, fday=${fday}
      integer, parameter :: ns=2, lev=2   !NH and SH, 1000hPa and 500hPa
      integer, parameter :: bin=20   
      integer, parameter :: nst=4          !cor,rms,bias,bincor in filein   
      real*4             :: points(fday,nday)
      real*4             :: alldata(fday,nday,ns,lev,8)  !8 variables
      real*4             :: cor(fday,nday,ns,lev), num(fday,ns,lev)
      real*4             :: mcor(fday,ns,lev)
      real*4             :: bincor(fday,bin,ns,lev), binbnd(bin+1)
      integer            :: dropcount(fday,ns,lev), overcount(fday,ns,lev)
      real*4             :: dropcor, dropfreq(fday,ns,lev)
      real*4             :: overcor, overfreq(fday,ns,lev)
      character*10       :: hems(ns),levs(lev)
      data bad/-99.9/
      data hems/"NH","SH"/,levs/"1000hPa","500hPa"/
      data dropcor/0.7e+0/,overcor/0.9e+0/

      if(nday .le. bin) then
       write(6,*) "samples are less than 20 bins, QUIT!"
       stop
      endif

      open(11,file="${fileina1}",form="unformatted",status="unknown")
      open(12,file="${fileina2}",form="unformatted",status="unknown")
      open(13,file="${fileinb1}",form="unformatted",status="unknown")
      open(14,file="${fileinb2}",form="unformatted",status="unknown")

      open(20,file="${fileout}_freq.bin",form="unformatted",status="unknown")
      open(30,file="${fileout}.txt",form="formatted",status="unknown")

      do nd=1,nday 
      do nv=1,nst
       read(11) (alldata(i,nd,1,1,nv),i=1,fday)   !1000mb, NH
       read(12) (alldata(i,nd,2,1,nv),i=1,fday)   !1000mb, SH
       read(13) (alldata(i,nd,1,2,nv),i=1,fday)   !500mb, NH
       read(14) (alldata(i,nd,2,2,nv),i=1,fday)   !500mb, SH
      enddo
      enddo

      do nl=1,lev
      do nd=1,nday 
      do i=1,fday
      do j=1,ns
       cor(i,nd,j,nl)=alldata(i,nd,j,nl,1)
      enddo
      enddo
      enddo
      enddo

! create bounds of bins for frequency distribution of anomaly correlations (0,1)
       delcor=1.0/bin
       do i=1,bin+1
        binbnd(i)=(i-1)*delcor
       enddo
       bincor=0.0; num=0.0; mcor=0.0
       dropcount=0; dropfreq=0.0
       overcount=0; overfreq=0.0

!--frequency calculation
      do 100 i=1,fday
      do 100 j=1,ns
      do 100 nl=1,lev
      do 200 nd=1,nday
      xtmp=cor(i,nd,j,nl)
      if(xtmp.ne.bad) then
       num(i,j,nl)=num(i,j,nl)+1
       mcor(i,j,nl)=mcor(i,j,nl)+xtmp
       if(xtmp.le.dropcor) dropcount(i,j,nl)=dropcount(i,j,nl)+1
       if(xtmp.ge.overcor) overcount(i,j,nl)=overcount(i,j,nl)+1
       do k=1,bin
        if(xtmp.gt.binbnd(k).and.xtmp.le.binbnd(k+1)) &
!       bincor(i,k,j,nl)=bincor(i,k,j,nl)+xtmp         
        bincor(i,k,j,nl)=bincor(i,k,j,nl)+1            
       enddo
      endif
 200  continue 
      if(num(i,j,nl).gt.0) then
       mcor(i,j,nl)=mcor(i,j,nl)/num(i,j,nl)
       dropfreq(i,j,nl)=dropcount(i,j,nl)/num(i,j,nl)
       overfreq(i,j,nl)=overcount(i,j,nl)/num(i,j,nl)
       do k=1,bin
         bincor(i,k,j,nl)=bincor(i,k,j,nl)/num(i,j,nl)
       enddo
      else
       mcor(i,j,nl)=bad
       dropfreq(i,j,nl)=bad
       overfreq(i,j,nl)=bad
       do k=1,bin
        bincor(i,k,j,nl)=bad
       enddo
      endif
 100  continue
       
      do i=1,fday
      do nl=1,lev
       write(20) ((bincor(i,k,j,nl),k=1,bin),j=1,ns)
      enddo
      enddo

      do nl=1,lev
      do j=1,ns
       write(30,*)hems(j),"   ",levs(nl)
       write(30,'(17i8)') (int(num(i,j,nl)),i=1,fday)
       write(30,'(17f8.3)') (mcor(i,j,nl),i=1,fday)
      enddo
      enddo

      write(30,*)"-------------------------------------------"
      write(30,*) "day-5 AC: total count; mean AC; drop<0.7 count; drop freq; over>0.9 count; over freq "
      do nl=1,lev
      do j=1,ns
       write(30,'(a,a,i6,f8.3,i6,f8.1,i6,f8.1)')hems(j),levs(nl), int(num(6,j,nl)), mcor(6,j,nl), &
          dropcount(6,j,nl),dropfreq(6,j,nl)*100,overcount(6,j,nl),overfreq(6,j,nl)*100
      enddo
      enddo

     end
EOF


ifort  -convert big_endian -FR -o conv_freq.x conv_freq.f
./conv_freq.x


#------------------------------------------------------------
# create GrADS control file
#------------------------------------------------------------
cat >${fileout}_freq.ctl <<EOF1
dset ^${fileout}_freq.bin  
undef -999.9   
options sequential 
title AC score frequency, x-bins, y-NH.SH
xdef   20 linear 0.025 0.05              
ydef   2  linear 1 1 
zdef  2 levels  1000 500
tdef $fday Linear 1Jan1900 1dy
vars    1
fcor  2 0  correlation frequency distribution
endvars

EOF1


###########################################################
done
done
###########################################################

exit
