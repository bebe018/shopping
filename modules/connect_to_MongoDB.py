#!usr/bin/env python3
import json
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['db']
collection = db['products']

with open('product.json') as f:
    data = json.load(f)

try:
    collection.insert_many(data)
except Exception as e:
    pass

client.close()

# connect to mongodb
def get_connection(col):
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['db']
    collection = db[col]
    return collection
