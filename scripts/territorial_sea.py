#!/usr/bin/env python3

import os
import matplotlib.pyplot as plt
import cartopy.crs as crs
import fiona
from shapely.geometry import Polygon, LineString

# China territorial sea baseline points
baseline_points = {
	'lon': [
		122.705, 122.705, 122.57 , 122.545, 122.518, 122.263, 120.885, 119.903, 121.347,
		121.64 , 122.243, 123.157, 123.162, 122.945, 122.275, 121.917, 121.912, 121.13 ,
		120.507, 120.405, 119.938, 119.478, 118.237, 117.688, 117.248, 117.232, 116.495,
		115.125, 113.967, 112.798, 112.358, 111.273, 111.213, 110.493, 110.485, 110.14 ,
		110.05 , 109.702, 109.697, 109.573, 109.127, 108.952, 108.688, 108.685, 108.677,
		108.675, 108.622, 108.6  , 108.643
	],
	'lat': [
		 37.4  ,  37.395,  36.963,  36.918,  36.895,  36.747,  35.893,  35.003,  33.363,
		 33.015,  31.422,  30.735,  30.725,  30.168,  28.888,  28.398,  28.392,  27.465,
		 26.377,  26.157,  25.43 ,  24.977,  24.162,  23.532,  23.215,  23.205,  22.935,
		 22.315,  21.808,  21.568,  21.462,  19.975,  19.883,  18.662,  18.657,  18.435,
		 18.383,  18.183,  18.183,  18.158,  18.243,  18.322,  18.503,  18.507,  18.517,
		 18.518,  18.842,  19.193,  19.352
	]
}

def get_china_territorial_sea_polygon():
	# Add some points to include the Bohai Sea.
	baseline_points['lon'].insert(0, 123.374)
	baseline_points['lon'].insert(0, 120.947)
	baseline_points['lon'].insert(0, 117.533)
	baseline_points['lon'].insert(0, 115.511)
	baseline_points['lat'].insert(0,  40.542)
	baseline_points['lat'].insert(0,  42.020)
	baseline_points['lat'].insert(0,  41.160)
	baseline_points['lat'].insert(0,  39.330)
	
	polygon = Polygon(zip(baseline_points['lon'], baseline_points['lat'])).buffer(1)

	# Add Taiwan province.
	with fiona.open(f'{os.path.dirname(os.path.realpath(__file__))}/../shapefiles/china.shp', 'r') as f:
		for feature in f:
			if 'Taiwan' in feature['properties']['FENAME'] and feature['properties']['AREA'] > 3:
				taiwan = Polygon(feature['geometry']['coordinates'][0])
				break
	polygon = taiwan.buffer(1).union(polygon)

	return polygon

if __name__ == '__main__':
	def plot(polygon):
		proj = crs.PlateCarree()
		ax = plt.axes(projection=proj)
		ax.plot(baseline_points['lon'], baseline_points['lat'], transform=proj, c='r')
		lon = [p[0] for p in list(polygon.exterior.coords)]
		lat = [p[1] for p in list(polygon.exterior.coords)]
		ax.plot(lon, lat, transform=proj, c='b')
		ax.set_extent((100, 128, 15, 45), crs=proj)
		ax.stock_img()
		ax.coastlines()
		plt.show()
		plt.close()

	plot(get_china_territorial_sea_polygon())
