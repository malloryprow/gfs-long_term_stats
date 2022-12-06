#!/bin/sh
set -x
# Send to production
prod=`cat /lfs/h1/ops/prod/config/prodmachinefile | grep "primary:" | sed -e 's/primary://g'`
prod_letter=`echo $prod | cut -c 1-1`
if [ $prod_letter = d ]; then
    transfer_host="cdxfer.wcoss2.ncep.noaa.gov"
fi
if [ $prod_letter = c ]; then
    transfer_host="ddxfer.wcoss2.ncep.noaa.gov"
fi
rsync -ahr -P /lfs/h2/emc/vpppg/save/emc.vpppg/verification/global/long_term_stats/long_term_archive/* $transfer_host:/lfs/h2/emc/vpppg/save/emc.vpppg/verification/global/long_term_stats/long_term_archive/.
