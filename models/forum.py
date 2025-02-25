from database import db
from bson import ObjectId

class ForumModel:
    collection = db.forum

    @staticmethod
    def create_post(title, content, author, category):
        new_post = {
            "title": title,
            "content": content,
            "author": ObjectId(author),
            "category": category,
            "likes": 0,
            "comments": []
        }
        return ForumModel.collection.insert_one(new_post)

    @staticmethod
    def get_posts():
        return list(ForumModel.collection.find({}))

    @staticmethod
    def get_post_by_id(post_id):
        # Tìm bài viết theo ID
        post = ForumModel.collection.find_one({"_id": ObjectId(post_id)})
        if post:
            post = ForumModel.serialize_post(post)  # Chuyển đổi toàn bộ post
        return post

    @staticmethod
    def serialize_post(post):
        """
        Chuyển đổi mọi ObjectId trong bài viết thành chuỗi để có thể trả về dạng JSON.
        """
        if isinstance(post, dict):
            return {k: (str(v) if isinstance(v, ObjectId) else v) for k, v in post.items()}
        return post
