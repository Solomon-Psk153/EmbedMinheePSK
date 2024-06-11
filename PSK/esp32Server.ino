// 서버에서 오는 요청을 아두이노에게 전달하고 아두이노에서 오는 응답을 와이파이로 서버에게 제공해 주는 역할

#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

// ESP32와 유선 시리얼 통신을 하기 위한 포트번호
#define RX_PIN 16
#define TX_PIN 17

// 와이파이 이름과 비밀번호
const char* ssid     = "7311"//"7313 캡스톤디자인(2.5Ghz)";
const char* password = "73117311"//"73137313";

// MQTT (모스키토) 프로토콜 설정, 서버가 서버 주소의 토픽으로 요청을 보내면 응답을 서버의 응답 토픽으로 보내준다.
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "arduino32cmd";
const char* mqtt_response_topic = "arduino32response";

// 일정 시간이 되면 증가되어 사용자에게 알려주기 위한 변수
int escape = 0;

// 하드웨어 타이머는 처음에 널 값으로 설정
hw_timer_t *timer = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

// 임계 구역에서 어떤 한 요청만 escape를 증가시켜서 레이스 컨디셔널이 발생하지 않도록 한다.
void IRAM_ATTR onTimer() {
  portENTER_CRITICAL_ISR(&timerMux);
  escape++;
  portEXIT_CRITICAL_ISR(&timerMux);
}

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  
  // Serial2 = EPS32 시리얼 모니터 출력
  // Serial1 = 아두이노 전송
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, RX_PIN, TX_PIN); // for Arduino

  // 와이파이 연결
  setup_wifi();

  // 모기 프로토콜을 이용하기 위한 구독과정, 중개자를 중간에 두어서 모든 통신은 중계자가 전달해준다.
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // 타이머는 최대 10초로 잡고 이 시간동안 응답이 없으면 onTimer로 이동한다. 그룹 0, 80MHz(분주기)로 카운트 업(true)모드를 설정한다.
  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, 10000000, true);
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  //와이파이 통신을 위한 연결
  WiFi.begin(ssid, password);

  //와이파이가 연결이 안되면 계속 연결될 때까지 무한 루프
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
	
  // 클라이언트가 연결되지 않으면 계속 재 연결
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}

void callback(char* topic, byte* payload, unsigned int length) {
	
	// JSON으로 들어온 요청을 파싱한다.
	String message = String((char*)payload).substring(0, length);

	Serial.print("Message arrived [");
	Serial.print(topic);
	Serial.print("] ");
	Serial.println(message);

	// 객체 직렬화를 통해서 doc에 그 결과를 저장
	DynamicJsonDocument doc(1024);
	DeserializationError error = deserializeJson(doc, message);

	// 에러가 발생하면 함수 응답 보내고 종료
	if (error) {
		Serial.println("Failed to parse JSON");
    sendResponse(400, "Invalid JSON");
		// client.publish("arduino32response", "{\"error\":\"Invalid JSON\"}");
		return;
	}

	String cmd = String(doc["cmd"].as<const char*>());
  Serial.println("cmd: " + cmd);
  
  //아두이노에 명령 전송
	Serial2.println(cmd);

	String rv;
	// 타이머 초기화 후, 알람 시작
	timerWrite(timer, 0);
	timerAlarmEnable(timer);

	//escape가 1이 되거나 아두이노로 부터 응답이 올 때까지 계속 루프 반복
	while (!escape) {
		if (Serial2.available() > 0) {
			rv = Serial2.readStringUntil('\n');
			break;
		}
	}

	// 아두이노로 부터 온 결과 trim 후 알람 끄기
	rv.trim();
	Serial.println("rv: " + rv);
	timerAlarmDisable(timer);

	// 1 이면 어떤 유선이 끊어졌다고 가정한다.(치명적)
	if (escape == 1) {
		Serial.println("wireError1");
		sendResponse(500, "Wire error");
		
	// 0 이면 성공적으로 통신이 완료된 것이다.
	} else if (escape == 0) {
		if (rv == cmd) {
			Serial.println("Success");
			sendResponse(200, "Success");
			
	// outOfRange -> 명령 값 범위 초과
		} else if(rv == "outOfRange"){
			Serial.println("outOfRange");
			sendResponse(400, "outOfRange");
			
	// wrongCmd -> 잘못된 명령
		} else if(rv == "wrongCmd"){
			Serial.println("wrongCmd");
			sendResponse(400, "wrongCmd");
			
	// error -> 서버 내부 오류
		} else if(rv == "error"){
			Serial.println("error");
			sendResponse(500, "error");
	// tooLong -> 명령이 너무 김
		} else if(rv == "tooLong"){
			Serial.println("tooLong");
			sendResponse(400, "tooLong");
			
	// 실패해서 명령을 이전 명령으로 rollback
	// 확인한 결과 롤백이 실패하는 것으로 확인, 하지만, 데이터베이스에는 저장이 안되서 정상적으로 대여가 되는 것을 확인
		} else {
			Serial.println("failed0");
			if(rv[0] != 'L' && rv[0] != 'O'){
				Serial.println("wrongCmd0");
				sendResponse(400, "wrongCmd0");
			} else {
				timerWrite(timer, 0);
				String rollbackCmd = String( rv[0] == 'L' ? 'O' : 'L') + rv[1];
				Serial.println( rollbackCmd );
        
        // 아두이노 버퍼 초기화
        Serial2.end();
        Serial2.begin(115200);
				
        Serial2.println( rollbackCmd );
				timerAlarmEnable(timer);
				while(!escape){
					if(Serial2.available() > 0){
						rv = Serial2.readStringUntil('\n');
						break;
					}
				}

				Serial.println("rollback rv: " + rv);
				timerAlarmDisable(timer);
				Serial.println("rollback0");
				sendResponse(500, "rollback0");
			}
		}
	} else { // 임계 구역 침범
    sendResponse(500, "CriticalError");
	}

	portENTER_CRITICAL(&timerMux);
	escape = 0; // 임계 구역 안에서 안전하게  escape를 0으로 설정
	portEXIT_CRITICAL(&timerMux);
}

// 응답 토픽으로 응답 JSON을 리턴한다.
void sendResponse(int code, const String& message) {
  DynamicJsonDocument responseDoc(1024);
  responseDoc["code"] = code;
  responseDoc["message"] = message;
  String response;
  serializeJson(responseDoc, response);
  client.publish(mqtt_response_topic, response.c_str());
}

// 재연결
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a unique client ID
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);

    // Attempt to connect
	// 연결 되었으면 구독한다.
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.subscribe(mqtt_topic);
      Serial.print("Subscribed to topic: ");
      Serial.println(mqtt_topic);
    } else { // 연결되지 않으면 5초 뒤에 재시도
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
