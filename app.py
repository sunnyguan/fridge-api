from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import pymongo
import json
import spoonacular as sp


from dotenv import load_dotenv
import os
load_dotenv()

MONGODB_URI=os.getenv("MONGODB_URI")
api = sp.API(os.getenv("SP_KEY"))

client = pymongo.MongoClient(MONGODB_URI, connect=False)
db = client["fridge-list"]
users = db["users"]

with open('sample.json', 'r') as f:
    sample_recipes = json.load(f)

with open('sample2.json', 'r') as f:
    detail_recipe = json.load(f)

app = Flask(__name__, static_url_path='')
cor = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def clean(obj):
    if obj:
        obj['_id'] = str(obj['_id'])

# get all user and their data
# no parameters required
@app.route('/users', methods=['GET'])
@cross_origin()
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
@cross_origin()
def respond():
    name = request.args.get('name')
    res = users.find_one({'name': name})
    if res:
        clean(res)
        return jsonify(res)
    else:
        return jsonify([])

# route: /add?name=NAME&item=ITEM&amount=AMOUNT&unit=UNIT
# example: /add?name=bob&item=watermelon&amount=1&unit
@app.route('/add', methods=['GET'])
@cross_origin()
def add():
    name = {'name': request.args.get('name')}
    item = request.args.get('item')
    amount = request.args.get('amount')
    unit = request.args.get('unit')
    col = users.find_one(name)
    print(col)
    if col:
        col = col['food']
        col[item] = {'amount': amount, 'unit': unit}
        users.update_one(name, {'$set': {'food': col}})
    else:
        users.insert_one({
            'name': name['name'],
            'food': {item: {'amount': amount, 'unit': unit}},
            'spending': []
        })
    upd = users.find_one(name)
    clean(upd)
    return jsonify(upd)

# route: /remove?name=NAME&item=ITEM
# example: /remove?name=bob&item=watermelon
@app.route('/remove', methods=['GET'])
@cross_origin()
def remove():
    name = {'name': request.args.get('name')}
    item = request.args.get('item')
    col = users.find_one(name)
    if col:
        col = col['food']
        try:
            del col[item]
        except:
            pass
        users.update_one(name, {'$set': {'food': col}})
        upd = users.find_one(name)
        clean(upd)
        return jsonify(upd)
    else:
        return jsonify([])

# route: /recipe?name=NAME
@app.route('/recipe', methods=['GET'])
@cross_origin()
def get_recipes():
    name = request.args.get('name')
    info = users.find_one({'name': name})
    ingredients = ', '.join(info['food'].keys())
    recipes = api.search_recipes_by_ingredients(ingredients, number=2, ranking=2).json()

    ids = ""
    for recipe in recipes:
        ids = ids + str(recipe['id']) + ','
    ids = ids[:len(ids)-1]
    recipeInfo = api.get_recipe_information_bulk(ids).json()

    for i in range(len(recipes)):
        recipes[i]["readyInMinutes"] = recipeInfo[i]["readyInMinutes"]
        recipes[i]["pricePerServing"] = recipeInfo[i]["pricePerServing"]
        del recipes[i]["id"]
        del recipes[i]["imageType"]
        del recipes[i]["likes"]

    return jsonify(recipes)

@app.route('/recipeFake', methods=['GET'])
@cross_origin()
def details():
    return jsonify(detail_recipe)
"""
This section is for weekly spending CRUD
"""
# route: /add?name=NAME&item=ITEM
# example: /add?name=bob&item=watermelon
@app.route('/spending/add', methods=['GET'])
@cross_origin()
def spending_add():
    name = {'name': request.args.get('name')}
    item = request.args.get('item')
    col = users.find_one({'name': name['name']})
    print(col)
    if col:
        col = col['spending']
        col.append(item)
        users.update_one(name, {'$set': {'spending': col}})
    else:
        users.insert_one({
            'name': name['name'],
            'food': [],
            'spending': [item]
        })
    upd = users.find_one({'name': name['name']})
    clean(upd)
    return jsonify(upd)

# route: /remove?name=NAME&item=ITEM
# example: /remove?name=bob&item=watermelon
@app.route('/spending/remove', methods=['GET'])
@cross_origin()
def spending_remove():
    name = {'name': request.args.get('name')}
    item = request.args.get('item')
    col = users.find_one({'name': name['name']})
    if col:
        col = col['spending']
        try:
            col.remove(item)
        except:
            pass
        users.update_one(name, {'$set': {'spending': col}})
        upd = users.find_one({'name': name['name']})
        clean(upd)
        return jsonify(upd)
    else:
        return jsonify([])

@app.route("/receipt", methods=['POST'])
def detect_face():
    try:
        req = request.json
        print(req["image"])

        # decode base64 string into np array
        # nparr = np.frombuffer(base64.b64decode(req['image'].encode('utf-8')), np.uint8)

        # decoded image
        # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        resp = jsonify(["apple", "oranges"])
        resp.status_code = 200
        return resp

    except Exception as e:
        response = {
            'success': False,
            'status code': 500,
            'message': str(e),
            }
        resp = jsonify(response)
        resp.status_code = 500
        return resp

@app.route('/')
def index():
    return send_from_directory('docs', 'index.html')

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
