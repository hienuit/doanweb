from .auth_routes import auth_blueprint
from .main_routes import main_blueprint
from .api_routes import api_blueprint
from .media_routes import media_blueprint
from .images_routes import images_blueprint
from .loginfb_routes import loginfb_blueprint

# Danh sách tất cả blueprint để register trong create_app()
all_blueprints = [
    auth_blueprint,
    main_blueprint,
    api_blueprint,
    media_blueprint,
    images_blueprint,
    loginfb_blueprint
]