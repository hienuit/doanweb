from flask import render_template, Blueprint
from flask import current_app, Flask,  redirect, render_template, request, jsonify, flash, url_for, send_from_directory, session
from app.models.destinations import search_from_db, search_describe
from app.models.hotels import get_hotels_by_province
from app.models.users import Users
from app.models.hotels import Hotel
import json
import google.generativeai as genai
import re
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail, oauth

from flask_mail import Mail, Message
import random
import string
genai.configure(api_key="AIzaSyAM-euCjLTAPiFQvXnI4X-5EeNGX2G-k0Q")
# Create a blueprint for your routes
routes_blueprint = Blueprint('routes', __name__)


@routes_blueprint.route('/')
def index():
    return render_template('index.html')


@routes_blueprint.route("/page2")
def page2():
    return render_template("page2.html")  # Trang thứ hai

@routes_blueprint.route("/page3")
def page3():
    return render_template("page3.html")  # Trang thứ hai

@routes_blueprint.route("/page4")
def page4():
    return render_template("page4.html")  # Trang thứ hai

@routes_blueprint.route("/schedule")
def schedule():
    return render_template("schedule.html")  # Trang thứ hai

@routes_blueprint.route("/map")
def map():
    return render_template("map.html")

@routes_blueprint.route("/login")
def login_page():
    return render_template("login.html")

@routes_blueprint.route("/register")
def register_page():
    
    return render_template("register.html")

@routes_blueprint.route('/search', methods=['GET'])
def search():
    # Lấy các tham số từ request
    mood = request.args.get('mood')  # Tham số 'mood' từ query string
    place = request.args.get('place')  # Tham số 'place' từ query string
    location = request.args.get('location')  # Tham số 'location' từ query string

    # Kiểm tra nếu thiếu bất kỳ tham số nào
    if not mood or not place or not location:
        return jsonify({"error": "Thiếu thông tin tìm kiếm!"}), 400

    # Gọi hàm tìm kiếm từ service (business logic)
    results = search_from_db(mood, place, location)
    
    # Trả kết quả dưới dạng JSON
    return jsonify(results)

@routes_blueprint.route('/navbar', methods=['GET'])
def navbar():
    return render_template('navbar.html')


@routes_blueprint.route('/describe', methods=['GET'])
def describe():
    # Lấy tên tỉnh từ query string
    province = request.args.get('province')
    
    if not province:
        return jsonify({"error": "Thiếu thông tin tìm kiếm!"}), 400

    # Gọi hàm search_describe để lấy mô tả tỉnh
    results = search_describe(province)
    
    if not results:
        return jsonify({"error": "Không tìm thấy thông tin về tỉnh này!"}), 404
    
    # Trả về mô tả tỉnh (chỉ trả về mô tả)
    return jsonify(results[0])  # Trả về phần tử đầu tiên, chỉ chứa mô tả



@routes_blueprint.route('/describe_hotel', methods=['GET'])
def describe_hotel():
    province_name = request.args.get('province')  # Get the province name from the query parameter
    
    # Debugging: Check if the 'province_name' is being passed correctly
    print(f"Received province_name: {province_name}")
    
    # Ensure you have data for the given province
    hotels = Hotel.query.filter_by(province_name=province_name).all()
    if not hotels:
        return jsonify({"message": f"No hotels found for province {province_name}"}), 404
    
    # Convert the hotels to dictionaries and return the data
    hotel_list = [hotel.to_dict() for hotel in hotels]
    print(f"Hotels found: {hotel_list}")  # Debugging: Check the hotels found
    return jsonify(hotel_list)





@routes_blueprint.route('/hotel', methods=['GET'])
def hotel():
    return render_template('hotel.html')




@routes_blueprint.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory("static/video", filename)

@routes_blueprint.route('/images/<filename>')
def serve_iamges(filename):
    return send_from_directory("static/images", filename)



