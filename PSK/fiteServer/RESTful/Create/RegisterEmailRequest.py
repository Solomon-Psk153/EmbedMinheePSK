from flask import session
from flask_restful import Resource, reqparse
from DB import User, db
from email_validator import validate_email, EmailNotValidError
from Function import MailProvider
from datetime import timedelta
import redis
import re

# 시스템 등록을 위해서 이메일 등록하기를 눌렀을 때, 형식을 확인하고 응답 코드를 저장하는 코드
class RegisterEmailRequest(Resource):
    def post(self):
        
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # 이메일을 post로 전송
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='your email must be string and necessary')
        
        args = parser.parse_args(strict=True)
        
        email = args['email']
        
        print("email is ", email)
        
        # 유저가 이미 존재하는지 확인하는 코드
        if User.query.filter(User.email == email).first() is not None:
            return {'message': 'the email is already used'}, 400

        try:
			# 이메일을 확인
            email_regex = re.compile(r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])')
            
            # 이메일이 위의 정규식에 만족하는지 확인
            if re.fullmatch(email_regex, email) == None:
                return {'message': 'email format is not good'}, 400
            
            # 이메일이 만족하여도 유효한지 확인하는 코드
            validatedEmail = validate_email(email)['email']
            
            # 랜덤코드를 생성하는 코드
            randomStr = MailProvider.randomCodeCreator()
            
            # 랜덤코드를 저장하는 코드
            redis_client.setex(email, timedelta(minutes=2), value=randomStr)
            
            return MailProvider(validatedEmail, '바다 비밀 상자 이메일 인증', randomStr).sendMail()
            
        except EmailNotValidError as e:
            return {'message': f'Email not valid: {str(e)}'}, 400
        
        except Exception as e:
            return {'message': f'internal server error: {str(e)}'}, 500
	
	# 응답 캐시를 피하기 위해 post를 응답 후, 수행하는 함수
    def after_request(self, response):
        # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
