from flask import Flask
from .config import TestConfig, DevConfig
from .extensions import mongo, cors, sql
from .stock_routes import stock_blueprint
from .user_routes import user_blueprint
from .user_routes_sql import user_blueprint as user_sql_blueprint
from flask_migrate import Migrate

def create_app(config_mode):
    app = Flask(__name__)
    
    if config_mode == 'test':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(DevConfig)
    
    # Initialize extensions
    mongo.init_app(app)
    cors.init_app(app)
    sql.init_app(app)
    migrate = Migrate(app, sql)

    @app.route('/', methods=['GET'])
    def get_hello():    
        return "Ye the server is working!!"

    # Register mongo blueprints
    app.register_blueprint(stock_blueprint, url_prefix='/mongo/stocks') 
    app.register_blueprint(user_blueprint, url_prefix='/mongo/users')
    app.register_blueprint(user_sql_blueprint, url_prefix='/sql/users')

    return app

app = create_app('dev')

if __name__ == '__main__':
    app.run(debug=True)