# app/routes/auth_routes.py
from flask import Blueprint,current_app, render_template, request, redirect, session, flash, url_for, jsonify,current_app
from app.models.users import Users
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, mail
from flask_mail import Message
import random, string
from app.extension import google

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/login')
def login_page():
    return render_template("login.html")

@auth_blueprint.route('/loginfunction', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = Users.query.filter_by(email=email).first()
    if user:
        uname = user.uname
        fname = user.fname
    if user and check_password_hash(user.password, password):
        session['full_name'] = fname
        session['user_name'] = uname
        return redirect(url_for('main.index'))
    else:
        flash("Tài khoản hoặc mật khẩu không đúng", "error")
        return render_template('login.html')

@auth_blueprint.route('/register')
def register_page():
    return render_template("register.html")

@auth_blueprint.route('/registerfunction', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        fname = request.form.get("fname")
        uname = request.form.get("uname")
        sdt = request.form.get("sdt")
        email = request.form.get("email")
        password = request.form.get("pass")
        confirm_pass = request.form.get("confirm_pass")

        user = Users.query.filter_by(email=email).first()
        if user:
            session['user_name'] = user.uname
            flash("Tài khoản đã tồn tại!", "error")
            return redirect(url_for("main.index"))

        if not fname or not email or not password:
            return jsonify({"error": "Missing required parameters"}), 400
        if password != confirm_pass:
            return jsonify({"error": "Passwords do not match"}), 400

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
                session.pop('temp_user', None)  
                session.pop('otp', None)  

                if 'user_id' in session:
                    print("User ID:", session['user_id'])
                else:
                    print("No user_id in session")
                    
                flash("Xác thực thành công!", "success")
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
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("full_name", None)
    flash("Bạn đã đăng xuất!", "success")
    return redirect(url_for("main.index"))

def generate_otp(length=6):
    # Tạo mã OTP ngẫu nhiên có độ dài 6 ký tự
    otp = ''.join(random.choices(string.digits, k=length))
    return otp

def send_otp_email(user_email, otp):
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
        if entered_otp == session.get('reset_otp'):
            flash("Xác thực OTP thành công. Vui lòng nhập mật khẩu mới.", "success")
            return redirect(url_for('auth.set_new_password'))
        else:
            flash("Mã OTP không đúng!", "error")
    return render_template('password_reset.html')

@auth_blueprint.route('/set-new-password', methods=['GET', 'POST'])
def set_new_password():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_pass = request.form.get('confirm_pass')
        if password != confirm_pass:
            flash("Mật khẩu không khớp!", "error")
            return redirect(url_for('auth.set_new_password'))
        
        email = session.get('reset_email')
        user = Users.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            session.pop('reset_email', None)
            session.pop('reset_otp', None)
            flash("Đặt lại mật khẩu thành công!", "success")
            return redirect(url_for('auth.login_page'))
    return render_template('password_reset.html')


@auth_blueprint.route('/login/google')
def login_google():
    try:
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
    
    session['user_name'] = username
    session['oauth_token'] = token

    return redirect(url_for('main.index'))