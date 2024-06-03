from flask_restful import Resource, reqparse
from datetime import datetime, timedelta
from DB import *

class GetHowManyTime(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        
        parser.add_argument('location1', type=str, required=True, help='location1 must be string and necessary')
        parser.add_argument('location2', type=str, required=True, help='location2 must be string and necessary')
        
        args = parser.parse_args(strict=True)
        
        location1 = args['location1']
        location2 = args['location2']
        
        findLocation1 = StartTime.query.filter( (StartTime.location == location1) ).first()
        findLocation2 = StartTime.query.filter( (StartTime.location == location2) ).first()
        
        if findLocation1 is None or findLocation2 is None:
            return {'message': 'location not found'}, 404
        
        try:
            firstStart = findLocation1.semesterStart
            secondStart = findLocation2.semesterStart
            
            nowDate = datetime.now() 
            year = nowDate.year
            month = nowDate.month
            
            startMonth1, day1 = map(int, firstStart.split('/'))
            startMonth2, day2 = map(int, secondStart.split('/'))
            
            startDate1 = datetime(year, startMonth1, day1, 0, 0, 0)
            startDate2 = datetime(year, startMonth2, day2, 0, 0, 0)
            endDate1 = datetime(year, 6, 30, 0, 0, 0)
            endDate2 = datetime(year, 12, 30, 0, 0, 0)
            
            if nowDate < startDate1:
                return {'message': int( (nowDate - startDate1).total_seconds() )}, 200
            
            elif nowDate < endDate1:
                return {'message': int( (endDate1 - nowDate).total_seconds() )}, 200
            
            elif nowDate < startDate2:
                return {'message': int( (endDate1 - nowDate).total_seconds() )}, 200
            
            elif nowDate < endDate2:
                return {'message': int( (endDate2 - nowDate).total_seconds() )}, 200
            
        except ValueError:
            return {'message': 'Invalid time format'}, 400