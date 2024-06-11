// ESP32에서 오는 요청을 수행하는 역할을 하는 파일

#include <SoftwareSerial.h>

#define RX_PIN 11 // 3
#define TX_PIN 10 // 2

// ESP32와 유선 시리얼 통신을 위해 소프트웨어 적으로 설치
SoftwareSerial espSerial(RX_PIN, TX_PIN);

void setup() {
	
  // espSerial는 esp32로 전송
  // Serial는 시리얼 모니터
  // 초기화 및 모든 LED는 초록색으로 시작
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
  
  // esp32에서 명령이 오는지 계속 확인해서 명령이 오면 개행 문자 전으로 명령으로 인식한다.
  if (espSerial.available()) {
    String cmd = espSerial.readStringUntil('\n');
    cmd.trim();

    Serial.print(cmd);
    
	// 명령 길이가 2이상이면 명령이 아님
    if(cmd.length() > 2) {
      espSerial.println("tooLong");
      Serial.println("tooLong");
      return;
    }
    
    //명령을 분리해서 올바르게 출력되는지 확인
    char alpha = cmd[0];
    int num = cmd[1] - '0';
    
    Serial.print("alpha: ");
    Serial.println(alpha);

    Serial.print("num: ");
    Serial.println(num);

	// 길이가 2이지만 앞 글자가 L이나 O가 아니면 명령이 아님
    if(alpha != 'L' && alpha != 'O') {

      espSerial.println("wrongCmd");
      Serial.println("wrongCmd");
      return;

	// 사물함 개수를 초과하면 안됨
    } else if(num < 1 || num > 4) {
      espSerial.println("outOfRange");
      Serial.println("outOfRange");
      return;

	// 번호로 열리는 핀과 닫히는 핀을 계산 후, esp32로 유선 시리얼 통신
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
