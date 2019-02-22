from pymongo import MongoClient
import config


client = MongoClient(config.BOT_CONFIG['DB'])
db = client['shdk_database']


