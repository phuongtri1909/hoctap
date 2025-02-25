from database import db
from bson.objectid import ObjectId
from datetime import datetime

class WordModel:
    collection = db.words  # Make sure "words" collection exists in MongoDB

    @staticmethod
    def get_word_by_id(word_id):
        return WordModel.collection.find_one({"_id": ObjectId(word_id)})

    @staticmethod
    def add_word(word):
        """Add a word to the database"""
        word_data = {
            "word": word,
            "created_at": datetime.utcnow()
        }
        result = WordModel.collection.insert_one(word_data)
        return result.inserted_id  # Return the inserted ID
