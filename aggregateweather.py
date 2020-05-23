#!/usr/bin/python3

from datetime import datetime
from eto import ETo, datasets
from io import StringIO
import argparse
import configparser
import mysql.connector
import pandas as pd
import requests
import sys


def usage():
    print(
        "Usage: " + __file__ +
        "[--config path_to_file.ini] [--station smhi_station_number ] --database database] [--host dbhost] [--user dbuser] [--password dbpassword]\n"
        "Default configfile is weather.ini, any parameter can be overwritten on the command line"
    )


parser = argparse.ArgumentParser()
parser.add_argument('--config')
parser.add_argument('--database')
parser.add_argument('--host')
parser.add_argument('--user')
parser.add_argument('--password')
parser.add_argument('--station')
args = parser.parse_args()
config_file = "weather.ini"
if args.config:
    config_file = args.config
config = configparser.ConfigParser()
config.read(config_file)
db = config['MySQL']['database']
host = config['MySQL']['host']
user = config['MySQL']['user']
password = config['MySQL']['password']

station = config['SMHI']['station']

# Defaults
z_msl = 48.854
lat = 59.178503
lon = 17.909265
TZ_lon = lon
freq = 'D'

if args.station:
    station = args.station
if not station:
    station = "97100"
if args.database:
    db = args.database
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

pd.options.mode.chained_assignment = None
station_data = requests.get(
    url=
    'https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/1/station/{}.json'
    .format(station)).json()
newest_to = 0
for i in station_data['position']:
    if i['to'] > newest_to:
        z_msl = i['height']
        lat = i['latitude']
        lon = i['longitude']
        TZ_lon = lon

mydb = mysql.connector.connect(auth_plugin='mysql_native_password',
                               database=db,
                               host=host,
                               passwd=password,
                               user=user)

cursor = mydb.cursor()

date_select = ("SELECT DISTINCT `date` FROM weather WHERE station = {}".format(station))
s_name = ""
cursor.execute(date_select)
dates = cursor.fetchall()
csv = "date,T_max,T_min,T_mean,RH_max,RH_min,RH_mean,Rainfall\n"
for i in dates:
    working_date = i[0].strftime('%Y-%m-%d')
    day_select = ('SELECT * FROM weather '
                  'WHERE date = "{}" AND station = {}'.format(working_date,station))
    cursor.execute(day_select)
    day = cursor.fetchall()
    sum_rain = 0
    T_max = -9999
    T_min = 9999
    RH_max = -9999
    RH_min = 9999
    sum_temp = 0
    sum_rel_hum = 0
    counter = 0
    for j in day:
        counter += 1
        #+----------------+---------------+------+-----+---------+----------------+
        #| Field          | Type          | Null | Key | Default | Extra          |
        #+----------------+---------------+------+-----+---------+----------------+
        #| observation_id | int           | NO   | PRI | NULL    | auto_increment |
        #| date           | date          | YES  | MUL | NULL    |                |
        #| time           | time          | YES  |     | NULL    |                |
        #| rainfall       | float         | YES  |     | NULL    |                |
        #| rel_hum        | decimal(10,0) | YES  |     | NULL    |                |
        #| temp           | float         | YES  |     | NULL    |                |
        #| windspeed      | float         | YES  |     | NULL    |                |
        #| station        | int           | YES  |     | NULL    |                |
        #| station_name   | varchar(255)  | YES  |     | NULL    |                |
        #| winddir        | int           | YES  |     | NULL    |                |
        #+----------------+---------------+------+-----+---------+----------------+

        observation_id = 0
        date = 1
        time = 2
        rainfall = 3
        rel_hum = 4
        temp = 5
        #windspeed = 6
        #station = 7
        station_name = 8
        #winddir = 9
        sum_rain += j[rainfall]
        sum_temp += j[temp]
        sum_rel_hum += j[rel_hum]
        s_name = j[station_name]
        if T_max < j[temp]:
            T_max = j[temp]
        if T_min > j[temp]:
            T_min = j[temp]
        if RH_max < j[rel_hum]:
            RH_max = j[rel_hum]
        if RH_min > j[rel_hum]:
            RH_min = j[rel_hum]
    T_mean = sum_temp / counter
    RH_mean = sum_rel_hum / counter
    csv += working_date + "," + str(T_max) + "," + str(T_min) + "," + str(
        T_mean) + "," + str(RH_max) + "," + str(RH_min) + "," + str(
            RH_mean) + "," + str(sum_rain) + "\n"
DATA = StringIO(csv)
tsdata = pd.read_csv(DATA,
                     parse_dates=True,
                     infer_datetime_format=True,
                     index_col='date')
et1 = ETo()
et1.param_est(tsdata, freq, z_msl, lat, lon, TZ_lon)
et1.ts_param.head()
eto1 = et1.eto_hargreaves()

upsert = (
    "REPLACE INTO aggregated_weather "
    "(Date, T_max, T_min, T_mean, RH_max, RH_min, RH_mean, Rainfall, ETo, station, station_name) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

for key, value in eto1.items():
    aggdate = key.strftime('%Y-%m-%d')
    data = (aggdate, float(tsdata.loc[aggdate, 'T_max']),
            float(tsdata.loc[aggdate,
                             'T_min']), float(tsdata.loc[aggdate, 'T_mean']),
            float(tsdata.loc[aggdate,
                             'RH_max']), float(tsdata.loc[aggdate, 'RH_min']),
            float(tsdata.loc[aggdate, 'RH_mean']),
            float(tsdata.loc[aggdate, 'Rainfall']), float(value), int(station), s_name)
    cursor.execute(upsert, data)

mydb.commit()
mydb.close()
