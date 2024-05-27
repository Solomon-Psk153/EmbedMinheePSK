from flask_restful import Resource, reqparse
from DB import *
import json, time
import paho.mqtt.client as mqtt

class DeleteBorrow(Resource):
    
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
            
            if self.response.get('code') == 200:
                try:
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