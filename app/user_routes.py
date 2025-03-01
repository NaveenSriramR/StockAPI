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
    return jsonify(users)

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
    print(id)
    user = mongo.db.users.find_one({"_id":ObjectId(id)})
                            #    ,{"_id": {"$toString": "$_id"},"email":1,"username":1})  # Projects user data with _id converted to String from ObjectId

    if user == None:
        return jsonify({'message':"No user found!"}),404
    
    return jsonify(user)


# Create a new user
@user_blueprint.route('/adduser', methods=['POST'])
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
    inserted_id = mongo.db.users.insert_one(new_user).inserted_id

    return jsonify({"id": str(inserted_id), **new_user}), 201

@user_blueprint.route('/updateuser/<userid>', methods=['PUT'])
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
        - 200 OK: If the user is successfully updated, returns the updated user data.
        - 400 Bad Request: If no valid fields are provided.
        - 404 Not Found: If the user does not exist.
    """

    data = request.get_json()

    # Ensure there is at least one field to update
    if not data:
        return jsonify({"error": "No data provided for update"}), 400

    # Remove empty values from update data
    update_fields = {key: value for key, value in data.items() if value}
    
    if not update_fields:
        return jsonify({"error": "No valid fields to update"}), 400

    # Find and update the user
    result = mongo.db.users.find_one_and_update(
        {"_id": ObjectId(userid)},
        {"$set": update_fields},
        return_document=True  # Returns the updated document
    )

    if result:
        result["_id"] = str(result["_id"])  # Convert ObjectId to string
        return jsonify({"message": "User updated successfully", "user": result}), 200

    return jsonify({"error": "User not found"}), 404


@user_blueprint.route('/deleteuser/<userid>', methods=['DELETE'])
def delete_user(userid):
    """
    Delete a user by their ID.

    Args:
        userid (str): The ObjectId of the user as a string.

    Returns:
        JSON response:
        - 200 OK: If the user is successfully deleted.
        - 404 Not Found: If the user does not exist.
    """

     
    result = mongo.db.users.delete_one({"_id": ObjectId(userid)})

    if result.deleted_count > 0:
        return jsonify({"message": "User deleted successfully"}), 200

    return jsonify({"error": "User not found"}), 404