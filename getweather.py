#!/usr/bin/python3

from datetime import datetime
import argparse
import configparser
import mysql.connector 
import requests
import sys

def usage():
    print(  "Usage: " + __file__ + "[--config path_to_file.ini] [--station smhi_station_number] [--period latest-hour|latest-day|latest-months] [--db database] [--host dbhost] [--user dbuser] [--password dbpassword]\n"
            "Default configfile is weather.ini, any parameter can be overwritten on the command line")
parser = argparse.ArgumentParser()
parser.add_argument('--config')
parser.add_argument('--station')
parser.add_argument('--period')
parser.add_argument('--db')
parser.add_argument('--host')
parser.add_argument('--user')
parser.add_argument('--password')
args = parser.parse_args()
config_file = "weather.ini"
if args.config:
    config_file = args.config
config = configparser.ConfigParser()
config.read(config_file)
db = config['MySQL']['db']
host = config['MySQL']['host']
user = config['MySQL']['user']
password = config['MySQL']['password']
station = config['SMHI']['station']
period = config['SMHI']['period']

if args.station:
    station = args.station
if not station:
    station = "97100"
if args.period:
    period = args.period
if not period:
    period = "latest-day"

if period not in ["latest-hour", "latest-day", "latest-months"]:
    period = "latest-day"

if args.db:
    db = args.db
if args.host:
    host = args.host
if not host:
    host = "localhost"
if args.user:
    user = args.usr
if args.password:
    password = args.password

if not (db and host and user and password):
    usage()
    sys.exit(1)

mydb = mysql.connector.connect(
  auth_plugin='mysql_native_password',
  database=db,
  host=host,
  passwd=password,
  user=user
)

cursor = mydb.cursor();

upsert = (
    "REPLACE INTO weather "
    "(date, time, rainfall, rel_hum, temp, winddir, windspeed, station) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
)
# Metrics mapping
rainfall = "7"
rel_hum = "6"
temp = "1"
winddir = "3"
windspeed = "4"
results = {}
for metric in [rainfall,rel_hum,temp,winddir,windspeed]:
    results[metric] = requests.get(url='https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/{}/station/{}/period/{}/data.json'.format(metric,station,period))

rainfall_arr = sorted(results[rainfall].json()['value'], key = lambda i: i['date'])
rel_hum_arr = sorted(results[rel_hum].json()['value'], key = lambda i: i['date'])
temp_arr = sorted(results[temp].json()['value'], key = lambda i: i['date'])
winddir_arr = sorted(results[winddir].json()['value'], key = lambda i: i['date'])
windspeed_arr = sorted(results[windspeed].json()['value'], key = lambda i: i['date'])
i = 0
for k in rainfall_arr:
    ts = int(k['date'] / 1000)
    date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
    time = datetime.utcfromtimestamp(ts).strftime('%H:%M:%S')
    rain = k['value']
    hum = rel_hum_arr[i]['value']
    te = temp_arr[i]['value']
    widi = winddir_arr[i]['value']
    wisp = windspeed_arr[i]['value']

    data = (
        date, time, rain, hum, te, widi, wisp, station
    )
    cursor.execute(upsert, data)
    i = i + 1

mydb.commit()
mydb.close()


