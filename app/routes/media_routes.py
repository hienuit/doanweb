# app/routes/media_routes.py
from flask import Blueprint,render_template,request,redirect,current_app,send_from_directory
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

    all_files = [prefix + f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jfif'))]

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
    return redirect("/choose-images")



