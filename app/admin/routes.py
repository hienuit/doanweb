from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from app.models.users import Users
from app.models.feedback import Feedback
from app.models.settings import Settings
from app.admin.models import Admin
from app import db
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from functools import wraps
from sqlalchemy import func

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # Kiểm tra chính xác xem current_user có phải là Admin instance không
        if not isinstance(current_user, Admin) or not current_user.is_admin:
            # Nếu là user thông thường, logout và redirect về admin login
            if isinstance(current_user, Users):
                logout_user()
                flash('Vui lòng đăng nhập bằng tài khoản admin.', 'warning')
                return redirect(url_for('admin.login'))
            # Nếu không phải admin, redirect về trang chính
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@admin_required
def index():
    return redirect(url_for('admin.dashboard'))

@admin.route('/dashboard')
@admin_required
def dashboard():
    from app.models.history import History
    
    # Tính toán thống kê
    total_users = Users.query.count()
    total_bookings = History.query.count()         
    # Tính tổng doanh thu từ history (chuyển đổi string thành số)
    histories = History.query.all()
    revenue = 0
    for history in histories:
        try:
            # Loại bỏ ký tự không phải số và chuyển đổi
            cost_str = str(history.total_cost).replace(',', '').replace('₫', '').strip()
            if cost_str:
                revenue += float(cost_str)
        except (ValueError, AttributeError):
            pass
    
    # Định dạng doanh thu
    revenue = f"{revenue:,.0f} ₫"
    
    # Dữ liệu cho biểu đồ đặt tour (7 ngày gần nhất)
    booking_labels = []
    booking_data = []
    
    for i in range(6, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        label = date.strftime('%d/%m')
        count = History.query.filter(
            func.date(History.created_at) == date.date()
        ).count()
        
        booking_labels.append(label)
        booking_data.append(count)
    
    # Dữ liệu cho biểu đồ tour phổ biến (top 5 điểm đến)
    destination_stats = db.session.query(
        History.destination,
        func.count(History.id).label('count')
    ).filter(
        History.destination.isnot(None)
    ).group_by(History.destination).order_by(
        func.count(History.id).desc()
    ).limit(5).all()
    
    tour_labels = [stat[0] for stat in destination_stats]
    tour_data = [stat[1] for stat in destination_stats]
    
    # Nếu không có dữ liệu, tạo dữ liệu mặc định
    if not tour_labels:
        tour_labels = ['Hà Nội', 'Đà Nẵng', 'Hồ Chí Minh', 'Phú Quốc', 'Nha Trang']
        tour_data = [0, 0, 0, 0, 0]
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_bookings=total_bookings,
                         revenue=revenue,
                         booking_labels=booking_labels,
                         booking_data=booking_data,
                         tour_labels=tour_labels,
                         tour_data=tour_data)

