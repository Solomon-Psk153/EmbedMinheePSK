from flask_restful import Resource, reqparse
from DB import Locker
from flask import jsonify

# 현재 사물함을 이메일을 확인해서 사용하고 있으면 X를 사용하지 않으면 해당 사물함 번호를 리턴하도록 한다.
class IsMyLocker(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        
        parser.add_argument('email', type=str, required=True, help='email must be string and necessary')
        
        args = parser.parse_args(strict=True)
        
        email = args['email']
        
        user = Locker.query.filter(Locker.email == email).first()
        
        if user is None:
            return {'message': 'X'}, 404
        
        else:
            return {'message': user.lockerNum}, 200
