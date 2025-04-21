# app/routes/api_routes.py
from flask import Blueprint, request, jsonify
from app.models.destinations import search_from_db, search_describe
from app.models.hotels import Hotel
import json, re
import google.generativeai as genai

genai.configure(api_key="AIzaSyAM-euCjLTAPiFQvXnI4X-5EeNGX2G-k0Q")

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/search', methods=['GET'])
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

@api_blueprint.route('/describe', methods=['GET'])
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

@api_blueprint.route('/describe_hotel', methods=['GET'])
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

@api_blueprint.route('/create-itinerary', methods=['POST'])
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

@api_blueprint.route('/du-lich', methods=['POST'])
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
