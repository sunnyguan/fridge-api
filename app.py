from flask import Flask, request, jsonify, send_from_directory
import pymongo

from dotenv import load_dotenv
import os
load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGODB_URI"), connect=False)
db = client["fridge-list"]
users = db["users"]

# print(users.find_one())

app = Flask(__name__, static_url_path='')

def clean(obj):
    if obj:
        obj['_id'] = str(obj['_id'])

# get all user and their data
# no parameters required
@app.route('/users', methods=['GET'])
def getAll():
    res = users.find({})
    arr = []
    for doc in res:
        clean(doc)
        arr.append(doc)
    return jsonify(arr)


# route: /get?name=NAME
# example: /get?name=bob
@app.route('/get', methods=['GET'])
def respond():
    name = request.args.get('name')
    res = users.find_one({'name': name})
    if res:
        clean(res)
        return jsonify(res)
    else:
        return jsonify([])

# route: /add?name=NAME&item=ITEM
# example: /add?name=bob&item=watermelon
@app.route('/add', methods=['GET'])
def add():
    name = {'name': request.args.get('name')}
    item = request.args.get('item')
    col = users.find_one({'name': name['name']})
    print(col)
    if col:
        col = col['food']
        col.append(item)
        users.update_one(name, {'$set': {'food': col}})
    else:
        users.insert_one({
            'name': name['name'],
            'food': [item]
        })
    upd = users.find_one({'name': name['name']})
    clean(upd)
    return jsonify(upd)

# route: /remove?name=NAME&item=ITEM
# example: /remove?name=bob&item=watermelon
@app.route('/remove', methods=['GET'])
def remove():
    name = {'name': request.args.get('name')}
    item = request.args.get('item')
    col = users.find_one({'name': name['name']})
    if col:
        col = col['food']
        try:
            col.remove(item)
        except:
            pass
        users.update_one(name, {'$set': {'food': col}})
        upd = users.find_one({'name': name['name']})
        clean(upd)
        return jsonify(upd)
    else:
        return jsonify([])

@app.route('/')
def index():
    return send_from_directory('docs', 'index.html')

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
