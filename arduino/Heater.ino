#include <SoftwareSerial.h>

#define BT_TX_PIN 12
#define BT_RX_PIN 11
#define LED 13

SoftwareSerial BTserial=SoftwareSerial(BT_RX_PIN,BT_TX_PIN);

void setup() {
  Serial.begin(9600);
  BTserial.begin(9600);
  pinMode(LED, OUTPUT);  
}

void loop() {
  
  String val = BTserial.readString();
  if(val=="ON"){
      digitalWrite(LED, HIGH);
      Serial.print("Acceso");
  delay(5000);
  }
  if(val=="OFF"){
       digitalWrite(LED, LOW);
       Serial.print("Spento");
  }
delay(5000);
  
}
