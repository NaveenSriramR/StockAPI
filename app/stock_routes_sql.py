from flask import Blueprint, jsonify, request, current_app 
import requests
from .extensions import sql
from .models import User,Portfolio,Order
from .extensions import mongo
from bson.objectid import ObjectId
# from .models import db, User

stock_blueprint = Blueprint('sqlapi', __name__)

@stock_blueprint.route('/search/<query>', methods=['GET'])
def stock_search(query):
    '''Searches market for stocks based on the query given.
    Args:   
        query (str): A stock's ticker name (partial or full) as a string.

    Returns:
        JSON response:
        - 200 OK: Returns a json containing a list of stocks(as Json objects ) under the key "bestMatches".
        eg: 
        {"bestMatches": [
        {
            "1. symbol": "AAPL",
            "2. name": "Apple Inc",
            "3. type": "Equity",
            "4. region": "United States",
            "5. marketOpen": "09:30",
            "6. marketClose": "16:00",
            "7. timezone": "UTC-04",
            "8. currency": "USD",
            "9. matchScore": "1.0000"
        },
        {
            "1. symbol": "AAPL.TRT",
            "2. name": "Apple CDR (CAD Hedged)",
            "3. type": "Equity",
            ...
        },
        ..,
        ]} 
        - If no portfolio is found, returns an empty list.

    '''

    url = current_app.config['API_URL']+'function=SYMBOL_SEARCH&keywords='+query+'&apikey='+current_app.config['STOCK_API_KEY']
    response = requests.get(url)
    return response.json()    

