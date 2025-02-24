from flask import Flask
from .config import Config
# from .extensions import db, migrate, cors
from .routes import api_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    # db.init_app(app)
    # migrate.init_app(app, db)
    # cors.init_app(app)
    @app.route('/', methods=['GET'])
    def get_hello():
        
        return "Ye the server is working!!"

    # Register blueprints
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app