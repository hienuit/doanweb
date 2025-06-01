from flask import Blueprint, render_template,request, session, redirect, url_for, flash,jsonify, Response
from app.models.destinations import search_describe 
from app.models.users import Users, UserActivity
from app.models.feedback import Feedback
from app import db
import os
from werkzeug.utils import secure_filename
import time
from app.models.experiences import Experience, ExperienceComment
from sqlalchemy import func
from app.utils import get_avatar_url

main_blueprint = Blueprint('main', __name__)

# Cấu hình upload
UPLOAD_FOLDER = 'app/static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Tạo thư mục upload nếu chưa tồn tại
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@main_blueprint.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

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
                birth_year = parts[0]
                birth_month = str(int(parts[1]))  # Bỏ số 0 đầu
                birth_day = str(int(parts[2]))    # Bỏ số 0 đầu
        except Exception as e:
            print(f"Error parsing birth_date: {e}")
            pass
    user_data = {
        'name': user.fname if user.fname else (user.email.split('@')[0] if user.email else "Người dùng mới"),
        'email': user.email,
        'phone': user.sdt if user.sdt else "",
        'address': user.address if user.address else "",
        'position': user.position if user.position else "",
        'gender': user.gender if user.gender else "",
        'birth_date': user.birth_date if user.birth_date else "",
        'birthYear': birth_year,
        'birthMonth': birth_month,
        'birthDay': birth_day,
        'is_google_user': 'oauth_token' in session,
        'avatar_url': get_avatar_url(user.avatar_url) 
    }
    
    # Thống kê experiences của user
    experiences_stats = {
        'total_experiences': Experience.query.filter_by(user_id=user.id).count(),
        'total_likes': db.session.query(func.sum(Experience.likes)).filter_by(user_id=user.id).scalar() or 0,
        'total_views': db.session.query(func.sum(Experience.views)).filter_by(user_id=user.id).scalar() or 0,
        'total_comments': db.session.query(func.count(ExperienceComment.id)).join(Experience).filter(Experience.user_id == user.id).scalar() or 0
    }
    
    # Thống kê theo điểm đến
    destination_stats_raw = db.session.query(
        Experience.destination, 
        func.count(Experience.id).label('count')
    ).filter_by(user_id=user.id).group_by(Experience.destination).all()

    # Chuyển đổi thành list of dictionaries để có thể serialize JSON
    destination_stats = [
        {'destination': row.destination, 'count': row.count} 
        for row in destination_stats_raw
    ]

    # Thống kê theo travel style
    travel_style_stats_raw = db.session.query(
        Experience.travel_style, 
        func.count(Experience.id).label('count')
    ).filter_by(user_id=user.id).group_by(Experience.travel_style).all()

    # Chuyển đổi thành list of dictionaries để có thể serialize JSON
    travel_style_stats = [
        {'travel_style': row.travel_style, 'count': row.count} 
        for row in travel_style_stats_raw
    ]
    
    # Thống kê ngân sách
    budget_stats = db.session.query(
        func.avg(Experience.budget).label('avg_budget'),
        func.min(Experience.budget).label('min_budget'),
        func.max(Experience.budget).label('max_budget'),
        func.sum(Experience.budget).label('total_budget')
    ).filter(Experience.user_id == user.id, Experience.budget.isnot(None)).first()
    
    achievements = []
    if experiences_stats['total_experiences'] >= 10:
        achievements.append({'name': 'Blogger Du Lịch', 'icon': 'fas fa-pen-fancy', 'description': 'Đã chia sẻ 10+ trải nghiệm'})
    if experiences_stats['total_likes'] >= 50:
        achievements.append({'name': 'Người Được Yêu Thích', 'icon': 'fas fa-heart', 'description': 'Nhận được 50+ lượt thích'})
    if len(destination_stats) >= 5:
        achievements.append({'name': 'Nhà Thám Hiểm', 'icon': 'fas fa-globe', 'description': 'Đã khám phá 5+ điểm đến'})
    
    # trải nghiệm được chia sẽ gần đây
    recent_experiences = Experience.query.filter_by(user_id=user.id)\
        .order_by(Experience.created_at.desc()).limit(5).all()
    
    # xếp bài viết đưuọc nhìu like nhất và ít nhất 
    most_liked_experience = Experience.query.filter_by(user_id=user.id)\
        .order_by(Experience.likes.desc()).first()
    most_viewed_experience = Experience.query.filter_by(user_id=user.id)\
        .order_by(Experience.views.desc()).first()
    
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
    
    return render_template("dashboard.html", 
                         user_data=user_data, 
                         history=history,
                         experiences_stats=experiences_stats,
                         destination_stats=destination_stats,
                         travel_style_stats=travel_style_stats,
                         budget_stats=budget_stats,
                         achievements=achievements,
                         recent_experiences=recent_experiences,
                         most_liked_experience=most_liked_experience,
                         most_viewed_experience=most_viewed_experience)


