#include <SoftwareSerial.h>

#define RX_PIN 11 // 3
#define TX_PIN 10 // 2

SoftwareSerial espSerial(RX_PIN, TX_PIN);

void setup() {
  Serial.begin(115200);
  espSerial.begin(115200);
  for(byte b = 2; b < 10; pinMode(b++, OUTPUT));
  for(byte b = 12; b < 20; pinMode(b++, INPUT));
  for(byte b = 2; b < 10; b += 2){
    digitalWrite(b, HIGH);
    digitalWrite(b + 1, LOW);
  }
  Serial.println("Setup complete");
}

void loop() {

  // if (Serial.available()) {
  //   String receivedChar = Serial.readStringUntil('\n');
  //   Serial.print("Print value to send to ESP32: ");
  //   Serial.println(receivedChar);
  //   espSerial.println(receivedChar);
  // }

  if (espSerial.available()) {
    String cmd = espSerial.readStringUntil('\n');
    cmd.trim();

    Serial.print(cmd);
    
    if(cmd.length() > 2) {
      espSerial.println("tooLong");
      Serial.println("tooLong");
      return;
    }
    
    char alpha = cmd[0];
    int num = cmd[1] - '0';
    
    Serial.print("alpha: ");
    Serial.println(alpha);

    Serial.print("num: ");
    Serial.println(num);

    if(alpha != 'L' && alpha != 'O') {

      espSerial.println("wrongCmd");
      Serial.println("wrongCmd");
      return;

    } else if(num < 1 || num > 4) {
      espSerial.println("outOfRange");
      Serial.println("outOfRange");
      return;

    } else {

      byte pinHigh = 2 * num + (alpha == 'L');
      byte pinLow = 2 * num + (alpha == 'O');

      digitalWrite(pinHigh, HIGH);
      digitalWrite(pinLow, LOW);
      
      int state = digitalRead(pinHigh);

      if(state == HIGH){
        espSerial.println(cmd);
        Serial.println("cmd: " + cmd);
      } else {
        espSerial.println("error");
        Serial.println("error");
      }

      /*
      if L
        2 * num + 1 on
        2 * num off
      if O
        2 * num on
        2 * num + 1 off
      */

    }


    // Serial.print("Print value received from ESP32: ");
    // Serial.println(receivedChar);
  }
}
