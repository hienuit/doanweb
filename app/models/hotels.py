from .. import db

class Hotel(db.Model):
    __tablename__ = "hotels"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    province_name = db.Column(db.String(100), nullable=False)
    hotel_name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    user_ratings_total = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    images = db.relationship('HotelImage', back_populates='hotel', cascade="all, delete-orphan")
    

    def __init__(self, province_name, hotel_name, latitude, longitude, rating, user_ratings_total, description):
        self.province_name = province_name
        self.hotel_name = hotel_name
        self.latitude = latitude
        self.longitude = longitude
        self.rating = rating
        self.user_ratings_total = user_ratings_total
        self.description = description
    def to_dict(self):
        return {
            'id': self.id,
            'hotel_name': self.hotel_name,
            'province_name': self.province_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'rating': self.rating,
            'user_ratings_total': self.user_ratings_total,
            'description': self.description
        }
class HotelImage(db.Model):
    __tablename__ = 'hotel_images'

    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

    hotel = db.relationship('Hotel', back_populates='images')
# Thêm dữ liệu mẫu khi app khởi động
def seed_hotels():
    if Hotel.query.first() is None:  # Kiểm tra xem đã có dữ liệu chưa
        sample_hotels = [
            Hotel(province_name="Hà Nội", hotel_name="Sofitel Legend Metropole Hotel", latitude=21.025611, longitude=105.856306, rating=4.7, user_ratings_total=120, description="Khách sạn 5 sao sang trọng, dịch vụ tuyệt vời, vị trí trung tâm Hà Nội"),
            Hotel(province_name="Hà Nội", hotel_name="Capella", latitude=21.02590665609475, longitude=105.8565920357642, rating=4.8, user_ratings_total=200, description="Khách sạn cao cấp, thiết kế độc đáo, không gian hiện đại và sang trọng"),
            Hotel(province_name="Hà Nội", hotel_name="Peridot Grand Luxury Boutique Hotel", latitude=21.03320214869202, longitude=105.8462934529626, rating=4.8, user_ratings_total=150, description="Khách sạn boutique sang trọng, dịch vụ hoàn hảo và vị trí lý tưởng"),
            Hotel(province_name="Hà Nội", hotel_name="GRAND HOTEL du LAC Hanoi", latitude=21.02852953841653, longitude=105.84967675296248, rating=4.8, user_ratings_total=180, description="Khách sạn cổ điển với không gian sang trọng, vị trí trung tâm Hà Nội"),
            Hotel(province_name="Hà Nội", hotel_name="Green Hotel Ha Noi", latitude=21.033606032272235, longitude=105.81129442412639, rating=3.6, user_ratings_total=50, description="Khách sạn giá rẻ, tiện nghi cơ bản nhưng không gian thoải mái"),
            Hotel(province_name="Hồ Chí Minh", hotel_name="Saigon Hotel", latitude=10.776111237219034, longitude=106.70443703370766, rating=4.0, user_ratings_total=100, description="Khách sạn trung tâm Sài Gòn, gần các điểm tham quan nổi tiếng"),
            Hotel(province_name="Hồ Chí Minh", hotel_name="C Central Hotel", latitude=10.767878647344324, longitude=106.69399576625067, rating=3.3, user_ratings_total=30, description="Khách sạn giá rẻ, dịch vụ chưa đạt kỳ vọng"),
            Hotel(province_name="Hồ Chí Minh", hotel_name="Boutique Hotel", latitude=10.767824781103736, longitude=106.69450099747952, rating=3.3, user_ratings_total=40, description="Khách sạn nhỏ với tiện nghi cơ bản, không gian bình thường"),
            Hotel(province_name="Hồ Chí Minh", hotel_name="New Sunny Hotel", latitude=10.767968428543279, longitude=106.69444936573329, rating=3.2, user_ratings_total=25, description="Khách sạn giá thấp, chất lượng dịch vụ chưa tốt"),
            Hotel(province_name="Hồ Chí Minh", hotel_name="Ben Thanh Retreats hotel", latitude=10.770435906471056, longitude=106.69071666625065, rating=4.6, user_ratings_total=150, description="Khách sạn sang trọng, gần chợ Bến Thành, dịch vụ tuyệt vời"),
            Hotel(province_name="Đà Nẵng", hotel_name="DLG Hotel Danang", latitude=16.058584327338494, longitude=108.24660305284446, rating=4.5, user_ratings_total=100, description="Khách sạn tiện nghi, gần bãi biển, dịch vụ ổn"),
            Hotel(province_name="Đà Nẵng", hotel_name="Salmalia Boutique Hotel & Spa", latitude=16.06092412563959, longitude=108.24528945099105, rating=4.8, user_ratings_total=120, description="Khách sạn boutique sang trọng, spa thư giãn tuyệt vời"),
            Hotel(province_name="Đà Nẵng", hotel_name="Hilton Đà Nẵng", latitude=16.072810817005223, longitude=108.22432891051719, rating=4.5, user_ratings_total=130, description="Khách sạn hiện đại, sang trọng, view đẹp ra sông Hàn"),
            Hotel(province_name="Đà Nẵng", hotel_name="Meliá Vinpearl Danang Riverfront", latitude=16.071266418127546, longitude=108.22941190866378, rating=4.9, user_ratings_total=200, description="Khách sạn cao cấp, dịch vụ đẳng cấp quốc tế, view đẹp"),
            Hotel(province_name="Đà Nẵng", hotel_name="Lychee Hotel", latitude=16.075961542607974, longitude=108.20695532586215, rating=4.8, user_ratings_total=110, description="Khách sạn tiện nghi, gần bãi biển, chất lượng dịch vụ tốt"),
            Hotel(province_name="Quảng Ninh", hotel_name="Citadines Marina Halong", latitude=20.95380767067663, longitude=107.0132413106329, rating=4.5, user_ratings_total=80, description="Khách sạn hiện đại, gần Vịnh Hạ Long, view đẹp"),
            Hotel(province_name="Quảng Ninh", hotel_name="HARMONY HALONG HOTEL", latitude=20.951702814359358, longitude=107.10018011063279, rating=4.4, user_ratings_total=60, description="Khách sạn gần bãi biển, không gian yên tĩnh, dịch vụ ổn"),
            Hotel(province_name="Quảng Ninh", hotel_name="Indotel Halong Hotel", latitude=20.947897837151064, longitude=107.02680158179649, rating=4.4, user_ratings_total=70, description="Khách sạn gần trung tâm Hạ Long, dịch vụ khá tốt"),
            Hotel(province_name="Quảng Ninh", hotel_name="KL Hotel Marina Square", latitude=20.955565256763258, longitude=107.00142333847697, rating=4.8, user_ratings_total=90, description="Khách sạn cao cấp, vị trí thuận tiện, dịch vụ tốt"),
            Hotel(province_name="Quảng Ninh", hotel_name="Marina Square Hạ Long", latitude=20.956700067403954, longitude=107.0017247632112, rating=4.3, user_ratings_total=50, description="Khách sạn trung bình, dịch vụ khá tốt nhưng cần cải thiện một số điểm"),
            Hotel(province_name="Kiên Giang", hotel_name="Wyndham Grand Phú Quốc", latitude=10.330267803873395, longitude=103.85532282391777, rating=4.9, user_ratings_total=220, description="Khách sạn 5 sao, dịch vụ đẳng cấp, gần biển Phú Quốc"),
            Hotel(province_name="Kiên Giang", hotel_name="Vinpearl Resort & Spa Phú Quốc", latitude=10.331551261989917, longitude=103.85263323318513, rating=4.9, user_ratings_total=250, description="Khách sạn cao cấp, tiện nghi hiện đại, dịch vụ tuyệt vời"),
            Hotel(province_name="Kiên Giang", hotel_name="Minh Phu Quoc Hotel", latitude=10.116116782743786, longitude=103.98207802391546, rating=4.0, user_ratings_total=90, description="Khách sạn bình dân, sạch sẽ, dịch vụ tốt nhưng cần nâng cấp cơ sở vật chất"),
            Hotel(province_name="Kiên Giang", hotel_name="Rosa Hotel Phú Quốc", latitude=10.210263673945173, longitude=103.96269179322681, rating=4.8, user_ratings_total=150, description="Khách sạn mới, không gian thoáng đãng, dịch vụ chất lượng"),
            Hotel(province_name="Kiên Giang", hotel_name="Lotus Home", latitude=10.220554768808997, longitude=104.07207050857173, rating=4.7, user_ratings_total=110, description="Khách sạn nhỏ, giá rẻ nhưng chất lượng dịch vụ tốt"),
        ]
        
        db.session.bulk_save_objects(sample_hotels)  # Bulk insert for efficiency
        db.session.commit()
        print("✅ Đã thêm dữ liệu mẫu vào bảng Hotels!")



def get_hotels_by_province(province_name):
    # Query the database for hotels in the given province
    hotels = Hotel.query.filter_by(province_name=province_name).all()
    print(hotels)
    return hotels

