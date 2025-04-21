# app/routes/main_routes.py
from flask import Blueprint, render_template,request
from app.models.destinations import search_describe

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
    province = request.args.get("province")
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
    return render_template("dashboard.html")
