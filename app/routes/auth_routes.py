from flask import Blueprint,current_app, render_template, request, redirect, session, flash, url_for, jsonify,current_app
from app.models.users import Users, UserActivity
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, mail
from flask_mail import Message
import random, string
from app.extension import google
from app.models.users import add_user_activity
from app.utils import validate_password_requirements


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/login')
def login_page():
    next_page = request.args.get('next')
    return render_template("login.html", next=next_page)

@auth_blueprint.route('/loginfunction', methods=['GET', 'POST'])
def login():
    # Nếu là GET request, redirect về trang login
    if request.method == 'GET':
        print("DEBUG: GET request to /loginfunction, redirecting to login page")
        return redirect(url_for('auth.login_page'))
        
    email = request.form.get('email')
    password = request.form.get('password')
    next_page = request.form.get('next_page')
    
    # Log để debug
    print(f"DEBUG: Login attempt for email: {email}")
    print(f"DEBUG: Session keys before login: {list(session.keys())}")
    print(f"DEBUG: next_page: {next_page}")
    
    user = Users.query.filter_by(email=email).first()
    if user:
        uname = user.uname
        fname = user.fname
    if user and check_password_hash(user.password, password):
        # Clear tất cả session liên quan đến auth khi đăng nhập thành công
        session.pop('reset_email', None)
        session.pop('reset_otp', None)
        session.pop('otp', None)  # Xóa OTP từ đăng ký nếu có
        session.pop('temp_user', None)  # Xóa temp_user nếu có
        
        session['user_id'] = user.id
        session['user_name'] = user.uname
        session['full_name'] = user.fname
        session['user_avatar'] = user.avatar_url if user.avatar_url else None
        add_user_activity(user.id, "Đăng nhập", "Đăng nhập thành công")
        flash(f"Xin chào {user.fname}! Đăng nhập thành công!", "success")

        print(f"DEBUG: Login successful for {user.fname}, next_page: {next_page}")
        print(f"DEBUG: Session keys after login: {list(session.keys())}")
        
        # Kiểm tra và loại bỏ next_page nếu nó liên quan đến auth hoặc chứa loginfunction
        dangerous_paths = ['forgot-password', 'reset-password-otp', 'set-new-password', 'verify_otp', 'verify-otp', 'register', 'loginfunction', 'login']
        if next_page and any(path in next_page for path in dangerous_paths):
            print(f"DEBUG: Ignoring dangerous next_page: {next_page}")
            next_page = None
        
        # Kiểm tra next_page có hợp lệ không
        if next_page and next_page.strip() and not next_page.startswith('http'):
            if next_page.startswith('/'):
                # Đường dẫn tuyệt đối
                if '/page2' in next_page:
                    print("DEBUG: Redirecting to page2")
                    return redirect('/page2')
                elif '/page3' in next_page:
                    print("DEBUG: Redirecting to page3")
                    return redirect('/page3')
                elif '/page4' in next_page:
                    print("DEBUG: Redirecting to page4")
                    return redirect('/page4')
                else:
                    print(f"DEBUG: Redirecting to next_page: {next_page}")
                    return redirect(next_page)
            else:
                # URL đầy đủ
                if next_page.startswith(request.host_url):
                    print(f"DEBUG: Redirecting to full URL: {next_page}")
                    return redirect(next_page)
        
        print("DEBUG: Redirecting to main.index")
        return redirect(url_for('main.index'))
    else:
        print(f"DEBUG: Login failed for email: {email}")
        flash("Tài khoản hoặc mật khẩu không đúng", "error")
        return render_template('login.html')

@auth_blueprint.route('/register')
def register_page():
    next_page = request.args.get('next')
    return render_template("register.html", next=next_page)

