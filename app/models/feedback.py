from app import db
from datetime import datetime

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user2.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, responded, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    response = db.Column(db.Text)
    response_at = db.Column(db.DateTime)
    
    # Relationship
    user = db.relationship('Users', backref=db.backref('feedbacks', lazy=True))

    def __repr__(self):
        return f'<Feedback {self.subject}>' 