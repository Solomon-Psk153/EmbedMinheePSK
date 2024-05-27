from flask_restful import Resource
from DB import Locker
from flask import jsonify

class GetLockerStatus(Resource):
    def get(self):
        
        lockers = Locker.query.order_by(Locker.lockerNum).all()
        #session.query(MyModel).order_by(MyModel.is_urgent.desc(), MyModel.creation_time)
        
        print( [ {c.name: getattr(locker, c.name) for c in locker.__table__.columns} for locker in lockers] )
        
        lockerStatus = [{
            'lockerNum': locker.lockerNum,
            'email': locker.email
        } for locker in lockers]
        
        return { 'message': {'lockerStatus': lockerStatus, 'count': Locker.query.filter(Locker.email == None).count()} }, 200
        