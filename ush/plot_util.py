import os
import datetime as datetime
import time
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

"""!@namespace plot_util
 @brief Provides utility functions for METplus plotting use case.
"""

def get_clevels(data, spacing):
    """! Get contour levels for plotting differences
         or bias (centered on 0)

              Args:
                  data    - array of data to be contoured
                  spacing - float for spacing for power function,
                            value of 1.0 gives evenly spaced
                            contour intervals
              Returns:
                  clevels - array of contour levels
    """
    if np.abs(np.nanmin(data)) > np.nanmax(data):
       cmax = np.abs(np.nanmin(data))
       cmin = np.nanmin(data)
    else:
       cmax = np.nanmax(data)
       cmin = -1 * np.nanmax(data)
    if cmax > 100:
        cmax = cmax - (cmax * 0.2)
        cmin = cmin + (cmin * 0.2)
    elif cmax > 10:
        cmax = cmax - (cmax * 0.1)
        cmin = cmin + (cmin * 0.1)
    if cmax > 1:
       cmin = round(cmin-1,0)
       cmax = round(cmax+1,0)
    else:
       cmin = round(cmin-0.1,1)
       cmax = round(cmax+0.1,1)
    steps = 6
    span = cmax
    dx = 1.0 / (steps-1)
    pos = np.array([0 + (i*dx)**spacing*span for i in range(steps)],
                   dtype=float)
    neg = np.array(pos[1:], dtype=float) * -1
    clevels = np.append(neg[::-1], pos)
    return clevels

def get_logo_paths():
    """! Get contour levels for plotting differences
         or bias (centered on 0)

              Args:

              Returns:
                  noaa_logo_path - string of path
                                   to NOAA logo
                  nws_logo_path -  string of path
                                   to NWS logo
    """
    noaa_logo_path = '/u/emc.vpppg/cron_jobs/scripts/verification/global/EMC_verif-global_daily_config/EMC_verif-global_all_models/ush/plotting_scripts/noaa.png'
    nws_logo_path = '/u/emc.vpppg/cron_jobs/scripts/verification/global/EMC_verif-global_daily_config/EMC_verif-global_all_models/ush/plotting_scripts/nws.png'
    return noaa_logo_path, nws_logo_path
