from flask_restful import Resource, reqparse
from DB import Locker
from flask import jsonify

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