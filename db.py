
import os
import pymongo
# for secure passwords
import bcrypt
from datetime import datetime
from bson.objectid import ObjectId

### Database setup ###
mongo_pass = os.getenv('mongoaccess')
mongo_uri = "mongodb+srv://admin:kdrC8y6Dtx8ThP1J@harvard.mrpdl.mongodb.net/t4sg?retryWrites=true&w=majority"
client = pymongo.MongoClient(mongo_uri)
db = client.main
users = db.users
threads = db.threads

def get_comments():
	return threads.find_one({})

def create_comment(thread_id, comment):
	comment["timestamp"] = datetime.now()
	comment["subthreads"] = []
	new = threads.insert_one(comment)
	threads.update_one({"_id": ObjectId(thread_id)}, {"$push":{"subthreads":new.inserted_id}})
	return new

### Utility functions ###
# Basic db structure of a user
def user_template():
	return {
		"name": "",
		"pwrd": "",
	}

def get_user_by(field, value):
	# Get user by field (username, password, id, etc)
	return users.find_one({field: value}, {"_id":0})

def create_user(name, pwrd):
	# Prevent creating a user if name already exists
	if not get_user_by("name", name):
		# Create user and password
		base = user_template()
		base["name"] = name
		base["pwrd"] = bcrypt.hashpw(pwrd.encode("UTF-8"), bcrypt.gensalt())
		users.insert_one(base)
		return base

def verify_user(name, pwrd):
	user = get_user_by("name", name)
	if user:
		# Make sure the user exists.
		return bcrypt.checkpw(pwrd.encode("UTF-8"), get_user_by("name", name)["pwrd"])
	return False

def delete_user(name):
	return users.delete_one({"name": name})

### DANGER ###
def delete_all_users():
	return users.delete_many({})
