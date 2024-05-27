from flask_restful import Resource, reqparse
from datetime import datetime, timedelta
from DB import *

class GetHowManyTime(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        
        parser.add_argument('location', type=str, required=True, help='location must be string and necessary')
        
        args = parser.parse_args(strict=True)
        
        location = args['location']
        
        findLocation = StartTime.query.filter( (StartTime.location == location) ).first()
        
        if findLocation is None:
            return {'message': 'location not found'}, 404
        
        try:
            year = datetime.now().year
            month, day = map(int, findLocation.semesterStart.split('/'))
            startTime = datetime(year, month, day, 0, 0, 0)
            
            time_difference = datetime.now() - startTime

            # timedelta 객체를 초 단위로 변환
            time_difference_seconds = time_difference.total_seconds()
            
        except ValueError:
            return {'message': 'Invalid time format'}, 400
        
        return {'message': time_difference_seconds}, 200