@auth_blueprint.route('/registerfunction', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        fname = request.form.get("fname")
        uname = request.form.get("uname")
        sdt = request.form.get("sdt")
        email = request.form.get("email")
        password = request.form.get("pass")
        confirm_pass = request.form.get("confirm_pass")
        next_page = request.form.get("next_page")
        
        # Kiểm tra và loại bỏ next_page nếu nó liên quan đến đăng ký hoặc xác thực
        if next_page and any(path in next_page for path in ['verify_otp', 'verify-otp', 'register', 'forgot-password', 'reset-password-otp', 'set-new-password']):
            print(f"DEBUG: Ignoring next_page in register because it's related to auth: {next_page}")
            next_page = None
        
        if next_page:
            session['next_page'] = next_page

        user = Users.query.filter_by(email=email).first()
        if user:
            flash("Tài khoản đã tồn tại!", "error")
            return redirect(url_for("auth.register_page"))

        if not fname or not email or not password:
            flash("Thiếu thông tin bắt buộc", "error")
            return redirect(url_for('auth.register_page'))
        if password != confirm_pass:
            flash("Mật khẩu không khớp", "error")
            return redirect(url_for('auth.register_page'))

        # Kiểm tra độ mạnh mật khẩu
        is_valid, errors = validate_password_requirements(password)
        if not is_valid:
            error_message = "Mật khẩu không đạt yêu cầu:\n" + "\n".join(errors)
            flash(error_message, "error")
            return redirect(url_for('auth.register_page'))

        hashed_password = generate_password_hash(password)
        otp = generate_otp()

        if send_otp_email(email, otp):
            session['otp'] = otp
            session['temp_user'] = {
                'fname': fname,
                'uname': uname,
                'sdt': sdt,
                'email': email,
                'password': hashed_password
            }
            flash("Đăng ký thành công! Vui lòng kiểm tra email và nhập mã OTP để xác thực.", "success")
            return redirect(url_for('auth.verify_otp'))
        else:
            flash("Lỗi khi gửi email OTP", "error")
            return redirect(url_for('auth.register'))

    return render_template('index.html')

@auth_blueprint.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    # Kiểm tra session có hợp lệ không trước khi cho phép truy cập
    if not session.get('otp') or not session.get('temp_user'):
        flash("Phiên làm việc đã hết hạn hoặc không hợp lệ. Vui lòng đăng ký lại.", "error")
        return redirect(url_for('auth.register_page'))
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        if otp == session.get('otp'):
            temp_user = session.get('temp_user')
            if temp_user:
                new_user = Users(
                    fname=temp_user['fname'],
                    uname=temp_user['uname'],
                    sdt=temp_user['sdt'],
                    email=temp_user['email'],
                    password=temp_user['password']
                )
                db.session.add(new_user)
                db.session.commit()
                session['user_id'] = new_user.id
                session['user_name'] = new_user.uname
                session['full_name'] = new_user.fname
                session['user_avatar'] = new_user.avatar_url if new_user.avatar_url else None
                session.pop('temp_user', None)  
                session.pop('otp', None)  

                if 'user_id' in session:
                    print("User ID:", session['user_id'])
                else:
                    print("No user_id in session")
                    
                flash("Xác thực thành công!", "success")
                
                next_page = session.pop('next_page', None)
                
                # Kiểm tra và loại bỏ next_page nếu nó liên quan đến auth (reset password, register, verify_otp)
                if next_page and any(path in next_page for path in ['forgot-password', 'reset-password-otp', 'set-new-password', 'verify_otp', 'verify-otp', 'register']):
                    print(f"DEBUG: Ignoring next_page in verify_otp because it's related to auth: {next_page}")
                    next_page = None
                
                if next_page and '/page2' in next_page:
                    return redirect('/page2')
                elif next_page and '/page3' in next_page:
                    return redirect('/page3')
                elif next_page and '/page4' in next_page:
                    return redirect('/page4')
                elif next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('main.index'))
        else:
            flash("Mã OTP không đúng!", "error")
            return redirect(url_for('auth.verify_otp'))

    return render_template('verify_otp.html')

@auth_blueprint.route('/verify_otp_ajax', methods=['POST'])
def verify_otp_ajax():
    otp = request.form.get('otp')
    if otp == session.get('otp'):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Mã OTP không đúng!'})

