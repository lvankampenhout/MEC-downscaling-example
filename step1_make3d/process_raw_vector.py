#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
   DESCRIPTION: 
      This script extracts MEC output from the CLM vector output and stores it as
      a 3-dimensional variable in a subdirectory called 'vector2gridded3d'. 

      In contrast to the previous version of this script, used in SMBMIP: 
         https://github.com/lvankampenhout/CESM_SMBmip2018
      no vertical interpolation is applied.

      The vertical interpolation will only happen after we regridded to the 
      target grid, and makes use of the actual MEC topography stored in variable TOPO_COL. 

   DATE: 
      May 2019 

   AUTHOR:
      Leo van Kampenhout
"""

import sys
import glob
import os, os.path

# Import libvector package from local directory tree
# git repo here: https://github.com/lvankampenhout/libvector/
sys.path.insert(0, "/glade/u/home/lvank/github/libvector/") # CHA: update path
from libvector import VectorMecVariable, vector2gridded3d 

casename = 'b.e21.BHIST.f09_g17.CMIP6-historical.003b' # CHA: update to SSP if needed

datadir  = os.path.join('/glade/work/lvank/CESM2', casename ) # CHA: update path
outdir   = os.path.join(datadir, 'vector2gridded3d') 

if not os.path.exists(outdir):
   os.makedirs(outdir)

stream_tag  = 'h1' # output stream identifier. Vector data is typically 'h1'.

print(casename)

varlist = []
varlist += 'QICE QRUNOFF QSNOMELT QICE_MELT QSNOFRZ QSOIL RAIN SNOW '.split()
varlist += 'U10 TSA TG FSDS FSR FSA FLDS FIRE FIRA FSH EFLX_LH_TOT FGR FSM RH2M'.split()
varlist += 'RAIN_FROM_ATM SNOW_FROM_ATM'.split()
varlist += 'TSOI_10CM',

# CHA: adapt this if you only need a subset of the time period
slices = '195001-196001', '196002-197001', '197002-198001', '198002-199001', '199002-200001'

for slic in slices:
   print(slic)

   for varname in varlist:
      #fname_vector = os.path.join(datadir, 'lnd', 'proc', 'tseries', 'month_1', casename + ".clm2." + stream_tag + "." + varname + "." + slic + ".nc")
      fname_vector = os.path.join(datadir, 'CLM_vector', casename + ".clm2." + stream_tag + "." + varname + "." + slic + ".nc")
      print(fname_vector)

      if (not os.path.exists(fname_vector)):
         raise FileNotFoundError(fname_vector)

      outfile = os.path.join(outdir, varname+'_'+slic+"_"+casename+'.nc')

      if (not os.path.exists(outfile)):
         vmv = VectorMecVariable(varname, fname_vector) 
         vector2gridded3d(vmv, outfile) 
         print('wrote %s' % outfile)

      else:
         print('file exists, skipping %s' % outfile)

