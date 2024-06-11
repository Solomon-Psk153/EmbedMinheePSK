# 아래 파일은 사물함 시스템이 필요한 API를 제공하기 위해서 엔드포인트를 지정하는 필수 파일이다.
from flask import Flask
from flask_restful import Api
from DB import db
from RESTful import * # 팀장이 만든 API
from datetime import timedelta
import redis # 인증 코드를 제한 시간동안 저장하기 위한 데이터베이스

# Flask API를 제공하기 위해서 설정하는 값들
class AppConfig(object):
    DEBUG = True
    FLASK_APP = 'FiteDev'
    ENV = 'development'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
    # IMAGE_FORDER = COVER_IMAGE_FORDER = image_folder = imgDir
    # IMAGE_URL = 'http://127.0.0.1:5901/images/'
    
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_POOL_RECYCLE = 3600
    JSON_AS_ASCII = False
    SQLALCHEMY_DATABASE_URI = 'mysql://psk153:20183317@localhost/Fite'
    SECRET_KEY = 'sdf9090erij34ijfq89j234e89j43&*(%^^&*%@'
    
app = Flask(__name__)
app.config.from_object(AppConfig)

if __name__ == '__main__':
	
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    
    api = Api(app)
    
    # create
    api.add_resource(RegisterEmailRequest, '/api/create/email/sendcode')
    api.add_resource(CheckVerifyCode, '/api/create/email/verify')
    api.add_resource(UseSystem, '/api/create/enter')
    api.add_resource(CreateBorrow, '/api/create/locker/borrow')
    
    # read
    api.add_resource(GetLockerStatus, '/api/read/locker/state')
    api.add_resource(GetHowManyTime, '/api/read/time/howmanytime')
    api.add_resource(IsMyLocker, '/api/read/locker/ismineempty')
    api.add_resource(IsReallyMe, '/api/read/check/existence')
    # /api/read/check/existence
    # IsReallyMe
    
    # delete
    api.add_resource(DeleteUserEmail, '/api/delete/email') 
    api.add_resource(DeleteBorrow, '/api/delete/locker/borrow')
    
    # db를 초기화 flask app을 통해 초기화
    db.init_app(app)
    
    # 모든 호스트가 접근할 수 있게 해준다.
    app.run(host='0.0.0.0', port=5902)
    
# 현재 집에 있는 공유기를 DDNS( duckdns )로 포트포워딩을 통해 할당한 상태이다.
