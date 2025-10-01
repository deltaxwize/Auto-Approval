# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01


from os import path, getenv

class Config:
    API_ID = int(getenv("API_ID", "25489830"))
    API_HASH = getenv("API_HASH", "b3df97daea65252260b2c2513a94ee5a")
    BOT_TOKEN = getenv("BOT_TOKEN", "8207506694:AAGLUiu9UUZcbvjnlfqBkfFOv4T7S8HdAes")
    # Your Force Subscribe Channel Id Below 
    CHID = int(getenv("CHID", "-1002706901945")) # Make Bot Admin In This Channel
    # Admin Or Owner Id Below
    SUDO = list(map(int, getenv("SUDO", "8132657352 7668133494 8076259467").split()))
    MONGO_URI = getenv("MONGO_URI", "mongodb+srv://approvex:approvex@cluster0.1nqvats.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    
cfg = Config()

# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01