# lịch sử hoạt động, lịch sử đăng nhập hoặc là chỉnh sủa
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
    
    # truy vấn lịch sử hoạt động
    activities = UserActivity.query.filter_by(user_id=user.id)\
        .order_by(UserActivity.timestamp.desc())\
        .paginate(page=page, per_page=per_page)
    
    # định dạng lại thời gian hoạt động
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

#feedback
@main_blueprint.route('/feedback', methods=['GET'])
def feedback():
    # Kiểm tra đăng nhập qua session
    if 'user_name' not in session and 'oauth_token' not in session:
        flash("Vui lòng đăng nhập để gửi góp ý", "error")
        return redirect(url_for('auth.login_page'))
    
    # Lấy thông tin user từ session
    if 'oauth_token' in session:
        email = session.get('user_name')
        user = Users.query.filter_by(email=email).first()
    else:
        uname = session.get('user_name')
        user = Users.query.filter_by(uname=uname).first()
    
    if not user:
        flash("Không tìm thấy thông tin người dùng", "error")
        return redirect(url_for('auth.logout'))
        
    user_feedbacks = Feedback.query.filter_by(user_id=user.id).order_by(Feedback.created_at.desc()).all()
    return render_template('feedback.html', feedbacks=user_feedbacks)

@main_blueprint.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    try:
        # Kiểm tra đăng nhập qua session
        if 'user_name' not in session and 'oauth_token' not in session:
            return jsonify({'error': 'Vui lòng đăng nhập để gửi góp ý'}), 401
            
        # Lấy thông tin user từ session
        if 'oauth_token' in session:
            email = session.get('user_name')
            user = Users.query.filter_by(email=email).first()
        else:
            uname = session.get('user_name')
            user = Users.query.filter_by(uname=uname).first()
            
        if not user:
            return jsonify({'error': 'Không tìm thấy thông tin người dùng'}), 404
            
        # Lấy dữ liệu từ JSON request
        data = request.get_json()
        subject = data.get('subject')
        message = data.get('message')
        
        if not subject or not message:
            return jsonify({'error': 'Vui lòng điền đầy đủ thông tin'}), 400
            
        print(f"User {user.id} gửi góp ý với chủ đề: {subject}")
        
        feedback = Feedback(
            user_id=user.id,
            subject=subject,
            message=message,
            status='pending'
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        # Thêm hoạt động vào lịch sử
        activity = UserActivity(
            user_id=user.id,
            activity='feedback_submit',
            details=f'Gửi góp ý với chủ đề: {subject}'
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Cảm ơn bạn đã gửi góp ý!'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi gửi góp ý'}), 500

