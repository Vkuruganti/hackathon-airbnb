import flask
import pickle
app = flask.Flask(__name__)

with open("pickled_model.pkl", "r") as p:
    predictor = pickle.load(p)
    
@app.route("/page")
def page():
    with open("../airbnb-inputs.html") a f:
        return f.read()

@app.route("/result", methods=["POST", "GET"])
def result():
    """Gets prediction using the HTML form"""
    if flask.request.method == "POST":
        inputs = flask.request.form
        something = inputs["something"][0]

        results = {"result" : score}
        return flask.jsonify(results)
