# import motor.motor_asyncio
import pymongo
from decouple import config
# client = motor.motor_asyncio.AsyncIOMotorClient()
#
# db = client.reminders
client = pymongo.MongoClient(config("MONGO"))
db = client.reminders
