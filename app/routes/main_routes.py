# app/routes/main_routes.py
from flask import Blueprint, render_template,request, session, redirect, url_for, flash,jsonify
from app.models.destinations import search_describe 
from app.models.users import Users, UserActivity

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
def index():
    return render_template('index.html')

@main_blueprint.route("/page2")
def page2():
    return render_template("page2.html")

@main_blueprint.route("/page3")
def page3():
    province = request.args.get("province")
    if not province:
        return "Thiếu tên tỉnh!", 400

    data = search_describe(province)
    if not data:
        return "Không tìm thấy tỉnh!", 404

    print("DEBUG PAGE3:", data)  # In ra để kiểm tra có gì không
    return render_template("page3.html",
                       province=data[0]["name"],
                       describe=data[0]["describe"],
                       images=data[0]["images"])

@main_blueprint.route("/page4")
def page4():
    return render_template("page4.html")

@main_blueprint.route("/schedule")
def schedule():
    province = request.args.get("province") or request.args.get("destination")
    return render_template("schedule.html",province=province)

@main_blueprint.route("/map")
def map():
    return render_template("map.html")

@main_blueprint.route("/hotel")
def hotel():
    return render_template("hotel.html")

@main_blueprint.route("/navbar")
def navbar():
    return render_template("navbar.html")

@main_blueprint.route("/dashboard")
def dashboard():
    # Kiểm tra xem người dùng đã đăng nhập chưa
    if 'user_name' not in session and 'oauth_token' not in session:
        flash("Vui lòng đăng nhập để xem dashboard", "error")
        return redirect(url_for('auth.login_page'))
    
    # Lấy thông tin người dùng từ database
    if 'oauth_token' in session:
        # Người dùng đăng nhập bằng Google
        email = session.get('user_name')  # Trong trường hợp Google, user_name là email
        user = Users.query.filter_by(email=email).first()
    else:
        # Người dùng đăng nhập thông thường
        uname = session.get('user_name')
        user = Users.query.filter_by(uname=uname).first()
    
    if not user:
        flash("Không tìm thấy thông tin người dùng", "error")
        return redirect(url_for('auth.logout'))
    
    # Tạo từ điển chứa thông tin người dùng

    birth_day = ""
    birth_month = ""
    birth_year = ""

    if user.birth_date:
        try:
            parts = user.birth_date.split('-')
            if len(parts) == 3:
                birth_year, birth_month, birth_day = parts
        except:
            pass
    user_data = {
        'name': user.fname if user.fname else (user.email.split('@')[0] if user.email else "Người dùng mới"),
        'email': user.email,
        'phone': user.sdt if user.sdt else "",
        'address': user.address if user.address else "",  # Thêm thông tin địa chỉ
        'position': user.position if user.position else "",  # Thêm thông tin chức vụ
        'gender': user.gender if user.gender else "",  # Thêm thông tin giới tính
        'birth_date': user.birth_date if user.birth_date else "",  # Thêm thông tin ngày sinh
        'birthYear': birth_year,
        'birthMonth': birth_month,
        'birthDay': birth_day,
        'is_google_user': 'oauth_token' in session
    }
    
    # In ra console để debug
    print("User data being sent to frontend:", user_data)
    
    # Giả lập lịch sử hoạt động (hoặc lấy từ database nếu có)
    activities = UserActivity.query.filter_by(user_id=user.id)\
        .order_by(UserActivity.timestamp.desc())\
        .limit(10).all()
    
    history = [
        {
            'date': activity.timestamp.strftime('%d/%m/%Y'),
            'time': activity.timestamp.strftime('%H:%M'),
            'activity': activity.activity,
            'details': activity.details
        }
        for activity in activities
    ]
    
    return render_template("dashboard.html", user_data=user_data, history=history)


#lichsuhoatdong
@main_blueprint.route("/get_more_history", methods=['POST'])
def get_more_history():
    if 'user_name' not in session and 'oauth_token' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    page = request.json.get('page', 1)
    per_page = request.json.get('per_page', 10)
    
    # Xác định người dùng
    if 'oauth_token' in session:
        email = session.get('user_name')
        user = Users.query.filter_by(email=email).first()
    else:
        uname = session.get('user_name')
        user = Users.query.filter_by(uname=uname).first()
    
    if not user:
        return jsonify({'success': False, 'message': 'Không tìm thấy thông tin người dùng'}), 404
    
    # Query lịch sử hoạt động
    activities = UserActivity.query.filter_by(user_id=user.id)\
        .order_by(UserActivity.timestamp.desc())\
        .paginate(page=page, per_page=per_page)
    
    # Format kết quả
    history = []
    for activity in activities.items:
        history.append({
            'date': activity.timestamp.strftime('%d/%m/%Y'),
            'time': activity.timestamp.strftime('%H:%M'),
            'activity': activity.activity,
            'details': activity.details
        })
    
    return jsonify({
        'success': True,
        'history': history,
        'has_next': activities.has_next
    })


@main_blueprint.route("/get_latest_activities")
def get_latest_activities():
    if 'user_name' not in session and 'oauth_token' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        # Xác định user
        if 'oauth_token' in session:
            email = session.get('user_name')
            user = Users.query.filter_by(email=email).first()
        else:
            uname = session.get('user_name')
            user = Users.query.filter_by(uname=uname).first()

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Lấy 10 hoạt động gần nhất
        activities = UserActivity.query.filter_by(user_id=user.id)\
            .order_by(UserActivity.timestamp.desc())\
            .limit(10).all()

        history = [{
            'date': activity.timestamp.strftime('%d/%m/%Y'),
            'time': activity.timestamp.strftime('%H:%M'),
            'activity': activity.activity,
            'details': activity.details
        } for activity in activities]

        return jsonify({'success': True, 'history': history})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main_blueprint.route('/history', methods=['GET'])
def history():
    return render_template('history.html')

@main_blueprint.route('/personalized-history', methods=['GET'])
def personalized_history():
    return render_template('personalized-history.html')

# Thêm route để hiển thị trang ưu đãi
@main_blueprint.route('/promotions')
def promotions():
    """Hiển thị trang ưu đãi du lịch."""
    return render_template('promotions.html')
