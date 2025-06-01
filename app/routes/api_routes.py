from flask import Blueprint, request, jsonify
from app.models.destinations import search_from_db, search_describe,extend_from_db, Destinations
import json, re
import google.generativeai as genai
import unicodedata

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
    # Tạo prompt chi tiết với thời gian, bữa ăn và nghỉ ngơi
    prompt = f"""
    Tạo lịch trình du lịch chi tiết cho {destination} trong {num_days} ngày, với ngân sách {budget} VND. 
    Mỗi ngày bao gồm 3 hoạt động chính (tham quan, trải nghiệm, v.v.), các bữa ăn (bữa sáng, bữa trưa, bữa tối) với gợi ý nhà hàng hoặc địa điểm ăn uống cụ thể, và thời gian nghỉ ngơi. 
    Định dạng trả về phải là JSON hợp lệ như sau:

    {{
        "days": [
            {{
                "day": 1,
                "schedule": [
                    {{
                        "time": "Giờ (HH:MM)",
                        "type": "meal/activity/rest",
                        "description": "Mô tả chi tiết (nếu là bữa ăn, gợi ý nhà hàng cụ thể; nếu là hoạt động, mô tả địa điểm và hoạt động; nếu là nghỉ ngơi, mô tả nơi nghỉ ngơi)",
                        "location": "Kinh độ,Vĩ độ (chỉ áp dụng cho hoạt động và bữa ăn)",
                        "cost": "Chi phí (VND, chỉ áp dụng cho hoạt động và bữa ăn)"
                    }}
                ],
                "estimated_cost": "Tổng chi phí ngày (VND)"
            }}
        ]
    }}

    Ví dụ:
    {{
        "days": [
            {{
                "day": 1,
                "schedule": [
                    {{
                        "time": "07:00",
                        "type": "meal",
                        "description": "Ăn sáng tại nhà hàng Phở Hùng, thưởng thức phở bò truyền thống",
                        "location": "106.123,10.456",
                        "cost": "50000"
                    }},
                    {{
                        "time": "08:30",
                        "type": "activity",
                        "description": "Tham quan Chùa Vĩnh Nghiêm, tìm hiểu kiến trúc độc đáo",
                        "location": "106.789,10.012",
                        "cost": "0"
                    }},
                    {{
                        "time": "12:00",
                        "type": "meal",
                        "description": "Ăn trưa tại quán Bún Bò Nam Bộ, món bún bò đặc trưng",
                        "location": "106.234,10.567",
                        "cost": "70000"
                    }},
                    {{
                        "time": "14:00",
                        "type": "rest",
                        "description": "Nghỉ ngơi tại khách sạn đã chọn hoặc công viên gần đó",
                        "location": "",
                        "cost": "0"
                    }},
                    {{
                        "time": "15:00",
                        "type": "activity",
                        "description": "Khám phá chợ Bến Thành, mua sắm đặc sản",
                        "location": "106.345,10.678",
                        "cost": "150000"
                    }},
                    {{
                        "time": "19:00",
                        "type": "meal",
                        "description": "Ăn tối tại nhà hàng Cục Gạch Quán, thưởng thức món Việt truyền thống",
                        "location": "106.456,10.789",
                        "cost": "200000"
                    }}
                ],
                "estimated_cost": "470000"
            }}
        ]
    }}

    Hãy đảm bảo lịch trình có thời gian hợp lý, các hoạt động, bữa ăn và nghỉ ngơi được phân bổ đều trong ngày từ khoảng 7:00 đến 21:00.
    """
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    clean_text = re.sub(r"```json|```", "", response.text).strip()

    try:
        itinerary_json = json.loads(clean_text)
        print("Lịch trình trả về:", itinerary_json)
        standard_info = search_describe(destination)
        standard_name = standard_info[0]["name"] if standard_info else destination
        itinerary_json["destination"] = standard_name 
        return itinerary_json
    except Exception as e:
        return f"Lỗi khi xử lý phản hồi lịch trình: {str(e)}"