@auth_blueprint.route("/logout")
def logout():
    session.clear()
    flash("Bạn đã đăng xuất!", "success")
    return redirect(url_for("main.index"))

def generate_otp(length=6):
    # Tạo mã OTP ngẫu nhiên có độ dài 6 ký tự
    otp = ''.join(random.choices(string.digits, k=length))
    return otp

def send_otp_email(user_email, otp):
    #Gửi otp cho người dùng
    msg = Message('Your OTP Code', recipients=[user_email])
    msg.body = f'Your OTP code is: {otp}'
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Error sending OTP email: {str(e)}")
        return False
    return True


@auth_blueprint.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    print(f"DEBUG: forgot_password called, method: {request.method}")
    print(f"DEBUG: Session keys: {list(session.keys())}")
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = Users.query.filter_by(email=email).first()
        if user:
            otp = generate_otp()
            session['reset_otp'] = otp
            session['reset_email'] = email
            send_otp_email(email, otp)
            flash("Đã gửi mã OTP khôi phục mật khẩu đến email của bạn", "success")
            return redirect(url_for('auth.reset_password_otp'))
        else:
            flash("Không tìm thấy tài khoản với email này", "error")
    return render_template('password_reset.html')


@auth_blueprint.route('/reset-password-otp', methods=['GET', 'POST'])
def reset_password_otp():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        stored_otp = session.get('reset_otp')
        
        if not stored_otp:
            flash("Phiên làm việc đã hết hạn. Vui lòng bắt đầu lại.", "error")
            return redirect(url_for('auth.forgot_password'))
            
        if entered_otp == stored_otp:
            flash("Xác thực OTP thành công. Vui lòng nhập mật khẩu mới.", "success")
            return redirect(url_for('auth.set_new_password'))
        else:
            flash("Mã OTP không đúng!", "error")
    
    # Kiểm tra session có hợp lệ không
    if not session.get('reset_email') or not session.get('reset_otp'):
        flash("Phiên làm việc đã hết hạn. Vui lòng bắt đầu lại.", "error")
        return redirect(url_for('auth.forgot_password'))
        
    return render_template('password_reset.html')

@auth_blueprint.route('/set-new-password', methods=['GET', 'POST'])
def set_new_password():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_pass = request.form.get('confirm_pass')
        if password != confirm_pass:
            flash("Mật khẩu không khớp!", "error")
            return redirect(url_for('auth.set_new_password'))
        
        # Kiểm tra độ mạnh mật khẩu
        is_valid, errors = validate_password_requirements(password)
        if not is_valid:
            error_message = "Mật khẩu mới không đạt yêu cầu:\n" + "\n".join(errors)
            flash(error_message, "error")
            return redirect(url_for('auth.set_new_password'))
        
        email = session.get('reset_email')
        if not email:
            flash("Phiên làm việc đã hết hạn. Vui lòng thử lại.", "error")
            return redirect(url_for('auth.forgot_password'))
            
        user = Users.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            
            # Clear tất cả session liên quan đến reset password và các session khác có thể gây xung đột
            session.pop('reset_email', None)
            session.pop('reset_otp', None)
            session.pop('otp', None)  # Xóa OTP từ đăng ký nếu có
            session.pop('temp_user', None)  # Xóa temp_user nếu có
            session.pop('next_page', None)  # Xóa next_page nếu có
            
            print(f"DEBUG: Password reset successful for {email}")
            print(f"DEBUG: Session keys after cleanup: {list(session.keys())}")
            
            flash("Đặt lại mật khẩu thành công! Vui lòng đăng nhập với mật khẩu mới.", "success")
            return redirect(url_for('auth.login_page'))
        else:
            flash("Không tìm thấy tài khoản!", "error")
            return redirect(url_for('auth.forgot_password'))
    
    # Kiểm tra session có hợp lệ không
    if not session.get('reset_email') or not session.get('reset_otp'):
        flash("Phiên làm việc đã hết hạn. Vui lòng bắt đầu lại.", "error")
        return redirect(url_for('auth.forgot_password'))
        
    return render_template('password_reset.html')


