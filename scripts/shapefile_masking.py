import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader as ShapeReader
from cartopy.feature import ShapelyFeature
from shapely.ops import cascaded_union
from shapely.geometry import Polygon, MultiPolygon

def mask_outside_shapes(shapefile_path, ax):
	extent = ax.get_extent()
	frame = Polygon([
		(extent[0], extent[2]),
		(extent[1], extent[2]),
		(extent[1], extent[3]),
		(extent[0], extent[3]),
		(extent[0], extent[2])
	])
	
	shapes = cascaded_union(list(
		ShapeReader(shapefile_path).geometries()
	))

	mask = ShapelyFeature(
		MultiPolygon([frame.difference(shapes)]),
		ax.projection,
		edgecolor='none',
		facecolor='white'
	)

	ax.add_feature(mask)
