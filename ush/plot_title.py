def get_lead_title(lead_hour_str):
    """! Get a formalized version of the
         forecast lead to use in plot title
 
             Args:
                 lead - string of the forecast lead [hour]

             Returns:
                 lead_title - string of a formalized version
                              of the forecast lead
                              to use in plot title
    """
    lead_hour_float = float(lead_hour_str)
    lead_day_float = lead_hour_float/24.
    if lead_day_float.is_integer():
        lead_day_str = str(int(lead_day_float))
    else:
        lead_day_str = str(lead_day_float)
    lead_title = 'Forecast Day '+lead_day_str+' (Forecast Hour '+lead_hour_str+')'
    return lead_title

def get_vx_mask_title(vx_mask):
    """! Get a formalized version of the
         verification vx_mask to use in plot title
 
             Args:
                 vx_mask - string of the verification
                          vx_mask abbrevation used for
                          MET

             Returns:
                 vx_mask_title - string of a formalized version
                                of the verification vx_mask
                                to use in plot title
    """
    vx_mask_title_dict = {
        'G002': 'Global',
        'NHX': 'Northern Hemisphere 20N-80N',
        'SHX': 'Southern Hemisphere 20S-80S',
        'TRO': 'Tropics 20S-20N', 
        'PNA': 'Pacific North America',
    }
    if vx_mask in list(vx_mask_title_dict.keys()):
        vx_mask_title = vx_mask_title_dict[vx_mask] 
    else:
        vx_mask_title = vx_mask
    return vx_mask_title

def get_var_info_title(var_name, var_level):
    """! Get a formalized version of the
         variable information to use in plot title
 
             Args:
                 var_name   - string of the variable GRIB name
                 var_level  - string of the variable level used
                              in MET

             Returns:
                 var_info_title - string of a formalized version
                                  of the variable information
                                  to use in plot title
    """
    # Build variable name title
    var_name_title_dict = {
        'HGT': 'Geopotential Height (gpm)',
        'HGT_WV1_0-3': 'Geopotential Height: Waves 0-3 (gpm)',
        'HGT_WV1_4-9': 'Geopotential Height: Waves 4-9 (gpm)',
        'HGT_WV1_10-20': 'Geopotential Height: Waves 10-20 (gpm)',
        'HGT_WV1_0-20': 'Geopotential Height: Waves 0-20 (gpm)',
        'PRES': 'Pressure (hPa)',
        'TMP': 'Temperature (K)',
        'UGRD': 'Zonal Wind (m 'r'$\mathregular{s^{-1}}$'')',
        'VGRD': 'Meridional Wind (m 'r'$\mathregular{s^{-1}}$'')',
        'UGRD_VGRD': 'Vector Wind (m 'r'$\mathregular{s^{-1}}$'')',
        'PRMSL': 'Pressure Reduced to MSL (hPa)',
    }
    if var_name in list(var_name_title_dict.keys()):
        var_name_title = var_name_title_dict[var_name]
    else:
        var_name_title = var_name
    # Build variable level title
    if 'P' in var_level:
        var_level_title = var_level.replace('P', '')+' hPa'
    var_info_title = var_level_title+' '+var_name_title
    return var_info_title
