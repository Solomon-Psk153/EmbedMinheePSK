from flask_restful import Resource, reqparse
from flask import request
from DB import *
import json, time
import paho.mqtt.client as mqtt

class CreateBorrow(Resource):
    
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
    
    def on_message(self, client, userdata, msg):
        print(f"Message received: {msg.payload.decode()}")
        self.response = json.loads(msg.payload.decode())
    
    def post(self):
        
        parser = reqparse.RequestParser()
        
        parser.add_argument('lockerNum', type=int, required=True, help='lockerNum is int and necessary key')
        parser.add_argument('email', type=str, required=True, help='email is string and neccesary key')
        
        args = parser.parse_args(strict=True)
        
        lockerNum = args['lockerNum']
        email = args['email']
        
        user = User.query.filter(User.email == email).first()
        
        if user is None:
            return {'message': 'User not Found'}, 404
        
        isThereLocker = Locker.query.filter( (Locker.lockerNum == lockerNum) ).first()
        
        print(isThereLocker)
        if isThereLocker is None:
            return {'message': 'Locker Not Found'}, 404
        elif isThereLocker.email is not None:
            return {'message': f'someone using {lockerNum}'}, 400
        
        self.response = None
        self.client.publish( self.mqtt_topic, json.dumps({'cmd': f'L{lockerNum}'}) )
        
        timeout = 10
        start_time = time.time()
        
        while self.response is None:
            if time.time() - start_time > timeout:
                return {"error": "Timeout waiting for response from ESP32"}, 504
            time.sleep(0.1)
        
        if self.response.get('code') == 200:
            try:
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
            
    def after_request(self, response):
        # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
    
#     The issue lies in how you're accessing attributes of the Locker object returned by the query. When you use isThereLocker['lenderID'], you're trying to access it like a dictionary, but SQLAlchemy objects are not dictionaries. Instead, you should access attributes directly from the object.

# Here's how you can fix it:

# python
# 코드 복사
# isThereLocker = Locker.query.filter(Locker.lockerID == lockerID).first()

# if isThereLocker is None:
#     return {'message': 'lockerID out of range'}, 400
# elif isThereLocker.lenderID is not None:
#     print(isThereLocker.lenderID)
#     return {'message': f'someone is using {lockerID}'}, 400
# By using dot notation (isThereLocker.lenderID) instead of dictionary access (isThereLocker['lenderID']), you'll correctly access the lenderID attribute of the Locker object. This should resolve the issue you're facing.