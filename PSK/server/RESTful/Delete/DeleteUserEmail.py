from flask_restful import Resource, reqparse
from DB import *
from flask import jsonify

class DeleteUserEmail(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='your id must be string and necessary')
        
        args = parser.parse_args(strict=True)
        
        email = args['email']
        
        user = User.query.filter(User.email == email).first()
        
        if user is None:
            return {'message': 'User not found'}, 404
        
        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'User is deleted sucessfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'internal server error:{e}'}, 500
        finally:
            db.session.close()