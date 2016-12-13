from machine import I2C, Pin
import time
import urequests
response = ""

secondsBetweenHTTPRequests = 10;

#Setup I2C
SDA = 4; # SDA
SCL = 5; # SCL
i2c = I2C(Pin(SCL), Pin(SDA),freq=100000)
soil1 = 0;
soil2 = 0;

#Reset Arduino MEGA
ardRes = 14;
ardResPin = Pin(ardRes,Pin.OUT);
ardResPin.value(0)
time.sleep(1)
ardResPin.value(1)
print("Waiting for XBees to configure...")
time.sleep(10) #wait for xbee configuration
print("MEGA available over I2C with address: ")
print(i2c.scan())

sendBuf = bytearray(4)     # create a buffer with 4 bytes
recBuf  = bytearray(4) 

def sendToArd(buf):
    #print(buf)
    i2c.writeto(0x08, buf)  # write the given buffer to the slave
    buf = bytearray(4) #clear buf array  
    #print(buf)  

def recFromArd(buf):
    i2c.readfrom_into(0x08, buf)  
    #print(buf)  

def sendToAWS(content):
    url = 'http://54.244.160.74/data'
    headers = {'content-type': 'application/json'}
    resp = urequests.post(url, data=content, headers=headers)
    #print(resp.content)
    recString = str(resp.content)
    return recString
                         
def parseResp(recString):
    import ujson
    st = recString.find("{")
    en = recString.find("}")+1
    jsonString = recString[st:en]
    recJSON = ujson.loads(jsonString)
    time1 = int(recJSON["valve1"])
    time2 = int(recJSON["valve2"])    
    return time1, time2     



#sendString = '{"s1":"%d", "s2":"%d","h":"%d","t":"%d","user":"esp"}' % (0,0,0,0)
                                                                                                                
if(__name__ == '__main__'):
    while True:
        sendString = '{"command":"getValves","user":"esp"}'
        
        print("String being sent to server: "+ sendString)
        try:
            response = sendToAWS(sendString)
        except OSError:
            time.sleep(.5)        
        time1, time2 = parseResp(response)
        print("response: "+response)


        #set buffer values here (valve times)
        sendBuf[0] = 1
        sendBuf[1] = time1
        sendBuf[2] = 2
        sendBuf[3] = time2
        print("sendBuf")
        print(sendBuf[0])
        print(sendBuf[1])        
        print(sendBuf[2])
        print(sendBuf[3])  
                
        sendToArd(sendBuf) 
        sendBuf[1] = time1
        sendBuf[3] = time2                   
        time.sleep_ms(50)  # wait for data to become available on Arduino      
    
        
        recFromArd(recBuf)        
        print("recBuf: ")
        print(recBuf[0])
        print(recBuf[1])
        print(recBuf[2])
        print(recBuf[3])                        
        soil1 = int(recBuf[1])
        soil2 = int(recBuf[3])
        
        sendString = '{"command":"postMoisture","s1":"%d", "s2":"%d","user":"esp"}' % (soil1,soil2)
        
        
        print("String being sent to server: "+ sendString)
        try:
            sendToAWS(sendString)
        except OSError:
            time.sleep(.5)  
            
        time.sleep(secondsBetweenHTTPRequests)
