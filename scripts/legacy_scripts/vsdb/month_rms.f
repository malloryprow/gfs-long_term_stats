      integer, parameter :: years=2008, yeare=2021,ny=yeare-years+2 
      integer, parameter :: nd=366         !days in a year 
      integer, parameter :: nreg=5     !number of areas
      integer, parameter :: nlev=14     !number of layers 
      integer, parameter :: nf=17          !number of forecasts 
      integer, parameter :: nm=12          !months in a year               
      integer, parameter :: nst=8          !pcor,rms,bias,emd,epv,rsd,msess,bincor
!!    integer, parameter :: nst7=7         !pcor,rms,bias,emd,epv,rsd,msess
      integer, parameter :: nst7=3         !pcor,rms,bias
!--daily stats  
      real*4 :: varday(nf,nreg,nlev,nd,nst)
!--monthly means
      real*4 :: varmon(nf,nreg,nlev,nm,nst7,ny)
!--annual means
      real*4 :: varyear(nf,nreg,nlev,nst7,ny)
!--
      character*5 :: stname(nst7),regname(nreg),levname(nlev)
!!    data stname /"PAC  ", "RMSE ", "BIAS ","EMD  ","EPV  ","RSD  ","MESS "/
      data stname /"PCOR ","RMSE ", "BIAS "/
      data regname/'G2  ','G2NHX','G2SHX','G2TRO','G2PNA'/                                      
      data levname/'P1000','P925','P850','P700','P500','P400','P300','P250','P200','P150','P100','P50','P20','P10' /             

      character*300 :: infile
      integer :: mday(nm)
      data mday/31,28,31,30,31,30,31,31,30,31,30,31/
      data bad/-99.9/
      logical leap
      character*4 yc

      open(10,file="RMS_WINDcfsr00Z_month.bin",form="unformatted",status="unknown")
      open(20,file="RMS_WINDcfsr00Z_mean.txt",form="formatted",status="unknown")
      varmon=bad    !initialize data
      varyear=bad   !initialize data

      do 1000 iy=years,yeare
       jy=iy-years+1
       leap=.false.
       if(mod(iy,4).eq.0) leap=.true.
       write(yc,'(i4)')iy

       do 50 j=1,nreg
        ndayinyear=365
        if(leap) ndayinyear=366

        infile="../daily/00/cfsr/WIND_"//trim(regname(j))//"_cfsr00Z"//yc//".bin" 
        open(1,iostat=iso,file=trim(infile),form="unformatted",status="old")
        if(iso.ne.0) goto 60 

        print*,trim(infile)        
        do m=1,ndayinyear
         do n=1,nst
         do k=1,nlev
           read(1) (varday(i,j,k,m,n),i=1,nf)
         enddo
         enddo
        enddo
        goto 50
   60   continue
        print*,trim(infile), "  is missing"        
        do m=1,ndayinyear
         do n=1,nst
          do k=1,nlev
           do i=1,nf
            varday(i,j,k,m,n)=bad       
           enddo
          enddo
         enddo
        enddo
   50  continue
   
!-- compute monthly means
      do 100 n=1,nst7     ! number of variables
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
        if(varday(i,j,k,ii,n).ne.bad .and. abs(varday(i,j,k,ii,n)).lt.99999.0) then
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
       do n=1,nst7
        do k=1,nlev
         write(10) ((varmon(i,j,k,mm,n,jy),i=1,nf),j=1,nreg)
        enddo
       enddo
      enddo
      close(1)
 1000 continue

!-- add one more year for computing running mean, all default data
      do mm=1,nm
       do n=1,nst7
        do k=1,nlev
         write(10) ((varmon(i,j,k,mm,n,ny),i=1,nf),j=1,nreg)
        enddo
       enddo
      enddo


!-----------------
! compute annual means
      do 101 iy=years,yeare
          jy=iy-years+1
      do 101 n=1,nst7     ! number of variables
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

      do n=1,nst7
      do j=1,nreg
      do k=1,nlev,2  
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
