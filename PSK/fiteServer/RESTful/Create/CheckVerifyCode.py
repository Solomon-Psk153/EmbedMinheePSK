# 임시 redis DB에 저장된 임시 코드를 확인하는 파일

from flask import session
from flask_restful import Resource, reqparse
from DB import User, db
import redis
from datetime import datetime, timezone

class CheckVerifyCode(Resource):
    
    def post(self):
        
        # 서버에서 자체적으로 만든 코드를 일정시간동안 저장하기 위해, redis 데이터베이스를 설정
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # 데이터베이스에 post로 보낸 값들을 저장하기 위해 reqparse 패키지를 이용해서 저장
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='your email must be string and necessary')
        parser.add_argument('verify', type=str, required=True, help='verify code must be string and necessary')
        args = parser.parse_args(strict=True)
        email = args['email']
        verifyCode = args['verify']
        stored_verify_code = redis_client.get(email)
        
        # 저장한 값이 존재하고 저장한 코드가 클라이언트가 보낸 코드와 일치한다면
        if stored_verify_code:
            if stored_verify_code == verifyCode:
               
               # 임시 데이터베이스에 저장한 코드를 지운다.
                redis_client.delete(email)
                
                try:
					# 이 사용자는 인증된 사용자이니 MySQL에 저장한다.
					# DB에 추가하고 commit해야 데이터베이스에 완전히 적용이 된다. 만약 에러가 나면 rollback을 하게 된다.
                    db.session.add( User( email=email,randomStr=verifyCode, latestUse=datetime.now(timezone.utc) ) )
                    db.session.commit()
                except Exception as e:
					# 만약 오류가 발생하면 전의 상태로 되돌린다.
                    db.session.rollback()
                    return {'message': f'internal server error: {str(e)}'}, 500
                return {'message': 'the verify code you input match'}, 200
			# 코드가 일치하지 않으면 오류를 발생시킨다.
            else:
                return {'message': 'the verify code you input does not match'}, 400
        else:
			# 시간이 초과되었다고 오류를 날린다.
            return {'message': 'Email verify time expired'}, 400
