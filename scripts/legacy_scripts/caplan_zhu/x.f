      integer, parameter :: ys=1984, ye=2013, ny=ye-ys+1
      integer, parameter :: mon=12,  mone=03 
      integer, parameter :: mdl=6   !number of models
      integer :: x(2,mdl,mon,ny)
      real*4 ::  y(2,mdl,mon,ny)
      real*4 ::  ym(2,mdl,ny)     !annual mean
      character*8 name(mdl),nameb(mdl)
      character*100 file1,file2
      data name/"mrf","cd","ec","uk","cn","fn"/
      data nameb/"GFS","CDAS","ECMWF","UKM","CMC","FNOMC"/
      data bad/-999.0/

      do 100 i=1,mdl
       file1="/global/save/globstat/stats/frontsave/"//trim(name(i))//"monn"
       file2="/global/save/globstat/stats/frontsave/"//trim(name(i))//"mons"
       open(11,file=file1,form="formatted",status="old")   !NH
       open(12,file=file2,form="formatted",status="old")   !SH

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

      open(40,file="Zac500mb_monday5.bin",form="unformatted",status="unknown")
      do n=1,ny
      do m=1,mon
       write(40) ((y(j,i,m,n),i=1,mdl),j=1,2)  
      enddo
      enddo

      open(61,file="Zac500mb_monday5_NH.txt",form="formatted",status="unknown")
      open(62,file="Zac500mb_monday5_SH.txt",form="formatted",status="unknown")
        write(61,*)"--------NH Monthly Mean 500hPa HGT AC---------"
        write(62,*)"--------SH Monthly Mean 500hPa HGT AC---------"
        write(61,*) "yymm         ",(nameb(i),i=1,mdl)
        write(62,*) "yymm         ",(nameb(i),i=1,mdl)
      do n=1,ny
      do m=1,mon
       write(61,'(i4,i2.2,2x,9f9.3)') (ys+n-1),m,(y(1,i,m,n),i=1,mdl)  
       write(62,'(i4,i2.2,2x,9f9.3)') (ys+n-1),m,(y(2,i,m,n),i=1,mdl)  
      enddo
      enddo

      
      open(41,file="Zac500mb_d5_yearmean.txt",form="formatted",status="unknown")
      do 200 j=1,2
        if(j.eq.1) write(41,*)"--------NH Annual Mean 500hPa HGT AC---------"
        if(j.eq.2) write(41,*)"--------SH Annual Mean 500hPa HGT AC---------"
        write(41,*) "         ",(nameb(i),i=1,mdl)
      do 150 n=1,ny
      do i=1,mdl
       ym(j,i,n)=0.
       nn=0
       do m=1,12
        if(y(j,i,m,n).ne.bad) then
         ym(j,i,n)=ym(j,i,n)+y(j,i,m,n)
         nn=nn+1
        endif
       enddo
       if(nn.ne.0) ym(j,i,n)=ym(j,i,n)/nn
      enddo
        write(41,'(i7, 9f8.3)') ys+n-1, (ym(j,i,n),i=1,mdl)
 150  continue
 200  continue



      end
