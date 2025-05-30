from flask import Blueprint, request, jsonify, session,json
from app.models.history import History
from app import db

histories_blueprint = Blueprint('history', __name__)

@histories_blueprint.route("/save-history", methods=["POST"])
def save_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Chưa đăng nhập"}), 401

    data = request.get_json()
    
    # Lấy dữ liệu cũ (để tương thích ngược)
    activity_names = json.dumps(data.get("activityNames", []))
    days = data.get("days", 0)
    budget = data.get("budget", 0)
    destination = data.get("destination", "Không rõ")
    
    # Lấy dữ liệu itinerary đầy đủ (mới)
    full_itinerary = data.get("fullItinerary", None)
    full_itinerary_json = None
    
    if full_itinerary:
        try:
            # Đảm bảo đây là JSON hợp lệ
            full_itinerary_json = json.dumps(full_itinerary)
            print("📝 Lưu itinerary đầy đủ:", len(full_itinerary_json), "ký tự")
        except (TypeError, ValueError) as e:
            print("❌ Lỗi khi serialize itinerary:", str(e))
            full_itinerary_json = None

    history = History(
        user_id=user_id,
        activity_names=activity_names,
        days=days,
        total_cost=budget,
        destination=destination,
        full_itinerary_data=full_itinerary_json
    )
    db.session.add(history)
    db.session.commit()

    return jsonify({"message": "Đã lưu lịch sử thành công!"}), 200

@histories_blueprint.route('/get-history', methods=['GET'])
def get_history():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"message": "Chưa đăng nhập"}), 401
    
    histories = History.query.filter_by(user_id=user_id).order_by(History.created_at.desc()).all()
    
    result = []
    for history in histories:
        try:
            activity_names = json.loads(history.activity_names)
        except (json.JSONDecodeError, TypeError):
            activity_names = []

        result.append({
            "id": history.id,
            "activity_names": activity_names,
            "days": history.days,
            "total_cost": history.total_cost,
            "destination": history.destination or "Không rõ",
            "created_at": history.created_at.strftime('%d-%m-%Y'),
        })

    # print("result", result)

    return jsonify({"histories": result}), 200


@histories_blueprint.route('/delete-history', methods=['DELETE'])
def delete_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Chưa đăng nhập"}), 401

    try:
        History.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({"message": "Đã xóa toàn bộ lịch sử!"}), 200
    except Exception as e:
        return jsonify({"message": "Lỗi khi xóa lịch sử!", "error": str(e)}), 500

@histories_blueprint.route("/schedule-from-history/<int:history_id>")
def schedule_from_history(history_id):
    """Route để hiển thị trang schedule từ lịch sử đã lưu"""
    from flask import render_template
    user_id = session.get("user_id")
    if not user_id:
        return "Chưa đăng nhập", 401
    
    # Kiểm tra xem lịch sử hiện tại có phải có user đó không
    history = History.query.filter_by(id=history_id, user_id=user_id).first()
    if not history:
        return "Không tìm thấy lịch sử", 404
    
    return render_template('schedule.html')

@histories_blueprint.route("/get-history-detail/<int:history_id>", methods=["GET"])
def get_history_detail(history_id):
    """API để lấy chi tiết lịch sử và chuyển đổi thành format itinerary"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"message": "Chưa đăng nhập"}), 401
    
    # Lấy lịch sử từ database
    history = History.query.filter_by(id=history_id, user_id=user_id).first()
    if not history:
        return jsonify({"message": "Không tìm thấy lịch sử"}), 404
    
    # Ưu tiên sử dụng full_itinerary_data nếu có
    if history.full_itinerary_data:
        try:
            # Parse dữ liệu itinerary đầy đủ
            full_itinerary = json.loads(history.full_itinerary_data)
            print("✅ Tìm thấy itinerary đầy đủ cho history ID:", history_id)
            
            # Thêm flag để biết đây là từ lịch sử
            full_itinerary["created_from_history"] = True
            full_itinerary["history_id"] = history.id
            
            return jsonify({
                "success": True,
                "itinerary": full_itinerary
            }), 200
            
        except (json.JSONDecodeError, TypeError) as e:
            print("❌ Lỗi parse full_itinerary_data:", str(e))
            # Fallback về cách cũ
    
    # Fallback: Sử dụng cách reconstruct cũ cho dữ liệu legacy
    print("⚠️ Không có full_itinerary_data, sử dụng cách reconstruct cũ")
    try:
        activity_names = json.loads(history.activity_names)
    except (json.JSONDecodeError, TypeError):
        activity_names = []
    
    # Tạo lại cấu trúc itinerary từ dữ liệu đã lưu (cách cũ)
    reconstructed_itinerary = re_constructure(history, activity_names)
    
    return jsonify({
        "success": True,
        "itinerary": reconstructed_itinerary
    }), 200


def re_constructure(history, activity_names):
    """Hàm tái tạo lịch trình từ dữ liệu lịch sử đã lưu"""
    days = []
    total_cost = 0
    
    try:
        total_budget = float(str(history.total_cost).replace(',', ''))
    except (ValueError, TypeError):
        total_budget = 0
    
    # Chia hoạt động và ngân sách cho từng ngày
    activities_per_day = len(activity_names) // history.days if history.days > 0 else 1
    budget_per_day = total_budget // history.days if history.days > 0 else total_budget
    
    for day_num in range(1, history.days + 1):
        # Lấy hoạt động cho ngày hiện tại
        start_idx = (day_num - 1) * activities_per_day
        end_idx = start_idx + activities_per_day
        
        # Đối với ngày cuối, lấy tất cả hoạt động còn lại
        if day_num == history.days:
            day_activities = activity_names[start_idx:]
        else:
            day_activities = activity_names[start_idx:end_idx]
        
        # Tạo schedule cho ngày
        schedule = []
        base_times = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00"]
        
        for i, activity in enumerate(day_activities):
            time_idx = i % len(base_times)
            activity_cost = budget_per_day / len(day_activities) if day_activities else 0
            
            schedule.append({
                "time": base_times[time_idx],
                "description": activity,
                "name": activity,
                "type": "activity",
                "cost": int(activity_cost),
                "location": history.destination or "Việt Nam"
            })
        
        # Thêm bữa ăn nếu cần
        if len(schedule) > 0:
            schedule.insert(2, {
                "time": "12:00",
                "description": f"Bữa trưa tại {history.destination}",
                "name": "Bữa trưa",
                "type": "meal",
                "cost": int(budget_per_day * 0.2),  # 20% ngân sách cho ăn uống
                "location": history.destination or "Việt Nam"
            })
        
        day_data = {
            "day": day_num,
            "schedule": schedule,
            "estimated_cost": int(budget_per_day),
            "activities": schedule  # Compatibility
        }
        
        days.append(day_data)
        total_cost += budget_per_day
    
    return {
        "destination": history.destination or "Việt Nam",
        "days": days,
        "total_cost": int(total_cost),
        "trip_duration": history.days,
        "created_from_history": True,  # đánh dấu được tạo từ lịch sử
        "history_id": history.id
    }
