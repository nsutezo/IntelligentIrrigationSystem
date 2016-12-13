from flask import Flask, request, json, render_template, jsonify, make_response, Response
from flaskext.mysql import MySQL
from flask_pymongo import PyMongo
from time import sleep, time
from threading import Thread, Event
from bson.json_util import dumps
import datetime
#from  dateutil.tz import tzlocal
from random import random
import socket, select, Queue
from celery import Celery
import pytz
from pytz import timezone
#from flaskapp import water_farm
import requests
import numpy as np
from learning import analyzer, calibrate
eastern = timezone('US/Eastern')
fmt = "%Y-%m-%d %H:%M:%S"

app = Flask(__name__)
mysql = MySQL()


def mysql_save(sm1,sm2,humidity_outside, temp_outside,pressure, temp_min, temp_max,wind_speed, clouds,tankvolume, sm1_calibrated, sm2_calibrated):
	app.config['MYSQL_DATABASE_USER'] ='simone'
	app.config['MYSQL_DATABASE_PASSWORD'] = 'iot'
	app.config['MYSQL_DATABASE_DB'] = 'irrigation'
	app.config['MYSQL_DATABASE_HOST'] = 'ec2-54-244-160-74.us-west-2.compute.amazonaws.com'
	app.config['PORT'] = '3306'
	mysql.init_app(app)
	conn = mysql.connect()
	cursor = conn.cursor()
	insert_stmt = ( "INSERT INTO iotdata (id, datetime, soilmoisture1, soilmoisture2,humidity,temperature,pressure,tempmin, tempmax, windspeed, clouds,tankvolume )"
			"VALUES (NULL, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)")
	insert_data = (datetime.datetime.now(eastern), sm1, sm2,humidity_outside, temp_outside,pressure, temp_min, temp_max,wind_speed,clouds,tankvolume)
	#print(insert_data)
	cursor.execute(insert_stmt, insert_data)
	
	insert_calibrated_stmt =( "INSERT INTO calibrated_data (id, datetime, soilmoisture1, soilmoisture2,humidity,temperature,pressure,tempmin, tempmax, windspeed, clouds,tankvolume )"
                        "VALUES (NULL, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s)")
	insert_calibrated = (datetime.datetime.now(eastern), sm1_calibrated, sm2_calibrated,humidity_outside, temp_outside,pressure, temp_min, temp_max,wind_speed,clouds,tankvolume)
	cursor.execute(insert_calibrated_stmt, insert_calibrated)
	conn.commit()
	conn.close()

def mysql_getdata(num):
	app.config['MYSQL_DATABASE_USER'] ='simone'
        app.config['MYSQL_DATABASE_PASSWORD'] = 'iot'
        app.config['MYSQL_DATABASE_DB'] = 'irrigation'
        app.config['MYSQL_DATABASE_HOST'] = 'ec2-54-244-160-74.us-west-2.compute.amazonaws.com'
        app.config['PORT'] = '3306'
        mysql.init_app(app)
        conn = mysql.connect()
        cursor = conn.cursor()
	
	cursor.execute("SELECT * FROM calibrated_data ORDER BY id DESC")
	headrow = cursor.fetchmany(size=num)	
        conn.commit()
        conn.close()
	return headrow


def get_LastWater():
	app.config['MYSQL_DATABASE_USER'] ='simone'
        app.config['MYSQL_DATABASE_PASSWORD'] = 'iot'
        app.config['MYSQL_DATABASE_DB'] = 'waterfarm'
        app.config['MYSQL_DATABASE_HOST'] = 'ec2-54-244-160-74.us-west-2.compute.amazonaws.com'
        app.config['PORT'] = '3306'
        mysql.init_app(app)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM water ORDER BY id DESC")
        headrow = cursor.fetchone()
        datetime = headrow[1]
	valve_w1 = headrow[2]
	valve_w2 = headrow[3]
        conn.commit()
        conn.close()
	return datetime, valve_w1, valve_w2


def get_Water():
	app.config['MYSQL_DATABASE_USER'] ='simone'
        app.config['MYSQL_DATABASE_PASSWORD'] = 'iot'
        app.config['MYSQL_DATABASE_DB'] = 'waterfarm'
        app.config['MYSQL_DATABASE_HOST'] = 'ec2-54-244-160-74.us-west-2.compute.amazonaws.com'
        app.config['PORT'] = '3306'
	mysql.init_app(app)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tempwater")
        headrow = cursor.fetchone()
	#print(headrow)
	valve1, valve2  = headrow[2], headrow[3]
	v1,v2 = 0,0
	insert_data = (datetime.datetime.now(eastern), v1, v2)
        insert_stmt1 = ( "UPDATE tempwater SET datetime= %s,valve1=%s, valve2=%s WHERE id =1")
        cursor.execute(insert_stmt1, insert_data)
        conn.commit()
        conn.close()

	return valve1, valve2

def save_Water(v1,v2):
	app.config['MYSQL_DATABASE_USER'] ='simone'
        app.config['MYSQL_DATABASE_PASSWORD'] = 'iot'
        app.config['MYSQL_DATABASE_DB'] = 'waterfarm'
        app.config['MYSQL_DATABASE_HOST'] = 'ec2-54-244-160-74.us-west-2.compute.amazonaws.com'
        app.config['PORT'] = '3306'
	mysql.init_app(app)
        conn = mysql.connect()
	cursor = conn.cursor()
	insert_stmt = ( "INSERT INTO water (id, datetime,valve1, valve2)"
                        "VALUES (NULL, %s, %s, %s)")
	insert_data = (datetime.datetime.now(eastern), v1, v2)
	insert_stmt1 = ( "UPDATE tempwater SET datetime= %s,valve1=%s, valve2=%s WHERE id =1")
	cursor.execute(insert_stmt, insert_data)
	cursor.execute(insert_stmt1, insert_data)
	conn.commit()
        conn.close()






