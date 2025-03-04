import pytest
from app import create_app
from app.extensions import mongo
from flask import json
from bson import ObjectId

@pytest.fixture
def client():
    """Setup test client and configure in-memory database."""
    app = create_app('test')
    # app.config["TESTING"] = True
    # app.config["MONGO_URI"] = "mongodb+srv://naveen:dbpasscode@cluster0.faokq.mongodb.net/testdata?retryWrites=true&w=majority&appName=Cluster0"  # Use a test DB
    
    with app.test_client() as client:
        with app.app_context():
            # Clear test database before each test
            mongo.db.users.delete_many({})
            mongo.db.portfolio.delete_many({})

            client.inserted_id = mongo.db.users.insert_one({"username": "alice", "email": "alice@example.com"}).inserted_id

        yield client  # Return test client
'''
def test_get_stock_search(client):
    """Test GET /stock/search/<query> to fetch stock search."""
    response = client.get("/stock/search/AAPL")
    
    assert response.status_code == 200
    assert response.json['bestMatches'] != [] # Expecting search response with results.
'''
def test_get_intraday(client):
    """Test GET /stock/intraday to fetch stock search."""
    response = client.get("/stock/intraday/AAPL")
    assert response.status_code == 200
    assert "Meta Data" in response.json and "Time Series (5min)" in response.json # Expecting search response with results.

def test_get_portfolio(client):
    """Test GET /stock/portfolio/ to fetch portfolio data."""
    
    mongo.db.portfolio.insert_one({
        "user_id":ObjectId(client.inserted_id),
        "ticker":"AAPL",
        "cost_price":1000,
        "quantity":10,
    })

    response = client.get("/stock/portfolio/"+str(client.inserted_id))
    assert response.status_code == 200
    assert 'user_id' not in response.json[0] # Expecting search response with results.
    assert 'ticker' in response.json[0]
    assert 'cost_price' in response.json[0]
    assert 'quantity' in response.json[0]

def test_buy_stock(client):
    """Test POST /stock/buystock to buy shares in a stock."""
    
    buy_stock = {
        "user_id":ObjectId(client.inserted_id),
        "ticker":"AAPL",
        "quantity":10,
    }
    response = client.post('/stock/buystock',json=buy_stock)

    assert response.status_code == 200
    assert response.json['message'] == "Stock added" # Expecting search response with results.
    assert 'cost' in response.json

def test_sell_stock(client):
    """Test POST /stock/sellstock to sell shares in a stock."""
    sell_stock = {
        "user_id":ObjectId(client.inserted_id),
        "ticker":"AAPL",
        "quantity":10,
        "cost_price":1000
    }
    mongo.db.portfolio.insert_one(sell_stock)

    response = client.post('/stock/sellstock',json=sell_stock)

    assert response.status_code == 200
    assert response.json['message'] == "stock sold!" # Expecting sale with success msg.
    assert 'price of shares sold' in response.json

    """Test POST /stock/sellstock to sell more shares than available ."""
    
    response = client.post('/stock/sellstock',json=sell_stock)

    assert response.status_code == 400
    assert response.json['message'] == "Error! Insuffient share held in AAPL" # Expecting error

    """Test POST /stock/sellstock to sell shares in invalid stock."""
    sell_stock['ticker']= 'jjjkl'
    response = client.post('/stock/sellstock',json=sell_stock)

    assert response.status_code == 400
    assert response.json['message'] == "Error! No shares held in jjjkl" # Expecting error
