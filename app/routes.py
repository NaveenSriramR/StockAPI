from flask import Blueprint, jsonify, request, current_app 
import requests
# from .models import db, User

api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/hello', methods=['GET'])
def get_hello():
    return "Ye the server is working!!"

@api_blueprint.route('/intraday', methods=['GET'])
def get_intraday():
    url = current_app.config['API_URL']+'function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey='+current_app.config['STOCK_API_KEY']
    r = requests.get(url)
    return r.json()    

@api_blueprint.route('/daily', methods=['GET'])
def get_daily():
    url = current_app.config['API_URL']+'function=TIME_SERIES_DAILY&symbol=IBM&interval=5min&apikey='+current_app.config['STOCK_API_KEY']
    r = requests.get(url)
    return r.json()    

@api_blueprint.route('/history', methods=['GET'])
def get_history():
    
    url = current_app.config['API_URL']+'function=HISTORICAL_OPTIONS&symbol=IBM&date=2025-02-20&&apikey='+current_app.config['STOCK_API_KEY']
    r = requests.get(url)
    return r.json()    

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
