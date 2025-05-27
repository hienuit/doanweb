from flask import Blueprint, jsonify, request, render_template
import requests
import os
from datetime import datetime

weather_blueprint = Blueprint('weather', __name__)

@weather_blueprint.route('/weather-demo')
def weather_demo():
    """Trang demo weather widget"""
    return render_template('weather_demo.html')

# API key cho OpenWeatherMap (bạn cần đăng ký tại openweathermap.org)
WEATHER_API_KEY = "fcf6c2e10d18ee9bdd022de688a5b57b"  # Sử dụng demo data khi không có API key
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"

# Cấu hình fallback - sử dụng demo data khi API thất bại
USE_DEMO_FALLBACK = True

# Demo weather data cho testing
DEMO_WEATHER_DATA = {
    "Hà Nội": {
        "temperature": 25,
        "feels_like": 27,
        "humidity": 65,
        "pressure": 1013,
        "description": "Trời nhiều mây",
        "icon": "fas fa-cloud",
        "wind_speed": 3.2,
        "wind_direction": 180,
        "visibility": 10,
        "sunrise": "06:15",
        "sunset": "18:30"
    },
    "Hồ Chí Minh": {
        "temperature": 32,
        "feels_like": 36,
        "humidity": 75,
        "pressure": 1010,
        "description": "Trời nắng",
        "icon": "fas fa-sun",
        "wind_speed": 2.5,
        "wind_direction": 90,
        "visibility": 15,
        "sunrise": "06:00",
        "sunset": "18:15"
    },
    "Đà Nẵng": {
        "temperature": 28,
        "feels_like": 31,
        "humidity": 70,
        "pressure": 1012,
        "description": "Trời ít mây",
        "icon": "fas fa-cloud-sun",
        "wind_speed": 4.1,
        "wind_direction": 120,
        "visibility": 12,
        "sunrise": "06:10",
        "sunset": "18:25"
    },
    "Nha Trang": {
        "temperature": 30,
        "feels_like": 33,
        "humidity": 68,
        "pressure": 1011,
        "description": "Trời nắng ít mây",
        "icon": "fas fa-cloud-sun",
        "wind_speed": 3.8,
        "wind_direction": 150,
        "visibility": 14,
        "sunrise": "06:05",
        "sunset": "18:20"
    },
    "Ninh Bình": {
        "temperature": 24,
        "feels_like": 26,
        "humidity": 72,
        "pressure": 1014,
        "description": "Trời nhiều mây",
        "icon": "fas fa-cloud",
        "wind_speed": 2.8,
        "wind_direction": 200,
        "visibility": 8,
        "sunrise": "06:18",
        "sunset": "18:32"
    },
    "Quảng Ninh": {
        "temperature": 23,
        "feels_like": 25,
        "humidity": 78,
        "pressure": 1015,
        "description": "Trời có mưa nhỏ",
        "icon": "fas fa-cloud-rain",
        "wind_speed": 4.5,
        "wind_direction": 220,
        "visibility": 6,
        "sunrise": "06:20",
        "sunset": "18:35"
    },
    "Hạ Long": {
        "temperature": 22,
        "feels_like": 24,
        "humidity": 80,
        "pressure": 1016,
        "description": "Trời nhiều mây",
        "icon": "fas fa-cloud",
        "wind_speed": 3.8,
        "wind_direction": 210,
        "visibility": 8,
        "sunrise": "06:22",
        "sunset": "18:38"
    },
    "Sa Pa": {
        "temperature": 18,
        "feels_like": 16,
        "humidity": 85,
        "pressure": 1018,
        "description": "Trời có sương mù",
        "icon": "fas fa-smog",
        "wind_speed": 2.2,
        "wind_direction": 180,
        "visibility": 5,
        "sunrise": "06:25",
        "sunset": "18:40"
    },
    "Huế": {
        "temperature": 26,
        "feels_like": 29,
        "humidity": 73,
        "pressure": 1012,
        "description": "Trời ít mây",
        "icon": "fas fa-cloud-sun",
        "wind_speed": 3.5,
        "wind_direction": 140,
        "visibility": 12,
        "sunrise": "06:08",
        "sunset": "18:22"
    },
    "Hội An": {
        "temperature": 27,
        "feels_like": 30,
        "humidity": 71,
        "pressure": 1011,
        "description": "Trời nắng ít mây",
        "icon": "fas fa-cloud-sun",
        "wind_speed": 3.2,
        "wind_direction": 130,
        "visibility": 13,
        "sunrise": "06:07",
        "sunset": "18:21"
    },
    "Quy Nhơn": {
        "temperature": 29,
        "feels_like": 32,
        "humidity": 69,
        "pressure": 1010,
        "description": "Trời nắng",
        "icon": "fas fa-sun",
        "wind_speed": 4.2,
        "wind_direction": 120,
        "visibility": 15,
        "sunrise": "06:05",
        "sunset": "18:18"
    },
    "Phan Thiết": {
        "temperature": 31,
        "feels_like": 34,
        "humidity": 66,
        "pressure": 1009,
        "description": "Trời nắng",
        "icon": "fas fa-sun",
        "wind_speed": 4.8,
        "wind_direction": 110,
        "visibility": 16,
        "sunrise": "06:02",
        "sunset": "18:15"
    },
    "Vũng Tàu": {
        "temperature": 30,
        "feels_like": 33,
        "humidity": 72,
        "pressure": 1010,
        "description": "Trời ít mây",
        "icon": "fas fa-cloud-sun",
        "wind_speed": 4.0,
        "wind_direction": 100,
        "visibility": 14,
        "sunrise": "06:00",
        "sunset": "18:12"
    },
    "Cần Thơ": {
        "temperature": 33,
        "feels_like": 37,
        "humidity": 76,
        "pressure": 1008,
        "description": "Trời nắng nóng",
        "icon": "fas fa-sun",
        "wind_speed": 2.8,
        "wind_direction": 80,
        "visibility": 12,
        "sunrise": "05:58",
        "sunset": "18:10"
    },
    "Phú Quốc": {
        "temperature": 29,
        "feels_like": 32,
        "humidity": 78,
        "pressure": 1009,
        "description": "Trời ít mây",
        "icon": "fas fa-cloud-sun",
        "wind_speed": 3.6,
        "wind_direction": 90,
        "visibility": 13,
        "sunrise": "05:55",
        "sunset": "18:08"
    },
    "Hà Giang": {
        "temperature": 20,
        "feels_like": 18,
        "humidity": 82,
        "pressure": 1020,
        "description": "Trời nhiều mây",
        "icon": "fas fa-cloud",
        "wind_speed": 2.5,
        "wind_direction": 200,
        "visibility": 7,
        "sunrise": "06:28",
        "sunset": "18:42"
    },
    "Cao Bằng": {
        "temperature": 19,
        "feels_like": 17,
        "humidity": 84,
        "pressure": 1021,
        "description": "Trời có sương mù",
        "icon": "fas fa-smog",
        "wind_speed": 2.0,
        "wind_direction": 190,
        "visibility": 6,
        "sunrise": "06:30",
        "sunset": "18:45"
    },
    "Hải Phòng": {
        "temperature": 24,
        "feels_like": 26,
        "humidity": 74,
        "pressure": 1014,
        "description": "Trời ít mây",
        "icon": "fas fa-cloud-sun",
        "wind_speed": 3.8,
        "wind_direction": 160,
        "visibility": 11,
        "sunrise": "06:18",
        "sunset": "18:33"
    },
    "Đà Lạt": {
        "temperature": 21,
        "feels_like": 19,
        "humidity": 79,
        "pressure": 1017,
        "description": "Trời mát mẻ",
        "icon": "fas fa-cloud",
        "wind_speed": 2.8,
        "wind_direction": 170,
        "visibility": 9,
        "sunrise": "06:12",
        "sunset": "18:25"
    },
    "Phú Yên": {
        "temperature": 28,
        "feels_like": 31,
        "humidity": 71,
        "pressure": 1011,
        "description": "Trời nắng ít mây",
        "icon": "fas fa-cloud-sun",
        "wind_speed": 3.8,
        "wind_direction": 125,
        "visibility": 13,
        "sunrise": "06:06",
        "sunset": "18:19"
    },
    "Bình Định": {
        "temperature": 29,
        "feels_like": 32,
        "humidity": 69,
        "pressure": 1010,
        "description": "Trời nắng",
        "icon": "fas fa-sun",
        "wind_speed": 4.2,
        "wind_direction": 120,
        "visibility": 15,
        "sunrise": "06:05",
        "sunset": "18:18"
    },
    "An Giang": {
        "temperature": 32,
        "feels_like": 36,
        "humidity": 74,
        "pressure": 1008,
        "description": "Trời nắng nóng",
        "icon": "fas fa-sun",
        "wind_speed": 2.5,
        "wind_direction": 85,
        "visibility": 11,
        "sunrise": "05:59",
        "sunset": "18:11"
    },
    "Đồng Tháp": {
        "temperature": 31,
        "feels_like": 35,
        "humidity": 77,
        "pressure": 1008,
        "description": "Trời nắng",
        "icon": "fas fa-sun",
        "wind_speed": 2.3,
        "wind_direction": 75,
        "visibility": 10,
        "sunrise": "05:57",
        "sunset": "18:09"
    },
    "Tiền Giang": {
        "temperature": 32,
        "feels_like": 36,
        "humidity": 75,
        "pressure": 1009,
        "description": "Trời nắng nóng",
        "icon": "fas fa-sun",
        "wind_speed": 2.7,
        "wind_direction": 82,
        "visibility": 12,
        "sunrise": "05:58",
        "sunset": "18:10"
    },
    "Bắc Ninh": {
        "temperature": 25,
        "feels_like": 27,
        "humidity": 68,
        "pressure": 1013,
        "description": "Trời ít mây",
        "icon": "fas fa-cloud-sun",
        "wind_speed": 3.2,
        "wind_direction": 165,
        "visibility": 11,
        "sunrise": "06:16",
        "sunset": "18:31"
    }
}

