from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
import pymongo
import json
import spoonacular as sp


from dotenv import load_dotenv
import os
load_dotenv()

MONGODB_URI="mongodb+srv://root:root@cluster0.ja1ul.mongodb.net/fridge-list?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
api = sp.API("9fd8eec03faa4b12a550cb6fc595d7da")

client = pymongo.MongoClient(MONGODB_URI, connect=False)
db = client["fridge-list"]
users = db["users"]

with open('sample.json', 'r') as f:
    sample_recipes = json.load(f)

with open('sample_recipe.json', 'r') as f:
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
            'food': {item: {'amount': amount, 'unit': unit}}
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

@app.route('/recipeDetails', methods=['GET'])
@cross_origin()
def details():
    recipe_id = request.args.get('id')
    return jsonify(detail_recipe)


@app.route('/')
def index():
    return send_from_directory('docs', 'index.html')

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
