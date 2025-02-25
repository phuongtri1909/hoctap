import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://admin:admin@cluster0.qmg6y.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

config = Config()
