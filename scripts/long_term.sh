#!/bin/bash
set -x

module reset
module load PrgEnv-intel/8.1.0
module load intel/19.1.3.304
module load python/3.8.6

YYYYmm=${1:-"$(date +%Y%m)"}
YYYY=$(echo $YYYYmm  | cut -c1-4)
mm=$(echo $YYYYmm  | cut -c5-6)

USHEMC_verif_global="/u/emc.vpppg/cron_jobs/scripts/verification/global/EMC_verif-global_daily_config/EMC_verif-global_all_models/ush"
USHlong_term_stats="/lfs/h2/emc/vpppg/save/emc.vpppg/verification/global/long_term_stats/ush"
PARMlong_term_stats="/lfs/h2/emc/vpppg/save/emc.vpppg/verification/global/long_term_stats/parm"

export webhost="emcrzdm.ncep.noaa.gov"
export webhostid="emc.vpppg"
export webdir="/home/people/emc/www/htdocs/users/verification/global/gfs/ops"

export output_dir="/lfs/h2/emc/stmp/$USER/output_crons/long_term_stats_update_${YYYYmm}"
mkdir -p ${output_dir}

## Monthly Means -- Stats
cd $USHEMC_verif_global
export monthly_mean_start_date="${YYYYmm}01"
month_end_date=$(cal ${mm} ${YYYY} | awk 'NF {DAYS = $NF}; END {print DAYS}')
export monthly_mean_end_date="${YYYYmm}${month_end_date}"
export model_list="gfs ecm cmc fno cdas ukm jma cfsr"
for model in $model_list ; do
    if [ $model = "gfs" ]; then
        cycle_list="00 06 12 18"
    elif [ $model = "cdas" -o $model = "cfsr" ]; then
        cycle_list="00"
    else
        cycle_list="00 12"
    fi
    if [ $model = "gfs" -o $model = "cfsr" ]; then
        model_anl_name="self_anl"
    else
        model_anl_name="self_f00"
    fi
    for cycle in $cycle_list ; do
        export model="${model}"
        export cycle="${cycle}"
        export model_anl_name="${model_anl_name}"
        ./run_verif_global.sh ${PARMlong_term_stats}/config/config.vrfy.monthly.mean
    done
done
cycle_list="00 12"
for cycle in $cycle_list ; do
    export cycle="${cycle}"
    ./run_verif_global.sh ${PARMlong_term_stats}/config/config.vrfy.monthly.mean.all_models
done
mms_submit_time=$(date -d "+2 hours" '+%Y%m%d%H')
mms_submit_year=$(echo $mms_submit_time|cut -c1-4)
mms_submit_month=$(echo $mms_submit_time|cut -c5-6)
mms_submit_day=$(echo $mms_submit_time|cut -c7-8)
mms_submit_hour=$(echo $mms_submit_time|cut -c9-10)
cd ${output_dir}
qsub -q "dev" -A "VERF-DEV" -N long_term_stats_monthly_means_${YYYYmm} -o ${output_dir}/long_term_stats_monthly_means_${YYYYmm}.out -e ${output_dir}/long_term_stats_monthly_means_${YYYYmm}.out -l walltime=02:00:00 -l select=1:ncpus=1 -v YYYYmm=${YYYYmm},working_dir=${output_dir},script_dir=${USHlong_term_stats},PATH=${PATH} -a ${mms_submit_year}${mms_submit_month}${mms_submit_day}${mms_submit_hour}00 ${USHlong_term_stats}/submit_monthly_means_stats.sh

## Annual Means -- Stats
if [ $mm = "01" ]; then
    ams_submit_time=$(date -d "+4 hours" '+%Y%m%d%H')
    ams_submit_year=$(echo $ams_submit_time|cut -c1-4)
    ams_submit_month=$(echo $ams_submit_time|cut -c5-6)
    ams_submit_day=$(echo $ams_submit_time|cut -c7-8)
    ams_submit_hour=$(echo $ams_submit_time|cut -c9-10)
    export YYYYm1=$(expr $YYYY - 1)
    cd ${output_dir}
    qsub -q "dev" -A "VERF-DEV" -N long_term_stats_annual_means_${YYYYm1} -o ${output_dir}/long_term_stats_annual_means_${YYYYm1}.out -e ${output_dir}/long_term_stats_annual_means_${YYYYm1}.out -l walltime=02:00:00 -l select=1:ncpus=1 -v- YYYY=${YYYYm1},script_dir=${USHlong_term_stats},PATH=${PATH} -a ${ams_submit_year}${ams_submit_month}${ams_submit_day}${ams_submit_hour}00 ${USHlong_term_stats}/submit_annual_means_stats.sh
fi