@api_blueprint.route('/du-lich', methods=['POST'])
def du_lich():
    # Nhận câu hỏi từ client
    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({"success": False, "error": "Câu hỏi không được để trống"}), 400

    try:
        # Kiểm tra xem câu hỏi có phải là một yêu cầu về địa điểm đơn giản không
        location_pattern = r"(tôi muốn đi|muốn đi|gợi ý|đi du lịch|du lịch|đi|địa điểm ở|tham quan|hướng dẫn)?\s*(đến|tới|ở|về|tại|về)?\s*([a-zA-ZÀ-ỹ\s]+)(?:\s|$)"
        location_match = re.search(location_pattern, question.lower(), re.IGNORECASE)
        
        # Nếu đây là yêu cầu về địa điểm đơn giản
        if location_match:
            location = location_match.group(3).strip()
            if location:
                # Sử dụng make_command2 để lấy thông tin về địa điểm
                result = make_command2(f"Gợi ý địa điểm du lịch ở {location}")
                return jsonify({"success": True, "itinerary": result})
        
        # Nếu không phải yêu cầu đơn giản, kiểm tra mẫu lịch trình chi tiết
        pattern = r"Tạo lịch trình cho (.+) trong (\d+) ngày với ngân sách (\d+) VND"
        match = re.match(pattern, question)
        if not match:
            return jsonify({"success": False, "error": "Câu hỏi không đúng định dạng! Vui lòng nhập theo dạng: 'Tạo lịch trình cho [địa điểm] trong [số ngày] ngày với ngân sách [ngân sách] VND'"}), 400
        
        destination = match.group(1)
        days = int(match.group(2))
        budget = match.group(3)

        itinerary = make_command(destination, days, budget)
        
        # Trả về kết quả lịch trình
        return jsonify({"success": True, "itinerary": itinerary})
    
    except Exception as e:
        print(f"Lỗi xử lý câu hỏi: {str(e)}")
        return jsonify({"success": False, "error": f"Đã xảy ra lỗi: {str(e)}"}), 500

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


@api_blueprint.route('/create-personalized-history', methods=['POST'])
def create_personalized_history():
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({"success": False, "message": "Dữ liệu phải là một danh sách."}), 400

        extended_histories = []

        for item in data:
            if not item.get('destination'):
                continue  # Bỏ qua nếu thiếu điểm đến

            db_results = extend_from_db(item['destination'])
            db_data = db_results[0] if db_results else {"mood": "", "place": "", "location": ""}

            extended_item = {
                "id": item.get("id"),
                "days": item.get("days"),
                "total_cost": item.get("total_cost"),
                "mood": db_data.get("mood", ""),
                "place": db_data.get("place", ""),
                "location": db_data.get("location", "")
            }

            extended_histories.append(extended_item)

        print("✅ Extended histories:", extended_histories)

        return jsonify({
            "success": True,
            "message": "Lịch sử cá nhân hóa đã được tạo thành công!",
            "data": extended_histories
        }), 200

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"success": False, "message": "Đã xảy ra lỗi khi xử lý dữ liệu."}), 500



def fetch_from_external_apis():
    """Lấy dữ liệu từ các API bên ngoài"""
    # Đây là nơi bạn sẽ thêm mã để gọi các API từ các trang web du lịch
    # Ví dụ: gọi API của Booking.com, Traveloka, hoặc Klook
    
    # TODO: Implement actual API calls to external providers
    
    # Ví dụ về cấu trúc:
    # try:
    #     response = requests.get('https://api.example.com/promotions', 
    #                            headers={'Authorization': 'Bearer your_api_key'})
    #     if response.status_code == 200:
    #         data = response.json()
    #         # Xử lý dữ liệu...
    # except Exception as e:
    #     print(f"Error fetching from external API: {str(e)}")
    
    pass  # Placeholder để sau này thực hiện

@api_blueprint.route('/suggest-provinces', methods=['GET'])
def suggest_provinces():
    """
    API endpoint để gợi ý tỉnh thành dựa trên từ khóa tìm kiếm
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    # Normalize query to remove accents for better matching
    def remove_accents(text):
        return ''.join(c for c in unicodedata.normalize('NFD', text) 
                      if unicodedata.category(c) != 'Mn').lower()
    
    normalized_query = remove_accents(query)
    
    # Get all destinations
    all_destinations = Destinations.query.with_entities(Destinations.name).distinct().all()
    
    # Filter destinations that match the normalized query
    matching_provinces = []
    for dest in all_destinations:
        normalized_name = remove_accents(dest.name)
        if normalized_query in normalized_name:
            matching_provinces.append(dest.name)
    
    # Limit results to 10
    return jsonify(matching_provinces[:10])
