from flask import Flask
from .config import TestConfig, DevConfig
from .extensions import mongo, cors
from .stock_routes import stock_blueprint
from .user_routes import user_blueprint

def create_app(config_mode):
    app = Flask(__name__)
    
    if config_mode == 'test':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(DevConfig)
    
    # Initialize extensions
    mongo.init_app(app)
    cors.init_app(app)

    @app.route('/', methods=['GET'])
    def get_hello():    
        return "Ye the server is working!!"

    # Register blueprints
    app.register_blueprint(stock_blueprint, url_prefix='/stock')
    app.register_blueprint(user_blueprint, url_prefix='/users')

    return app