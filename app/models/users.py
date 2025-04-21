from .. import db

class Users(db.Model):
    __tablename__ = "user2"
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), nullable=True)
    uname = db.Column(db.String(50), unique=True, nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    sdt = db.Column(db.String(15), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    
    def __init__(self, email, fname=None, uname=None, sdt=None, password=None):
        self.fname = fname
        self.uname = uname
        self.email = email
        self.sdt = sdt
        self.password = password