@auth_blueprint.route('/login/google')
def login_google():
    try:
        next_page = request.args.get('next')
        if next_page:
            session['next_page'] = next_page
            
        redirect_uri = url_for('auth.authorize_google', _external=True)
        return google.authorize_redirect(redirect_uri)
    except Exception as e:
        current_app.logger.error(f"Có lỗi xảy ra trong quá trình đăng nhập:{str(e)}")
        return "Có lỗi xảy ra trong quá trình đăng nhập",500

@auth_blueprint.route('/authorize/google')
def authorize_google():
    token = google.authorize_access_token()
    print("token:", token)
    userinfo_endpoint = google.server_metadata['userinfo_endpoint']
    resp = google.get(userinfo_endpoint)
    user_info = resp.json()
    username = user_info['email']

    user = Users.query.filter_by(email = username).first()
    if not user:
        user = Users(email = username)
        db.session.add(user)
        db.session.commit()
    
    session['user_id'] = user.id
    session['user_name'] = username
    session['oauth_token'] = token
    session['user_avatar'] = user.avatar_url if user.avatar_url else None

    next_page = session.pop('next_page', None)
    if next_page and '/page2' in next_page:
        return redirect('/page2')
    elif next_page and '/page3' in next_page:
        return redirect('/page3')
    elif next_page and '/page4' in next_page:
        return redirect('/page4')
    elif next_page:
        return redirect(next_page)
    else:
        return redirect(url_for('main.index'))


    
#changepass
@auth_blueprint.route('/change_password', methods=['POST'])
def change_password():
    if 'user_name' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401

    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'success': False, 'message': 'Thiếu thông tin mật khẩu'}), 400

    uname = session.get('user_name')
    user = Users.query.filter_by(uname=uname).first()

    if not user:
        return jsonify({'success': False, 'message': 'Không tìm thấy thông tin người dùng'}), 404

    if not check_password_hash(user.password, current_password):
        return jsonify({'success': False, 'message': 'Mật khẩu hiện tại không đúng'}), 400

    # Kiểm tra độ mạnh mật khẩu mới
    is_valid, errors = validate_password_requirements(new_password)
    if not is_valid:
        error_message = "Mật khẩu mới không đạt yêu cầu: " + "; ".join(errors)
        return jsonify({'success': False, 'message': error_message}), 400

    user.password = generate_password_hash(new_password)
    try:
        db.session.commit()
        add_user_activity(user.id, "Đổi mật khẩu", "Đã thay đổi mật khẩu")
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    


    #updateprofile