@routes_blueprint.route('/create-itinerary', methods=['POST'])
def create_itinerary():
    # Đảm bảo yêu cầu là JSON
    if request.is_json:
        # Lấy dữ liệu JSON từ yêu cầu
        data = request.get_json()
        destination = data.get('destination')
        days = data.get('days')
        budget = data.get('budget')
        # Kiểm tra các tham số cần thiết
        if not destination or not days or not budget:
            return jsonify({"success": False, "error": "Missing required parameters"}), 400
        # Tạo lịch trình
        itinerary = make_command(destination, days, budget)
        # Trả về kết quả lịch trình
        return jsonify({"success": True, "itinerary": itinerary})
    else:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400


def make_command(destination, num_days, budget):
    # Tạo prompt sử dụng thông tin từ yêu cầu
    prompt = f"Tạo lịch trình du lịch cho {destination} trong {num_days} ngày, với ngân sách {budget}. Hãy đề xuất địa điểm du lịch phổ biến nhất mỗi ngày đi ba địa điểm không chú thích thêm. Định dạng trả về như sau:\n" \
             "{\n" \
             "  \"days\": [\n" \
             "    {\n" \
             "      \"day\": 1,\n" \
             "      \"activities\": [\n" \
             "        {\"name1\": \"Activity 1\", \"description\": \"Description\",\"location\": \"Longitude,Latitude\", \"cost\": \"Amount\"},\n" \
             "        {\"name2\": \"Activity 2\", \"description\": \"Description\",\"location\": \"Longitude,Latitude\" , \"cost\": \"Amount\"}\n" \
             "      ],\n" \
             "      \"estimated_cost\": \"Amount\"\n" \
             "    },\n" \
             "    ...\n" \
             "  ]\n" \
             "}\n" \
             "Đây là ví dụ về cấu trúc, hãy trả lời đúng theo cấu trúc JSON này." 
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    clean_text = re.sub(r"```json|```", "", response.text).strip()

    try:
        itinerary_json = json.loads(clean_text)
        return itinerary_json
    except Exception as e:
        return f"Error processing itinerary response: {str(e)}"





@routes_blueprint.route('/du-lich', methods=['POST'])
def du_lich():
    # Nhận câu hỏi từ client
    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({"success": False, "error": "Câu hỏi không được để trống"}), 400

    try:
        # Tạo lịch trình du lịch
        itinerary = make_command2(question)
        
        # Trả về kết quả lịch trình
        return jsonify({"success": True, "itinerary": itinerary})
    
    except Exception as e:
        return jsonify({"success": False, "error": f"Đã xảy ra lỗi khi kết nối với Gemini Flash 2000: {str(e)}"}), 500


def make_command2(question):
    # Tạo prompt sử dụng thông tin từ câu hỏi
    prompt = f"""
    Hãy đưa ra 3 tỉnh thành du lịch và 2 địa điểm nổi bật ở mỗi tỉnh đó dựa theo câu hỏi: {question}. 
    Định dạng trả về phải là JSON hợp lệ như sau:

    {{
        "provinces": [
            {{
                "province": "Tỉnh 1",
                "places": [
                    {{
                        "name": "Địa điểm 1",
                        "location": "kinh độ, vĩ độ",
                        "description": "Mô tả hoạt động tại địa điểm 1 tỉnh 1",
                    }},
                    {{
                        "name": "Địa điểm 2",
                        "location": "kinh độ, vĩ độ",
                        "description": "Mô tả hoạt động tại địa điểm 2 tỉnh 1",
                    }}
                ]
            }},
            {{
                "province": "Tỉnh 2",
                "places": [
                    {{
                        "name": "Địa điểm 1",
                        "location": "kinh độ, vĩ độ",
                        "description": "Mô tả hoạt động tại địa điểm 1 tỉnh 2",
                    }},
                    {{
                        "name": "Địa điểm 2",
                        "location": "kinh độ, vĩ độ",
                        "description": "Mô tả hoạt động tại địa điểm 2 tỉnh 2",
                    }}
                ]
            }},
            {{
                "province": "Tỉnh 3",
                "places": [
                    {{
                        "name": "Địa điểm 1",
                        "location": "kinh độ, vĩ độ",
                        "description": "Mô tả hoạt động tại địa điểm 1 tỉnh 3",
                    }},
                    {{
                        "name": "Địa điểm 2",
                        "location": "kinh độ, vĩ độ",
                        "description": "Mô tả hoạt động tại địa điểm 2 tỉnh 3",
                    }}
                ]
            }}
        ]
    }}
    """

    # Sử dụng generative.ai để gọi API và nhận phản hồi
    model = genai.GenerativeModel("gemini-2.0-flash")  # Sử dụng mô hình Gemini Flash 2000
    response = model.generate_content(prompt)

    # Làm sạch và phân tích kết quả thành JSON
    clean_text = re.sub(r"```json|```", "", response.text).strip()

    try:
        result_json = json.loads(clean_text)
        return result_json
    except json.JSONDecodeError:
        raise Exception("Kết quả trả về không phải định dạng JSON hợp lệ.")
    


