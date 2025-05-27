from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        print(f"Password hash generated: {self.password_hash[:20]}...")  # Debug: In ra một phần của hash
        
    def check_password(self, password):
        if not self.password_hash:
            print("No password hash found!")  # Debug
            return False
        result = check_password_hash(self.password_hash, password)
        print(f"Password check - Hash in DB: {self.password_hash[:20]}...")  # Debug
        print(f"Password check result: {result}")  # Debug
        return result
        
    def __repr__(self):
        return f'<Admin {self.email}>' 