@auth_blueprint.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_name' not in session:
        return jsonify({'success': False, 'message': 'Người dùng chưa đăng nhập'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Dữ liệu không hợp lệ'}), 400

    # Xác định user từ session
    if 'oauth_token' in session:
        email = session['user_name']  # Lúc này là email
        user = Users.query.filter_by(email=email).first()
    else:
        uname = session['user_name']
        user = Users.query.filter_by(uname=uname).first()

    if not user:
        return jsonify({'success': False, 'message': 'Không tìm thấy người dùng'}), 404

    # Cập nhật các trường thông tin
    print("Data received from client:", data)
    user.fname = data.get('name', user.fname)
    user.email = data.get('email', user.email)  # Thêm cập nhật email
    user.address = data.get('address', user.address)
    user.position = data.get('position', user.position)
    user.sdt = data.get('phone', user.sdt)
    
    # Xử lý các trường mới
    user.gender = data.get('gender', user.gender)
    user.birth_date = data.get('birth_date', user.birth_date)
    print("Birth date before commit:", user.birth_date)

    # Nếu là user Google chưa có username, tạo một cái mặc định
    if 'oauth_token' in session and not user.uname:
        suggested_uname = data.get('name', '').lower().replace(' ', '_') or user.email.split('@')[0]
        existing_user = Users.query.filter_by(uname=suggested_uname).first()
        if not existing_user:
            user.uname = suggested_uname
        else:
            import random
            user.uname = f"{suggested_uname}_{random.randint(100, 999)}"

    # Cập nhật session
    session['full_name'] = user.fname

    if 'oauth_token' not in session:
        # Với user thường, nếu uname thay đổi thì cập nhật lại session
        if user.fname != session.get('full_name'):
            session['full_name'] = user.fname
    else:
        # Giữ nguyên user_name là email cho user Google
        session['user_name'] = user.email

    try:
        from app import db
        db.session.commit()
        print("Birth date after commit:", user.birth_date)
        add_user_activity(user.id, "Cập nhật thông tin", "Đã cập nhật thông tin cá nhân")
        return jsonify({'success': True, 'message': 'Cập nhật thông tin thành công'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Lỗi khi cập nhật: {str(e)}'}), 500

    

@auth_blueprint.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    try:
        user_id = session['user_id']
        
        # Import các models cần thiết
        from app.models.feedback import Feedback
        from app.models.experiences import Experience, ExperienceImage, ExperienceComment, ExperienceLike
        
        # Bắt đầu transaction
        print(f"Starting deletion process for user_id: {user_id}")
        
        # Xóa theo thứ tự từ bảng con đến bảng cha
        # 1. Xóa ExperienceImage trước (không có foreign key đến user)
        experiences_to_delete = Experience.query.filter_by(user_id=user_id).all()
        for exp in experiences_to_delete:
            ExperienceImage.query.filter_by(experience_id=exp.id).delete()
            ExperienceComment.query.filter_by(experience_id=exp.id).delete()
            ExperienceLike.query.filter_by(experience_id=exp.id).delete()
        
        # 2. Xóa các bình luận và likes của user trên experiences của người khác
        ExperienceComment.query.filter_by(user_id=user_id).delete()
        ExperienceLike.query.filter_by(user_id=user_id).delete()
        
        # 3. Xóa tất cả experiences của user
        Experience.query.filter_by(user_id=user_id).delete()
        
        # 4. Xóa các hoạt động của người dùng
        UserActivity.query.filter_by(user_id=user_id).delete()
        
        # 5. Xóa các feedback của người dùng
        Feedback.query.filter_by(user_id=user_id).delete()
        
        # 6. Xóa lịch sử nếu có (History table)
        try:
            from app.models.history import History
            History.query.filter_by(user_id=user_id).delete()
            print("History records deleted")
        except ImportError:
            print("No History model found, skipping")
        except Exception as history_error:
            print(f"Error deleting history: {str(history_error)}")
            # Không dừng quá trình nếu lỗi history
        
        # 7. Commit các thay đổi trước khi xóa user
        db.session.flush()
        
        # 8. Xóa người dùng cuối cùng
        user = Users.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            
            print(f"User {user_id} deleted successfully")
            
            # Xóa session
            session.clear()
            
            return jsonify({'success': True, 'message': 'Tài khoản đã được xóa thành công'})
        else:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Không tìm thấy tài khoản'}), 404
            
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting account: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        
        # Trả về lỗi chi tiết hơn
        error_message = str(e)
        if "violates" in error_message.lower() or "constraint" in error_message.lower():
            return jsonify({'success': False, 'message': 'Không thể xóa tài khoản do còn dữ liệu liên quan. Vui lòng liên hệ admin để được hỗ trợ.'}), 500
        else:
            return jsonify({'success': False, 'message': f'Lỗi khi xóa tài khoản: {error_message}'}), 500

@auth_blueprint.route('/check_user_data', methods=['GET'])
def check_user_data():
    """Debug route để kiểm tra dữ liệu liên quan đến user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    try:
        user_id = session['user_id']
        
        # Import các models
        from app.models.feedback import Feedback
        from app.models.experiences import Experience, ExperienceImage, ExperienceComment, ExperienceLike
        
        # Kiểm tra dữ liệu liên quan
        data_check = {
            'user_id': user_id,
            'experiences_count': Experience.query.filter_by(user_id=user_id).count(),
            'comments_count': ExperienceComment.query.filter_by(user_id=user_id).count(),
            'likes_count': ExperienceLike.query.filter_by(user_id=user_id).count(),
            'activities_count': UserActivity.query.filter_by(user_id=user_id).count(),
            'feedbacks_count': Feedback.query.filter_by(user_id=user_id).count(),
        }
        
        # Kiểm tra History nếu có
        try:
            from app.models.history import History
            data_check['history_count'] = History.query.filter_by(user_id=user_id).count()
        except ImportError:
            data_check['history_count'] = 'N/A (model not found)'
        
        # Kiểm tra các experience images liên quan
        user_experiences = Experience.query.filter_by(user_id=user_id).all()
        total_images = 0
        for exp in user_experiences:
            total_images += ExperienceImage.query.filter_by(experience_id=exp.id).count()
        data_check['experience_images_count'] = total_images
        
        return jsonify({'success': True, 'data': data_check})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_blueprint.route('/delete_account_safe', methods=['POST'])
def delete_account_safe():
    """Alternative approach sử dụng raw SQL để xóa tài khoản an toàn"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    try:
        user_id = session['user_id']
        print(f"Starting safe deletion process for user_id: {user_id}")
        
        # Sử dụng raw SQL để xóa theo thứ tự nghiêm ngặt
        # Tắt foreign key checks tạm thời
        db.session.execute("SET foreign_key_checks = 0")
        
        # 1. Xóa experience images
        db.session.execute("""
            DELETE FROM experience_images 
            WHERE experience_id IN (
                SELECT id FROM experiences WHERE user_id = :user_id
            )
        """, {"user_id": user_id})
        
        # 2. Xóa experience comments của experiences của user này
        db.session.execute("""
            DELETE FROM experience_comments 
            WHERE experience_id IN (
                SELECT id FROM experiences WHERE user_id = :user_id
            )
        """, {"user_id": user_id})
        
        # 3. Xóa experience likes của experiences của user này
        db.session.execute("""
            DELETE FROM experience_likes 
            WHERE experience_id IN (
                SELECT id FROM experiences WHERE user_id = :user_id
            )
        """, {"user_id": user_id})
        
        # 4. Xóa comments của user trên experiences của người khác
        db.session.execute("""
            DELETE FROM experience_comments WHERE user_id = :user_id
        """, {"user_id": user_id})
        
        # 5. Xóa likes của user trên experiences của người khác
        db.session.execute("""
            DELETE FROM experience_likes WHERE user_id = :user_id
        """, {"user_id": user_id})
        
        # 6. Xóa experiences của user
        db.session.execute("""
            DELETE FROM experiences WHERE user_id = :user_id
        """, {"user_id": user_id})
        
        # 7. Xóa user activities
        db.session.execute("""
            DELETE FROM user_activity WHERE user_id = :user_id
        """, {"user_id": user_id})
        
        # 8. Xóa feedbacks
        db.session.execute("""
            DELETE FROM feedback WHERE user_id = :user_id
        """, {"user_id": user_id})
        
        # 9. Xóa history nếu có
        try:
            db.session.execute("""
                DELETE FROM history WHERE user_id = :user_id
            """, {"user_id": user_id})
        except Exception as e:
            print(f"History deletion failed (table might not exist): {e}")
        
        # 10. Cuối cùng xóa user
        db.session.execute("""
            DELETE FROM user2 WHERE id = :user_id
        """, {"user_id": user_id})
        
        # Bật lại foreign key checks
        db.session.execute("SET foreign_key_checks = 1")
        
        # Commit tất cả
        db.session.commit()
        
        print(f"User {user_id} deleted successfully using safe method")
        
        # Xóa session
        session.clear()
        
        return jsonify({'success': True, 'message': 'Tài khoản đã được xóa thành công'})
        
    except Exception as e:
        db.session.rollback()
        # Bật lại foreign key checks trong trường hợp lỗi
        try:
            db.session.execute("SET foreign_key_checks = 1")
            db.session.commit()
        except:
            pass
            
        print(f"Error in safe deletion: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        
        error_message = str(e)
        return jsonify({'success': False, 'message': f'Lỗi khi xóa tài khoản: {error_message}'}), 500
    