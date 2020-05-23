# weather
Some pythonscripts that get weather data from SMHI and calculates evapotranspiration.

Needs a mysql database:

````
mysql -e "CREATE DATABASE weather"
mysql -e "CREATE USER 'weather'@'localhost' IDENTIFIED BY 'password'"
mysql -e "GRANT ALL PRIVILEGES ON weather.* TO 'weather'@'localhost'"
mysql weather < weather.sql
vim weather.ini
./getweather.py
./aggregateweather.py
````
