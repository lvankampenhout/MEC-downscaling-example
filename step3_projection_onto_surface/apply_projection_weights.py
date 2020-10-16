#!/gpfs/u/home/lvank/miniconda3/bin/python3
###!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
projection of 3D gridded data to 2D using vertical interpolation weights
"""

import sys
import glob
import os, os.path
#import subprocess 
import xarray as xr
import numpy as np

#casenames = ('c2b8_UNI_fdm.004', 'c2b8_VRGRN_55.003', 'c2b8_VRGRN_28.003') 
#indirs = ('input_uni', 'input_55km', 'input_28km')
#outdirs = ('output_uni', 'output_55km', 'output_28km')

casenames = ("b.e21.BHIST.f09_g17.CMIP6-historical.003b", )
indirs = ('input', )
outdirs = ('output', )

# weights file
wgtfile = 'projection_weights.nc'

######
# END OF USER SETTINGS
######

ds_wgt = xr.open_dataset(wgtfile)
wgt = ds_wgt['weights'].values

#for varname in varlist:
for (casename, indir_var, outdir_var) in zip(casenames, indirs, outdirs):

#   indir_var = os.path.join(outdir, casename, 'dstGrid3d', varname)
#   outdir_var = os.path.join(outdir, casename, 'dstGrid2d', varname)
#   if not os.path.exists(outdir_var):
#       os.makedirs(outdir_var)

   files = glob.glob(os.path.join(indir_var, '*.nc')) # all CLM vector data
   files = sorted(files)

   print('INFO: processing directory %s' % indir_var)
   print('INFO: number of files: %d' % len(files))

   for infile in files:
      ds = xr.open_dataset(infile)

      # OPTION A
      # guess variable name from file contents
      varname = list(ds.data_vars)[-1]

      if (varname == 'TOPO_COL'):
         # do not downscale TOPO_COL itself, not really makes sense? 
         print('Skipping TOPO_COL file:',infile)
         ds.close()
         continue

      # OPTION B
      # guess variable name from filename
      basename = infile.split('/')[-1] # filename without path
      #varname = basename.split('_' + casename)[0]
      #varname = basename.split('_' + casename)[0]

      print('INFO: varname = %s' % varname)
      outfile = os.path.join(outdir_var, basename)

      if (os.path.exists(outfile)): 
         print("INFO: file exists, skipping: "+outfile)
         continue

      print(ds[varname].shape)
      print(wgt.shape)
      ds[varname].values *=  wgt

      da_var = ds[varname].sum(dim='lev', skipna=False, keep_attrs=True)
      da_var.encoding = {'dtype': 'float32', '_FillValue': 9.96921e+36}

      ds.drop(varname)
      ds[varname] = da_var

      #ds = ds.squeeze(drop=True) # drop time dimension

      #print(ds[varname])
      #ds[varname].encoding = {'dtype': 'float32', '_FillValue': 9.96921e+36}
      ds.to_netcdf(outfile,'w') #, encoding={'_FillValue': 9.96921e36})

      ds.close()
      print("INFO: written %s" % outfile)