def remove_vietnamese_accents(text):
    """Chuyển đổi tiếng Việt có dấu thành không dấu"""
    vietnamese_map = {
        'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a', 'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
        'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
        'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
        'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o', 'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
        'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u', 'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
        'đ': 'd',
        'À': 'A', 'Á': 'A', 'Ạ': 'A', 'Ả': 'A', 'Ã': 'A', 'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ậ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ặ': 'A', 'Ẳ': 'A', 'Ẵ': 'A',
        'È': 'E', 'É': 'E', 'Ẹ': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ệ': 'E', 'Ể': 'E', 'Ễ': 'E',
        'Ì': 'I', 'Í': 'I', 'Ị': 'I', 'Ỉ': 'I', 'Ĩ': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ọ': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ộ': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ợ': 'O', 'Ở': 'O', 'Ỡ': 'O',
        'Ù': 'U', 'Ú': 'U', 'Ụ': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ự': 'U', 'Ử': 'U', 'Ữ': 'U',
        'Ỳ': 'Y', 'Ý': 'Y', 'Ỵ': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y',
        'Đ': 'D'
    }
    
    result = ""
    for char in text:
        result += vietnamese_map.get(char, char)
    return result

def normalize_city_name(city_name):
    """Chuẩn hóa tên thành phố để tìm kiếm"""
    # Loại bỏ dấu
    normalized = remove_vietnamese_accents(city_name)
    # Chuyển về lowercase và loại bỏ khoảng trắng thừa
    normalized = normalized.lower().strip()
    # Loại bỏ các từ phổ biến
    common_words = ['thanh pho', 'tp', 'tinh', 'huyen', 'quan', 'phuong']
    for word in common_words:
        normalized = normalized.replace(word, '').strip()
    return normalized

