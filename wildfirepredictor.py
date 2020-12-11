# -*- coding: utf-8 -*-
"""WildfirePredictor.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NAy4j-dHs8fh1utMJZ33bPYHSa3jqu7L
"""

# Commented out IPython magic to ensure Python compatibility.
import time
start = time.perf_counter()

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

path2 = r"cf.csv"
CF = pd.read_csv(path2)

path = r"final_weather.csv"
final_weather = pd.read_csv(path)
final_weather['Date'] = pd.to_datetime(final_weather['Date'])

def closest_station(fire_lat, fire_lon, stations):
    stations['Distance'] = ((stations['Latitude'] - fire_lat)**2 + (stations['Longitude'] - fire_lon)**2)**.5
    stations_sort = stations.sort_values('Distance', ascending=True)
    return int(stations_sort['Station Id'].iloc[0])

def days_ago(date, ago):
    split_date = date.split('-')
    final_year = split_date[0]
    year =  [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if final_year in ['2012', '2016', '2020']:
        year[2] = 29
    day = sum(year[:int(split_date[1])]) + int(split_date[2])
    day_ago = day - ago
    if day_ago < 0:
        final_year = str(int(final_year) - 1)
        if year[2] == 29:
            year[2] = 28
        day_ago = sum(year) + day_ago
    for i in range(len(year)):
        if day_ago > year[i+1]:
            day_ago = day_ago - year[i+1]
            continue
        else:
            return final_year + '-' + str(i+1) + '-' + str(day_ago)

def find_weather_data(weather, fire, days):
    fire_started = fire['Started']
    days_before = days_ago(fire_started, days)
    dated_weather = weather[(weather['Date'] <= fire_started) & (final_weather['Date'] > days_before)]
    stations = dated_weather[['Station Id', 'Latitude', 'Longitude']]
    weather_station = closest_station(fire['Latitude'], fire['Longitude'], stations)
    return dated_weather[dated_weather['Station Id'] == weather_station]

def fires_last_year(fire):
    start = fire['Started']
    last_year = CF[(CF['Started'] < start) & (CF['Started'] >= days_ago(start, 365))]
    last_year = last_year[last_year['Counties'] == fire['Counties']]
    return len(last_year)

path3 = r"features.csv"
features_df = pd.read_csv(path3)

from sklearn.model_selection import train_test_split
X = features_df[['Latitude', 'Longitude', 'precip', 'max_temp', 'min_hum', 'avg_wind', 'fires_last_year']]
y = features_df['AcresBurned']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

import sklearn.svm
from sklearn.svm import SVR
svrreg = SVR(C=1.0).fit(X_train, y_train)

def get_features_dict(fire, days_ago):
    weather_data = find_weather_data(final_weather, fire, 60)
    weather_data['Precipitation'] = np.where(weather_data['Precipitation'] == '--', 0, weather_data['Precipitation'])
    weather_data['Maximum Air Temperature '] = np.where(weather_data['Maximum Air Temperature '] == '--', 0, weather_data['Maximum Air Temperature '])
    weather_data['Minimum Relative Humidity '] = np.where(weather_data['Minimum Relative Humidity '] == '--', 0, weather_data['Minimum Relative Humidity '])
    weather_data['Average Wind Speed '] = np.where(weather_data['Average Wind Speed '] == '--', 0, weather_data['Average Wind Speed '])
    total_precip = 0
    for i in range(len(weather_data)):
        total_precip += (((i+1)/len(weather_data)) * float(weather_data['Precipitation'].iloc[i]))
    total_max_temp = 0
    for i in range(len(weather_data)):
        total_max_temp += (((i+1)/len(weather_data)) * float(weather_data['Maximum Air Temperature '].iloc[i]))
    total_min_hum = 0
    for i in range(len(weather_data)):
        total_min_hum += (((i+1)/len(weather_data)) * float(weather_data['Minimum Relative Humidity '].iloc[i]))
    total_avg_wind = 0
    for i in range(len(weather_data)):
        total_avg_wind += (((i+1)/len(weather_data)) * float(weather_data['Average Wind Speed '].iloc[i]))
    total_fires = fires_last_year(fire)
    feature_dict = {'Started':fire['Started'],'Latitude':fire['Latitude'],'Longitude':fire['Longitude'],'precip':total_precip,'max_temp':total_max_temp,'min_hum':total_min_hum,'avg_wind':total_avg_wind,'fires_last_year':total_fires}
    return feature_dict

def combine_dicts(dicts):
    n = len(dicts)
    final = {}
    final['Started'] = dicts[0]['Started']
    final['Latitude'] = dicts[0]['Latitude']
    final['Longitude'] = dicts[0]['Longitude']
    final['precip'] = np.mean([dicts[i]['precip'] for i in range(n)])
    final['max_temp'] = np.mean([dicts[i]['max_temp'] for i in range(n)])
    final['min_hum'] = np.mean([dicts[i]['min_hum'] for i in range(n)])
    final['avg_wind'] = np.mean([dicts[i]['avg_wind'] for i in range(n)])
    final['fires_last_year'] = np.mean([dicts[i]['fires_last_year'] for i in range(n)])
    return final

def predictor(fire_date, fire_lat, fire_lon, fire_county, model):
    if int(fire_date[:4]) > 2019:
        feature_dicts = []
        for year in ['2015', '2016', '2017', '2018', '2019']:
            date = year + fire_date[4:]
            fire = pd.Series({'Started':date, 'Latitude':fire_lat, 'Longitude':fire_lon, 'Counties':fire_county})
            feature_dicts.append(get_features_dict(fire, 60))
        feature_dict = combine_dicts(feature_dicts)
    else:
        fire = pd.Series({'Started':fire_date, 'Latitude':fire_lat, 'Longitude':fire_lon, 'Counties': fire_county})
        feature_dict = get_features_dict(fire, 60)
    fire_df = pd.DataFrame(feature_dict, index=[0]).drop('Started', axis=1)
    return model.predict(fire_df)[0]
end = time.perf_counter()
print('total time: ' + str(end-start))

import pgeocode
nomi = pgeocode.Nominatim('us')
while True:
    print('Where will the fire be?')
    print('Date: (YYYY-MM-DD)')
    date = input()
    print('Zip Code: ')
    zip = input()
    zip_search = nomi.query_postal_code(zip)
    latitude = zip_search['latitude']
    longitude = zip_search['longitude']
    county = zip_search['county_name']
    model = svrreg
    size = np.round(predictor(date, latitude, longitude, county, model), 3)
    print('We predict the fire in this location to grow to ' + str(size) + ' acres.')
    print('Predict another fire? (y/n)')
    ans = input()
    if ans == 'n':
        break
