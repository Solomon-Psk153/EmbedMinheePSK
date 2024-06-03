from flask import session
from flask_restful import Resource, reqparse
from DB import User, db
import redis
from datetime import datetime, timezone

class CheckVerifyCode(Resource):
    def post(self):
        
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='your email must be string and necessary')
        parser.add_argument('verify', type=str, required=True, help='verify code must be string and necessary')
        args = parser.parse_args(strict=True)
        email = args['email']
        verifyCode = args['verify']
        stored_verify_code = redis_client.get(email)
        
        if stored_verify_code:
            if stored_verify_code == verifyCode:
                
                redis_client.delete(email)
                
                try:
                    db.session.add( User( email=email,randomStr=verifyCode, latestUse=datetime.now(timezone.utc) ) )
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return {'message': f'internal server error: {str(e)}'}, 500
                return {'message': 'the verify code you input match'}, 200
            else:
                return {'message': 'the verify code you input does not match'}, 400
        else:
            return {'message': 'Email verify time expired'}, 400
