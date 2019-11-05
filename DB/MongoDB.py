
# using python3  
# pip install  pymongo
# pip install dnspython
# replace the password , include the <>
import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://rickyyhqi:<PASSWORD>@cluster0-m825i.mongodb.net/test?retryWrites=true&w=majority")
db = cluster["6733"]
collection = db["6733"]

post1 = {"_id": 5, "class": "ricky", "timestame": "2020"}

#collection.insert_many([post1, post2, post3])  # insert many data to MongoDB
results = collection.find({"_id": 5})       # find all the data which ID is 5
#print(results)
#results = collection.find_one({"_id": 5})   # only find the first match
#results = collection.delete_one({"_id":0})  # delete
#results = collection.update_one({"_id":5}, {"$set":{"name":"ti"}}) ## inside is a search query
# we can also  use  "$inc":{"hellp":5}
#  .count_documents({})









