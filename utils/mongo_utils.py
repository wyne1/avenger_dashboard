from pymongo import DESCENDING

def get_doc_count(db_collection):
    return db_collection.find({}).sort("timestamp",DESCENDING).skip(1).limit(10).count()
