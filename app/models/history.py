from .. import db
import json
from datetime import datetime

class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    activity_names = db.Column(db.Text, nullable=False)  # Danh sách địa điểm (JSON) - deprecated nhưng giữ để tương thích
    days = db.Column(db.Integer, nullable=False)
    total_cost = db.Column(db.String(50), nullable=False)  # 👈 Đổi từ Float sang String
    destination = db.Column(db.String(255), nullable=True)
    # Thêm cột mới để lưu toàn bộ itinerary data
    full_itinerary_data = db.Column(db.Text, nullable=True)  # Lưu toàn bộ dữ liệu lịch trình chi tiết (JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, activity_names, days, total_cost, destination=None, full_itinerary_data=None):
        self.user_id = user_id
        self.activity_names = activity_names
        self.days = days
        self.total_cost = total_cost
        self.destination = destination
        self.full_itinerary_data = full_itinerary_data

    def to_dict(self):
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'activity_names': json.loads(self.activity_names),
            'days': self.days,
            'total_cost': self.total_cost,
            'destination': self.destination,
            'created_at': self.created_at.strftime('%d-%m-%Y'),
        }
        
        # Thêm full_itinerary_data nếu có
        if self.full_itinerary_data:
            try:
                result['full_itinerary_data'] = json.loads(self.full_itinerary_data)
            except (json.JSONDecodeError, TypeError):
                result['full_itinerary_data'] = None
                
        return result
