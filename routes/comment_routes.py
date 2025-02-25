from bson import ObjectId
from flask import Blueprint, request, jsonify
from models.forum import ForumModel
from models.comment import CommentModel
from models.users import UserModel

comment_bp = Blueprint('comment', __name__)

@comment_bp.route("/forum/comments", methods=["POST"])
def create_comment():
    data = request.json

    post_id = data.get("post_id")
    content = data.get("content")
    author = data.get("author")

    # Kiểm tra nếu thiếu dữ liệu
    if not post_id or not content or not author:
        return jsonify({"message": "Missing required fields"}), 400

    # Kiểm tra nếu bài viết có tồn tại
    post = ForumModel.get_post_by_id(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    # Kiểm tra nếu người dùng có tồn tại
    user = UserModel.get_user_by_name(author)
    if not user:
        return jsonify({"message": "Author not found"}), 404

    # Debug thông tin bài viết và user
   

    # Tạo bình luận
    try:
        CommentModel.create_comment(post_id, content, user["_id"])
        return jsonify({"message": "Comment created successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500

@comment_bp.route("/forum/comments/<post_id>", methods=["GET"])
def get_comments(post_id):
    # Lấy danh sách bình luận của bài viết
    comments = CommentModel.get_comments_by_post(post_id)

    # Chuyển ObjectId thành chuỗi để có thể trả về JSON
    comments = [{key: str(value) if isinstance(value, ObjectId) else value for key, value in comment.items()} for comment in comments]
    
    return jsonify(comments), 200

@comment_bp.route("/forum/comments/<comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    # Xoá bình luận
    result = CommentModel.delete_comment(comment_id)

    if result.deleted_count == 0:
        return jsonify({"message": "Comment not found"}), 404

    return jsonify({"message": "Comment deleted successfully"}), 200
