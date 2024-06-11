# 빌린 사물함을 삭제하도록 하는 기능을 가진 파일

from flask_restful import Resource, reqparse
from DB import *
import json, time
import paho.mqtt.client as mqtt

class DeleteBorrow(Resource):
    
    # MQTT 프로토콜을 이용하기 위해서 설정할 값들
    mqtt_broker = "broker.hivemq.com"
    mqtt_port = 1883
    mqtt_topic = "arduino32cmd"
    mqtt_response_topic = "arduino32response"
    
    # 클라이언트는 브로커를 통해서 응답을 받는다. 그러기 위해서 응답 토픽으로 서버에 클라이언트로 등록시킨다.
    def __init__(self):
        self.response = None
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect( self.mqtt_broker, self.mqtt_port, 60)
        self.client.subscribe( self.mqtt_response_topic )
        self.client.loop_start()
    
    def on_message(self, client, userdata, msg):
        print(f"Message received: {msg.payload.decode()}")
        self.response = json.loads(msg.payload.decode())
        
    def post(self):
        
        parser = reqparse.RequestParser()
        
        parser.add_argument('lockerNum', type=int, required=True, help='lockerNum is int and necessary key')
        parser.add_argument('email', type=str, required=True, help='email is string and neccesary key')
        
        args = parser.parse_args(strict=True)
        
        # 휴대폰이 보낸 요청을 저장하기 위해 파싱하고 변수에 저장
        lockerNum = args['lockerNum']
        email = args['email']
        
        # 사용자가 시스템에 등록되어 있고 사물함이 존재하고 사물함을 빌린 사람이 존재하면 MQTT 프로토콜로 브로커에게 요청한다.
        user = User.query.filter(User.email == email).first()
        
        if user is None:
            return {'message': 'User not found'}, 404
        
        locker = Locker.query.filter( Locker.lockerNum == lockerNum ).first()
        
        if locker is None:
            return {'message': 'That Locker Not Found'}, 404
        
        elif locker.email is None:
            return {'message': 'That Locker Lender does not exist'}, 404
        
        elif locker.email == email:
            self.response = None
            self.client.publish( self.mqtt_topic, json.dumps({'cmd': f'O{lockerNum}'}) )
            
            timeout = 10
            start_time = time.time()
            
            while self.response is None:
                if time.time() - start_time > timeout:
                    return {"error": "Timeout waiting for response from ESP32"}, 504
                time.sleep(0.1)
            
            # 시간이 10초과 초과하면 응답으로 timeout을 보낸다. ESP32에서 응답이 제 시간안에 오면 응답코드를 확인해서 DB에서 해당 사용자를 제거한다.
            if self.response.get('code') == 200:
                try:
					# DB에서 수정하고 commit해야 데이터베이스에 완전히 적용이 된다. 만약 에러가 나면 rollback을 하게 된다.
                    locker.email = None
                    db.session.commit()
                    return {'message': 'Locker can Borrow anyone now'}, 200
                except Exception as e:
                    db.session.rollback()
                    return {'message': f'internal server Error:{e}'}, 500
                finally:
                    db.session.close()
            else:
                return self.response.get('message'), self.response.get('code')
        else:
            return {'message': 'the locker lender is not same what you search for'}, 400
