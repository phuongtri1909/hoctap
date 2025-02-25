from flask import Blueprint, request, jsonify, current_app
from models.message import MessageModel
mess_bp = Blueprint("message", __name__)

# API lấy danh sách tin nhắn
@mess_bp.route("/messages", methods=["GET"])
def get_messages():
    room = request.args.get("room", "general")
    messages = MessageModel.get_messages(room)
    return jsonify(messages), 200

# API xóa tin nhắn theo ID
@mess_bp.route("/messages/<message_id>", methods=["DELETE"])
def delete_message(message_id):
    success = MessageModel.delete_message(message_id)
    if not success:
        return jsonify({"message": "Message not found"}), 404

    return jsonify({"message": "Message deleted successfully"}), 200
