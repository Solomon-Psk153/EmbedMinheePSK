# 휴대폰의 사용하기 버튼을 누르면 사용자를 확인하는 기능을 하는 파일

from flask_restful import Resource, reqparse
from DB import *

class UseSystem(Resource):
	
    def post(self):
        
        # post 요청을 통해 휴대폰이 전달한 값을 받아서 처리
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='your email must be string and necessary')
        parser.add_argument('verify', type=str, required=True, help='verify code must be string and necessary')
        args = parser.parse_args(strict=True)
        email = args['email']
        verifyCode = args['verify']
        
        # 사용자의 이메일과 등록할 때, 발행한 랜덤코드를 검색
        userEamil = User.query.filter(User.email == email).first()
        userRandomStr = User.query.filter(User.randomStr == verifyCode).first()
        
        # 검색 결과가 일치하는 지 검색
        if userEamil is None:
            return {'message': 'User not found'}, 404
        
        elif userRandomStr is None:
            return {'message': 'verifyCode not match'}, 400
        
        else: # 일치하면 시스템을 이용할 수 있다.
            return {'message': 'system enter successfully'}, 200