# Mapping tên thành phố tiếng Việt sang tiếng Anh (bao gồm cả có dấu và không dấu)
CITY_MAPPING = {
    # Có dấu
    "Hà Nội": "Hanoi",
    "Hồ Chí Minh": "Ho Chi Minh City", 
    "Đà Nẵng": "Da Nang",
    "Hải Phòng": "Hai Phong",
    "Cần Thơ": "Can Tho",
    "Nha Trang": "Nha Trang",
    "Đà Lạt": "Da Lat",
    "Phú Quốc": "Phu Quoc",
    "Sa Pa": "Sapa",
    "Hạ Long": "Ha Long",
    "Quảng Ninh": "Quang Ninh",
    "Ninh Bình": "Ninh Binh",
    "Hà Giang": "Ha Giang",
    "Cao Bằng": "Cao Bang",
    "Bắc Ninh": "Bac Ninh",
    "Cà Mau": "Ca Mau",
    "Huế": "Hue",
    "Quy Nhơn": "Quy Nhon",
    "Vũng Tàu": "Vung Tau",
    "Phan Thiết": "Phan Thiet",
    "Mỹ Tho": "My Tho",
    "Rạch Giá": "Rach Gia",
    "Châu Đốc": "Chau Doc",
    "Bến Tre": "Ben Tre",
    "Sóc Trăng": "Soc Trang",
    "Cà Mau": "Ca Mau",
    "Kiên Giang": "Kien Giang",
    
    # Không dấu
    "Ha Noi": "Hanoi",
    "Ho Chi Minh": "Ho Chi Minh City",
    "Da Nang": "Da Nang", 
    "Hai Phong": "Hai Phong",
    "Can Tho": "Can Tho",
    "Da Lat": "Da Lat",
    "Phu Quoc": "Phu Quoc",
    "Ha Long": "Ha Long",
    "Quang Ninh": "Quang Ninh",
    "Ninh Binh": "Ninh Binh",
    "Ha Giang": "Ha Giang",
    "Cao Bang": "Cao Bang",
    "Bac Ninh": "Bac Ninh",
    "Ca Mau": "Ca Mau",
    "Hue": "Hue",
    "Quy Nhon": "Quy Nhon",
    "Vung Tau": "Vung Tau",
    "Phan Thiet": "Phan Thiet",
    "My Tho": "My Tho",
    "Rach Gia": "Rach Gia",
    "Chau Doc": "Chau Doc",
    "Ben Tre": "Ben Tre",
    "Soc Trang": "Soc Trang",
    "Kien Giang": "Kien Giang",
    
    # Viết tắt phổ biến
    "HN": "Hanoi",
    "HCM": "Ho Chi Minh City",
    "TPHCM": "Ho Chi Minh City",
    "TP.HCM": "Ho Chi Minh City",
    "Sài Gòn": "Ho Chi Minh City",
    "Saigon": "Ho Chi Minh City",
    "DN": "Da Nang",
    "HP": "Hai Phong",
    "CT": "Can Tho",
    "NT": "Nha Trang",
    "DL": "Da Lat",
    "PQ": "Phu Quoc",
    "HL": "Ha Long",
    "QN": "Quang Ninh",
    "NB": "Ninh Binh",
    "HG": "Ha Giang",
    "CB": "Cao Bang",
    "BN": "Bac Ninh",
    "CM": "Ca Mau",
    
    # Alternative names cho các địa điểm khó tìm
    "Phú Quốc": "Duong Dong",  # Thị trấn chính của Phú Quốc
    "Phu Quoc": "Duong Dong",
    "Hội An": "Hoi An",
    "Hoi An": "Hoi An",
    "Phú Yên": "Tuy Hoa",  # Thành phố chính của Phú Yên
    "Phu Yen": "Tuy Hoa",
    "Bình Định": "Quy Nhon",  # Thành phố chính của Bình Định
    "Binh Dinh": "Quy Nhon",
    "An Giang": "Long Xuyen",  # Thành phố chính của An Giang
    "Đồng Tháp": "Cao Lanh",  # Thành phố chính của Đồng Tháp
    "Dong Thap": "Cao Lanh",
    "Tiền Giang": "My Tho",  # Thành phố chính của Tiền Giang
    "Tien Giang": "My Tho",
    "Kiên Giang": "Rach Gia",  # Thành phố chính của Kiên Giang
    "Kien Giang": "Rach Gia"
}

