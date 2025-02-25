from database import db
from datetime import datetime

class MinigameModel:
    collection = db.minigame  
    @staticmethod
    def get_config():
        config = MinigameModel.collection.find_one({"type": "config"})
        if config is None:
            config = {
                "type": "config",
                "open_days": [3, 4, 5, 6],  # Mặc định: mở game vào Thứ Tư, Thứ Năm, Thứ Sáu, Thứ Bảy
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            MinigameModel.collection.insert_one(config)
        return config

    @staticmethod
    def update_config(open_days):
        result = MinigameModel.collection.update_one(
            {"type": "config"},
            {"$set": {
                "open_days": open_days,
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )
        return result.modified_count


