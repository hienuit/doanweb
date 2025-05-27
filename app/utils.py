import re
from typing import Tuple, Dict
from flask import url_for

def check_password_strength(password: str) -> Tuple[str, int, Dict[str, bool]]:
    """
    Kiểm tra độ mạnh của mật khẩu
    
    Args:
        password: Mật khẩu cần kiểm tra
        
    Returns:
        Tuple[str, int, Dict]: (mức độ, điểm số, chi tiết kiểm tra)
    """
    if not password:
        return "weak", 0, {}
    
    # Điều kiện kiểm tra
    criteria = {
        'length': len(password) >= 8,
        'uppercase': bool(re.search(r'[A-Z]', password)),
        'lowercase': bool(re.search(r'[a-z]', password)),
        'digit': bool(re.search(r'\d', password)),
        'special': bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password)),
        'no_common': not is_common_password(password)
    }
    
    # Tính điểm
    score = 0
    
    # Điểm cơ bản cho độ dài
    if criteria['length']:
        score += 25
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
    
    # Điểm cho các loại ký tự
    if criteria['uppercase']:
        score += 15
    if criteria['lowercase']:
        score += 10
    if criteria['digit']:
        score += 15
    if criteria['special']:
        score += 20
    
    # Điểm thưởng cho không phải mật khẩu phổ biến
    if criteria['no_common']:
        score += 5
    
    # Xác định mức độ
    if score >= 80 and criteria['length'] and criteria['uppercase'] and criteria['special']:
        level = "strong"
    elif score >= 60 and criteria['length']:
        level = "medium"
    else:
        level = "weak"
    
    return level, score, criteria

def is_common_password(password: str) -> bool:
    """Kiểm tra có phải mật khẩu phổ biến không"""
    common_passwords = [
        'password', '123456', '123456789', 'qwerty', 'abc123',
        'password123', 'admin', '12345678', '1234567890', 'welcome',
        'monkey', 'dragon', 'letmein', 'baseball', 'football',
        'iloveyou', 'trustno1', 'sunshine', 'master', 'hello',
        'freedom', 'whatever', 'minecraft', 'mustang', 'michael'
    ]
    return password.lower() in common_passwords

def get_password_suggestions(criteria: Dict[str, bool]) -> list:
    """Đưa ra gợi ý cải thiện mật khẩu"""
    suggestions = []
    
    if not criteria.get('length', False):
        suggestions.append("Sử dụng ít nhất 8 ký tự")
    
    if not criteria.get('uppercase', False):
        suggestions.append("Thêm ít nhất 1 chữ cái viết hoa (A-Z)")
    
    if not criteria.get('lowercase', False):
        suggestions.append("Thêm ít nhất 1 chữ cái viết thường (a-z)")
    
    if not criteria.get('digit', False):
        suggestions.append("Thêm ít nhất 1 chữ số (0-9)")
    
    if not criteria.get('special', False):
        suggestions.append("Thêm ít nhất 1 ký tự đặc biệt (!@#$%^&*)")
    
    if not criteria.get('no_common', False):
        suggestions.append("Tránh sử dụng mật khẩu phổ biến")
    
    return suggestions

def validate_password_requirements(password: str) -> Tuple[bool, list]:
    """
    Kiểm tra mật khẩu có đạt yêu cầu tối thiểu không
    
    Returns:
        Tuple[bool, list]: (có hợp lệ, danh sách lỗi)
    """
    level, score, criteria = check_password_strength(password)
    
    if level == "weak":
        suggestions = get_password_suggestions(criteria)
        return False, suggestions
    
    return True, []

def get_avatar_url(user_avatar_url):
    """Helper function để xử lý avatar URL"""
    if not user_avatar_url:
        return None
    
    # Nếu đã là URL đầy đủ (bắt đầu với /static/), trả về trực tiếp
    if user_avatar_url.startswith('/static/'):
        return user_avatar_url
    
    # Nếu là đường dẫn cũ (bắt đầu với /uploads/), chuyển đổi
    if user_avatar_url.startswith('/uploads/'):
        filename = user_avatar_url.split('/')[-1]
        return url_for('static', filename=f'uploads/avatars/{filename}')
    
    # Trường hợp khác, coi như là filename
    return url_for('static', filename=f'uploads/avatars/{user_avatar_url}')
 