def find_city_english_name(vietnamese_city):
    """Tìm tên tiếng Anh của thành phố từ tên tiếng Việt"""
    # Thử tìm trực tiếp trước
    if vietnamese_city in CITY_MAPPING:
        return CITY_MAPPING[vietnamese_city]
    
    # Thử tìm với tên đã chuẩn hóa
    normalized_input = normalize_city_name(vietnamese_city)
    
    # Tìm kiếm trong mapping với tên đã chuẩn hóa
    for vn_name, en_name in CITY_MAPPING.items():
        if normalize_city_name(vn_name) == normalized_input:
            return en_name
    
    # Nếu không tìm thấy, thử tìm kiếm gần đúng
    for vn_name, en_name in CITY_MAPPING.items():
        if normalized_input in normalize_city_name(vn_name) or normalize_city_name(vn_name) in normalized_input:
            return en_name
    
    # Trả về tên gốc nếu không tìm thấy
    return vietnamese_city

def get_demo_data_fallback(city):
    """Lấy demo data khi API thất bại"""
    # Thử tìm demo data với tên gốc trước
    demo_data = DEMO_WEATHER_DATA.get(city)
    
    # Nếu không tìm thấy, thử với tên đã chuẩn hóa
    if not demo_data:
        normalized_city = find_city_english_name(city)
        # Tìm trong demo data với tên tiếng Việt tương ứng
        for demo_city, demo_info in DEMO_WEATHER_DATA.items():
            if find_city_english_name(demo_city) == normalized_city:
                demo_data = demo_info
                break
    
    # Nếu vẫn không tìm thấy, thử tìm kiếm gần đúng
    if not demo_data:
        normalized_input = normalize_city_name(city)
        for demo_city, demo_info in DEMO_WEATHER_DATA.items():
            if normalized_input in normalize_city_name(demo_city) or normalize_city_name(demo_city) in normalized_input:
                demo_data = demo_info
                break
    
    if demo_data:
        return {
            'city': city,
            'temperature': demo_data['temperature'],
            'feels_like': demo_data['feels_like'],
            'humidity': demo_data['humidity'],
            'pressure': demo_data['pressure'],
            'description': demo_data['description'],
            'icon': demo_data['icon'],
            'wind_speed': demo_data['wind_speed'],
            'wind_direction': demo_data['wind_direction'],
            'visibility': demo_data['visibility'],
            'sunrise': demo_data['sunrise'],
            'sunset': demo_data['sunset'],
            'last_updated': datetime.now().strftime('%H:%M')
        }
    
    return None

