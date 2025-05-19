from .. import db

class Users(db.Model):
    __tablename__ = "user2"
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), nullable=True)
    uname = db.Column(db.String(50), unique=True, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    sdt = db.Column(db.String(15), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)  # Thêm trường address
    position = db.Column(db.String(100), nullable=True)  # Thêm trường position
    gender = db.Column(db.String(20), nullable=True)  # Thêm trường gender
    birth_date = db.Column(db.String(50), nullable=True)  # Thêm trường birth_date để lưu ngày sinh

    
    def __init__(self, email, fname=None, uname=None, sdt=None, password=None, address=None, position=None, gender=None, birth_date=None):
        self.fname = fname
        self.uname = uname
        self.email = email
        self.sdt = sdt
        self.password = password
        self.address = address
        self.position = position
        self.gender = gender
        self.birth_date = birth_date


# Thêm vào users.py
class UserActivity(db.Model):
    __tablename__ = "user_activity"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user2.id'), nullable=False)
    activity = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    user = db.relationship('Users', backref=db.backref('activities', lazy=True))


    # Thêm hàm helper vào cuối file sau class UserActivity
def add_user_activity(user_id, activity, details=None):
    try:
        new_activity = UserActivity(
            user_id=user_id,
            activity=activity,
            details=details
        )
        db.session.add(new_activity)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error adding activity: {e}")
        return False