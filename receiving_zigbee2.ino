#include <XBee.h> 


XBee xbee = XBee();
XBeeResponse response = XBeeResponse();
unsigned long start = millis();
uint8_t payload[] = { 0,0 };
int k = 0;
int moisPin = 5;
int moisVal = 0;
int radioNum = 2;
unsigned long timeRec = 0;
int openTime = 0;
int valvePin = 6;

// create reusable response objects for responses we expect to handle 
Rx16Response rx16 = Rx16Response();
Rx64Response rx64 = Rx64Response();


// 16-bit addressing: Enter address of remote XBee, typically the coordinator
//Tx16Request tx = Tx16Request(0x1874, payload, sizeof(payload));


// 64-bit addressing: This is the SH + SL address of remote XBee
XBeeAddress64 addr64 = XBeeAddress64(0x0013a200, 0x40d7c048);
// Address of coordinator
// unless you have MY on the receiving radio set to FFFF, this will be received as a RX16 packet
Tx64Request tx = Tx64Request(addr64, payload, sizeof(payload));

TxStatusResponse txStatus = TxStatusResponse();
int pin5 = 0;


int statusLed = 11; // Green
int errorLed = 12; // Red
int dataLed = 10; // Yellow
int sendingled = 7;

uint8_t option = 0;
uint8_t data1 = 0;
uint8_t data2 = 0;


void flashLed(int pin, int times, int wait) {
    
    for (int i = 0; i < times; i++) {
      digitalWrite(pin, HIGH);
      delay(wait);
      digitalWrite(pin, LOW);
      
      if (i + 1 < times) {
        delay(wait);
      }
    }
}

void setup() {
  pinMode(statusLed, OUTPUT);
  pinMode(errorLed,  OUTPUT);
  pinMode(dataLed,   OUTPUT);
  pinMode(sendingled, OUTPUT);
  pinMode(moisPin, INPUT);
  pinMode(valvePin, OUTPUT);
  
  // start serial
  Serial.begin(9600);
  xbee.setSerial(Serial);
  Serial.println("Starting Up...");
  flashLed(statusLed, 5, 100);
}
void openValve(){
  digitalWrite(valvePin, HIGH);
}

void closeValve(){
  digitalWrite(valvePin, LOW);  
}



void receiving(){
   // continuously reads packets, looking for RX16 or RX64
   xbee.readPacket();
    if (xbee.getResponse().isAvailable()) {
      if (xbee.getResponse().getApiId() == RX_16_RESPONSE || xbee.getResponse().getApiId() == RX_64_RESPONSE) {
        if (xbee.getResponse().getApiId() == RX_16_RESPONSE) {
                xbee.getResponse().getRx16Response(rx16);
          option = rx16.getOption();
          data1 = rx16.getData(0); // radio number
          data2 = rx16.getData(1); // time command
          openTime = data2*1000; 
          Serial.print("Open Time: ");
          Serial.println(openTime);                    
//          Serial.println("Data Received");
//          Serial.println();
          Serial.print("data1: ");  
          Serial.println(data1);     
//          Serial.print("data2: ");
//          Serial.println(data2);                    
          flashLed(dataLed, 3, 25);
          if (data1 == radioNum){
            flashLed(statusLed, 3, 25);
            k = 1;
          }
          if (data2 > 0){            
            Serial.print("Opening valve for: ");          
            Serial.println(openTime);     
            timeRec = millis();
            openValve();
          }
          

            
        } else {
                xbee.getResponse().getRx64Response(rx64);
          option = rx64.getOption();
          data1 = rx64.getData(0);  
        }
        Serial.print(rx16.getData(0));
        Serial.print(rx16.getData(1));

      }else {
        // not something we were expecting
        flashLed(errorLed, 1, 25);    
      }
    } else if (xbee.getResponse().isError()) {
      //Serial.print("Error reading packet.  Error code: ");  
      //Serial.println(xbee.getResponse().getErrorCode());
      // or flash error led
    } 
    delay(1000);
}

void sending(){
      if (millis() - start > 5000) {
      moisVal = analogRead(moisPin);
      Serial.print(moisVal);
      uint8_t payload[] = { radioNum, moisVal };
      Tx64Request tx = Tx64Request(addr64, payload, sizeof(payload));
      xbee.send(tx);
    }
  
    // after sending a tx request, we expect a status response
    // wait up to 5 seconds for the status response
    if (xbee.readPacket(5000)) {
        // got a response!

        // should be a znet tx status              
      if (xbee.getResponse().getApiId() == TX_STATUS_RESPONSE) {
         xbee.getResponse().getTxStatusResponse(txStatus);
        
         // get the delivery status, the fifth byte
           if (txStatus.getStatus() == SUCCESS) {
              // success.  time to celebrate
              flashLed(sendingled, 5, 50);
           } else {
              // the remote XBee did not receive our packet. is it powered on?
              flashLed(errorLed, 3, 500);
           }
        }      
    } else if (xbee.getResponse().isError()) {
      //nss.print("Error reading packet.  Error code: ");  
      //nss.println(xbee.getResponse().getErrorCode());
      // or flash error led
    } else {
      // local XBee did not provide a timely TX Status Response.  Radio is not configured properly or connected
      flashLed(errorLed, 2, 50);
    }
    
    //delay(3000);

}


void loop() {
   if (k == 1){
      sending();
      Serial.println("Sending Data To Coordinator");

      k = 0;
   } 
   if (millis()-timeRec > openTime){
    Serial.print("millis(): "); 
    Serial.println(millis());     
    Serial.print("timeRec: "); 
    Serial.println(timeRec);  
    Serial.print("openTime: "); 
    Serial.println(openTime);            
    closeValve();        
   }
   receiving();
   delay(1000);
   }

   
