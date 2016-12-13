import numpy as np
import math
import datetime
def get_Moisture(data):
	#print("Start Moisture")
	moisture_1 =[]
	moisture_2 =[]
	dates_x = []
	for i in range(len(data)):
		moisture_1.append(data[i][2])
		moisture_2.append(data[i][3])
		dates_x.append((data[i][1] - data[-1][1]).total_seconds())
	m1 = np.asarray(moisture_1)
	m2 = np.asarray(moisture_2)
	x = np.asarray(dates_x)
	#print("End Moisture")
	return m1, m2,x


def calibrate(raw):
	max_valve = 130.0
	min_valve = 65.0
	max_moisture = 100.0
	min_moisture = 0.0
	moisture_slope = (max_valve - min_valve)/(max_moisture)
	vwc = float(raw) *moisture_slope
        return vwc



def slopeOLS(y,x):
    #print("Start OLS")
    n= len(y)
    sumxy = sum(x*y)
    sumx = sum(x)
    sumy = sum(y)
    sumx2 = sumx**2
    squarexsum = sum(x**2)
     
    slope = (n*sumxy - sumx*sumy)/(n*squarexsum-sumx2)
    #print("End OLS")
    return slope

#def get_Slope(x1,x3,y1,y3):
#	delta_x = (x_3 -x1)*(10**-9)
#	delta_y = y3-y1
#	slope = delta_y / delta_x
#	return slope

def get_Intercept(x1,y1, slope):
	intercept = y1 - (slope*x1)
	return intercept

def get_Trend(m1,m2,valve_w1, valve_w2,x):  # get trend using last X datapoints
	#print("Start Trend")
	if valve_w1 == 0 and valve_w2 == 0:
		pass
	elif valve_w1  ==0:
		slope2 = slopeOLS(m2,x)
		#v2_y1,v2_y3 = m2[len(m2) -4:-1]
		#v2_x1,v2_x2,v2_x3 = x[len(x)-4:-1]
		#slope2 = get_Slope(v2_x1,v2_x3,v2_y1,v2_y3)
		intercept2 = get_Intercept(x[-1],m2[-1],slope2)
		slope1 =0
		intercept1 =0
	elif valve_w2 == 0:
		slope1 = slopeOLS(m1,x)
		#v1_y1,v1_y2,v1_y3 = m1[len(m1) -4:-1]
                #v1_x1,v1_x2,v1_x3 = x[len(x)-4:-1]
                #slope1 = get_Slope(v1_x1,v1_x3,v1_y1,v1_y3)
                #intercept1 = get_Intercept(v1_x1,v1_x3,v1_y1,v1_y3)
		intercept1 = get_Intercept(x[-1],m1[-1],slope1)
		slope2 = 0
		intercept2 = 0
	else:
		slope2 = slopeOLS(m2,x)
                intercept2 = get_Intercept(x[-1],m2[-1],slope2)
		## v1
		slope1 = slopeOLS(m1,x)
		intercept1 = get_Intercept(x[-1],m1[-1],slope1)
	#print("End Trend")
	return slope1, intercept1, slope2, intercept2

def get_nextWater(slope, intercept, last_measurement):
	#print("Start Next Water")
	desired_moisture = 30
	#print(slope, intercept,last_measurement, desired_moisture)
	#print(slope)
	#print(intercept)
	seconds_to_next_watering = (desired_moisture - intercept) / slope
	# check time addition
	#print(seconds_to_next_watering)
	#print(last_measurement)
	water_next =last_measurement + datetime.timedelta(seconds = seconds_to_next_watering)
	#print("End Next Water")
	return water_next



def analyzer(data, valve_w1, valve_w2):
	#print("start analyzer")
	m1, m2, x = get_Moisture(data)
	#print(data)
	last_measurement = data[0][1]
	slope1, intercept1, slope2, intercept2 = get_Trend(m1,m2,valve_w1, valve_w2,x)
	if valve_w1 !=0 and valve_w2 != 0:
		water_next_1 = get_nextWater(slope1, intercept1, last_measurement)
		water_next_2 = get_nextWater(slope2, intercept2, last_measurement)
	elif valve_w1 !=0 and valve_w2 ==0:
		water_next_1 = get_nextWater(slope1, intercept1, last_measurement)
		water_next_2 = 0
	elif valve_w1 ==0 and valve_w2 !=0:
		water_next_1 = 0
		water_next_2 = get_nextWater(slope2, intercept2, last_measurement)
	else:
		return "Invalid Request: No valve is turned on"
	#print("End analyzer")
	return water_next_1, water_next_2


 


