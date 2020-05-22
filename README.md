# weather
Some pythonscripts that get weather data from SMHI and calculates evapotranspiration.

Needs a mysql database:

````
mysql -e "CREATE DATABASE weather"
mysql weather < weather.sql
vim weather.ini
./getweather.py
./aggregateweather.py
````