@stock_blueprint.route('/info/<ticker>', methods=['GET'])
def get_stock_info(ticker):
    ''' Returns Intraday prices for a stock in 5mins intervals.
        Includes Meta-data and values like high, low, open, close and volume for that interval.
        Output format similar to 'daily' route.

        Args:
        'frequency': frequency of prices to be displayed. ('INTRADAY','DAILY')
        
        Returns:
            Meta of the stock and price information for frequency specified
        Eg:
        {
            "Meta Data":{...} ,
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
    data = request.get_json()
    if data['frequency'] == None:
        return jsonify({ "error": "Frequency not specified"})
    if data['frequency'] not in ['INTRADAY','DAILY']:
        return jsonify({ "error": "Invalid frequency", "frequency":data['frequency']})
    url = (current_app.config['API_URL'] +
            'function=TIME_SERIES_'+data['frequency']+'&symbol='+ticker+'&interval=5min&apikey=' +
            current_app.config['STOCK_API_KEY'])
    
    response = requests.get(url)
    return response.json()    

@stock_blueprint.route('/history/<ticker>', methods=['GET'])
def get_history(ticker):
    ''' Returns information on expired Options contracts 
        
        Args:
            ticker (str): Ticker name of the share to be searched.
        
        Returns:
            Returns a JSON containing the keys "Time Series (5min)" and "Meta Data" about the stock ticker.

    '''

    url = current_app.config['API_URL']+'function=HISTORICAL_OPTIONS&symbol='+ticker+'&date=2025-02-20&&apikey='+current_app.config['STOCK_API_KEY']
    response = requests.get(url)
    return response.json(), 200


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
    if not ObjectId.is_valid(userid):
        return jsonify({'error':"Invalid ObjectId"}), 400
    portfolio = mongo.db.portfolio.find({'user_id':ObjectId(userid)},{'user_id':0,'_id':0})
    return jsonify(portfolio),200

@stock_blueprint.route('/orders', methods=['POST'])
def create_orders():
    ''' Adds a stock order with the current ticker price and updates portfolio.

        Required parameters:
            action: string mentioning 'buy' or 'sell' to denote the action for the order
            ticker: stock ticker name (string),
            quantity: quantity (int),
            user_id: user id in (string)
        
        Returns:
            A JSON containing a success or error message with relevant information.
    '''
    data = request.get_json()

    # fetching current ticker price for the stock.
    url = current_app.config['API_URL']+'function=GLOBAL_QUOTE&symbol='+data['ticker']+'&apikey='+current_app.config['STOCK_API_KEY']
    api_response = requests.get(url).json()
    stock_price = float(api_response['Global Quote']['05. price'])

    try:
        # portfolio_data = mongo.db.portfolio.find_one( { "user_id":ObjectId(data['user_id']),'ticker':data['ticker']})    
        portfolio_data = Portfolio.query.get({'user_id':data['user_id'], 'ticker':data['ticker']})

        if data['action'] == 'buy':
            if portfolio_data == None:
                new_quantity = data['quantity'] 
                new_cost_price = data['quantity']*stock_price 
            else:
                new_quantity = data['quantity'] + portfolio_data.quantity
                new_cost_price = data['quantity']*stock_price + portfolio_data.cost_price

        elif data['action'] == 'sell':
            
            if portfolio_data == None:
                return jsonify({ "error": "No shares held in the stock" }), 400    
            if portfolio_data.quantity < data['quantity']:
                return jsonify({ "error": "Insufficient quantity!", "quantity available": portfolio_data.quantity }), 400
            
            new_quantity = data['quantity'] - portfolio_data.quantity
            new_cost_price = portfolio_data.quantity * portfolio_data.cost_price + data['quantity']*stock_price

        else:
            return jsonify({"error":"Invalid action!","action":data['action'] }), 400

        # inserts order data into a separate orders collection
        # order_id = mongo.db.orders.insert_one({**data, "user_id": ObjectId(data['user_id']), "price": stock_price }).inserted_id
        new_order = Order(ticker = data['ticker'], 
                            price = stock_price, 
                            quantity = data['quantity'], 
                            user_id = data['user_id'], 
                            action = data['action'])

        sql.session.add(new_order)

        if portfolio_data == None:
            portfolio = Portfolio(user_id=data['user_id'], ticker=data['ticker'], cost_price=new_cost_price, quantity=new_quantity)
            sql.session.add(portfolio)

        else:
            portfolio.cost_price = new_cost_price
            portfolio.quantity = new_quantity
            # updates portfolio to reflect newly purchased stocks
            # mongo.db.portfolio.update_one({"user_id":ObjectId(data['user_id']),'ticker':data['ticker']},
                                            # {   
                                            #     '$set':{'quantity':new_quantity,
                                            #             'cost_price':new_cost_price
                                            #             }
                                            # },upsert=True)
        sql.session.commit()
        return jsonify({"message": "Order added and portfolio updated!", 
                        "order ID": new_order.id,
                        "ticker": data['ticker'],
                        "action":data['action'],
                        "quantity": data['quantity'], 
                        "order price": stock_price }), 201
    except Exception as e:
        sql.session.rollback()
        return jsonify({"error":str(e)}), 500
    
'''
@stock_blueprint.route('/orders', methods=['POST'])
def sell_stock():
    # stock's shares from a user's portfolio.

    # Required parameters:
    #     ticker: stock ticker name (string),
    #     quantity: quantity (int),
    #     'user_id': user id in (string)
    
    data = request.get_json()
    stock_data = mongo.db.portfolio.find_one( { "user_id":ObjectId(data['user_id']),'ticker':data['ticker']})
    
    # Checking for stock in portfolio
    if stock_data == None:
        return jsonify({"message":"Error! No shares held in "+data['ticker']}),400
    
    if stock_data['quantity'] < data['quantity']:
        return jsonify({"message":"Error! Insuffient share held in "+data['ticker']}),400

    # adds the sell order to orders collection
    mongo.db.orders.insert_one({**data, "user_id":ObjectId(data['user_id'])})

    # fetches current price of the ticker to calculate profit from purchase
    url = current_app.config['API_URL']+'function=GLOBAL_QUOTE&symbol='+data['ticker']+'&apikey='+current_app.config['STOCK_API_KEY']
    api_response = requests.get(url).json()

    # Updates portfolio to reflect sale
    mongo.db.portfolio.update_many( { "user_id":ObjectId(data['user_id']),'ticker':data['ticker']},
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
'''
@stock_blueprint.route('/orders/<userid>', methods=['GET'])
def get_order(userid):
    ''' Returns information on expired Options contracts 
        
        Args:
            userid (str): ObjectId of the user as a string.
        
        Returns:
            List of json objects containing order information.

    '''
    orders = Order.query.filter_by(user_id = userid)
    # orders  = mongo.db.orders.find({"user_id":ObjectId(userid)},
    #                                             { "orderDate": { "$convert": { "input": "$_id", "to": "date" } },
    #                                                 "ticker": 1,
    #                                                 "quantity": 1,
    #                                                 "price": 1
    #                                                 }) 
    order_list = [{"id": order.id, 
                    "ticker": order.ticker, 
                    "price" : order.price,
                    "quantity" : order.quantity, 
                    "user_id" : order.user_id, 
                    "action" : order.action,
                    "created_at": order.created_at} for order in orders]
    
    return jsonify(order_list), 200
