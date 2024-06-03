from flask_restful import Resource, reqparse
from DB import *

class UseSystem(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='your email must be string and necessary')
        parser.add_argument('verify', type=str, required=True, help='verify code must be string and necessary')
        args = parser.parse_args(strict=True)
        email = args['email']
        verifyCode = args['verify']
        
        userEamil = User.query.filter(User.email == email).first()
        userRandomStr = User.query.filter(User.randomStr == verifyCode).first()
        
        if userEamil is None:
            return {'message': 'User not found'}, 404
        
        elif userRandomStr is None:
            return {'message': 'verifyCode not match'}, 400
        
        else:
            return {'message': 'system enter successfully'}, 200