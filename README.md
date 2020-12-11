# California Wildfire Predictor

To predict how large a fire will become, we pulled in data from multiple sources. First, we had previous fire data from CalFire, with information on the date, location, and ultimate size of every fire from 2014 to 2019. Second, we brought in weather data from over 150 weather stations located across California, this data had daily weather data including temperature, humidity, precipitation, and wind speed, all of which we believe have an effect on how big the fire will grow. And third, we brought in location data for the weather stations, so we could find which station was closest to each fire.

From this data we created seven input features for each fire, the latitude and longitude, precipitation, maximum temperature, minimum humidity, average wind speed, and fires in that county over the last year. We calculated these features for all of the fire data in our training and test sets, and for each input we also calculate these averages across all years of data. Finally, the model we have chosen is a Support Vector Regression model, which works by finding a hyperplane of best fit by minimizing the absolute error of the model and finetuning its own internal hyperparameters.

After passing a date and a zip code into our predictor, it calculates an estimate for the size of a wildfire, in acres, if it were to start at that location, on that day.
