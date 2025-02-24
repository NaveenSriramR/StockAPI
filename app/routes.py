from flask import Blueprint, jsonify, request
# from .models import db, User

api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/hello', methods=['GET'])
def get_hello():
    
    return "Ye the server is working!!"


# @api_blueprint.route('/users', methods=['GET'])
# def get_users():
#     users = User.query.all()
#     return jsonify([user.to_dict() for user in users])

# @api_blueprint.route('/users', methods=['POST'])
# def create_user():
#     data = request.get_json()
#     new_user = User(username=data['username'], email=data['email'])
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify(new_user.to_dict()), 201
