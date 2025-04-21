from flask import Blueprint,render_template,request,redirect,current_app
from app.models.destinations import Destinations,DestinationImage
from app.extension import db
import os
from app.models.hotels import Hotel, HotelImage


images_blueprint = Blueprint('images', __name__)

@images_blueprint.route("/choose-images")
def choose_images():
    image_folder = os.path.join(current_app.root_path, "static", "images", "anh")
    
    # Đây là prefix đúng để trùng DB
    prefix = "images/anh/"

    all_files = [prefix + f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jfif'))]

    # Toàn bộ file đã tồn tại trong DB
    existing_files = {img.image_url for img in DestinationImage.query.all()}

    # Lọc ra các ảnh chưa có trong DB
    image_files = [f[len("images/"):] for f in all_files if f not in existing_files]

    destinations = Destinations.query.all()
    return render_template("choose_images.html", image_files=image_files, destinations=destinations)


@images_blueprint.route("/add-images-from-static", methods=["POST"])
def add_images_from_static():
    destination_id = request.form["destination_id"]
    selected_images = request.form.getlist("selected_images")

    for filename in selected_images:
        image_url = "images/" + filename  # đường dẫn tương đối từ static/
        img = DestinationImage(destination_id=destination_id, image_url=image_url)
        db.session.add(img)

    db.session.commit()
    return redirect("/choose-images")

@images_blueprint.route("/choose-hotel-images")
def choose_hotel_images():
    image_folder = os.path.join(current_app.root_path, "static", "images", "hotel_images")
    prefix = "images/hotel_images/"
    all_files = [prefix + f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jfif'))]
    existing_files = {img.image_url for img in HotelImage.query.all()}
    image_files = [f[len("images/"):] for f in all_files if f not in existing_files]
    hotels = Hotel.query.all()
    return render_template("choose_hotel_images.html", hotels=hotels, image_files=image_files)


@images_blueprint.route("/add-hotel-images", methods=["POST"])
def add_hotel_images():
    hotel_id = request.form.get("hotel_id")
    selected_images = request.form.getlist("selected_images")

    for filename in selected_images:
        image_url = "images/" + filename
        img = HotelImage(hotel_id=hotel_id, image_url=image_url)
        db.session.add(img)

    db.session.commit()
    return redirect("/choose-hotel-images")