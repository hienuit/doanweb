from .auth_routes import auth_blueprint
from .main_routes import main_blueprint
from .api_routes import api_blueprint
from .media_routes import media_blueprint
from .loginfb_routes import loginfb_blueprint
from .history_routes import histories_blueprint
# from .federated_routes import federated_blueprint
from .experience_routes import experience_blueprint
from .weather_routes import weather_blueprint
from .sitemap_routes import sitemap_blueprint
from app.admin import admin as admin_blueprint


# Danh sách tất cả blueprint để register trong create_app()
all_blueprints = [
    auth_blueprint,
    main_blueprint,
    api_blueprint,
    media_blueprint,
    loginfb_blueprint,
    histories_blueprint,
    # federated_blueprint,
    experience_blueprint,
    weather_blueprint,
    sitemap_blueprint,
    admin_blueprint
]