## Monthly Means -- Plots
start_YYYYmm="199601"
end_YYYYmm=${1:-"$(date +%Y%m)"}
mmp_submit_time=$(date -d "+4 hours" '+%Y%m%d%H')
mmp_submit_year=$(echo $mmp_submit_time|cut -c1-4)
mmp_submit_month=$(echo $mmp_submit_time|cut -c5-6)
mmp_submit_day=$(echo $mmp_submit_time|cut -c7-8)
mmp_submit_hour=$(echo $mmp_submit_time|cut -c9-10)
cd ${output_dir}
qsub -q "dev" -A "VERF-DEV" -N long_term_plots_monthly_means -o ${output_dir}/long_term_plots_monthly_means.out -e ${output_dir}/long_term_plots_monthly_means.out -l walltime=02:00:00 -l select=1:ncpus=1 -v start_YYYYmm=${start_YYYYmm},end_YYYYmm=${end_YYYYmm},working_dir=${output_dir},script_dir=${USHlong_term_stats},PATH=${PATH} -a ${mmp_submit_year}${mmp_submit_month}${mmp_submit_day}${mmp_submit_hour}00 ${USHlong_term_stats}/submit_monthly_means_plots.sh

## Annual Means -- Plots
if [ $mm = "01" ]; then
    amp_submit_time=$(date -d "+6 hours" '+%Y%m%d%H')
    amp_submit_year=$(echo $amp_submit_time|cut -c1-4)
    amp_submit_month=$(echo $amp_submit_time|cut -c5-6)
    amp_submit_day=$(echo $amp_submit_time|cut -c7-8)
    amp_submit_hour=$(echo $amp_submit_time|cut -c9-10)
    cd ${output_dir}
    qsub -q "dev" -A "VERF-DEV" -N long_term_plots_annual_means -o ${output_dir}/long_term_plots_annual_means.out -e ${output_dir}/long_term_plots_annual_means.out -l walltime=02:00:00 -l select=1:ncpus=1 -v YYYY=${YYYYm1},working_dir=${output_dir},script_dir=${USHlong_term_stats},PATH=${PATH} -a ${amp_submit_year}${amp_submit_month}${amp_submit_day}${amp_submit_hour}00 ${USHlong_term_stats}/submit_annual_means_plots.sh
fi

## Send stats to HPSS
hpss_submit_time=$(date -d "+4 hours" '+%Y%m%d%H')
hpss_submit_year=$(echo $hpss_submit_time|cut -c1-4)
hpss_submit_month=$(echo $hpss_submit_time|cut -c5-6)
hpss_submit_day=$(echo $hpss_submit_time|cut -c7-8)
hpss_submit_hour=$(echo $hpss_submit_time|cut -c9-10)
cd ${output_dir}
qsub -q "dev_transfer" -A "VERF-DEV" -N hpss_long_term_stats -o ${output_dir}/hpss_long_term_stats.out -e ${output_dir}/hpss_long_term_stats.out -l walltime=02:00:00 -l select=1:ncpus=1 -v script_dir=${USHlong_term_stats},PATH=${PATH} -a ${hpss_submit_year}${hpss_submit_month}${hpss_submit_day}${hpss_submit_hour}00 ${USHlong_term_stats}/submit_hpss.sh

## Send stats to other machine
rsync_submit_time=$(date -d "+4 hours" '+%Y%m%d%H')
rsync_submit_year=$(echo $rsync_submit_time|cut -c1-4)
rsync_submit_month=$(echo $rsync_submit_time|cut -c5-6)
rsync_submit_day=$(echo $rsync_submit_time|cut -c7-8)
rsync_submit_hour=$(echo $rsync_submit_time|cut -c9-10)
cd ${output_dir}
qsub -q "dev_transfer" -A "VERF-DEV" -N rsync_long_term_stats -o ${output_dir}/rsync_long_term_stats.out -e ${output_dir}/rsync_long_term_stats.out -l walltime=02:00:00 -l select=1:ncpus=1 -v script_dir=${USHlong_term_stats},PATH=${PATH} -a ${rsync_submit_year}${rsync_submit_month}${rsync_submit_day}${rsync_submit_hour}00 ${USHlong_term_stats}/submit_rsync.sh

## Send plots to web
web_submit_time=$(date -d "+8 hours" '+%Y%m%d%H')
web_submit_year=$(echo $web_submit_time|cut -c1-4)
web_submit_month=$(echo $web_submit_time|cut -c5-6)
web_submit_day=$(echo $web_submit_time|cut -c7-8)
web_submit_hour=$(echo $web_submit_time|cut -c9-10)
cd ${output_dir}
qsub -q "dev_transfer" -A "VERF-DEV" -N long_term_plots_copy_to_web -o ${output_dir}/long_term_plots_copy_to_web.out -e ${output_dir}/long_term_plots_copy_to_web.out -l walltime=02:00:00 -l select=1:ncpus=1 -v working_dir=${output_dir},webhost=${webhost},webhostid=${webhostid},webdir=${webdir},script_dir=${USHlong_term_stats},PATH=${PATH},YYYYmm=${YYYYmm} -a ${web_submit_year}${web_submit_month}${web_submit_day}${web_submit_hour}00 ${USHlong_term_stats}/submit_copy_to_web.sh
