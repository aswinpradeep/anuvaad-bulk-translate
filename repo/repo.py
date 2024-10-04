#!/bin/python
import os
import pymongo

from config.config import mongo_server_host
from config.config import mongo_wfm_db
from config.config import mongo_wfm_jobs_col

mongo_instance = None

class WFMRepository:

    def __init__(self):
        pass

    # Initialises and fetches mongo client
    def instantiate(self):
        client = pymongo.MongoClient(mongo_server_host)
        db = client[mongo_wfm_db]
        mongo_instance = db[mongo_wfm_jobs_col]
        return mongo_instance

    def get_mongo_instance(self):
        if not mongo_instance:
            return self.instantiate()
        else:
            return mongo_instance

    # Inserts the object into mongo collection
    def create_job(self, object_in):
        col = self.get_mongo_instance()
        col.insert_one(object_in)

    # Updates the object in the mongo collection
    def update_job(self, filename,object_in):
        col = self.get_mongo_instance()
        col.update_one(
            {"filename": filename},
            { "$set": object_in }
        )

    # Searches the object into mongo collection
    def search_job(self, query, exclude = None, offset = None, res_limit = None):
        col = self.get_mongo_instance()
        if offset is None and res_limit is None:
            res = col.find(query, exclude).sort([('_id', 1)])
        else:
            res = col.find(query, exclude).sort([('_id', -1)]).skip(offset).limit(res_limit)
        result = []
        for record in res:
            result.append(record)
        return result

    def delete_job(self, key_value_pair):
        col = self.get_mongo_instance()
        col.delete_one(key_value_pair)
