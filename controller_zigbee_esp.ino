#include <XBee.h>
#include <Wire.h>
#include <stdint.h>

int j;
int recBuf[4];
byte i2cSendBuf[4] = {1,0,2,0};

XBee xbee = XBee();
XBeeResponse response = XBeeResponse();
unsigned long start = millis();

uint8_t payload1[] = { 1, 25 };
uint8_t payload2[] = { 2, 45 };

// create reusable response objects for responses we expect to handle
Rx16Response rx16 = Rx16Response();
Rx64Response rx64 = Rx64Response();

int errorLed = 12; // Red
int sending1Led = 11; // Green
int receiving1Led = 10; // Yellow
int sending2Led = 9; // White
int receiving2Led = 8; // Blue
//int ESPpin = 7;

// 64-bit addressing: This is the SH + SL address of remote XBee
XBeeAddress64 addr64Rec1 = XBeeAddress64(0x0013a200, 0x40d7c06b);
XBeeAddress64 addr64Rec2 = XBeeAddress64(0x0013a200, 0x40d7c3e6);

// Address of coordinator
// unless you have MY on the receiving radio set to FFFF, this will be received as a RX16 packet
Tx64Request tx1 = Tx64Request(addr64Rec1, payload1, sizeof(payload1));
Tx64Request tx2 = Tx64Request(addr64Rec2, payload2, sizeof(payload2));
TxStatusResponse txStatus1 = TxStatusResponse();
TxStatusResponse txStatus2 = TxStatusResponse();


uint8_t option = 0;
uint8_t data = 0;

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
//    I2C Setup
  Wire.begin(8);                // join i2c bus with address #8
  Wire.onReceive(receiveEvent); // register event
  Wire.onRequest(requestEvent); // register event
//
  pinMode(errorLed, OUTPUT);
  pinMode(sending1Led, OUTPUT);
  pinMode(receiving1Led,  OUTPUT);
  pinMode(sending2Led, OUTPUT);
  pinMode(receiving2Led,  OUTPUT);
//  pinMode(ESPpin, OUTPUT);
  
  // start serial
  Serial1.begin(9600); // USB serial
  Serial.begin(9600); // XBee serial
  xbee.setSerial(Serial1);

  flashLed(sending1Led, 3, 50);
  flashLed(sending2Led, 3, 50);
}

void receiving() {
  xbee.readPacket();
  if (xbee.getResponse().isAvailable()) {
    if (xbee.getResponse().getApiId() == RX_16_RESPONSE || xbee.getResponse().getApiId() == RX_64_RESPONSE) {
      if (xbee.getResponse().getApiId() == RX_16_RESPONSE) {
        xbee.getResponse().getRx16Response(rx16);
        option = rx16.getOption();
        data = rx16.getData(0);
        
        if (rx16.getData(0) == 1){
          i2cSendBuf[1] = rx16.getData(1);} 
                 
        if (rx16.getData(0) == 2){
          i2cSendBuf[3] = rx16.getData(1);}
          
        Serial.print("I2C data to ESP: ");
        Serial.print(i2cSendBuf[0]);
        Serial.print(", ");
        Serial.print(i2cSendBuf[1]);
        Serial.print(", ");
        Serial.print(i2cSendBuf[2]);
        Serial.print(", ");
        Serial.println(i2cSendBuf[3]);

//        for (int i=0;i<=1;i++){       
//          byte (i2cSendBuf[i] = rx16.getData(i));
//          Serial.print("data");          
//          Serial.print(i); 
//          Serial.print(": ");          
//          Serial.println(i2cSendBuf[i]);}
      
        int (data1) = rx16.getData(0); 
        int (data2) = rx16.getData(1);
        int (data3) = rx16.getData(2);
      
        flashLed(receiving1Led,3,50);
        if (data1 == 1){
          flashLed(receiving2Led,3,50);
        } else{
          flashLed(receiving2Led,3,50);
        }
        
      } else {
        xbee.getResponse().getRx64Response(rx64);
        option = rx64.getOption();
        data = rx64.getData(0);
      }
      
    } else {
      // not something we were expecting
      flashLed(errorLed, 1, 25);
    }
  } else if (xbee.getResponse().isError()) {
  }
}

