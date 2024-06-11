# 사용자의 이메일을 삭제하는 파일

from flask_restful import Resource, reqparse
from DB import *
from flask import jsonify

class DeleteUserEmail(Resource):
	
    def post(self):
        
        # 휴대폰에서 전송한 이메일 데이터를 파이썬의 변수에 저장한다.
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='your id must be string and necessary')
        
        args = parser.parse_args(strict=True)
        
        email = args['email']
        
        user = User.query.filter(User.email == email).first()
        
        
        # DB에 사용자의 데이터가 없으면 사용자가 없다고 나타나게 한다. 이 경우 앱을 삭제하고 다시 설치해야 한다.
        if user is None:
            return {'message': 'User not found'}, 404
        
        try:
			# DB에서 삭제하고 commit해야 데이터베이스에 완전히 적용이 된다. 만약 에러가 나면 rollback을 하게 된다.
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User is deleted sucessfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'internal server error:{e}'}, 500
        finally:
            db.session.close()
