from pymongo import DESCENDING

def get_doc_count(db_collection):
    return db_collection.find({}).sort("timestamp", DESCENDING).skip(1).limit(10).count()

def get_alert_doc(db_collection, num_new_samples):
    cursor = db_collection.find().sort([('_id', -1)]).limit(num_new_samples)
    return [doc for doc in cursor]