void sending1() {
 if (millis() - start > 5000) {
//      Tx64Request tx1 = Tx64Request(addr64Rec1, payload1, sizeof(payload1));
      Serial.println("Rewriting Payload");
//      for(int i = 0; i < 2; i++){
//          Serial.print(payload1[i]);
//        }
      xbee.send(tx1);
      //Serial.println("Sending Packet");
    }
  
    // after sending a tx request, we expect a status response
    // wait up to 5 seconds for the status response
    if (xbee.readPacket(5000)) {
        // got a response!

        // should be a znet tx status              
      if (xbee.getResponse().getApiId() == TX_STATUS_RESPONSE) {
         xbee.getResponse().getTxStatusResponse(txStatus1);
        
         // get the delivery status, the fifth byte
           if (txStatus1.getStatus() == SUCCESS) {
              // success.  time to celebrate
              Serial.println("Sending Success");
              flashLed(sending1Led, 5, 50);
           } else {
              // the remote XBee did not receive our packet. is it powered on?
              Serial.println("Sending Failure");
              flashLed(errorLed, 3, 500);
           }
        }      
    } else if (xbee.getResponse().isError()) {
      //nss.print("Error reading packet.  Error code: ");  
      //nss.println(xbee.getResponse().getErrorCode());
      // or flash error led
    } else {
      Serial.println("Another Sending Failure");
      // local XBee did not provide a timely TX Status Response.  Radio is not configured properly or connected
      //flashLed(errorLed, 2, 50);
    }  
//    delay(3000);
}

void sending2() {
 if (millis() - start > 15000) {
//      Tx64Request tx2 = Tx64Request(addr64Rec1, payload2, sizeof(payload2));
      Serial.println("Rewriting Payload");      
      xbee.send(tx2);
    }
  
    // after sending a tx request, we expect a status response
    // wait up to 5 seconds for the status response
    if (xbee.readPacket(5000)) {
        // got a response!

        // should be a znet tx status              
      if (xbee.getResponse().getApiId() == TX_STATUS_RESPONSE) {
         xbee.getResponse().getTxStatusResponse(txStatus2);
        
         // get the delivery status, the fifth byte
           if (txStatus2.getStatus() == SUCCESS) {
              // success.  time to celebrate
              flashLed(sending2Led, 5, 50);
           } else {
              // the remote XBee did not receive our packet. is it powered on?
              //flashLed(errorLed, 3, 500);
           }
        }      
    } else if (xbee.getResponse().isError()) {
      //nss.print("Error reading packet.  Error code: ");  
      //nss.println(xbee.getResponse().getErrorCode());
      // or flash error led
    } else {
      // local XBee did not provide a timely TX Status Response.  Radio is not configured properly or connected
      //flashLed(errorLed, 2, 50);
    }
//    delay(1000);
}

// continuously reads packets, looking for RX16 or RX64
void loop() {
  if (j == 1){
    sending1(); 
    sending2();    
    j = 0;
    } 
    receiving(); 
    delay(10);     
  }
void receiveEvent(int howMany){
  int i = 0;
  while (Wire.available()) {
    int x = Wire.read(); // receive byte as a character
    recBuf[i] = x;
    i = i+1;
    }
  Serial.println();
  Serial.print("Payload Data from ESP: ");
  for(int i = 0; i < 4; i++){
    Serial.print(recBuf[i]);
        }
  Serial.println();   
    payload1[0] = recBuf[0];
    payload1[1] = recBuf[1];
    payload2[0] = recBuf[2];
    payload2[1] = recBuf[3];    
    j = 1;
//  for(int i = 0; i < 2; i++){
//  Serial.print(payload1[i]);
//      }
}
 
void requestEvent(){
  Wire.write(i2cSendBuf,4); // respond with message
  // as expected by master
}