def check_lastirrigation():
	data = mysql_getdata(3600)
	water_next_1, water_next_2 = analyzer(data,1,1)
	print(water_next_1, water_next_2)
	day_time, sky = rain_forecast()
	raindate = check_rain_before_Water(day_time, sky)
	return water_next_1,water_next_2, raindate
	



def get_weather():
    lat = 40.813890;
    lon = -73.962402;
    weather_key = '&APPID=248ba8a75508737d35215268e055c142'
    data = requests.get('http://api.openweathermap.org/data/2.5/weather?lat=%f&lon=%f' % (lat,lon) + weather_key)
    bulk_json = json.loads(data.content)
    #print(bulk_json)
    temp,  pressure , humidity,temp_min, temp_max, wind_speed, clouds = bulk_json['main']['temp'], bulk_json['main']['pressure'], bulk_json['main']['humidity'], bulk_json['main']['temp_min'], bulk_json['main']['temp_max'],bulk_json['wind']['speed'], bulk_json['clouds']['all']
    return temp,  pressure , humidity,temp_min, temp_max, wind_speed, clouds




def get_rainydays(data):
	day_time = []
	sky = []
	for item in range(len(data)):
		day_time.append(data[item]["dt_txt"])
		
		sky.append(data[item]["weather"][0]["main"])
	return day_time, sky



def check_rain_before_Water(day_time, sky):
        for i in range(len(day_time)):
                cur_date = datetime.datetime.strptime(day_time[i], '%Y-%m-%d %H:%M:%S')
                if sky[i] == 'Rain':
                        break
        return cur_date




def rain_forecast():
	lat = 40.813890;
    	lon = -73.962402;
    	weather_key = '&APPID=248ba8a75508737d35215268e055c142'
    	data = requests.get('http://api.openweathermap.org/data/2.5/forecast?lat=%f&lon=%f' % (lat,lon) + weather_key)
    	forecast_json = json.loads(data.content)
	day_time, sky = get_rainydays(forecast_json["list"])
	return day_time , sky
    	#return r

@app.route('/')
def api_home():
        return " Welcome To Irrigation of Things: The Ideal Irrigation Solution."  #render_template('index.html', data='test')



@app.route('/data',methods = ['POST'])
def api_data():
	if request.headers['Content-Type'] == 'application/json':
		cur_r = json.loads(request.get_data())
		if cur_r['user'] == 'esp':
			if cur_r['command'] == 'postMoisture':
				temp_outside,  pressure , humidity_outside,temp_min, temp_max, wind_speed, clouds = get_weather()
				temp_outside_c = temp_outside - 273
				temp_min_c = temp_min  - 273
				temp_max_c = temp_max - 273   
				sm1,sm2= cur_r["s1"], cur_r["s2"]
				tankvolume = 10
			
				sm1_calibrated = calibrate(sm1)
				sm2_calibrated = calibrate(sm2)

				mysql_save(sm1,sm2,humidity_outside, temp_outside_c,pressure, temp_min_c, temp_max_c,wind_speed, clouds,tankvolume, sm1_calibrated,sm2_calibrated)
				resp = make_response(json.dumps({}))
				resp.status_code =200
        			return resp
			elif cur_r['command'] == 'getValves':
				v1 , v2 = get_Water()
				resp = make_response(json.dumps({"valve1":int(v1), "valve2":int(v2)}))
				resp.status_code =200
				return resp
		elif cur_r['user'] == 'app':
			v1 =0
			v2 =0
			#print(cur_r["command"])
			command = json.loads(cur_r["command"])
			if int(command[0]) == 1 :
				v1 = float(command[1])
				v2 =0
			elif int(command[0]) == 2:
				v1 = 0
				v2 = float(command[1])
			save_Water(v1,v2)
			aresp = make_response(json.dumps({"valve1": v1, "valve2": v2}))
			aresp.status_code =200
			return aresp


@app.route('/app_terry', methods =['POST', 'GET'])
def app_terry():
	water_next_1,water_next_2, raindate = check_lastirrigation()
	num_data_point = 48
	predicted = {"water_valve1":water_next_1, "water_valve2": water_next_2, "raindate":raindate}
	requested_data = json.dumps((mysql_getdata(num_data_point),predicted))
	dresp = make_response(requested_data)
	dresp.content_type = 'application/json'
	dresp.status_code = 200
    	return dresp

@app.route('/live-data')
def live_data():
    for i in mongo.db.smartwatch.find().sort("_id",-1).limit(1):
        newax = int(i['ax'])
        neway = int(i['ay'])
        newaz = int(i['az'])
    data = [[time()*1000, newax], [time()*1000, neway], [time()*1000, newaz]]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response
@app.route('/learning', methods = ['POST','GET'])
def learning():
	water_next_1,water_next_2, raindate1, raindate2 = check_lastirrigation()
	return "happy"


if __name__ == '__main__':
    app.run(debug = True, passthrough_errors=True)
