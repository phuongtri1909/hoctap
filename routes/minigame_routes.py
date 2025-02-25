from flask import Blueprint, request, jsonify
from models.minigame import MinigameModel
from models.word import WordModel  # Import WordModel
from bson.objectid import ObjectId  # For MongoDB IDs

minigame_bp = Blueprint("minigame", __name__)

@minigame_bp.route("/minigame/config", methods=["GET"])
def get_minigame_config():
    config = MinigameModel.get_config()
    if config.get("_id"):
        config["_id"] = str(config["_id"])
    if config.get("created_at"):
        config["created_at"] = config["created_at"].isoformat()
    if config.get("updated_at"):
        config["updated_at"] = config["updated_at"].isoformat()
    return jsonify(config)

@minigame_bp.route("/minigame/config", methods=["POST"])
def update_minigame_config():
    data = request.get_json()
    if not data or "open_days" not in data:
        return jsonify({"message": "Thiếu dữ liệu 'open_days'"}), 400

    open_days = data["open_days"]
    if not isinstance(open_days, list):
        return jsonify({"message": "open_days phải là một danh sách"}), 400

    for day in open_days:
        if not isinstance(day, int) or day < 0 or day > 6:
            return jsonify({"message": "Giá trị của open_days không hợp lệ. Mỗi ngày phải là số nguyên từ 0 đến 6."}), 400

    modified_count = MinigameModel.update_config(open_days)
    return jsonify({"message": "Cập nhật cấu hình thành công", "modified_count": modified_count})

@minigame_bp.route("/minigame/add_word", methods=["POST"])
def add_word():
    data = request.get_json()
    
    if not data or "word" not in data:
        return jsonify({"message": "Thiếu dữ liệu 'word'"}), 400

    word = data["word"].strip()
    
    if not word:
        return jsonify({"message": "Từ không được để trống"}), 400

    word_id = WordModel.add_word(word)
    
    return jsonify({"message": "Thêm từ thành công", "word_id": str(word_id)}), 201
