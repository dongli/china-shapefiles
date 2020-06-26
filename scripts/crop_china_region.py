#!/usr/bin/env python3

import argparse
from netCDF4 import Dataset
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
import os

parser = argparse.ArgumentParser(description='Crop China region from data using shapefile.')
parser.add_argument('-f', '--data', help='NetCDF data with lon and lat coordinates will be changed inplace', required=True)
parser.add_argument('-s', '--shapefile', help='China shapefile used as mask', default=f'{os.path.dirname(os.path.realpath(__file__))}/../shapefiles/china_without_islands.shp')
args = parser.parse_args()

if not os.path.isfile(args.data):
	print(f'[Error]: File {args.data} does not exist!')
	exit(1)

def create_mask_array(lon, lat, shapefile_path):
	df = gpd.read_file(shapefile_path)

	shapes = [(polygon, 1) for polygon in df['geometry']]

	min_raster_lon = df['geometry'].total_bounds[0]
	min_raster_lat = df['geometry'].total_bounds[1]
	max_raster_lon = df['geometry'].total_bounds[2]
	max_raster_lat = df['geometry'].total_bounds[3]
	num_raster_lon = 1000
	num_raster_lat = 1000
	raster_dlon = (max_raster_lon - min_raster_lon) / num_raster_lon
	raster_dlat = (max_raster_lat - min_raster_lat) / num_raster_lat
	raster_lon = np.linspace(min_raster_lon, max_raster_lat, num_raster_lon)
	raster_lat = np.linspace(min_raster_lat, max_raster_lat, num_raster_lat)
	raster = np.zeros((num_raster_lat, num_raster_lon))

	transform = rasterio.transform.from_bounds(*df['geometry'].total_bounds, num_raster_lat, num_raster_lon)

	rasterize(shapes=shapes, out=raster, transform=transform, all_touched=True)
	raster = raster[::-1,:]

	mask = np.zeros((len(lat), len(lon)))
	for j in range(len(lat)):
		rj = int((lat[j] - min_raster_lat) / raster_dlat) - 1
		for i in range(len(lon)):
			ri = int((lon[i] - min_raster_lon) / raster_dlon)
			if 0 <= ri < num_raster_lon and 0 <= rj < num_raster_lat:
				if raster[rj,ri] == 1:
					mask[j,i] = 1

	return mask

f = Dataset(args.data, 'a')
lon = f.variables['lon'][:]
lat = f.variables['lat'][:]

print(f'[Notice]: Create mask array ...')
mask = create_mask_array(lon, lat, args.shapefile)

print(f'[Notice]: Crop file {args.data} ...')
for name, var in f.variables.items():
	if 'lat' in var.dimensions and 'lon' in var.dimensions:
		var[:] = np.where(mask == 0, var._FillValue, var[:])

f.close()
