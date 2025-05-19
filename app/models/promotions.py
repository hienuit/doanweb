from .. import db
from datetime import datetime, timezone

class Promotion(db.Model):
    __tablename__ = 'promotions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    original_price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float, nullable=False)
    discount_percent = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    provider = db.Column(db.String(100), nullable=False)  # Nguồn cung cấp (VNTravel, Mytour, v.v.)
    booking_url = db.Column(db.String(255), nullable=False)  # URL để đặt vé
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.UTC))
    is_featured = db.Column(db.Boolean, default=False)  # Đánh dấu những ưu đãi nổi bật
    
    def __init__(self, title, description, destination, original_price, discount_price, 
                discount_percent, image_url, provider, booking_url, start_date, end_date, is_featured=False):
        self.title = title
        self.description = description
        self.destination = destination
        self.original_price = original_price
        self.discount_price = discount_price
        self.discount_percent = discount_percent
        self.image_url = image_url
        self.provider = provider
        self.booking_url = booking_url
        self.start_date = start_date
        self.end_date = end_date
        self.is_featured = is_featured
        
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'destination': self.destination,
            'original_price': self.original_price,
            'discount_price': self.discount_price,
            'discount_percent': self.discount_percent,
            'image_url': self.image_url,
            'provider': self.provider,
            'booking_url': self.booking_url,
            'start_date': self.start_date.strftime('%d-%m-%Y'),
            'end_date': self.end_date.strftime('%d-%m-%Y'),
            'is_featured': self.is_featured
        } 