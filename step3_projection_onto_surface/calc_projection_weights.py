#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
interpolation of 3D gridded data to destination grid 
"""

import sys
import os, os.path
import numpy as np
import netCDF4
from netCDF4 import Dataset, default_fillvals
from scipy.interpolate import InterpolatedUnivariateSpline

# Output file
outfile = 'projection_weights.nc'

# Choose target elevation -- DIMENSIONS OBVIOUSLY NEED TO MATCH TARGET GRID! 
if (False):
   elev_file   = '/gpfs/p/work/lvank/SMBmip/MARv3.9-yearly-ERA-Interim-1980.nc' # contains target elevation
   elev_varname = 'SRF_GIMP'
   elev_lat = 'LAT'
   elev_lon = 'LON'

if (False): # ISMIP6-1km 
   elev_file = '/gpfs/fs1/work/lvank/SMBmip/1km-ISMIP6.nc'
   elev_varname = 'SRF'
   elev_lat = 'lat'
   elev_lon = 'lon'

if (False): # CISM 4km 
   elev_file = '/gpfs/fs1/work/lvank/SCRIP/cism_4km_scrip/cism_topography.nc' 
   elev_varname = 'topg'
   elev_lat = 'lat'
   elev_lon = 'lon'
 
if (False): # RACMO topo
   elev_file = "/glade/work/lvank/racmo/racmo23p2_GRN_monthly/elev.nc"
   elev_varname = "Elevation"
   elev_lat = 'lat'
   elev_lon = 'lon'

if (True): # 1 km grid 2700x1496 
   elev_file = "CHA: find this file here: aux/Icemask_Topo_Iceclasses_lon_lat_average_1km.nc"
   elev_varname = "Topography"
   elev_lat = 'LAT'
   elev_lon = 'LON'

with Dataset(elev_file,'r') as fid:
   target_srf = fid.variables[elev_varname][:].squeeze() # Two dimensional

   lat2d = fid.variables[elev_lat][:]
   lon2d = fid.variables[elev_lon][:]
   

# construct mask with invalid values, which will be used during output phase
topo_dst_masked = np.ma.masked_greater(target_srf, 4000.)  # removes all values of 9999
topo_dst_masked = np.ma.masked_less(topo_dst_masked, 0.) # removes negative values

# standard numpy array for calculating weights; invalid values are treated as if they 
# were at sea level (z=0) and will be masked later.
topo_dst = topo_dst_masked.filled(fill_value = 0)

#print(topo_dst.min())
#print(topo_dst.max())
#print(topo_dst.shape)
nlat, nlon = topo_dst.shape
print(topo_dst.shape)


fname_topo_mec = 'input/TOPO_COL_196002-197001_b.e21.BHIST.f09_g17.CMIP6-historical.003b.nc'
with Dataset(fname_topo_mec,'r') as fid:
   topo_mec = fid.variables['TOPO_COL'][0].squeeze() # Three dimensional, nLEV, nlat, nlon

print(topo_mec.shape)
nlev = len(topo_mec)


# -------------------
# determine interpolation weights
# -------------------
wgt = np.ma.zeros((nlev,nlat,nlon), dtype=np.float64)

# SPECIAL CASE: below lowest MEC topo
foo = np.where(topo_dst <= topo_mec[0], 1, 0)
wgt[0]   += 1 * foo

# SPECIAL CASE: above highest MEC topo
foo = np.where(topo_dst > topo_mec[nlev-1], 1, 0)
wgt[nlev-1]   += 1 * foo


for ilev in range(0,nlev-1):
    print(ilev)
    if (ilev < nlev-1):
        foo = np.where( np.logical_and(topo_mec[ilev] <= topo_dst, topo_mec[ilev+1] > topo_dst), 1, 0)

    # compute weights for each level (linear interpolation)
    dH = topo_mec[ilev+1] - topo_mec[ilev]
    wgt_A = (topo_mec[ilev+1] - topo_dst) / dH
    wgt_B = (topo_dst - topo_mec[ilev]) / dH

    wgt[ilev]   += wgt_A * foo
    wgt[ilev+1] += wgt_B * foo   

wgt_sum = wgt.sum(axis=0)

assert np.allclose(wgt_sum, 1), 'Interpolation weights do not add to 1.0!'
#assert np.allclose(np.sum(wgt,axis=2), 1.0, rtol=1e-05, atol=1e-08)

# Set mask to account for invalid values
wgt.mask = False
for ilev in range(nlev):
   #wgt.mask[:,:,ilev] = topo_dst_masked.mask 
   wgt.mask[ilev] = topo_mec[ilev].mask


# reorder dimensions to (nlev, nlat, nlon)
#wgt2 = wgt.transpose((2,0,1)) 
wgt2 = wgt


# -------------------
# write output file
# -------------------
print("INFO: writing %s" % outfile)
ncfile = Dataset(outfile, 'w', format='NETCDF4')
ncfile.title = 'Linear interpolation weights for projecting levelled CLM output onto target elevation '
ncfile.elev_file = elev_file

ncfile.institute = "NCAR / Utrecht University"
ncfile.contact = "L.vankampenhout@uu.nl"

ncfile.netcdf = netCDF4.__netcdf4libversion__

# Create dimensions
ncfile.createDimension('y', nlat)
ncfile.createDimension('x', nlon)
ncfile.createDimension('lev',nlev)

# Define the coordinate var
lons   = ncfile.createVariable('lon', 'f8', ('y','x'))
lats   = ncfile.createVariable('lat', 'f8', ('y','x'))
levs   = ncfile.createVariable('lev', 'i4', ('lev',))

# Assign units attributes to coordinate var data
lons.standard_name = "longitude" ;
lons.long_name = "longitude" ;
lons.units   = "degrees_east"
lons.axis = "Y"

lats.standard_name = "latitude" ;
lats.long_name = "latitude" ;
lats.units   = "degrees_north"
lats.axis = "X"

levs.units   = "MEC level number"

# Write data to coordinate var
lons[:]    = lon2d[:]
lats[:]    = lat2d[:]
levs[:]    = range(0,nlev)

var            = ncfile.createVariable('weights','f4',('lev','y','x',), fill_value=default_fillvals['f4'])
var.units      = "-"
var.long_name  = "interpolation weights"
var[:] = wgt2
ncfile.close()
print("INFO: done")


