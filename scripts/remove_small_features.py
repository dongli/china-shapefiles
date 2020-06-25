#!/usr/bin/env python3

import argparse
import fiona
from shapely.geometry import Polygon
from collections import OrderedDict
import argparse
from pprint import pprint

parser = argparse.ArgumentParser(description='Remove features with small area.')
parser.add_argument('-i', '--input', help='Input shapefile', required=True)
parser.add_argument('-o', '--output', help='Output shapefile', required=True)
parser.add_argument('-a', '--min-area', dest='min_area', help='Minimum area to keep', required=True, type=float)
args = parser.parse_args()

with fiona.open(args.input, 'r') as f:
	filtered_features = []
	for feature in f:
		if feature['geometry']['type'] == 'MultiPolygon':
			for lines in feature['geometry']['coordinates']:
				for line in lines:
					p = Polygon(line)
					if p.area >= args.min_area:
						filtered_features.append({
							'type': 'Feature',
							'geometry': {
								'type': 'Polygon',
								'coordinates': [line[::-1]]
							},
							'properties': {
								'area': p.area
							}
						})
		elif feature['geometry']['type'] == 'Polygon':
			p = Polygon(feature['geometry']['coordinates'])
			if p.area >= args.min_area:
				filtered_features.append({
					'type': 'Feature',
					'geometry': {
						'type': 'Polygon',
						'coordinates': [line]
					},
					'properties': {
						'area': p.area
					}
				})

schema = {
	'geometry': 'Polygon',
	'properties': OrderedDict([
		('area', 'float')
	])
}
with fiona.open(args.output, 'w', driver='ESRI Shapefile', schema=schema) as f:
	for feature in filtered_features:
		f.write(feature)
