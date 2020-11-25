import numpy as np
import pandas as pd
import folium

cleaned_CF = pd.read_csv('cleaned_CF.csv')

def create_map(): 
	zoom_factor = 6
	radius_scaling = 1 #scale of fire bubble size 

	base_map = folium.Map(location=[36,-120], zoom_start=zoom_factor, tiles = None)
	folium.TileLayer('Open Street Map', control=False).add_to(base_map)
	for year, year_grp in cleaned_CF.groupby('ArchiveYear'):
	    feature_group = folium.FeatureGroup(year)
	    for row in year_grp.itertuples():
	      folium.CircleMarker(
	        location=[row.Latitude, row.Longitude],
	        radius= (row.Fixed0AcresBurned)*0.00015,
	        color='red',
	        popup='CanonicalUrl:' + row.CanonicalUrl + '<br>' + 'Year:' + str(int(row.ArchiveYear)) + '<br>' + 'Acres Burned:' + str(row.AcresBurned),
	        fill=True,
	        fill_color='red' 
	        ).add_to(feature_group)
	    feature_group.add_to(base_map)

	folium.LayerControl().add_to(base_map)
	
	return base_map
