import json
with open('sample.json', 'r') as f:
    sample_recipes = json.load(f)

del sample_recipes[0]["id"]
print (sample_recipes)