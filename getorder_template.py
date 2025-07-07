'''
Author: Rodrigo Angulo (rangulo1@jhu.edu)

The following is a simple script to order a group of images in descending order based on how well they perform as a template in Difference Image Analysis (DIA).
'''

import sys,os
import pandas as pd
import numpy as np



def dist2line(fwhm, depth, slope, ref_p):
    # the distance between a point and a line defined using a line through the origin and a point on a delta_m5sigma vs. 10logR_FWHM (see Angulo et al. 2025)
    
    # yline = m*x                      # line through origin
    # m = np.tan(angle*(np.pi/180.))    # slope given angle
    m = slope
    fw_ref, m5_ref = ref_p            # reference point of FWHM/Depth
        
    x_p = 10*np.log10(fw_ref/fwhm)       # scaled log ratio FWHMs (i.e, 10logR_FWHM)
    y_p = m5_ref - depth                 # difference of depth (i.e., delta_m5sigma)
    
    dist = (y_p - m*x_p)/np.sqrt(1+m**2)    # distance from point to line; negative sign assigned to points underneath line
    
    return(dist)

        
def calc_FoM(table, slope, ref_point='median'):
    # calculate the Figure of Merit value where the smaller number implies the better choice of image to use as template in DIA
    
    if ref_point == 'median':
        # Using the median value of seeing and depth work well as the reference point for all images in calculating the FoM
        
        ref_fw = table['FWHM'].median()
        ref_m5 = table['M5SIGMA'].median()
    elif len(ref_point) == 2:
        # You can specify the seeing and depth reference point if needed
        
        ref_fw = ref_point[0]
        ref_m5 = ref_point[1]
    
    for i in range(len(table)):
        # Loop through all images to get a FoM value
        
        fw_i = table['FWHM'][i]
        m5_i = table['M5SIGMA'][i]
        
        dist = dist2line(fw_i,m5_i,slope=slope,ref_p=[ref_fw,ref_m5])
        
        table.loc[i,'FoM_dist'] = np.round(dist,3)

    return('Calculated FoMs -- Completed')


def sort_by_FoM(table, split_by_filter=False):
    # Order the table based on FoM, resulting with images ordered from best to worse use as template
    
    order_ind = []

    if split_by_filter is True:
        # we use DECam images in Angulo et al. 2025 which have a photcode to specify filter and ccd
        # Order by FoM per filter should be done separately
        
        phot_codes = np.unique(table['PHOTCODE'])
        for i in phot_codes:
            phcd_i = np.where(table.loc[:,'PHOTCODE'].eq(i))
            order_i = table.loc[phcd_i].sort_values('FoM_dist',ascending=True).index.values
            order_ind += list(order_i)
    else:
        order_ind = table.loc[:].sort_values('FoM_dist',ascending=True).index.values

    return(order_ind)



if __name__ == '__main__':
    txt_file = sys.argv[1]
    table_ims = pd.read_csv(txt_file, sep='\s+')     # txt file should be pandas readable table of filename, fwhm (seeing), and m5sigma (depth)

    calc_FoM(table_ims,0.81)                           # found optimal slope of 0.81 +/- 0.4; see Angulo et al. 2025
    ordered = sort_by_FoM(table_ims)

    table_ims.loc[ordered].to_csv(str(txt_file.rpartition('.')[0])+'_tmplorder.txt', sep='\t', index=False)      # saves as table in new order















