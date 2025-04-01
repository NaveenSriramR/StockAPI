from .extensions import sql as db
from sqlalchemy.sql import func

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

    def __repr__(self):
        return f'<User {self.username}>'

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship definition (Optional, but useful for easy access)
    user = db.relationship('User', backref=db.backref('portfolios', lazy=True))

    def __repr__(self):
        return f'<Portfolio {self.ticker} - Quantity: {self.quantity}>'    

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(5), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

    # Relationship definition (Optional, but useful for easy access)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f'<Order {self.ticker} - Quantity: {self.quantity} - Action {self.action}>'      