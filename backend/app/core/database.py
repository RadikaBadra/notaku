from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = None

async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    try:
        # Ping the database to ensure connection
        await client.admin.command('ping')
        print("MongoDB connected successfully!")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")

def get_database():
    return client[settings.MONGODB_DB]
