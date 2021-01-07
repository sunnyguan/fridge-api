from flask import Flask, request, jsonify
app = Flask(__name__)

sample_data = {
        "joe": ["apple", "orange"],
        "john": ["eggs", "milk"],
        "bob": ["rice", "pasta"]
}

@app.route('/users', methods=['GET'])
def respond():
    name = request.args.get('name')
    return jsonify(sample_data[name])


@app.route('/')
def index():
    return "<h1>Hello World!</h1>"

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
