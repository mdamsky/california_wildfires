from flask import Flask, render_template, request
from wildfirepredictor import predictor, map_gen
from explore import create_map
import pgeocode
import folium

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
	if request.method == 'GET':
		cal = folium.Map(location=[37.166110, -119.449440], zoom_start=6)
		cal.save('templates/map.html')
		return render_template('index.html')

	else: 
		loc = request.form['loc']
		season = request.form['month'].lower()

		date_dict = {"january": "2020-01-01", "february": "2020-02-01", "march": "2020-03-01", "april": "2020-04-01", "may": "2020-05-01", "june": "2020-06-01",
		"july": "2020-07-01", "august": "2020-08-01", "september": "2020-09-01", "october": "2020-10-01", "november": "2020-11-01", "december": "2020-12-01"}
		nomi = pgeocode.Nominatim('us')
		zip_search = nomi.query_postal_code(loc)

		fire_date = date_dict[season]
		fire_lat = zip_search['latitude']
		fire_lon = zip_search['longitude']
		fire_county = zip_search['county_name']
		
		fire_size = predictor(fire_date, fire_lat, fire_lon, fire_county)
		fire_map = map_gen(fire_date, fire_lat, fire_lon, fire_county, fire_size)
		fire_map.save('templates/map.html')

		return render_template('index.html')

@app.route('/final')
def final():
	return render_template('map.html')

@app.route('/explore')
def explore():
	explore_map = create_map()
	explore_map.save('templates/explore.html')
	return render_template('explore.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)
