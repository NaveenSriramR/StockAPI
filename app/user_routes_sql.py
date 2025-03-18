from .models import User
from .extensions import sql
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

user_blueprint = Blueprint('sqlusers', __name__)

# Get all users
@user_blueprint.route('/', methods=['GET'])
def get_users():
    ''' Returns all users'''

    users = User.query.all() # Fetch all users
                        #    ,{"_id": {"$toString": "$_id"},"email":1,"username":1})  # Projects user data with _id converted to String from ObjectId    
    users_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
        
    return jsonify({"users":users_list}),200

@user_blueprint.route('/<id>', methods=['GET'])
def get_user_by_id(id):
    """
    Retrieve a user by their ID.

    Args:
        user_id (str): The ObjectId of the user as a string.

    Returns:
        JSON response:
        - 200 OK: If the user is found, returns the user data with `_id` as a string.
        - 404 Not Found: If the user does not exist, returns an error message.
    """
    user = sql.get_or_404(User, id)
    # user = User.find_one({"_id":ObjectId(id)})
                            #    ,{"_id": {"$toString": "$_id"},"email":1,"username":1})  # Projects user data with _id converted to String from ObjectId

    if user == None:
        return jsonify({'error':"User not found"}),404
    
    return jsonify(user)

@user_blueprint.route('/', methods=['POST'])
def create_user():
    """
    Create a new user.

    Expects a JSON request body containing:
    - "username" (str): The username of the user.
    - "email" (str): The email address of the user.

    Returns:
        JSON response:
        - 201 Created: If the user is successfully added, returns the user data with the new ID.
        - 400 Bad Request: If required fields are missing, returns an error message.
    """

    data = request.get_json()

    # Validate required fields
    if not data or "username" not in data or "email" not in data:
        return jsonify({"error": "Missing required fields: 'username' and 'email'"}), 400

    new_user = {"username": data["username"], "email": data["email"]}

    user = User(
            username=data["username"],
            email=data["email"],
        )
    sql.session.add(user)
    try:
        sql.session.commit()
    except IntegrityError as err:
        if "user.email" in str(err):
            return jsonify({"error":"Email already in use!"}), 409
        if "user.username" in str(err):
            return jsonify({"error":"Username already in use!"}), 409

    return jsonify({"id":user.id, **new_user}), 201

@user_blueprint.route('/<userid>', methods=['PATCH'])
def update_user(userid):
    """
    Update an existing user's information.

    Args:
        userid (str): The ObjectId of the user as a string.

    Expects a JSON request body containing any of the following fields:
    - "username" (str, optional): The updated username.
    - "email" (str, optional): The updated email.

    Returns:
        JSON response:
        {
        "message":"...", 
        "user":{...}
        }
        - 200 OK: If the user is successfully updated, returns the updated user data.
        - 400 Bad Request: If no valid fields are provided.
        - 404 Not Found: If the user does not exist.
    """

    data = request.get_json()

    user = User.query.get(userid)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        # Update fields only if they are provided in the request
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        
        # Commit changes to the database
        sql.session.commit()

        return jsonify({"message": "User updated successfully", "user": {"id": user.id, "username": user.username, "email": user.email}}), 200
    
    except Exception as e:
        sql.session.rollback()  # Rollback if there is any error
        return jsonify({"error": str(e)}), 500