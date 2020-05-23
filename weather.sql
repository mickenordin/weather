CREATE TABLE IF NOT EXISTS `weather` (
  `observation_id` int NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  `time` time DEFAULT NULL,
  `rainfall` float DEFAULT NULL,
  `rel_hum` decimal(10,0) DEFAULT NULL,
  `temp` float DEFAULT NULL,
  `windspeed` float DEFAULT NULL,
  `station` int DEFAULT NULL,
  `station_name` varchar(255) DEFAULT NULL,
  `winddir` int DEFAULT NULL,
  PRIMARY KEY (`observation_id`),
  UNIQUE KEY `date_time_idx` (`date`,`time`,`station`)
);

CREATE TABLE IF NOT EXISTS `aggregated_weather` (
  `Date_id` int NOT NULL AUTO_INCREMENT,
  `Date` date DEFAULT NULL,
  `T_max` float DEFAULT NULL,
  `T_min` float DEFAULT NULL,
  `T_mean` float DEFAULT NULL,
  `RH_max` float DEFAULT NULL,
  `RH_min` float DEFAULT NULL,
  `RH_mean` float DEFAULT NULL,
  `Rainfall` float DEFAULT NULL,
  `ETo` float DEFAULT NULL,
  `station` int DEFAULT NULL,
  `station_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Date_id`),
  UNIQUE KEY `date_idx` (`Date`,`station`)
);
