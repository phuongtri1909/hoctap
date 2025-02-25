from flask import Blueprint, request, jsonify
from models.forum import ForumModel
from bson import ObjectId
from models.users import UserModel

forum_bp = Blueprint('forum', __name__)

def serialize_objectid(obj):
    """Helper function to convert ObjectId to string"""
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj

@forum_bp.route("/forum/posts", methods=["POST"])
def create_post():
    data = request.json
    title = data.get("title")
    content = data.get("content")
    author = data.get("author")
    category = data.get("category")

    if ObjectId.is_valid(author):
        author_id = author
    else:
        user = UserModel.get_user_by_name(author)
        if not user:
            return jsonify({"message": "Author not found"}), 404
        author_id = str(user["_id"])

    ForumModel.create_post(title, content, author_id, category)
    return jsonify({"message": "Post created successfully"}), 201

@forum_bp.route("/forum/posts", methods=["GET"])
def get_posts():
    posts = ForumModel.get_posts()
    posts = [{key: serialize_objectid(value) for key, value in post.items()} for post in posts]
    return jsonify(posts), 200

@forum_bp.route("/forum/posts/<post_id>", methods=["GET"])
def get_post(post_id):
    post = ForumModel.get_post_by_id(post_id)
    if post:
        return jsonify(post), 200
    return jsonify({"message": "Post not found"}), 404

@forum_bp.route("/forum/posts/<post_id>/like", methods=["POST"])
def like_post(post_id):
    """API để thêm lượt thích vào bài viết"""
    post = ForumModel.get_post_by_id(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    new_likes = post.get("likes", 0) + 1
    ForumModel.collection.update_one({"_id": ObjectId(post_id)}, {"$set": {"likes": new_likes}})
    
    return jsonify({"message": "Post liked", "likes": new_likes}), 200

@forum_bp.route("/forum/posts/<post_id>/comments", methods=["POST"])
def add_comment(post_id):
    """API để thêm bình luận vào bài viết"""
    data = request.json
    comment_content = data.get("content")
    commenter = data.get("author")

    if not ObjectId.is_valid(post_id):
        return jsonify({"message": "Invalid post ID"}), 400

    if not comment_content or not commenter:
        return jsonify({"message": "Content and author are required"}), 400

    post = ForumModel.get_post_by_id(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    # Kiểm tra nếu commenter là ObjectId hợp lệ, nếu không tìm theo tên
    if ObjectId.is_valid(commenter):
        commenter_id = commenter
    else:
        user = UserModel.get_user_by_name(commenter)
        if not user:
            return jsonify({"message": "Author not found"}), 404
        commenter_id = str(user["_id"])

    comment = {
        "author": commenter_id,
        "content": comment_content
    }

    ForumModel.collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment}}
    )

    # Chuyển đổi ObjectId của author thành chuỗi nếu cần
    comment["author"] = serialize_objectid(comment["author"])

    return jsonify({"message": "Comment added", "comment": comment}), 201
