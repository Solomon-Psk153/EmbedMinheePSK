#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

#define RX_PIN 16
#define TX_PIN 17

const char* ssid     = "7313 캡스톤디자인(2.5Ghz)";
const char* password = "73137313";

const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "arduino32cmd";
const char* mqtt_response_topic = "arduino32response";

int escape = 0;

hw_timer_t *timer = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

void IRAM_ATTR onTimer() {
  portENTER_CRITICAL_ISR(&timerMux);
  escape++;
  portEXIT_CRITICAL_ISR(&timerMux);
}

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, RX_PIN, TX_PIN); // for Arduino

  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, 10000000, true);
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

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
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}

void callback(char* topic, byte* payload, unsigned int length) {

	String message = String((char*)payload).substring(0, length);

	Serial.print("Message arrived [");
	Serial.print(topic);
	Serial.print("] ");
	Serial.println(message);

	DynamicJsonDocument doc(1024);
	DeserializationError error = deserializeJson(doc, message);

	if (error) {
		Serial.println("Failed to parse JSON");
    sendResponse(400, "Invalid JSON");
		// client.publish("arduino32response", "{\"error\":\"Invalid JSON\"}");
		return;
	}

	String cmd = String(doc["cmd"].as<const char*>());
  Serial.println("cmd: " + cmd);
	Serial2.println(cmd);

	String rv;
	timerWrite(timer, 0);
	timerAlarmEnable(timer);

	while (!escape) {
		if (Serial2.available() > 0) {
			rv = Serial2.readStringUntil('\n');
			break;
		}
	}

	rv.trim();
	Serial.println("rv: " + rv);
	timerAlarmDisable(timer);

	if (escape == 1) {
		Serial.println("wireError1");
		sendResponse(500, "Wire error");
		
	} else if (escape == 0) {
		if (rv == cmd) {
			Serial.println("Success");
			sendResponse(200, "Success");
		} else if(rv == "outOfRange"){
			Serial.println("outOfRange");
			sendResponse(400, "outOfRange");
		} else if(rv == "wrongCmd"){
			Serial.println("wrongCmd");
			sendResponse(400, "wrongCmd");
		} else if(rv == "error"){
			Serial.println("error");
			sendResponse(500, "error");
		} else if(rv == "tooLong"){
			Serial.println("tooLong");
			sendResponse(400, "tooLong");
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
	} else {
    sendResponse(500, "CriticalError");
	}

	portENTER_CRITICAL(&timerMux);
	escape = 0;
	portEXIT_CRITICAL(&timerMux);
}

void sendResponse(int code, const String& message) {
  DynamicJsonDocument responseDoc(1024);
  responseDoc["code"] = code;
  responseDoc["message"] = message;
  String response;
  serializeJson(responseDoc, response);
  client.publish(mqtt_response_topic, response.c_str());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a unique client ID
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);

    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.subscribe(mqtt_topic);
      Serial.print("Subscribed to topic: ");
      Serial.println(mqtt_topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}