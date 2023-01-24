#include "DHT.h"
#include <SoftwareSerial.h>


#define DHTPIN 2   
#define DHTTYPE DHT11   

#define BT_TX_PIN 12
#define BT_RX_PIN 11

DHT dht(DHTPIN, DHTTYPE);
SoftwareSerial BTserial=SoftwareSerial(BT_RX_PIN,BT_TX_PIN);
void setup() {
  Serial.begin(9600);
  BTserial.begin(9600);
  dht.begin();
}

void loop() {

  float t = dht.readTemperature();
  if (isnan(t)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }
  String msg=String(t) + "\n";
  Serial.print(msg);
  BTserial.print(msg);


  while(BTserial.available()>0){
    char a= BTserial.read();
    Serial.print(a);
  }

  delay(2000);

}
