# 락커들의 상태를 가지고 오는 파일

from flask_restful import Resource
from DB import Locker
from flask import jsonify

class GetLockerStatus(Resource):
    def get(self):
        
        # 락커가 존재하는지 검사
        lockers = Locker.query.order_by(Locker.lockerNum).all()
        
        # 디버깅 용도의 출력문
        print( [ {c.name: getattr(locker, c.name) for c in locker.__table__.columns} for locker in lockers] )
        
        # 락커의 상태를 딕셔너리 형태로 만들어서 리스트로 묶는다.
        lockerStatus = [{
            'lockerNum': locker.lockerNum,
            'email': locker.email
        } for locker in lockers]
        
        # 만든 리스트의 상태와 숫자는 중첩 딕셔너리로 리턴한다.
        return { 'message': {'lockerStatus': lockerStatus, 'count': Locker.query.filter(Locker.email == None).count()} }, 200
        
