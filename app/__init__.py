from flask import Flask
from app.extension import db, mail, oauth, cors, init_oauth  # Import từ extensions.py
from config import Config
from app.models.users import Users  # Import models sau khi khởi tạo app
from app.models.destinations import seed_destinations
from flask_migrate import Migrate
from app.routes import all_blueprints
from flask_login import LoginManager


migrate = Migrate()
login_manager = LoginManager()

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

    migrate.init_app(app, db)
    
    # Cấu hình login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_page'  # Đổi về user login
    login_manager.login_message = 'Vui lòng đăng nhập để truy cập trang này.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        try:
            # Thử tìm trong bảng Users trước
            user = Users.query.get(int(user_id))
            if user:
                return user
            # Nếu không tìm thấy, thử tìm trong bảng Admin
            from app.admin.models import Admin
            return Admin.query.get(int(user_id))
        except:
            return None

    with app.app_context():
        db.create_all()  # Tạo tất cả bảng trong database
        seed_destinations()
        
        # Tạo tài khoản admin mặc định nếu chưa có
        from app.admin.models import Admin
        admin = Admin.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = Admin(email='admin@example.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    # Đăng ký các blueprint
    for bp in all_blueprints:
        app.register_blueprint(bp)

    return app

    # Import và đăng ký Blueprints (module) cho từng tính năng
    # from .auth import auth_blueprint
    # app.register_blueprint(auth_blueprint)




    
    