# 아래 파일은 MySQL에 있는 속성들을 파이썬 객체로 변환하기 위한 코드가 모여 있다.

# 필요한 패키지: sqlalchemy에서 지원하는 데이터 타입들이 대부분이다.
from .DBShare import db
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey
from datetime import datetime, timezone

#사용자 계정
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
    
    # 초기화(생성자) 함수에서 데이터를 입력할 수 있도록 해야 객체가 올바르게 생성된다.
    def __init__(self, email, randomStr, latestUse):
        self.email=email
        self.randomStr=randomStr
        self.latestUse=latestUse
    
# 사물함 정보
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

# 각 위치별 끝나는 시간
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
    
