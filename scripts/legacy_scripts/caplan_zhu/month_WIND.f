      integer, parameter :: years=1996, yeare=2013,ny=yeare-years+2 
      integer, parameter :: nd=366, nh=1, nz=2,nf=17
      integer, parameter :: nvar=32, nm=12               
!--daily stats  
      real*4 :: varday(nf,nh,nz,nd,nvar)
!--monthly means
      real*4 :: varmon(nf,nh,nz,nm,nvar,ny)
!--annual means
      real*4 :: varyear(nf,nh,nz,nvar,ny)
!--
      character*200 :: infile
      character*18   :: vname(nvar) 
      character*8    :: lev(nz), hemis(nh)
      data vname/"U   AC Wave1-3    ", "U   AC Wave4-9    ","U   AC Wave10-20  ","U   AC Wave1-20   ",&
                 "U   RMSE          ", "U   Error         ","U   RMSEC         ","U   ERRORC        ",&
                 "V   AC Wave1-3    ", "V   AC Wave4-9    ","V   AC Wave10-20  ","V   AC Wave1-20   ",&
                 "V   RMSE          ", "V   Error         ","V   RMSEC         ","V   ERRORC        ",&
                 "SPD AC Wave1-3    ", "SPD AC Wave4-9    ","SPD AC Wave10-20  ","SPD AC Wave1-20   ",&
                 "SPD RMSE          ", "SPD Error         ","SPD RMSEC         ","SPD ERRORC        ",&
                 "UV  AC Wave1-3    ", "UV  AC Wave4-9    ","UV  AC Wave10-20  ","UV  AC Wave1-20   ",&
                 "UV  RMSE          ", "UV  Error         ","UV  RMSEC         ","UV  ERRORC        "/
      data lev/"850 hPa ", "200 hPa "/
      data hemis/"Tropics "/
      integer :: mday(nm)
      data mday/31,28,31,30,31,30,31,31,30,31,30,31/
      data bad/-999.9/
      logical leap
      character*4 yc

      open(10,file="WINDs18Z_month.bin",form="unformatted",status="unknown")
      open(20,file="WINDs18Z_mean.txt",form="formatted",status="unknown")
      varmon=bad     !initialize data
      varyear=bad    !initialize data

      do 1000 iy=years,yeare
      jy=iy-years+1
      leap=.false.
      if(mod(iy,4).eq.0) leap=.true.
      write(yc,'(i4)')iy

      infile="/global/save/Fanglin.Yang/vrfygfs/vsdb_data/legacy/daily/WINDs18Z_"//yc//".bin"
      print*,infile        
      open(1,iostat=iso,file=trim(infile),form="unformatted",status="old")
      if(iso.ne.0) goto 999
     
      ndayinyear=365
      if(leap) ndayinyear=366
      do m=1,ndayinyear
       do n=1,nvar
        do k=1,nz
         read(1) ((varday(i,j,k,m,n),i=1,nf),j=1,nh)
        enddo
       enddo
      enddo
   
!-- compute monthly means
      do 100 n=1,nvar     ! number of variables
      do 100 k=1,nz       ! vertical layers
      do 100 i=1,nf       ! forecasts days 
      do 100 j=1,nh       ! area: northern and southern hemisphere
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
        if(ngood.ge.15)  then               !at least have 15 points in the month
         varmon(i,j,k,mm,n,jy)=xtmp/ngood
        else
         varmon(i,j,k,mm,n,jy)=bad
        endif
         nday=nday+iday
       enddo
  100 continue
       

 999  continue
      do mm=1,nm
       do n=1,nvar
        do k=1,nz
         write(10) ((varmon(i,j,k,mm,n,jy),i=1,nf),j=1,nh)
        enddo
       enddo
      enddo
      close(1)
 1000 continue

!-- add one more year for computing running means, all default data
      do mm=1,nm
       do n=1,nvar
        do k=1,nz
         write(10) ((varmon(i,j,k,mm,n,ny),i=1,nf),j=1,nh)
        enddo
       enddo
      enddo

!-----------------
! compute annual means
      do 101 iy=years,yeare
          jy=iy-years+1
      do 101 n=1,nvar     ! number of variables
      do 101 k=1,nz       ! vertical layers
      do 101 i=1,nf       ! forecasts days
      do 101 j=1,nh       ! area: northern and southern hemisphere
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
      do k=nz,1,-1
      do j=1,nh
      do n=1,nvar
       write(20,*)
       write(20,*)"-------------------------------------------------------------------------------------"
       write(20,*)"---", vname(n),hemis(j),lev(k),"--- for forecast days 0 ~ ",nf-1
       write(20,*)"-------------------------------------------------------------------------------------"

       write(20,*)"--- Annual Means --"
       do iy=years,yeare
          jy=iy-years+1
         write(20,'(i5,5x,17f9.3)')iy, (varyear(i,j,k,n,jy),i=1,nf)
       enddo

       write(20,*)
       write(20,*)"--- Monthly Means --"
       do iy=years,yeare
          jy=iy-years+1
       do mm=1,12
         write(20,'(2i5,17f9.3)')iy, mm, (varmon(i,j,k,mm,n,jy),i=1,nf)
       enddo
       enddo

      enddo
      enddo
      enddo


      stop
      end
