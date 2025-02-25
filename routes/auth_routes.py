from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.users import UserModel
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    hashed_pw = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())

    # Mặc định tất cả user mới là "user", admin phải được tạo thủ công trong DB
    role = data.get("role", "user")  

    UserModel.create_user(data["username"], data["email"], hashed_pw.decode(), role)
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    user = UserModel.find_by_email(data["email"])

    if user and bcrypt.checkpw(data["password"].encode(), user["password_hash"].encode()):
        # CHỈ lưu email vào identity để tránh lỗi "Subject must be a string"
        token = create_access_token(identity=user["email"])  

        return jsonify({
            "token": token,
            "role": user["role"],  
             "username": user["username"],
             "password": data["password"]
        }), 200

    return jsonify({"message": "Invalid credentials"}), 401


@auth_bp.route("/auth/users", methods=["GET"])
def get_users():
    users = UserModel.get_all_users()
    user_list = [
        {"username": user["username"], "email": user["email"], "role": user["role"]}
        for user in users
    ]
    return jsonify(user_list), 200


@auth_bp.route("/auth/change-role", methods=["PUT"])
@jwt_required()
def change_role():
    current_user_email = get_jwt_identity()
    current_user = UserModel.find_by_email(current_user_email)

    if not current_user or current_user["role"] != "admin":
        return jsonify({"message": "Access denied. Only admin can change roles"}), 403

    data = request.json
    user_email = data.get("email")
    new_role = data.get("role")

    if not user_email or not new_role:
        return jsonify({"message": "Missing email or role"}), 400

    user = UserModel.find_by_email(user_email)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Cập nhật role người dùng
    UserModel.update_role(user_email, new_role)
    return jsonify({"message": f"User {user_email} role updated to {new_role}"}), 200
