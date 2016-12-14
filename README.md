# Intelligent Irrigation System
Implementation Of A Smart Irrigation System for Small  Scale Farming

# Requirements 
Hardware:
- ESP8266: Used as main controller and used to aggregate and transmit data to the server.
- Arduino Mega : Used as coordinator. Send commands zigbees and receives data from them.
- Arduinos (UNO) and Zigbees : Collect data at a given location and relays it to the Arduino Mega or Nearest Zigbee.
- Sensors: Soil Moisture (Temperature and Humidity Sensor to be included in next iteration).

Software Installation: 
- Micropython for ESP8266: http://micropython.org/
- XCTU for Zigbee communication: https://www.digi.com/products/xbee-rf-solutions/xctu-software/xctu
- AWS  EC2 Instance for Virtual Server (Ubuntu 14.04): https://aws.amazon.com/ec2/
- Flask (Python) for request handling with virtual server: http://flask.pocoo.org/
- MySQL Database for Data Storage: https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-14-04




# ESP Code for Communication with Mega and Server
maini2c.py
- This is for data transfer between the Arduino Mega(Coordinator) and the ESP8266  Feather Huzzah Controller. Data from the ESP8266 is transfered to the Server.

# Arduinos and Zigbees
controller_zigbee_esp_ino
- Install on the Mega which acts as the controller.

receiving_zigbee1.ino & receiving_zigbee2.ino
-Install on the endpoint UNOs / receiving zigbees.

# AWS EC2 Instance
flaskapp.py
- Use flaskapp.py to handle request from the ESP8266 and the android application.
- Need to install Apache2, WSGI, MySQL apriori in order to get flaskapp.py working in AWS Ubuntu 14.04.

learning.py
- Analyzes the previous X number of datapoints and determines when soil moisture will cross the 30 % moisture level.

# Android Application
IrrigationApp
- Install on Phone to access data from the Server.

# Project Website
Download ProjectWebsite Folder and open the index.html (with a broswer) to view our Project Website.

# Project Video
Access https://www.youtube.com/watch?v=_MsWReY_bcE for our Project Video.



GOOD LUCK!!!
