from flask import Flask, request, jsonify
import pymongo

from dotenv import load_dotenv
import os
load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGODB_URI"), connect=False)
db = client["fridge-list"]
users = db["users"]

# print(users.find_one())

app = Flask(__name__)

@app.route('/users', methods=['GET'])
def respond():
    name = request.args.get('name')
    res = users.find_one({'name': name})
    res['_id'] = str(res['_id'])
    return jsonify(res)


@app.route('/')
def index():
    return "<h1>Hello World!</h1>"

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