@routes_blueprint.route('/verify_otp', methods=['GET', 'POST'])
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
                return redirect(url_for('routes.index'))
        else:
            flash("Mã OTP không đúng!", "error")
            return redirect(url_for('routes.verify_otp'))

    return render_template('verify_otp.html')

@routes_blueprint.route('/verify_otp_ajax', methods=['POST'])
def verify_otp_ajax():
    otp = request.form.get('otp')
    if otp == session.get('otp'):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Mã OTP không đúng!'})


@routes_blueprint.route('/loginfunction', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = Users.query.filter_by(email=email).first()
    if user:
        uname = user.uname
    if user and check_password_hash(user.password, password):
        session['user_id'] = uname
        return redirect(url_for('routes.index'))
    else:
        return jsonify({"error": "Invalid credentials"}), 401
    

@routes_blueprint.route('/registerfunction', methods=['GET','POST'])
def register():
    
    if request.method == 'POST':
        
        fname = request.form.get("fname")
        uname = request.form.get("uname")
        sdt = request.form.get("sdt")
        email = request.form.get("email")
        password = request.form.get("pass")
        confirm_pass = request.form.get("confirm_pass")

        # Kiểm tra xem email đã tồn tại trong cơ sở dữ liệu chưa
        # if Users.query.filter_by(email=email).first():
        #     flash("Email đã tồn tại!", "error")
        #     return redirect(url_for("routes.register"))
        user = Users.query.filter_by(email=email).first()
        if user:
            uname=user.uname
            flash("Tài khoản đã tồn tại!","error")
            session['user_id'] = uname
            return redirect(url_for("routes.index"))
        # if Users.query.filter_by(mail=mail).first():
        #     flash("Tài khoản đã tồn tại!", "error")
        #     return redirect(url_for("routes.register"))

        # Kiểm tra các trường bắt buộc
        if not fname or not email or not password:
            return jsonify({"error": "Missing required parameters"}), 400
        if password != confirm_pass:
            return jsonify({"error": "Passwords do not match"}), 400
        # Mã hóa mật khẩu
        hashed_password = generate_password_hash(password)
        # Tạo OTP và gửi email
        otp = generate_otp()
        print(send_otp_email(email, otp))
        if send_otp_email(email, otp):
            print(email, otp)
            # Lưu mã OTP vào session để xác thực sau
            session['otp'] = otp
            session['temp_user'] = {
                'fname': fname,
                'uname': uname,
                'sdt': sdt,
                'email': email,
                'password': hashed_password
            }
            flash("Đăng ký thành công! Vui lòng kiểm tra email và nhập mã OTP để xác thực.", "success")
            return redirect(url_for('routes.verify_otp'))
        else:
            flash("Lỗi khi gửi email OTP", "error")
            return redirect(url_for('routes.register'))

    return render_template('index.html')



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



@routes_blueprint.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)  
    flash("Bạn đã đăng xuất!", "success")
    return redirect(url_for("routes.index"))




# @routes_blueprint.route('/verify_email')
# def verify_email():
#     return "An email has been sent to your address. Please verify your email."


# client_id = current_app.config['CLIENT_ID']
# client_secret = current_app.config['CLIENT_SECRET']
# google = oauth.register(
#     name = 'google',
#     client_id = client_id,
#     client_secret = client_secret,
#     server_metadata_url = 'https://accounts.google.com/.well-known/openid-configuration', 
#     client_kwargs = {'scope': 'openid email profile'}

# )