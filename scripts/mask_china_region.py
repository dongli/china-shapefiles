#!/usr/bin/env python3

import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader as ShapeReader
from cartopy.feature import ShapelyFeature
import matplotlib.pyplot as plt
from shapely.ops import cascaded_union
from shapely.geometry import Polygon, MultiPolygon
import os
import sys
sys.path.append(f'{os.path.dirname(os.path.realpath(__file__))}')
from territorial_sea import *

def mask_china_region(ax, facecolor='white', include_sea=False):
	china_shapefile_path = f'{os.path.dirname(os.path.realpath(__file__))}/../shapefiles/china_without_islands.shp'

	extent = ax.get_extent()
	frame = Polygon([
		(extent[0], extent[2]),
		(extent[1], extent[2]),
		(extent[1], extent[3]),
		(extent[0], extent[3]),
		(extent[0], extent[2])
	])
	
	shapes = cascaded_union(list(
		ShapeReader(china_shapefile_path).geometries()
	))

	if include_sea:
		for polygon in shapes:
			if polygon.area > 900:
				china_mainland = polygon
				break
		mask_polygon = frame.difference(china_mainland.union(get_china_territorial_sea_polygon()))
		if type(mask_polygon) != MultiPolygon:
			mask_polygon = MultiPolygon([mask_polygon])
	else:
		mask_polygon = MultiPolygon([frame.difference(shapes)])

	mask = ShapelyFeature(
		mask_polygon,
		ccrs.PlateCarree(),
		edgecolor='none',
		facecolor=facecolor
	)
	ax.add_feature(mask)

if __name__ == '__main__':
	proj = ccrs.PlateCarree()
	ax = plt.axes(projection=proj)
	ax.set_extent((70, 140, 10, 60), crs=proj)
	mask_china_region(ax, facecolor='red', include_sea=False)
	plt.show()
	plt.close()
