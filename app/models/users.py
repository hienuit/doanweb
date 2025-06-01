from .. import db
from datetime import datetime

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Thêm trường created_at
    
    # Thêm các trường cho OAuth
    facebook_id = db.Column(db.String(100), unique=True, nullable=True)  # Facebook ID
    provider = db.Column(db.String(50), nullable=True, default='local')  # Nhà cung cấp: 'local', 'facebook', 'google'
    avatar_url = db.Column(db.String(1000), nullable=True)  # Tăng độ dài lên 1000 ký tự

    @property
    def name(self):
        """Return user's name, fallback to username if fname is not set"""
        return self.fname or self.uname or self.email

    def __init__(self, email=None, fname=None, uname=None, sdt=None, password=None, address=None, position=None, gender=None, birth_date=None, facebook_id=None, provider='local', avatar_url=None):
        self.fname = fname
        self.uname = uname
        self.email = email
        self.sdt = sdt
        self.password = password
        self.address = address
        self.position = position
        self.gender = gender
        self.birth_date = birth_date
        self.facebook_id = facebook_id
        self.provider = provider
        self.avatar_url = avatar_url

    @staticmethod
    def generate_unique_username(base_name):
        """Tạo username duy nhất từ tên"""
        import re
        # Chuyển tên thành dạng username hợp lệ
        username = re.sub(r'[^\w\s-]', '', base_name.lower())
        username = re.sub(r'[-\s]+', '_', username)
        
        # Kiểm tra xem username đã tồn tại chưa
        original_username = username
        counter = 1
        while Users.query.filter_by(uname=username).first() is not None:
            username = f"{original_username}_{counter}"
            counter += 1
        
        return username

    @staticmethod
    def find_by_facebook_id(facebook_id):
        """Tìm user theo Facebook ID"""
        return Users.query.filter_by(facebook_id=facebook_id).first()
    
    @staticmethod
    def find_by_email(email):
        """Tìm user theo email"""
        return Users.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_phone(phone):
        """Tìm user theo số điện thoại"""
        return Users.query.filter_by(sdt=phone).first()
    
    @staticmethod
    def create_facebook_user(facebook_data):
        """Tạo user mới từ dữ liệu Facebook"""
        try:
            # In ra dữ liệu nhận được từ Facebook để debug
            print("Facebook data received:", facebook_data)
            
            # Tạo username duy nhất từ tên người dùng
            name = facebook_data.get('name', 'user')
            username = Users.generate_unique_username(name)
            
            # Tạo user mới
            user = Users(
                fname=name,
                uname=username,
                email=facebook_data.get('email'),  # Lưu email từ Facebook
                facebook_id=facebook_data.get('id'),
                provider='facebook',
                avatar_url=facebook_data.get('picture', {}).get('data', {}).get('url') if facebook_data.get('picture') else None
            )
            
            # Log thông tin user trước khi lưu
            print("Attempting to create user:", {
                'fname': user.fname,
                'uname': user.uname,
                'email': user.email,
                'facebook_id': user.facebook_id,
                'provider': user.provider,
                'avatar_url': user.avatar_url
            })
            
            db.session.add(user)
            db.session.commit()
            
            print("User created successfully with ID:", user.id)
            return user
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating Facebook user: {str(e)}")
            # Log chi tiết lỗi
            import traceback
            traceback.print_exc()
            return None


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