@admin.route('/login', methods=['GET', 'POST'])
def login():
    # Kiểm tra nếu đã đăng nhập và là admin thực sự
    if current_user.is_authenticated:
        # Nếu là user thông thường, logout user session trước
        if isinstance(current_user, Users):
            logout_user()
            flash('Vui lòng đăng nhập bằng tài khoản admin.', 'info')
        # Nếu là admin, redirect đến dashboard
        elif isinstance(current_user, Admin) and current_user.is_admin:
            return redirect(url_for('admin.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        admin_user = Admin.query.filter_by(email=email).first()
        
        if admin_user and admin_user.check_password(password):
            # Đảm bảo logout user session trước khi login admin
            if current_user.is_authenticated:
                logout_user()
            
            login_user(admin_user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('admin.index'))
        
        flash('Email hoặc mật khẩu không đúng', 'danger')
    
    return render_template('admin/login.html')

@admin.route('/logout')
@admin_required
def logout():
    # Chỉ logout nếu là admin
    if isinstance(current_user, Admin):
        logout_user()
        flash('Đã đăng xuất khỏi tài khoản admin.', 'info')
    return redirect(url_for('admin.login'))

@admin.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Users.query.paginate(page=page, per_page=per_page)
    return render_template('admin/users.html', users=pagination.items, pagination=pagination)

@admin.route('/users/<int:id>/details')
@admin_required
def user_details(id):
    user = Users.query.get_or_404(id)
    return jsonify({
        'email': user.email,
        'name': user.name,
        'created_at': user.created_at.strftime('%d-%m-%Y %H:%M') if user.created_at else 'N/A',
        'is_active': user.is_active if hasattr(user, 'is_active') else True,
        'total_bookings': len(user.activities) if hasattr(user, 'activities') else 0,
        'total_spent': sum(float(activity.details.split(':')[1].strip()) 
                         for activity in user.activities 
                         if activity.activity == 'booking' and activity.details 
                         and ':' in activity.details) if hasattr(user, 'activities') else 0,
        'bookings': [{
            'tour_name': activity.details.split(':')[0].strip(),
            'booking_date': activity.timestamp.strftime('%d-%m-%Y'),
            'status': 'Completed'
        } for activity in user.activities if activity.activity == 'booking'] if hasattr(user, 'activities') else []
    })

@admin.route('/users/<int:id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(id):
    user = Users.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True})

@admin.route('/feedback')
@admin_required
def feedback():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    per_page = 10
    
    query = Feedback.query
    if status:
        query = query.filter_by(status=status)
    
    feedbacks = query.order_by(Feedback.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('admin/feedback.html', feedbacks=feedbacks)

@admin.route('/feedback/<int:id>/details')
@admin_required
def feedback_details(id):
    feedback = Feedback.query.get_or_404(id)
    return jsonify({
        'user_name': feedback.user.name,
        'user_email': feedback.user.email,
        'subject': feedback.subject,
        'message': feedback.message,
        'created_at': feedback.created_at.strftime('%d-%m-%Y %H:%M'),
        'status': feedback.status,
        'response': feedback.response,
        'response_at': feedback.response_at.strftime('%d-%m-%Y %H:%M') if feedback.response_at else None
    })

@admin.route('/feedback/<int:id>/respond', methods=['POST'])
@admin_required
def respond_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    data = request.get_json()
    
    feedback.response = data.get('response')
    feedback.response_at = datetime.utcnow()
    feedback.status = 'responded'
    
    db.session.commit()
    return jsonify({'success': True})

@admin.route('/feedback/<int:id>/close', methods=['POST'])
@admin_required
def close_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    feedback.status = 'closed'
    db.session.commit()
    return jsonify({'success': True})

@admin.route('/settings')
@admin_required
def settings():
    all_settings = Settings.get_all()
    return render_template('admin/settings.html', settings=all_settings)

@admin.route('/settings/site', methods=['POST'])
@admin_required
def update_site_settings():
    data = request.get_json()
    
    Settings.set('site_name', data.get('site_name'))
    Settings.set('site_description', data.get('site_description'))
    Settings.set('contact_email', data.get('contact_email'))
    Settings.set('contact_phone', data.get('contact_phone'))
    
    return jsonify({'success': True})

@admin.route('/settings/email', methods=['POST'])
@admin_required
def update_email_settings():
    data = request.get_json()
    
    Settings.set('smtp_server', data.get('smtp_server'))
    Settings.set('smtp_port', data.get('smtp_port'), type='int')
    Settings.set('smtp_username', data.get('smtp_username'))
    Settings.set('smtp_password', data.get('smtp_password'))
    Settings.set('email_from', data.get('email_from'))
    
    return jsonify({'success': True})

@admin.route('/settings/email/test', methods=['POST'])
@admin_required
def test_email_settings():
    data = request.get_json()
    
    try:
        # Tạo kết nối SMTP
        server = smtplib.SMTP(data.get('smtp_server'), int(data.get('smtp_port')))
        server.starttls()
        server.login(data.get('smtp_username'), data.get('smtp_password'))
        
        # Gửi email test
        msg = MIMEText('This is a test email from your website.')
        msg['Subject'] = 'Test Email'
        msg['From'] = data.get('email_from')
        msg['To'] = data.get('smtp_username')
        
        server.send_message(msg)
        server.quit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@admin.route('/settings/payment', methods=['POST'])
@admin_required
def update_payment_settings():
    data = request.get_json()
    
    Settings.set('payment_currency', data.get('payment_currency'))
    Settings.set('paypal_client_id', data.get('paypal_client_id'))
    Settings.set('paypal_secret', data.get('paypal_secret'))
    Settings.set('vnpay_tmn_code', data.get('vnpay_tmn_code'))
    Settings.set('vnpay_hash_secret', data.get('vnpay_hash_secret'))
    
    return jsonify({'success': True})

@admin.route('/settings/security', methods=['POST'])
@admin_required
def update_security_settings():
    data = request.get_json()
    
    Settings.set('enable_two_factor', data.get('enable_two_factor'), type='bool')
    Settings.set('enable_captcha', data.get('enable_captcha'), type='bool')
    Settings.set('session_timeout', data.get('session_timeout'), type='int')
    Settings.set('max_login_attempts', data.get('max_login_attempts'), type='int')
    
    return jsonify({'success': True}) 