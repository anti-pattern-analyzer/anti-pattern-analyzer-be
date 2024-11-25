import certifi
from pymongo import MongoClient

client = MongoClient("mongodb+srv://root:crEvLa1okbhyJ5fB@cluster0.u92fv.mongodb.net/traces_db?retryWrites=true&w=majority&appName=Cluster0", tlsCAFile=certifi.where())
db = client["traces_db"]
traces = db["traces"]

duplicates = traces.aggregate([
    {"$group": {"_id": "$traceID", "count": {"$sum": 1}}},
    {"$match": {"count": {"$gt": 1}}}
])

for doc in duplicates:
    print(f"Duplicate traceID: {doc['_id']}, Count: {doc['count']}")
