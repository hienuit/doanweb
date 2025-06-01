# app/routes/media_routes.py
from flask import Blueprint,render_template,request,redirect,current_app,send_from_directory,flash,jsonify
from app.models.destinations import Destinations,DestinationImage
from app.extension import db
import os
from app.admin.routes import admin_required

media_blueprint = Blueprint('media', __name__)

@media_blueprint.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory("static/video", filename)

@media_blueprint.route('/images/<filename>')
def serve_images(filename):
    return send_from_directory("static/images", filename)

@media_blueprint.route("/choose-images")
@admin_required
def choose_images():
    image_folder = os.path.join(current_app.root_path, "static", "images", "anh")
    
    # prefix của ảnh trung với đường dẫn
    prefix = "images/anh/"

    all_files = [prefix + f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jfif','.webp'))]

    # tìm các file đã tồn tại trong db
    existing_files = {img.image_url for img in DestinationImage.query.all()}

    # Lọc ra các ảnh chưa có trong db
    image_files = [f[len("images/"):] for f in all_files if f not in existing_files]

    destinations = Destinations.query.all()
    return render_template("choose_images.html", image_files=image_files, destinations=destinations)

@media_blueprint.route("/add-images-from-static", methods=["POST"])
@admin_required
def add_images_from_static():
    destination_id = request.form["destination_id"]
    selected_images = request.form.getlist("selected_images")

    for filename in selected_images:
        image_url = "images/" + filename  # đường dẫn tương đối từ thư mục static
        img = DestinationImage(destination_id=destination_id, image_url=image_url)
        db.session.add(img)

    db.session.commit()
    flash('Đã thêm ảnh thành công!', 'success')
    return redirect("/choose-images")

@media_blueprint.route("/manage-images")
@admin_required
def manage_images():
    """Trang quản lý ảnh đã gán cho các tỉnh thành"""
    # Lấy tất cả ảnh đã gán kèm thông tin tỉnh thành
    images_with_destinations = db.session.query(DestinationImage, Destinations).join(
        Destinations, DestinationImage.destination_id == Destinations.id
    ).order_by(Destinations.name, DestinationImage.id).all()
    
    destinations = Destinations.query.all()
    return render_template("manage_images.html", 
                         images_with_destinations=images_with_destinations,
                         destinations=destinations)

@media_blueprint.route("/delete-image/<int:image_id>", methods=["POST"])
@admin_required
def delete_image(image_id):
    """Xóa ảnh khỏi database"""
    try:
        image = DestinationImage.query.get_or_404(image_id)
        destination_name = image.destination.name
        
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Đã xóa ảnh khỏi {destination_name} thành công!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False, 
            'message': f'Có lỗi xảy ra khi xóa ảnh: {str(e)}'
        }), 500

@media_blueprint.route("/filter-images-by-destination/<int:destination_id>")
@admin_required  
def filter_images_by_destination(destination_id):
    """Lọc ảnh theo tỉnh thành"""
    if destination_id == 0:  # Hiển thị tất cả
        images_with_destinations = db.session.query(DestinationImage, Destinations).join(
            Destinations, DestinationImage.destination_id == Destinations.id
        ).order_by(Destinations.name, DestinationImage.id).all()
    else:
        images_with_destinations = db.session.query(DestinationImage, Destinations).join(
            Destinations, DestinationImage.destination_id == Destinations.id
        ).filter(Destinations.id == destination_id).order_by(DestinationImage.id).all()
    
    return render_template("manage_images_list.html", 
                         images_with_destinations=images_with_destinations)



