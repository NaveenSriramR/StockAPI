from flask import Blueprint, jsonify, request, current_app 
import requests
from .extensions import mongo
from bson.objectid import ObjectId
# from .models import db, User

stock_blueprint = Blueprint('api', __name__)

@stock_blueprint.route('/search/<query>', methods=['GET'])
def search_stock(query):
    '''Searches market for stocks based on the query given.
    '''

    url = current_app.config['API_URL']+'function=SYMBOL_SEARCH&keywords='+query+'&apikey='+current_app.config['STOCK_API_KEY']
    response = requests.get(url)
    return response.json()    

@stock_blueprint.route('/intraday', methods=['GET'])
def get_intraday():
    ''' Returns Intraday prices for a stock in 5mins intervals.
        Includes Meta-data and values like high, low, open, close and volume for that interval.
         Output format similar to 'daily' route.
    '''

    url = (current_app.config['API_URL'] +
            'function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=' +
            current_app.config['STOCK_API_KEY'])
    
    response = requests.get(url)
    return response.json()    

@stock_blueprint.route('/daily', methods=['GET'])
def get_daily():
    ''' Returns daily prices for a stock.
    Includes Meta-data and values like high, low, open, close and volume for that interval.
    Eg:
    {"Meta Data":{...} ,
     "Time Series (5min)": {
    "2025-02-25 19:55:00": {
      "1. open": "258.6500",
      "2. high": "258.6600",
      "3. low": "258.0472",
      "4. close": "258.0472",
      "5. volume": "28"
    },
    ...}
    '''

    url = current_app.config['API_URL']+'function=TIME_SERIES_DAILY&symbol=IBM&interval=5min&apikey='+current_app.config['STOCK_API_KEY']
    response = requests.get(url)
    return response.json()    

@stock_blueprint.route('/history', methods=['GET'])
def get_history():
    ''' Returns information on expired Options contracts '''

    url = current_app.config['API_URL']+'function=HISTORICAL_OPTIONS&symbol=IBM&date=2025-02-20&&apikey='+current_app.config['STOCK_API_KEY']
    r = requests.get(url)
    return r.json()    

################### pending correction
@stock_blueprint.route('/portfolio/<userid>', methods=['GET'])
def get_portfolio(userid):
    '''
    Args:
        userid (str): The ObjectId of the user as a string.

    Returns:
        JSON response:
        - 200 OK: If the user's portfolio is found, returns a list of stocks.
        - If no portfolio is found, returns an empty list.

    Example Response:
    [
        {
            "ticker": "TSCO.LON",
            "quantity": 8.0,
            "cost_price": 1600.0
        },
        {
            "ticker": "AAPL",
            "quantity": 5.0,
            "cost_price": 150.0
        }
    ]
    '''
    portfolio = mongo.db.portfolio.find({'user_id':ObjectId(userid)},{'user_id':0,'_id':0})
    return jsonify(portfolio)

@stock_blueprint.route('/buystock', methods=['POST'])
def buy_stock():
    ''' Adds a stock's shares to a user's portfolio.
        Adds quantity to stock's qua
        Required parameters:
        stock: stock ticker name (string),
        quantity: quantity (int),
        'user_id': user id in (string)
    
    '''

    data = request.get_json()

    # fetching current ticker price for the stock.
    url = current_app.config['API_URL']+'function=GLOBAL_QUOTE&symbol='+data['stock']+'&apikey='+current_app.config['STOCK_API_KEY']
    api_response = requests.get(url).json()
    stock_price = float(api_response['Global Quote']['05. price'])
    
    mongo.db.portfolio.update_one({"user_id":ObjectId(data['user_id']),'ticker':data['stock']},
                                    {   
                                        # '$set':{'ticker': data['stock']},
                                        '$inc':{'quantity':data['quantity'],
                                                'cost_price':data['quantity']*stock_price 
                                                }
                                    },upsert=True)
    return jsonify({"message":"Stock added","cost":data['quantity']*stock_price })

@stock_blueprint.route('/sellstock', methods=['POST'])
def sell_stock():
    ''' Sells a stock's shares from a user's portfolio.
    Required parameters:
        stock: stock ticker name (string),
        quantity: quantity (int),
        'user_id': user id in (string)
    '''
    data = request.get_json()
    stock_data = mongo.db.portfolio.find_one( { "user_id":ObjectId(data['user_id']),'ticker':data['stock']})
    
    # Checking for stock in portfolio
    if stock_data == None:
        return jsonify({"message":"Error! No shares held in "+data['stock']}),404
    
    if stock_data['quantity'] < data['quantity']:
        return jsonify({"message":"Error! Insuffient share held in "+data['stock']}),400

    url = current_app.config['API_URL']+'function=GLOBAL_QUOTE&symbol='+data['stock']+'&apikey='+current_app.config['STOCK_API_KEY']
    api_response = requests.get(url).json()

    mongo.db.portfolio.update_many( { "user_id":ObjectId(data['user_id']),'ticker':data['stock']},
                                    [

                                    # Updates cost_price to reflect original cost of remaining using the formula below,
                                    # cost_price = cost_price * (quantity_held-quantity_sold)/quantity_held
                                    {'$replaceWith':{ 
                                    '$setField':{'field':'cost_price',
                                                    'input':'$$ROOT',
                                                    'value':{'$multiply':['$cost_price',
                                                                            {'$divide':[
                                                                                {'$subtract':['$quantity',data['quantity']]},
                                                                                '$quantity'
                                                                                ]}  
                                                                        ]
                                                            }
                                                },
                                    }},
                                    
                                    # Updates quantity to reflect sale in shares
                                    {  '$replaceWith':{ 
                                    '$setField':{'field':'quantity',
                                                    'input':'$$ROOT',
                                                    'value':{'$subtract':['$quantity',data['quantity']]}
                                    },
                                    }}
                                    
                                    ],)

    return jsonify({"message":"stock sold!",
                    "price of shares sold":data['quantity']*float(api_response['Global Quote']['05. price'])})