def get_demo_forecast_fallback(city):
    """Lấy demo forecast data khi API thất bại"""
    # Tạo dự báo demo dựa trên thời tiết hiện tại
    current_demo = get_demo_data_fallback(city)
    if not current_demo:
        return None
    
    base_temp = current_demo['temperature']
    base_icon = current_demo['icon']
    
    # dự báo 5 ngày tới
    forecasts = []
    days = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu']
    
    for i in range(5):
        temp_variation = (i - 2) * 1.5  
        temp = int(base_temp + temp_variation)
        
        # chọn icon dựa trên thời tiết
        icons = [base_icon, 'fas fa-cloud', 'fas fa-cloud-sun', 'fas fa-sun', 'fas fa-cloud-rain']
        descriptions = ['Trời ít mây', 'Trời nhiều mây', 'Trời nắng ít mây', 'Trời nắng', 'Có mưa nhỏ']
        
        forecast = {
            'date': f'{26+i}/01',
            'day_name': days[i],
            'temperature': temp,
            'temp_min': temp - 3,
            'temp_max': temp + 3,
            'description': descriptions[i],
            'icon': icons[i],
            'humidity': current_demo['humidity'] + (i * 2),
            'wind_speed': current_demo['wind_speed'] + (i * 0.3)
        }
        forecasts.append(forecast)
    
    return forecasts

def get_weather_icon_class(weather_code, is_day=True):
    """Chuyển đổi mã thời tiết thành icon class"""
    icon_mapping = {
        "01": "fas fa-sun" if is_day else "fas fa-moon",
        "02": "fas fa-cloud-sun" if is_day else "fas fa-cloud-moon",
        "03": "fas fa-cloud",
        "04": "fas fa-cloud",
        "09": "fas fa-cloud-rain",
        "10": "fas fa-cloud-sun-rain" if is_day else "fas fa-cloud-moon-rain",
        "11": "fas fa-bolt",
        "13": "fas fa-snowflake",
        "50": "fas fa-smog"
    }
    
    weather_id = weather_code[:2]
    return icon_mapping.get(weather_id, "fas fa-cloud")

