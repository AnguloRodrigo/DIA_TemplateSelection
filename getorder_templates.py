#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 13:11:06 2022

@author: rangulo
"""

import argparse,glob,re,sys,os
import matplotlib.pyplot as plt
import numpy as np
from pdastro import *
from scipy.optimize import minimize


def dist2line(fwhm, depth, slope, ref_p):
    #yline = m*x                      # line through origin
    # m = np.tan(angle*(np.pi/180.))    # slope given angle
    m = slope
    fw_ref, m5_ref = ref_p            # reference point of FWHM/Depth
        
    x_p = 10*np.log10(fw_ref/fwhm)       # scaled logr
    y_p = m5_ref - depth                 # diff
    
    dist = (y_p - m*x_p)/np.sqrt(1+m**2)    # distance from point to line
    
    return(dist)


class templorder_class(pdastrostatsclass):
    def __init__(self):
        pdastrostatsclass.__init__(self)
        self.verbose=0

    def define_options(self,parser=None,usage=None,conflict_handler='resolve'):
        if parser is None:
            parser = argparse.ArgumentParser(usage=usage,conflict_handler=conflict_handler)

        parser.add_argument('input_files', nargs='+',  help='list of fits file(pattern)s for which the fits keys should be obtained. "input_dir" is used if not None (default=%(default)s)')
        parser.add_argument('--input_dir', default=None, help='Directory in which the fits images are located. (default=%(default)s)')
        parser.add_argument('-v','--verbose', default=0, action='count')

        return(parser)
    
    def get_files(self,filepatterns,directory=None):
        filenames=[]
        for filepattern in filepatterns:
            if directory is not None:
                filepattern=os.path.join(directory,filepattern)
            if self.verbose>2:
                print(f'Looking for filepattern {filepattern}')
            filenames.extend(glob.glob(filepattern))
        
        for i in range(len(filenames)):
            filenames[i] = os.path.abspath(filenames[i])
        if self.verbose:
            print(f'Found {len(filenames)} files matching filepatterns {filepatterns}')
        return(filenames)
    
    
    def calc_FOM(self, slope, median_ref=True):
        self.t['FOM_dist'] = self.t['FWHM']
        
        ref_fw = self.t['FWHM'].median()
        ref_m5 = self.t['M5SIGMA'].median()
        
        for i in range(len(self.t)):
            fw_i = self.t['FWHM'][i]
            m5_i = self.t['M5SIGMA'][i]
            
            if m5_i is not None:
                dist = dist2line(fw_i,m5_i,slope=slope,ref_p=[ref_fw,ref_m5])
                self.t.loc[i,'FOM_dist'] = dist
            else:
                self.t.loc[i,'FOM_dist'] = 1000      # big number to put at bottom of list

        return('Calculated FOMs -- Completed')


    def sort_by_FOM(self):
        order_ind = []
        phot_codes = np.unique(self.t['PHOTCODE'])

        for i in phot_codes:
            phcd_i = self.ix_equal('PHOTCODE', i)
            order_i = self.ix_sort_by_cols('FOM_dist', indices=phcd_i)
            order_ind += list(order_i)

        return(order_ind)
    
    
        
if __name__ == '__main__':
    templ_order = templorder_class()
    parser = templ_order.define_options()
    args = parser.parse_args()
    templ_order.verbose=args.verbose
    
    filenames = templ_order.get_files(args.input_files, directory=args.input_dir)
    
    templ_order.t['dcmpfile']=filenames
    
    templ_order.fitsheader2table('dcmpfile',requiredfitskeys=['PHOTCODE','FWHM','M5SIGMA','EXPTIME','SKYADU','SKYSIG'], raiseError=False)
        
    templ_order.calc_FOM(0.81)           # range: 0.81 +/- 0.3
    
    order_inds = templ_order.sort_by_FOM()
    
    templ_order.default_formatters['FWHM']='{:.2f}'.format
    templ_order.default_formatters['M5SIGMA']='{:.2f}'.format
    templ_order.default_formatters['SKYADU']='{:.1f}'.format
    templ_order.default_formatters['SKYSIG']='{:.1f}'.format
    templ_order.default_formatters['FOM_dist']='{:.2f}'.format
    
    field_nm = str(templ_order.t['dcmpfile'][0]).rpartition('/')[-1]
    field_nm = field_nm.partition('.')[0]
    
    templ_order.write(filename=field_nm+'_tmpl_order.txt', indices=order_inds)