@main_blueprint.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    if 'user_name' not in session and 'oauth_token' not in session:
        return jsonify({'error': 'Vui lòng đăng nhập để thực hiện chức năng này'}), 401
        
    # Lấy thông tin user từ session
    if 'oauth_token' in session:
        email = session.get('user_name')
        user = Users.query.filter_by(email=email).first()
    else:
        uname = session.get('user_name')
        user = Users.query.filter_by(uname=uname).first()
    
    if not user:
        return jsonify({'error': 'Không tìm thấy thông tin người dùng'}), 404
        
    if 'avatar' not in request.files:
        return jsonify({'error': 'Không tìm thấy file ảnh'}), 400
        
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'Chưa chọn file ảnh'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'Định dạng file không được hỗ trợ'}), 400
        
    try:
        # Tạo tên file duy nhất
        filename = secure_filename(f"avatar_{user.id}_{int(time.time())}{os.path.splitext(file.filename)[1]}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Lưu file
        file.save(filepath)
        
        # Cập nhật đường dẫn avatar trong database
        # Lưu đường dẫn đầy đủ tương thích với Flask static
        full_avatar_url = url_for('static', filename=f'uploads/avatars/{filename}')
        user.avatar_url = full_avatar_url
        db.session.commit()
        
        # Cập nhật session để các trang khác cũng hiển thị avatar mới
        session['user_avatar'] = full_avatar_url
        
        # Thêm hoạt động vào lịch sử
        activity = UserActivity(
            user_id=user.id,
            activity='avatar_update',
            details='Đã cập nhật ảnh đại diện'
        )
        db.session.add(activity)
        db.session.commit()
        
        # Trả về đường dẫn đầy đủ cho frontend
        return jsonify({
            'success': True,
            'avatar_url': full_avatar_url
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi upload avatar'}), 500

@main_blueprint.route('/get-user-feedbacks', methods=['GET'])
def get_user_feedbacks():
    # Kiểm tra đăng nhập
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

        # Lấy danh sách góp ý của user
        user_feedbacks = Feedback.query.filter_by(user_id=user.id).order_by(Feedback.created_at.desc()).all()
        
        # Chuyển đổi thành format JSON
        feedbacks_data = []
        for feedback in user_feedbacks:
            feedback_dict = {
                'id': feedback.id,
                'subject': feedback.subject,
                'message': feedback.message,
                'status': feedback.status,
                'created_at': feedback.created_at.strftime('%d-%m-%Y %H:%M'),
                'response': feedback.response,
                'response_at': feedback.response_at.strftime('%d-%m-%Y %H:%M') if feedback.response_at else None
            }
            feedbacks_data.append(feedback_dict)

        return jsonify({
            'success': True,
            'feedbacks': feedbacks_data
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main_blueprint.route('/get-user-experiences', methods=['GET'])
def get_user_experiences():
    """Lấy danh sách experiences của user với phân trang"""
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

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Lấy danh sách experiences của user
        experiences_paginated = Experience.query.filter_by(user_id=user.id)\
            .order_by(Experience.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        # Chuyển đổi thành format JSON
        experiences_data = []
        for experience in experiences_paginated.items:
            experience_dict = {
                'id': experience.id,
                'title': experience.title,
                'destination': experience.destination,
                'content': experience.content[:100] + '...' if len(experience.content) > 100 else experience.content,
                'rating': experience.rating,
                'travel_date': experience.travel_date.strftime('%d/%m/%Y') if experience.travel_date else None,
                'budget': experience.budget,
                'travel_style': experience.travel_style,
                'travel_duration': experience.travel_duration,
                'created_at': experience.created_at.strftime('%d/%m/%Y %H:%M'),
                'likes': experience.likes,
                'views': experience.views,
                'comments_count': len(experience.comments),
                'images_count': len(experience.images),
                'is_featured': experience.is_featured,
                'is_approved': experience.is_approved
            }
            experiences_data.append(experience_dict)

        return jsonify({
            'success': True,
            'experiences': experiences_data,
            'has_next': experiences_paginated.has_next,
            'has_prev': experiences_paginated.has_prev,
            'total': experiences_paginated.total,
            'pages': experiences_paginated.pages,
            'current_page': page
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@main_blueprint.route('/delete-experience', methods=['POST'])
def delete_experience():
    """Xóa experience của user"""
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

        experience_id = request.json.get('experience_id')
        experience = Experience.query.filter_by(id=experience_id, user_id=user.id).first()
        
        if not experience:
            return jsonify({'success': False, 'message': 'Experience not found or not authorized'}), 404

        # Xóa experience (cascade sẽ tự động xóa images, comments, likes)
        db.session.delete(experience)
        db.session.commit()
        
        # Thêm hoạt động vào lịch sử
        activity = UserActivity(
            user_id=user.id,
            activity='experience_delete',
            details=f'Đã xóa trải nghiệm: {experience.title}'
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Xóa trải nghiệm thành công'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@main_blueprint.route('/get-experience-stats', methods=['GET'])
def get_experience_stats():
    """Lấy thống kê chi tiết về experiences của user"""
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

        # Thống kê tổng quan
        total_stats = {
            'total_experiences': Experience.query.filter_by(user_id=user.id).count(),
            'total_likes': db.session.query(func.sum(Experience.likes)).filter_by(user_id=user.id).scalar() or 0,
            'total_views': db.session.query(func.sum(Experience.views)).filter_by(user_id=user.id).scalar() or 0,
            'total_comments': db.session.query(func.count(ExperienceComment.id)).join(Experience).filter(Experience.user_id == user.id).scalar() or 0
        }
        
        # Thống kê theo điểm đến
        destination_stats_raw = db.session.query(
            Experience.destination, 
            func.count(Experience.id).label('count')
        ).filter_by(user_id=user.id).group_by(Experience.destination).all()
        
        # Chuyển đổi thành list of dictionaries để có thể serialize JSON
        destination_stats = [
            {'destination': row.destination, 'count': row.count} 
            for row in destination_stats_raw
        ]
        
        # Thống kê theo travel style
        travel_style_stats_raw = db.session.query(
            Experience.travel_style, 
            func.count(Experience.id).label('count')
        ).filter_by(user_id=user.id).group_by(Experience.travel_style).all()
        
        # Chuyển đổi thành list of dictionaries để có thể serialize JSON
        travel_style_stats = [
            {'travel_style': row.travel_style, 'count': row.count} 
            for row in travel_style_stats_raw
        ]
        
        # Thống kê ngân sách
        budget_stats = db.session.query(
            func.avg(Experience.budget).label('avg_budget'),
            func.min(Experience.budget).label('min_budget'),
            func.max(Experience.budget).label('max_budget'),
            func.sum(Experience.budget).label('total_budget')
        ).filter(Experience.user_id == user.id, Experience.budget.isnot(None)).first()

        return jsonify({
            'success': True,
            'total_stats': total_stats,
            'destination_stats': destination_stats,
            'travel_style_stats': travel_style_stats,
            'budget_stats': {
                'avg_budget': float(budget_stats.avg_budget) if budget_stats.avg_budget else 0,
                'min_budget': float(budget_stats.min_budget) if budget_stats.min_budget else 0,
                'max_budget': float(budget_stats.max_budget) if budget_stats.max_budget else 0,
                'total_budget': float(budget_stats.total_budget) if budget_stats.total_budget else 0
            } if budget_stats else {'avg_budget': 0, 'min_budget': 0, 'max_budget': 0, 'total_budget': 0}
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@main_blueprint.route('/robots.txt')
def robots_txt():
    """Serve robots.txt file for SEO"""
    robots_content = """User-agent: *
Allow: /

# Sitemap location
Sitemap: https://dulichbyai.id.vn/sitemap.xml

# Disallow admin and API pages
Disallow: /admin/
Disallow: /api/
Disallow: /auth/facebook
Disallow: /auth/google
Disallow: /.git/
Disallow: /uploads/

# Allow important pages
Allow: /
Allow: /experiences
Allow: /page2
Allow: /page3
Allow: /page4
Allow: /schedule
Allow: /map
Allow: /login
Allow: /register
"""
    
    response = Response(robots_content, mimetype='text/plain')
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response
