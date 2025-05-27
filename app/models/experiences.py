from .. import db
from datetime import datetime
from ..utils import get_avatar_url

class Experience(db.Model):
    __tablename__ = 'experiences'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user2.id'), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 sao
    travel_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float)
    travel_style = db.Column(db.String(50))  # solo, couple, family, group
    travel_duration = db.Column(db.Integer)  # số ngày
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('Users', backref=db.backref('experiences', lazy=True))
    images = db.relationship('ExperienceImage', back_populates='experience', cascade="all, delete-orphan")
    comments = db.relationship('ExperienceComment', back_populates='experience', cascade="all, delete-orphan")
    likes_rel = db.relationship('ExperienceLike', back_populates='experience', cascade="all, delete-orphan")
    
    def __init__(self, user_id, destination, title, content, rating, travel_date, 
                 budget=None, travel_style=None, travel_duration=None):
        self.user_id = user_id
        self.destination = destination
        self.title = title
        self.content = content
        self.rating = rating
        self.travel_date = travel_date
        self.budget = budget
        self.travel_style = travel_style
        self.travel_duration = travel_duration
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.fname if self.user.fname else self.user.email.split('@')[0],
            'user_avatar': get_avatar_url(self.user.avatar_url) or '/static/images/default-avatar.png',
            'destination': self.destination,
            'title': self.title,
            'content': self.content,
            'rating': self.rating,
            'travel_date': self.travel_date.strftime('%d/%m/%Y') if self.travel_date else None,
            'budget': self.budget,
            'travel_style': self.travel_style,
            'travel_duration': self.travel_duration,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
            'likes': self.likes,
            'views': self.views,
            'is_featured': self.is_featured,
            'images': [img.image_url for img in self.images],
            'comments_count': len(self.comments)
        }

class ExperienceImage(db.Model):
    __tablename__ = 'experience_images'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experience_id = db.Column(db.Integer, db.ForeignKey('experiences.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    experience = db.relationship('Experience', back_populates='images')

class ExperienceComment(db.Model):
    __tablename__ = 'experience_comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experience_id = db.Column(db.Integer, db.ForeignKey('experiences.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user2.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    experience = db.relationship('Experience', back_populates='comments')
    user = db.relationship('Users', backref=db.backref('experience_comments', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user.fname if self.user.fname else self.user.email.split('@')[0],
            'user_avatar': get_avatar_url(self.user.avatar_url) or '/static/images/default-avatar.png',
            'content': self.content,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M')
        }

class ExperienceLike(db.Model):
    __tablename__ = 'experience_likes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experience_id = db.Column(db.Integer, db.ForeignKey('experiences.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user2.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    experience = db.relationship('Experience', back_populates='likes_rel')
    user = db.relationship('Users', backref=db.backref('experience_likes', lazy=True))
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('experience_id', 'user_id', name='unique_experience_like'),) 