@weather_blueprint.route('/api/weather/current/<city>')
def get_current_weather(city):
    """Lấy thời tiết hiện tại cho một thành phố"""
    try:
        # dùng dữ liệu fake tạo sẵn
        if WEATHER_API_KEY == "demo_key":
            demo_data = DEMO_WEATHER_DATA.get(city)
            
            if not demo_data:
                normalized_city = find_city_english_name(city)
                for demo_city, demo_info in DEMO_WEATHER_DATA.items():
                    if find_city_english_name(demo_city) == normalized_city:
                        demo_data = demo_info
                        break
            
            if demo_data:
                weather_data = {
                    'city': city,
                    'temperature': demo_data['temperature'],
                    'feels_like': demo_data['feels_like'],
                    'humidity': demo_data['humidity'],
                    'pressure': demo_data['pressure'],
                    'description': demo_data['description'],
                    'icon': demo_data['icon'],
                    'wind_speed': demo_data['wind_speed'],
                    'wind_direction': demo_data['wind_direction'],
                    'visibility': demo_data['visibility'],
                    'sunrise': demo_data['sunrise'],
                    'sunset': demo_data['sunset'],
                    'last_updated': datetime.now().strftime('%H:%M')
                }
                
                return jsonify({
                    'success': True,
                    'data': weather_data
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Không có dữ liệu demo cho thành phố này'
                }), 404
        
        # Chuyển đổi tên thành phố
        english_city = find_city_english_name(city)
        
        # Gọi API OpenWeatherMap
        url = f"{WEATHER_BASE_URL}/weather"
        params = {
            'q': english_city + ",VN",
            'appid': WEATHER_API_KEY,
            'units': 'metric',
            'lang': 'vi'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Xử lý dữ liệu thời tiết
            weather_data = {
                'city': city,
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].title(),
                'icon': get_weather_icon_class(data['weather'][0]['icon']),
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
                'last_updated': datetime.now().strftime('%H:%M')
            }
            
            return jsonify({
                'success': True,
                'data': weather_data
            })
        else:
            # nếu gọi api thất bại thì dùng data có sẵn
            if USE_DEMO_FALLBACK:
                demo_data = get_demo_data_fallback(city)
                if demo_data:
                    return jsonify({
                        'success': True,
                        'data': demo_data
                    })
            
            return jsonify({
                'success': False,
                'message': f'Không thể lấy dữ liệu thời tiết cho {city}. API response: {response.status_code}'
            }), 400
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'message': 'Timeout khi gọi API thời tiết'
        }), 408
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500

