from .connection import client

def get_collection(collection_name, database_name="dafarmz"):
    db = client.get_database(database_name)
    
    return db.get_collection(collection_name)