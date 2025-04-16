'''
Author: Rodrigo Angulo (rangulo1@jhu.edu)

'''

import sys,os
import pandas as pd
import numpy as np



def dist2line(fwhm, depth, slope, ref_p):
    #yline = m*x                      # line through origin
    # m = np.tan(angle*(np.pi/180.))    # slope given angle
    m = slope
    fw_ref, m5_ref = ref_p            # reference point of FWHM/Depth
        
    x_p = 10*np.log10(fw_ref/fwhm)       # scaled log ratio FWHMs
    y_p = m5_ref - depth                 # difference of depth (e.g. m5sigma)
    
    dist = (y_p - m*x_p)/np.sqrt(1+m**2)    # distance from point to line; negative sign assigned to points underneath line
    
    return(dist)

        
def calc_FOM(table, slope, ref_point='median'):
        if ref_point == 'median':
            ref_fw = table['FWHM'].median()
            ref_m5 = table['M5SIGMA'].median()
        elif len(ref_point) == 2:
            ref_fw = ref_point[0]
            ref_m5 = ref_point[1]
        
        for i in range(len(table)):
            fw_i = table['FWHM'][i]
            m5_i = table['M5SIGMA'][i]
            
            dist = dist2line(fw_i,m5_i,slope=slope,ref_p=[ref_fw,ref_m5])
            
            table.loc[i,'FOM_dist'] = np.round(dist,3)

        return('Calculated FOMs -- Completed')


def sort_by_FOM(table, split_by_filter=False):
    order_ind = []

    if split_by_filter is True:
        phot_codes = np.unique(table['PHOTCODE'])          # we use DECam images which have a photcode to specify filter and ccd
        for i in phot_codes:
            phcd_i = np.where(table.loc[:,'PHOTCODE'].eq(i))
            order_i = table.loc[phcd_i].sort_values('FOM_dist',ascending=True).index.values
            order_ind += list(order_i)
    else:
        order_ind = table.loc[:].sort_values('FOM_dist',ascending=True).index.values

    return(order_ind)



if __name__ == '__main__':
    txt_file = sys.argv[1]
    table_ims = pd.read_csv(txt_file, sep='\s+')     # txt file should be pandas readable table of filename, fwhm (seeing), and m5sigma (depth)

    calc_FOM(table_ims,81)                           # found optimal slope of 81 +/- 17; see Angulo et al. 2025
    ordered = sort_by_FOM(table_ims)

    table_ims.loc[ordered].to_csv(str(txt_file.rpartition('.')[0])+'_tmplorder.txt', sep='\t', index=False)















