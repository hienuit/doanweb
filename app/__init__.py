from flask import Flask
from app.extension import db, mail, oauth, cors,init_oauth  # Import từ extensions.py
from config import Config
from app.models.users import Users  # Import models sau khi khởi tạo app
from app.models.destinations import Destinations, seed_destinations
from app.models.hotels import Hotel, seed_hotels
from flask_migrate import Migrate
from .routes import all_blueprints



def create_app(config_filename="config.py"):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY  
    
    # Khởi tạo các phần mở rộng
    db.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)
    cors.init_app(app)
    init_oauth(app)  # Khởi tạo OAuth với Flask app


    migrate = Migrate(app, db)

    with app.app_context():  # Đảm bảo Flask đang chạy trong context này
        seed_destinations()
        seed_hotels()
    
    for bp in all_blueprints:
        app.register_blueprint(bp)

    return app

    # Import và đăng ký Blueprints (module) cho từng tính năng
    # from .auth import auth_blueprint
    # app.register_blueprint(auth_blueprint)




    
    