#!/usr/bin/env python3

import argparse
from pyproj import CRS, Transformer
from netCDF4 import Dataset
import numpy as np
import numpy.ma as ma
from scipy.interpolate import interp2d
import os

parser = argparse.ArgumentParser(description='Remap data from lat-lon grids to Web Mercator grids for visualization.')
parser.add_argument('-f', '--data', help='NetCDF data with lon and lat coordinates will be changed', required=True)
parser.add_argument('-o', '--output', help='Output remapped NetCDF data on Web Mercator grids')
args = parser.parse_args()

if not os.path.isfile(args.data):
	print(f'[Error]: File {args.data} does not exist!')
	exit(1)

f1 = Dataset(args.data, 'r')
lon1 = f1.variables['lon'][:]
lat1 = f1.variables['lat'][:]

crs1 = CRS.from_proj4('+proj=latlon')
crs2 = CRS.from_epsg(3857)

t12 = Transformer.from_crs(crs1, crs2)
t21 = Transformer.from_crs(crs2, crs1)

min_x2, min_y2 = t12.transform(lon1[ 0], lat1[ 0])
max_x2, max_y2 = t12.transform(lon1[-1], lat1[-1])

x2 = np.linspace(min_x2, max_x2, len(lon1))
y2 = np.linspace(min_y2, max_y2, len(lat1))

lon2 = [t21.transform(x2[i], y2[0])[0] for i in range(len(x2))]
lat2 = [t21.transform(x2[0], y2[j])[1] for j in range(len(y2))]

if not args.output:
	args.output = os.path.join(os.path.dirname(args.data), os.path.basename(args.data).replace('.nc', '') + '_web.nc')
print(f'[Notice]: Create file {args.output} ...')
f2 = Dataset(args.output, 'w', format='NETCDF3_CLASSIC')
f2.createDimension('lon', len(lon2))
f2.createDimension('lat', len(lat2))
f2.createVariable('lon', 'f4', ('lon'))
f2.createVariable('lat', 'f4', ('lat'))
f2.variables['lon'][:] = lon2
f2.variables['lat'][:] = lat2

for name, var1 in f1.variables.items():
	if 'lat' in var1.dimensions and 'lon' in var1.dimensions:
		print(f'[Notice]: Remap variable {name} ...')
		missing_value = var1.missing_value
		interp = interp2d(lon1, lat1, var1[:], kind='linear', fill_value=missing_value)
		var2 = ma.masked_outside(interp(lon2, lat2), -100, 100)
		f2.createVariable(name, 'f4', ('lat', 'lon'), fill_value=missing_value)
		f2.variables[name].units = var1.units
		f2.variables[name].long_name = var1.long_name
		f2.variables[name][:] = var2

f1.close()
f2.close()
