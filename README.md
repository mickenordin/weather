# weather
Some pythonscripts that get weather data from SMHI and calculates evapotranspiration.
Create a user to run scripts:
````
useradd -s /usr/sbin/nologin -r -M -d /opt/weather weather
````
Clone repo:
````
git clone https://github.com/mickenordin/weather.git /opt/weather
````
Chown:
````
chown -R weather:weather /opt/weather
````
Create mysql database:

````
mysql -e "CREATE DATABASE weather"
mysql -e "CREATE USER 'weather'@'localhost' IDENTIFIED BY 'password'"
mysql -e "GRANT ALL PRIVILEGES ON weather.* TO 'weather'@'localhost'"
mysql weather < weather.sql
````
Configure and run:
````
vim weather.ini
./getweather.py
./aggregateweather.py
````
