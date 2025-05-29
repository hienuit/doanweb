from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app.models.experiences import Experience, ExperienceImage, ExperienceComment, ExperienceLike
from app.models.users import Users
from app import db
from datetime import datetime
import os

experience_blueprint = Blueprint('experience', __name__)

# Cấu hình upload
UPLOAD_FOLDER = 'app/static/uploads/experiences'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Tạo thư mục upload nếu chưa tồn tại
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@experience_blueprint.route('/experiences')
def experiences():
    """Trang hiển thị tất cả trải nghiệm"""
    page = request.args.get('page', 1, type=int)
    per_page = 9
    
    # Lọc theo các tiêu chí
    destination = request.args.get('destination', '')
    rating = request.args.get('rating', type=int)
    travel_style = request.args.get('travel_style', '')
    sort_by = request.args.get('sort_by', 'newest')  # newest, oldest, rating, likes
    
    # Query cơ bản
    query = Experience.query.filter_by(is_approved=True)
    
    # Áp dụng filters
    if destination:
        query = query.filter(Experience.destination.ilike(f'%{destination}%'))
    if rating:
        query = query.filter(Experience.rating >= rating)
    if travel_style:
        query = query.filter(Experience.travel_style == travel_style)
    
    # Sắp xếp
    if sort_by == 'oldest':
        query = query.order_by(Experience.created_at.asc())
    elif sort_by == 'rating':
        query = query.order_by(Experience.rating.desc())
    elif sort_by == 'likes':
        query = query.order_by(Experience.likes.desc())
    else:  # newest
        query = query.order_by(Experience.created_at.desc())
    
    # Phân trang
    experiences_paginated = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Lấy trải nghiệm nổi bật
    featured_experiences = Experience.query.filter_by(
        is_featured=True, is_approved=True
    ).order_by(Experience.created_at.desc()).limit(3).all()
    
    return render_template('experiences.html', 
                         experiences=experiences_paginated,
                         featured_experiences=featured_experiences,
                         current_filters={
                             'destination': destination,
                             'rating': rating,
                             'travel_style': travel_style,
                             'sort_by': sort_by
                         })

@experience_blueprint.route('/experience/<int:experience_id>')
def experience_detail(experience_id):
    """Trang chi tiết trải nghiệm"""
    experience = Experience.query.get_or_404(experience_id)
    
    # Tăng lượt xem
    experience.views += 1
    db.session.commit()
    
    # Lấy các trải nghiệm liên quan (cùng điểm đến)
    related_experiences = Experience.query.filter(
        Experience.destination == experience.destination,
        Experience.id != experience.id,
        Experience.is_approved == True
    ).order_by(Experience.rating.desc()).limit(4).all()
    
    # Kiểm tra user đã like chưa
    user_liked = False
    if 'user_name' in session or 'oauth_token' in session:
        user = get_current_user()
        if user:
            user_liked = ExperienceLike.query.filter_by(
                experience_id=experience.id, user_id=user.id
            ).first() is not None
    
    # Lấy comments có cấu trúc parent-child
    # Chỉ lấy comments gốc (parent_id = None) và sắp xếp theo thời gian tạo
    cac_binh_luan_goc = ExperienceComment.query.filter_by(
        experience_id=experience_id, 
        parent_id=None
    ).order_by(ExperienceComment.created_at.desc()).all()
    
    # Với mỗi comment gốc, lấy các replies của nó
    danh_sach_binh_luan_day_du = []
    for binh_luan_goc in cac_binh_luan_goc:
        cac_tra_loi = ExperienceComment.query.filter_by(
            parent_id=binh_luan_goc.id
        ).order_by(ExperienceComment.created_at.asc()).all()
        
        danh_sach_binh_luan_day_du.append({
            'binh_luan_goc': binh_luan_goc,
            'cac_tra_loi': cac_tra_loi
        })
    
    return render_template('experience_detail.html', 
                         experience=experience,
                         related_experiences=related_experiences,
                         user_liked=user_liked,
                         danh_sach_binh_luan_day_du=danh_sach_binh_luan_day_du)

@experience_blueprint.route('/share-experience')
def share_experience():
    """Trang chia sẻ trải nghiệm mới"""
    if 'user_name' not in session and 'oauth_token' not in session:
        flash("Vui lòng đăng nhập để chia sẻ trải nghiệm", "error")
        return redirect(url_for('auth.login_page'))
    
    return render_template('share_experience.html')

@experience_blueprint.route('/submit-experience', methods=['POST'])
def submit_experience():
    """Xử lý submit trải nghiệm mới"""
    if 'user_name' not in session and 'oauth_token' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Không tìm thấy thông tin người dùng'}), 404
    
    try:
        # Lấy dữ liệu từ form
        data = request.get_json()
        
        # Tạo trải nghiệm mới
        experience = Experience(
            user_id=user.id,
            destination=data['destination'],
            title=data['title'],
            content=data['content'],
            rating=int(data['rating']),
            travel_date=datetime.strptime(data['travel_date'], '%Y-%m-%d').date(),
            budget=float(data['budget']) if data.get('budget') else None,
            travel_style=data.get('travel_style'),
            travel_duration=int(data['travel_duration']) if data.get('travel_duration') else None
        )
        
        db.session.add(experience)
        db.session.flush()  # Để lấy ID
        
        # Xử lý upload ảnh
        if 'images' in data and data['images']:
            for image_url in data['images']:
                experience_image = ExperienceImage(
                    experience_id=experience.id,
                    image_url=image_url,
                    caption=data.get('image_caption', '')
                )
                db.session.add(experience_image)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Chia sẻ trải nghiệm thành công!',
            'experience_id': experience.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'}), 500

