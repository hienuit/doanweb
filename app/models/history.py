from .. import db
import json
from datetime import datetime

class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    activity_names = db.Column(db.Text, nullable=False)  # Danh sách địa điểm (JSON)
    days = db.Column(db.Integer, nullable=False)
    total_cost = db.Column(db.String(50), nullable=False)  # 👈 Đổi từ Float sang String
    destination = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, activity_names, days, total_cost, destination=None):
        self.user_id = user_id
        self.activity_names = activity_names
        self.days = days
        self.total_cost = total_cost
        self.destination = destination

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_names': json.loads(self.activity_names),
            'days': self.days,
            'total_cost': self.total_cost,
            'destination': self.destination,
            'created_at': self.created_at.strftime('%d-%m-%Y'),
        }
