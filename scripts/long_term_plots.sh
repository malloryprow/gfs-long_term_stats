#!/bin/sh
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
cd ${output_dir}

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

# Annual Means -- Plots
if [ $mm = "01" ]; then
    amp_submit_time=$(date -d "+6 hours" '+%Y%m%d%H')
    amp_submit_year=$(echo $amp_submit_time|cut -c1-4)
    amp_submit_month=$(echo $amp_submit_time|cut -c5-6)
    amp_submit_day=$(echo $amp_submit_time|cut -c7-8)
    amp_submit_hour=$(echo $amp_submit_time|cut -c9-10)
    cd ${output_dir}
    qsub -q "dev" -A "VERF-DEV" -N long_term_plots_annual_means -o ${output_dir}/long_term_plots_annual_means.out -e ${output_dir}/long_term_plots_annual_means.out -l walltime=02:00:00 -l select=1:ncpus=1 -v YYYY=${YYYYm1},working_dir=${output_dir},script_dir=${USHlong_term_stats},PATH=${PATH} -a ${amp_submit_year}${amp_submit_month}${amp_submit_day}${amp_submit_hour}00 ${USHlong_term_stats}/ush/submit_annual_means_plots.sh
fi

## Send plots to web
web_submit_time=$(date -d "+8 hours" '+%Y%m%d%H')
web_submit_year=$(echo $web_submit_time|cut -c1-4)
web_submit_month=$(echo $web_submit_time|cut -c5-6)
web_submit_day=$(echo $web_submit_time|cut -c7-8)
web_submit_hour=$(echo $web_submit_time|cut -c9-10)
cd ${output_dir}
#qsub -q "dev_transfer" -A "VERF-DEV" -N long_term_plots_copy_to_web -o ${output_dir}/long_term_plots_copy_to_web.out -e ${output_dir}/long_term_plots_copy_to_web.out -l walltime=02:00:00 -l select=1:ncpus=1 -v working_dir=${output_dir},webhost=${webhost},webhostid=${webhostid},webdir=${webdir},script_dir=${USHlong_term_stats},PATH=${PATH},YYYYmm=${YYYYmm} -a ${web_submit_year}${web_submit_month}${web_submit_day}${web_submit_hour}00 ${USHlong_term_stats}/submit_copy_to_web.sh
