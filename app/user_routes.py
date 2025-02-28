from flask import Blueprint, jsonify, request
from .extensions import mongo
from bson.objectid import ObjectId
user_blueprint = Blueprint('users', __name__)

# Get all users
@user_blueprint.route('/', methods=['GET'])
def get_users():
    ''' Returns all users'''

    users = mongo.db.users.find()  # Fetch all users
                        #    ,{"_id": {"$toString": "$_id"},"email":1,"username":1})  # Projects user data with _id converted to String from ObjectId    
    # user_list = [{"id": str(user["_id"]), "username": user["username"], "email": user["email"]} for user in users]
    return jsonify(users)

@user_blueprint.route('/<id>', methods=['GET'])
def get_user_by_id(id):
    ''' Returns user data by id'''
    print(id)
    user = mongo.db.users.find_one({"_id":ObjectId(id)})
                            #    ,{"_id": {"$toString": "$_id"},"email":1,"username":1})  # Projects user data with _id converted to String from ObjectId

    # user_list = [{"id": str(user["_id"]), "username": user["username"], "email": user["email"]} for user in users]
    # print(user)
    return jsonify(user)


# Create a new user
@user_blueprint.route('/adduser', methods=['POST'])
def create_user():
    ''' Adds new user to the platform. Contains username, email. '''
    data = request.get_json()
    new_user = {"username": data["username"], "email": data["email"]}
    inserted_id = mongo.db.users.insert_one(new_user).inserted_id

    # new_portfolio = {"user_id":ObjectId(inserted_id),"stocks":{}}
    # mongo.db.portfolio.insert_one(new_portfolio)
    return jsonify({"id": str(inserted_id), **new_user}), 201

