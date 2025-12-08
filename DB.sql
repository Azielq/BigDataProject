CREATE DATABASE bigdata_aziel;
--**************************************************
DROP TABLE IF EXISTS bigdata_aziel.taxis;
--********************************************************
CREATE EXTERNAL TABLE bigdata_aziel.taxis (
	key STRING,
	fare_amount DOUBLE,
	pickup_datetime STRING,
	pickup_longitude DOUBLE,
	pickup_latitude DOUBLE,
	dropoff_longitude DOUBLE,
	dropoff_latitude DOUBLE,
	passenger_count INT
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
	"separatorChar" = ",",
	"quoteChar" = "\"",
	"escapeChar" = "\\"
)
LOCATION 's3://ulacit-datos-masivos/output/'
TBLPROPERTIES (
	"skip.header.line.count" = "1",
	"use.null.for.invalid.data" = "true"
);


SELECT * FROM bigdata_aziel.taxis;