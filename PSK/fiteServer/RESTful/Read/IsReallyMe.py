from flask_restful import Resource, reqparse
from DB import *

# 이메일을 검사해서 사용자가 존재하면 O, 그렇지 않으면 X를 리턴한다.
class IsReallyMe(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        
        parser.add_argument('email', type=str, required=True, help='email must be string and necessary')
        
        args = parser.parse_args(strict=True)
        
        email = args['email']
        
        user = User.query.filter(User.email == email).first()
        
        if user is None:
            return {'message': 'X'}, 404
        
        else:
            return {'message': 'O'}, 200
