#!/usr/bin/env python3

import argparse
from netCDF4 import Dataset
import fiona
import numpy as np
import rasterio
from rasterio.features import rasterize
import os
import sys
sys.path.append(f'{os.path.dirname(os.path.realpath(__file__))}')
from territorial_sea import *

parser = argparse.ArgumentParser(description='Crop China region from data using shapefile.')
parser.add_argument('-f', '--data', help='NetCDF data with lon and lat coordinates will be changed inplace', required=True)
parser.add_argument('-s', '--shapefile', help='China shapefile used as mask', default=f'{os.path.dirname(os.path.realpath(__file__))}/../shapefiles/china_without_islands.shp')
parser.add_argument(      '--sea', help='Also include China territorial sea', action='store_true')
args = parser.parse_args()

if not os.path.isfile(args.data):
	print(f'[Error]: File {args.data} does not exist!')
	exit(1)

def create_mask_array(lon, lat, shapefile_path, include_sea=False):
	shapefile = fiona.open(shapefile_path)
	bbox = list(shapefile.bounds)

	shapes = [(feature['geometry'], 1) for feature in shapefile]

	if include_sea:
		shapes.append((get_china_territorial_sea_polygon(), 1))
		bbox[0] = min(bbox[0], shapes[-1][0].bounds[0])
		bbox[1] = min(bbox[1], shapes[-1][0].bounds[1])
		bbox[2] = max(bbox[2], shapes[-1][0].bounds[2])
		bbox[3] = max(bbox[3], shapes[-1][0].bounds[3])

	min_raster_lon = bbox[0]
	min_raster_lat = bbox[1]
	max_raster_lon = bbox[2]
	max_raster_lat = bbox[3]
	num_raster_lon = 1000
	num_raster_lat = 1000
	raster_dlon = (max_raster_lon - min_raster_lon) / num_raster_lon
	raster_dlat = (max_raster_lat - min_raster_lat) / num_raster_lat
	raster_lon = np.linspace(min_raster_lon, max_raster_lat, num_raster_lon)
	raster_lat = np.linspace(min_raster_lat, max_raster_lat, num_raster_lat)
	raster = np.zeros((num_raster_lat, num_raster_lon))

	transform = rasterio.transform.from_bounds(*bbox, num_raster_lat, num_raster_lon)

	rasterize(shapes=shapes, out=raster, transform=transform, all_touched=True)
	raster = raster[::-1,:]

	mask = np.zeros((len(lat), len(lon)))
	for j in range(len(lat)):
		rj = int((lat[j] - min_raster_lat) / raster_dlat)
		for i in range(len(lon)):
			ri = int((lon[i] - min_raster_lon) / raster_dlon)
			if 0 <= ri < num_raster_lon and 0 <= rj < num_raster_lat:
				if raster[rj,ri] == 1:
					mask[j,i] = 1

	shapefile.close()

	return mask

f = Dataset(args.data, 'a')
if 'lon' in f.variables:
	lon_name = 'lon'
elif 'longitude' in f.variables:
	lon_name = 'longitude'
lon = f.variables[lon_name][:]
if 'lat' in f.variables:
	lat_name = 'lat'
elif 'latitude' in f.variables:
	lat_name = 'latitude'
lat = f.variables[lat_name][:]

print(f'[Notice]: Create mask array ...')
mask = create_mask_array(lon, lat, args.shapefile, args.sea)

print(f'[Notice]: Crop file {args.data} ...')
for name, var in f.variables.items():
	if lat_name in var.dimensions and lon_name in var.dimensions:
		if '_FillValue' in var.ncattrs():
			missing_value = var._FillValue
		elif 'missing_value' in var.ncattrs():
			missing_value = var.missing_value
		else:
			missing_value = 9.96921e+36
		var[:] = np.where(mask == 0, missing_value, var[:])

f.close()
