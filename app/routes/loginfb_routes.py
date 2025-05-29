from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app, flash
from app.extension import oauth
from app.models.users import Users
from werkzeug.security import generate_password_hash
from app.models.users import db

loginfb_blueprint = Blueprint('loginfb', __name__)

@loginfb_blueprint.route('/test-facebook-url')
def test_facebook_url():
    """Test route để kiểm tra URL callback"""
    from flask import current_app
    with current_app.app_context():
        callback_url = url_for('loginfb.facebook_callback', _external=True, _scheme='http')
        return {
            "callback_url": callback_url,
            "scheme": "http (forced)",
            "message": "Đây là URL sẽ được gửi cho Facebook"
        }

@loginfb_blueprint.route('/auth/facebook')
def facebook_login():
    """Bắt đầu quá trình đăng nhập Facebook"""
    redirect_uri = url_for('loginfb.facebook_callback', _external=True, _scheme='http')
    print(f"Facebook redirect URI: {redirect_uri}")  # Debug log
    return oauth.facebook.authorize_redirect(redirect_uri)


@loginfb_blueprint.route('/auth/facebook/callback')
def facebook_callback():
    """Xử lý callback từ Facebook sau khi user đồng ý"""
    try:
        # Lấy token từ Facebook
        token = oauth.facebook.authorize_access_token()
        
        # Lấy thông tin cơ bản của user từ Facebook Graph API
        resp = oauth.facebook.get('me?fields=id,name,picture')
        user_info = resp.json()
        
        print("Received Facebook user info:", user_info)  # Debug log
        
        if not user_info or 'id' not in user_info:
            flash("Không thể lấy thông tin từ Facebook!", "error")
            return redirect(url_for('auth.login_page'))
        
        # Kiểm tra xem user đã tồn tại chưa (theo Facebook ID)
        user = Users.find_by_facebook_id(user_info['id'])
        
        if user:
            print(f"Existing user found with Facebook ID: {user_info['id']}")  # Debug log
            # User đã tồn tại, đăng nhập
            session['user_name'] = user.uname if user.uname else user.email  # Sử dụng uname hoặc email
            session['full_name'] = user.fname
            session['provider'] = 'facebook'
            flash(f"Chào mừng {user.fname}!", "success")
            return redirect(url_for('main.index'))
        else:
            print("Creating new user from Facebook data")  # Debug log
            # Tạo user mới từ Facebook
            new_user = Users.create_facebook_user(user_info)
            
            if new_user:
                print(f"New user created with ID: {new_user.id}")  # Debug log
                session['user_name'] = new_user.uname
                session['full_name'] = new_user.fname
                session['provider'] = 'facebook'
                flash(f"Đăng ký thành công qua Facebook! Chào mừng {new_user.fname}!", "success")
                return redirect(url_for('main.index'))
            else:
                print("Failed to create new user")  # Debug log
                flash("Lỗi khi tạo tài khoản từ Facebook! Vui lòng thử lại sau.", "error")
                return redirect(url_for('auth.login_page'))
                    
    except Exception as e:
        import traceback
        traceback.print_exc()  # In ra stack trace đầy đủ
        current_app.logger.error(f"Facebook OAuth error: {str(e)}")
        flash("Lỗi trong quá trình đăng nhập Facebook! Vui lòng thử lại.", "error")
        return redirect(url_for('auth.login_page'))


@loginfb_blueprint.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """API để lấy thông tin profile user hiện tại"""
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401
    
    try:
        # Tìm user theo session
        user = Users.query.filter(
            (Users.uname == session['user_id']) | 
            (Users.email == session['user_id'])
        ).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_data = {
            "id": user.id,
            "name": user.fname,
            "username": user.uname,
            "email": user.email,
            "phone": user.sdt,
            "address": user.address,
            "gender": user.gender,
            "birth_date": user.birth_date,
            "provider": user.provider,
            "avatar_url": user.avatar_url
        }
        
        return jsonify({"success": True, "user": user_data})
        
    except Exception as e:
        current_app.logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@loginfb_blueprint.route('/api/users', methods=['POST'])
def create_user_api():
    """API để tạo user mới (thủ công)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Kiểm tra các field bắt buộc
        required_fields = ['email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Kiểm tra email đã tồn tại chưa
        existing_user = Users.find_by_email(data['email'])
        if existing_user:
            return jsonify({"error": "Email already exists"}), 409
        
        # Mã hóa mật khẩu nếu có
        password = data.get('password')
        if password:
            password = generate_password_hash(password)
        
        # Tạo user mới
        new_user = Users(
            email=data['email'],
            fname=data.get('fname'),
            uname=data.get('uname'),
            sdt=data.get('sdt'),
            password=password,
            address=data.get('address'),
            position=data.get('position'),
            gender=data.get('gender'),
            birth_date=data.get('birth_date'),
            provider=data.get('provider', 'local')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "User created successfully",
            "user_id": new_user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating user: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500