@experience_blueprint.route('/like-experience', methods=['POST'])
def like_experience():
    """Like/Unlike trải nghiệm"""
    if 'user_name' not in session and 'oauth_token' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Không tìm thấy thông tin người dùng'}), 404
    
    experience_id = request.json.get('experience_id')
    experience = Experience.query.get_or_404(experience_id)
    
    # Kiểm tra đã like chưa
    existing_like = ExperienceLike.query.filter_by(
        experience_id=experience_id, user_id=user.id
    ).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        experience.likes -= 1
        liked = False
    else:
        # Like
        new_like = ExperienceLike(experience_id=experience_id, user_id=user.id)
        db.session.add(new_like)
        experience.likes += 1
        liked = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'liked': liked,
        'likes_count': experience.likes
    })

@experience_blueprint.route('/comment-experience', methods=['POST'])
def comment_experience():
    """Thêm bình luận cho trải nghiệm"""
    if 'user_name' not in session and 'oauth_token' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Không tìm thấy thông tin người dùng'}), 404
    
    experience_id = request.json.get('experience_id')
    content = request.json.get('content', '').strip()
    
    if not content:
        return jsonify({'success': False, 'message': 'Nội dung bình luận không được để trống'}), 400
    
    experience = Experience.query.get_or_404(experience_id)
    
    # Tạo bình luận mới
    comment = ExperienceComment(
        experience_id=experience_id,
        user_id=user.id,
        content=content
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': comment.to_dict()
    })

@experience_blueprint.route('/reply-comment', methods=['POST'])
def tra_loi_binh_luan():
    """Trả lời bình luận - giống chức năng reply của Facebook"""
    if 'user_name' not in session and 'oauth_token' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Không tìm thấy thông tin người dùng'}), 404
    
    id_binh_luan_goc = request.json.get('parent_id')  # ID của comment gốc
    id_trai_nghiem = request.json.get('experience_id')
    noi_dung_tra_loi = request.json.get('content', '').strip()
    
    if not noi_dung_tra_loi:
        return jsonify({'success': False, 'message': 'Nội dung trả lời không được để trống'}), 400
    
    # Kiểm tra comment gốc có tồn tại không
    binh_luan_goc = ExperienceComment.query.get_or_404(id_binh_luan_goc)
    if binh_luan_goc.parent_id is not None:
        return jsonify({'success': False, 'message': 'Chỉ có thể trả lời comment gốc, không thể trả lời reply'}), 400
    
    # Tạo reply mới
    tra_loi_moi = ExperienceComment(
        experience_id=id_trai_nghiem,
        user_id=user.id,
        parent_id=id_binh_luan_goc,
        content=noi_dung_tra_loi
    )
    
    db.session.add(tra_loi_moi)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'reply': tra_loi_moi.to_dict()
    })

@experience_blueprint.route('/delete-comment', methods=['POST'])
def xoa_binh_luan():
    """Xóa bình luận - chỉ người tạo mới được xóa"""
    if 'user_name' not in session and 'oauth_token' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    user_hien_tai = get_current_user()
    if not user_hien_tai:
        return jsonify({'success': False, 'message': 'Không tìm thấy thông tin người dùng'}), 404
    
    id_binh_luan = request.json.get('comment_id')
    if not id_binh_luan:
        return jsonify({'success': False, 'message': 'ID bình luận không hợp lệ'}), 400
    
    # Tìm bình luận cần xóa
    binh_luan_can_xoa = ExperienceComment.query.get_or_404(id_binh_luan)
    
    # Kiểm tra quyền sở hữu - chỉ người tạo mới được xóa
    if binh_luan_can_xoa.user_id != user_hien_tai.id:
        return jsonify({'success': False, 'message': 'Bạn chỉ có thể xóa bình luận của chính mình'}), 403
    
    try:
        # Nếu là comment gốc, xóa tất cả replies của nó
        if binh_luan_can_xoa.parent_id is None:
            # Đếm số replies trước khi xóa
            so_luong_replies = ExperienceComment.query.filter_by(parent_id=id_binh_luan).count()
            
            # Xóa tất cả replies
            ExperienceComment.query.filter_by(parent_id=id_binh_luan).delete()
            
            # Xóa comment gốc
            db.session.delete(binh_luan_can_xoa)
            
            # Tổng số bình luận bị xóa
            tong_so_xoa = so_luong_replies + 1
        else:
            # Nếu là reply, chỉ xóa reply đó
            db.session.delete(binh_luan_can_xoa)
            tong_so_xoa = 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Xóa bình luận thành công',
            'deleted_count': tong_so_xoa,
            'comment_id': id_binh_luan,
            'is_parent': binh_luan_can_xoa.parent_id is None
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'}), 500

@experience_blueprint.route('/get-experience-comments/<int:experience_id>')
def get_experience_comments(experience_id):
    """Lấy danh sách bình luận của trải nghiệm"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    comments = ExperienceComment.query.filter_by(experience_id=experience_id)\
        .order_by(ExperienceComment.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'success': True,
        'comments': [comment.to_dict() for comment in comments.items],
        'has_next': comments.has_next,
        'total': comments.total
    })

def get_current_user():
    """Helper function để lấy user hiện tại"""
    if 'oauth_token' in session:
        email = session.get('user_name')
        return Users.query.filter_by(email=email).first()
    else:
        uname = session.get('user_name')
        return Users.query.filter_by(uname=uname).first() 