from .DBShare import db
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey
from datetime import datetime, timezone

class User(db.Model):
    
    __tablename__ = 'User'
    
    email = db.Column(
        String(50),
        nullable=False,
        comment="사용자가 입력한 아이디"
    )
    
    randomStr = db.Column(
        String(10),
        nullable=True,
        comment="앱을 다시 설치한 사용자를 위한 인증 수단"
    )
    
    latestUse = db.Column(
        DateTime,
        nullable=False,
        comment="사용자가 앱을 최근에 이용한 시간"
    )
    
    __table_args__ = (
        db.PrimaryKeyConstraint('email', name='pk_email'),
        {'comment': '사용자의 정보를 저장: 사용자(이메일, 랜덤 문자열)'}
    )
    
    def __init__(self, email, randomStr, latestUse):
        self.email=email
        self.randomStr=randomStr
        self.latestUse=latestUse
    
class Locker(db.Model):
    __tablename__ = 'Locker'
    
    lockerNum = db.Column(
        Integer,
        nullable=False,
        comment="사물함의 고유 번호"
    )
    
    email = db.Column(
        String(50),
        nullable=True,
        comment="사물함을 빌리고 있는 사람의 이메일"
    )
    
    __table_args__ = (
        db.PrimaryKeyConstraint('lockerNum', name='pk_lockerNum'),
        db.ForeignKeyConstraint(['email'], ['User.email'], name='fk_email', ondelete='SET NULL', onupdate='CASCADE'),
        {'comment': '사물함의 정보를 저장: 사물함(사물함 번호, 사용자 이메일)'}
    )
    
    def __init__(self, lockerNum, email):
        self.lockerNum=lockerNum
        self.email=email
        
class StartTime(db.Model):
    
    __tablename__ = 'StartTime'
    
    location = db.Column(
        String(50),
        nullable=False,
        comment="사물함의 위치"
    )
    
    semesterStart = db.Column(
        String(10),
        nullable=False,
        comment="사물함의 위치에서 사물함을 이용할 수 있는 시간"
    )
    
    __table_args__ = (
        db.PrimaryKeyConstraint('location', name='pk_location'),
        {'comment': "학기 시작 시간: 시작 시간(위치, 학기 시작 시간)"}
    )
    
    def __init__(self, location, semesterStart):
        self.location=location
        self.semesterStart=semesterStart
    