@weather_blueprint.route('/api/weather/forecast/<city>')
def get_weather_forecast(city):
    """Lấy dự báo thời tiết 5 ngày cho một thành phố"""
    try:
        #dùng data fake nếu key bị lỗi
        if WEATHER_API_KEY == "demo_key":
            demo_forecasts = [
                {
                    'date': '26/01',
                    'day_name': 'Thứ Hai',
                    'temperature': 26,
                    'temp_min': 22,
                    'temp_max': 28,
                    'description': 'Trời nắng',
                    'icon': 'fas fa-sun',
                    'humidity': 65,
                    'wind_speed': 3.0
                },
                {
                    'date': '27/01',
                    'day_name': 'Thứ Ba',
                    'temperature': 24,
                    'temp_min': 20,
                    'temp_max': 26,
                    'description': 'Trời nhiều mây',
                    'icon': 'fas fa-cloud',
                    'humidity': 70,
                    'wind_speed': 3.5
                },
                {
                    'date': '28/01',
                    'day_name': 'Thứ Tư',
                    'temperature': 23,
                    'temp_min': 19,
                    'temp_max': 25,
                    'description': 'Có mưa nhỏ',
                    'icon': 'fas fa-cloud-rain',
                    'humidity': 80,
                    'wind_speed': 4.0
                },
                {
                    'date': '29/01',
                    'day_name': 'Thứ Năm',
                    'temperature': 25,
                    'temp_min': 21,
                    'temp_max': 27,
                    'description': 'Trời ít mây',
                    'icon': 'fas fa-cloud-sun',
                    'humidity': 68,
                    'wind_speed': 2.8
                },
                {
                    'date': '30/01',
                    'day_name': 'Thứ Sáu',
                    'temperature': 27,
                    'temp_min': 23,
                    'temp_max': 29,
                    'description': 'Trời nắng',
                    'icon': 'fas fa-sun',
                    'humidity': 60,
                    'wind_speed': 2.5
                }
            ]
            
            return jsonify({
                'success': True,
                'data': {
                    'city': city,
                    'forecasts': demo_forecasts
                }
            })
        # Chuyển đổi tên thành phố
        english_city = find_city_english_name(city)
        
        # Gọi API OpenWeatherMap
        url = f"{WEATHER_BASE_URL}/forecast"
        params = {
            'q': english_city + ",VN",
            'appid': WEATHER_API_KEY,
            'units': 'metric',
            'lang': 'vi'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Xử lý dữ liệu dự báo (lấy 1 dự báo mỗi ngày vào 12:00)
            daily_forecasts = []
            processed_dates = set()
            
            for item in data['list']:
                date_str = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                time_str = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
                
                # Lấy dự báo vào 12:00 hoặc gần nhất
                if date_str not in processed_dates and ('12:00' in time_str or len(daily_forecasts) < 5):
                    forecast_data = {
                        'date': datetime.fromtimestamp(item['dt']).strftime('%d/%m'),
                        'day_name': datetime.fromtimestamp(item['dt']).strftime('%A'),
                        'temperature': round(item['main']['temp']),
                        'temp_min': round(item['main']['temp_min']),
                        'temp_max': round(item['main']['temp_max']),
                        'description': item['weather'][0]['description'].title(),
                        'icon': get_weather_icon_class(item['weather'][0]['icon']),
                        'humidity': item['main']['humidity'],
                        'wind_speed': item['wind']['speed']
                    }
                    
                    daily_forecasts.append(forecast_data)
                    processed_dates.add(date_str)
                    
                    if len(daily_forecasts) >= 5:
                        break
            
            return jsonify({
                'success': True,
                'data': {
                    'city': city,
                    'forecasts': daily_forecasts
                }
            })
        else:
            # API thất bại, trả về demo data
            if USE_DEMO_FALLBACK:
                demo_forecasts = get_demo_forecast_fallback(city)
                if demo_forecasts:
                    return jsonify({
                        'success': True,
                        'data': {
                            'city': city,
                            'forecasts': demo_forecasts
                        }
                    })
            
            return jsonify({
                'success': False,
                'message': f'Không thể lấy dữ liệu dự báo thời tiết cho {city}. API response: {response.status_code}'
            }), 400
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'message': 'Timeout khi gọi API thời tiết'
        }), 408
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500

@weather_blueprint.route('/api/weather/multiple')
def get_multiple_weather():
    """Lấy thời tiết cho nhiều thành phố cùng lúc"""
    try:
        cities = request.args.get('cities', '').split(',')
        cities = [city.strip() for city in cities if city.strip()]
        
        if not cities:
            return jsonify({
                'success': False,
                'message': 'Vui lòng cung cấp danh sách thành phố'
            }), 400
        
        weather_data = {}
        
        for city in cities:
            try:
                english_city = find_city_english_name(city)
                
                url = f"{WEATHER_BASE_URL}/weather"
                params = {
                    'q': english_city + ",VN",
                    'appid': WEATHER_API_KEY,
                    'units': 'metric',
                    'lang': 'vi'
                }
                
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    weather_data[city] = {
                        'temperature': round(data['main']['temp']),
                        'description': data['weather'][0]['description'].title(),
                        'icon': get_weather_icon_class(data['weather'][0]['icon']),
                        'humidity': data['main']['humidity']
                    }
                else:
                    weather_data[city] = {
                        'error': 'Không thể lấy dữ liệu'
                    }
                    
            except Exception as e:
                weather_data[city] = {
                    'error': f'Lỗi: {str(e)}'
                }
        
        return jsonify({
            'success': True,
            'data': weather_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }), 500 