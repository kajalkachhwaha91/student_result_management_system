from bson import ObjectId

def serialize_mongo(doc: dict):
    """
    Converts ALL ObjectId fields to string
    """
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
    return doc
