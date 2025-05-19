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
    activity_names = json.dumps(data.get("activityNames", []))
    days = data.get("days", 0)
    budget = data.get("budget", 0)
    destination = data.get("destination", "Không rõ")

    history = History(
        user_id=user_id,
        activity_names=activity_names,
        days=days,
        total_cost=budget,
        destination=destination  # nhớ thêm nếu chưa có trong model
    )
    db.session.add(history)
    db.session.commit()

    # ✅ Trả JSON để frontend parse được
    return jsonify({"message": "Đã lưu lịch sử thành công!"}), 200



@histories_blueprint.route('/get-history', methods=['GET'])
def get_history():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"message": "Chưa đăng nhập"}), 401
    print("hello")
    histories = History.query.filter_by(user_id=user_id).order_by(History.created_at.desc()).all()
    print("hello")
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

    print("hello")

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
