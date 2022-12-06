#!/bin/sh
set -x

# read monthly day-6 500hPa HGT AC Scores
# output in binary format for GrADS 

ys=2001
ye=2012    #current year
mone=12     #current month

#----------------
cat >x.f <<EOF
      integer, parameter :: ys=$ys, ye=$ye, ny=ye-ys+1
      integer, parameter :: mon=12,  mone=$mone 
      integer, parameter :: mdl=6   !number of models
      integer :: x(2,mdl,mon,ny)
      real*4 ::  y(2,mdl,mon,ny)
      character*3 name(mdl)
      character*100 file1,file2
      data name/"mrf","cd","ec","uk","cn","fn"/
      data bad/-999.0/

      do 100 i=1,mdl
       file1="/global/save/globstat/stats/frontsave6/"//trim(name(i))//"monn"
       file2="/global/save/globstat/stats/frontsave6/"//trim(name(i))//"mons"
       open(11,file=file1,form="formatted",status="unknown")   !NH
       open(12,file=file2,form="formatted",status="unknown")   !NH

      read(11,*) 
      read(12,*)
      do n=1,ny-1
        read(11,*) (x(1,i,m,n),m=1,mon)
        read(12,*) (x(2,i,m,n),m=1,mon)
      enddo
        read(11,*) (x(1,i,m,ny),m=1,mone)    !current year
        read(12,*) (x(2,i,m,ny),m=1,mone)    !current year
        if(mone.lt.12) then
        do m=mone+1,mon
         x(1,i,m,ny)=999
         x(2,i,m,ny)=999
        enddo
        endif
      close(11)
      close(12)

! convert to real(4)
      do n=1,ny
      do m=1,mon
      do j=1,2
       y(j,i,m,n)=bad
       if(x(j,i,m,n).ne.999) y(j,i,m,n)=0.001*x(j,i,m,n)
      enddo
      enddo
      enddo
 100  continue

      open(40,file="Zac500mb_monday6.bin",form="unformatted",status="unknown")
      do n=1,ny
      do m=1,mon
       write(40) ((y(j,i,m,n),i=1,mdl),j=1,2)  
      enddo
      enddo

      end
EOF

xlf90 x.f
./a.out
#rm x.f a.out

cat >Zac500mb_monday6.ctl <<EOF1
dset ^Zac500mb_monday6.bin
undef -999.0
options sequential
title monthly mean day-6 NH (20N-80N) 500hPa Height AC scores
title x-models: gfs cdas ecm ukm cmc fno.   y=1,NH; y=2,SH
title peter-Zhu stats, upto year $ye mon $mone
xdef   6 linear 1 1
ydef   2 linear 1 1 
zdef   1 linear 1 1
tdef 1000 Linear Jan$ys 1mon
vars    1
cor   0 0  correlation
endvars
EOF1


cat >Zac500mb_monday6.ctl1 <<EOF2
dset ^Zac500mb_monday6.bin
undef -999.0
options sequential
title monthly mean day-6 NH (20N-80N) 500hPa Height AC scores
title x-models: gfs cdas ecm ukm cmc fno. y=1,NH; y=2,SH;  z-month
title peter-Zhu stats, upto year $ye mon $mone
xdef   6 linear 1 1
ydef   2 linear 1 1 
zdef   12 linear 1 1
tdef 1000 Linear Jan$ys 1yr
vars    1
cor   12 0  correlation
endvars
EOF2

exit
      

