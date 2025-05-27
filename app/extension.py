from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from config import Config

db = SQLAlchemy()
mail = Mail()
oauth = OAuth()
cors = CORS()

google = oauth.register(
    name = 'google',
    client_id = Config.CLIENT_ID,
    client_secret = Config.CLIENT_SECRET,
    server_metadata_url = 'https://accounts.google.com/.well-known/openid-configuration', 
    client_kwargs = {'scope': 'openid email profile'}
)

def init_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name='facebook',
        client_id=Config.FACEBOOK_CLIENT_ID,
        client_secret=Config.FACEBOOK_CLIENT_SECRET,
        access_token_url='https://graph.facebook.com/v18.0/oauth/access_token',
        authorize_url='https://www.facebook.com/v18.0/dialog/oauth',
        api_base_url='https://graph.facebook.com/v18.0/',
        client_kwargs={
            'scope': 'public_profile,email',
            'response_type': 'code'
        }
    )