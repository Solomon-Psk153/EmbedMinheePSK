# 사용자를 확인해서 사물함을 빌리는 기능을 하는 파일

from flask_restful import Resource, reqparse
from flask import request
from DB import *
import json, time
import paho.mqtt.client as mqtt

class CreateBorrow(Resource):
    
    # MQTT 프로토콜을 이용하기 위해서 설정할 값들을 지정한다.
    mqtt_broker = "broker.hivemq.com"
    mqtt_port = 1883
    mqtt_topic = "arduino32cmd"
    mqtt_response_topic = "arduino32response"
    
    def __init__(self):
        self.response = None
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect( self.mqtt_broker, self.mqtt_port, 60)
        self.client.subscribe( self.mqtt_response_topic )
        self.client.loop_start()
    
    # MQTT를 통해서 응답을 받는 기능을 수행하는 함수
    def on_message(self, client, userdata, msg):
        print(f"Message received: {msg.payload.decode()}")
        self.response = json.loads(msg.payload.decode())
    
    def post(self):
        
        # 휴대폰에서 post로 요청을 보내면 데이터를 파싱한다.
        parser = reqparse.RequestParser()
        
        parser.add_argument('lockerNum', type=int, required=True, help='lockerNum is int and necessary key')
        parser.add_argument('email', type=str, required=True, help='email is string and neccesary key')
        
        args = parser.parse_args(strict=True)
        
        lockerNum = args['lockerNum']
        email = args['email']
        
        # 내부 DB에 이메일을 통해서 사용자를 찾고 있는지 없는지 확인한다.
        user = User.query.filter(User.email == email).first()
        
        if user is None:
            return {'message': 'User not Found'}, 404
        
        isThereLocker = Locker.query.filter( (Locker.lockerNum == lockerNum) ).first()
        
        # 락커가 존재하는지, 사용하고 있는지 확인
        print(isThereLocker)
        if isThereLocker is None:
            return {'message': 'Locker Not Found'}, 404
        elif isThereLocker.email is not None:
            return {'message': f'someone using {lockerNum}'}, 400
        
        
        # 10초 동안 기다리고 응답을 위해 서버에 구독을 하는 코드
        self.response = None
        self.client.publish( self.mqtt_topic, json.dumps({'cmd': f'L{lockerNum}'}) )
        
        timeout = 10
        start_time = time.time()
        
        # 10초 동안 응답이 없으면 timeout으로 뜨게 한다.
        while self.response is None:
            if time.time() - start_time > timeout:
                return {"error": "Timeout waiting for response from ESP32"}, 504
            time.sleep(0.1)
        
        # code가 200이면, 사물함을 할당한다.
        if self.response.get('code') == 200:
            try:
				# DB에 수정하고 commit해야 데이터베이스에 완전히 적용이 된다. 만약 에러가 나면 rollback을 하게 된다.
                isThereLocker.email = email
                db.session.commit()
                return {'message': 'locker is successFully borrowed'}, 201
                
            except Exception as e:
                db.session.rollback()
                return {'message', f'internal server error: {str(e)}'}, 500
            
            finally:
                db.session.close()
        else: 
            return self.response.get('message'), self.response.get('code')
	
	# post의 요청이 캐시되지 않도록 한다.
    def after_request(self, response):
        # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
