import flask
import pickle
import pandas as pd
import numpy as np
app = flask.Flask(__name__)

with open("n_ranks.pkl", "r") as p:
    n_ranks = pickle.load(p)

with open("bn_list.pkl", "r") as p:
    bn_list = pickle.load(p)

with open("room.pkl", "r") as p:
    room_types = pickle.load(p)

def convert_nb(borough, nb):
    ref = n_ranks[borough]
    return ref[nb]

model_list = {}
boroughs = ['Manhattan', 'Brooklyn', 'Queens', 'Staten Island', 'Bronx']
model_files = [i.lower().replace(" ", "_")+".pkl" for i in boroughs]
for i, j in enumerate(boroughs):
    with open(model_files[i], "r") as p:
        model_list[j] = pickle.load(p)


def unconvert_nb(borough, num):
    ref = n_ranks[borough]
    ref = {ref[k]:k for k in ref}
    return ref[num]

def gen_output(borough, neighbourhood, accommodates, bedrooms, room_type):
    features = ["neighbourhood", "accommodates", "bedrooms","room_type"]
    X = [neighbourhood, accommodates, bedrooms, room_type]
    model = model_list[borough]

    old_input = pd.DataFrame(X).T
    old_input.columns = features
    original = round(model.predict(old_input)[0],2)


    out = {}
    out["original"] = original
    for i,a in enumerate(features):
        new_input = old_input.copy()
        if a != "accommodates":
            if new_input.loc[0, a]-1 >= 0:
                new_input.loc[0, a] = new_input.loc[0, a]-1
        else:
            if new_input.loc[0,a]-1 > 0:
                new_input.loc[0, a] = new_input.loc[0, a]-1
#         print new_input
        out[a] = [new_input.loc[0,a], round(model.predict(new_input)[0],2)]
    return out

def convert_out(borough, neighbourhood, accommodates, bedrooms, room_type):
    sample_out = gen_output(borough, neighbourhood, accommodates, bedrooms, room_type)
    final_out = {}
    features = ["borough", "neighbourhood", "accommodates", "bedrooms", "room_type"]
    sample_out_list = [i for i in sample_out.keys()]
    for i in sample_out_list:
        if i == "original":
            final_out["original"] = sample_out[i]
        elif i == "neighbourhood":
            n_name = unconvert_nb(borough, sample_out[i][0])
            key_name = i + "_" + n_name.replace(" ", "_")
            final_out[key_name] = sample_out[i][1]
        elif i == "accommodates" or i == "bedrooms":
            key_name = i + "_" + str(sample_out[i][0])
            final_out[key_name] = sample_out[i][1]
        else:
            ref = {room_types[k]:k for k in room_types}
            key_name = i + "_" + ref[sample_out[i][0]].replace(" ", "_")
            final_out[key_name] = sample_out[i][1]
    return final_out

@app.route("/boroughs_neighborhoods")
def boroughs():
    with open("boroughs_neighborhoods.pkl", "r") as p:
        out = pickle.load(p)
    return flask.jsonify(out)

@app.route("/room")
def room_():
    return flask.jsonify(room_types)

@app.route("/page")
def page():
    with open("../airbnb-inputs.html") as f:
        return f.read()

@app.route("/result", methods=["POST", "GET"])
def result():
    """Gets prediction using the HTML form"""

    if flask.request.method == "POST":
        inputs = flask.request.form
        borough = inputs["borough"]
        neighbourhood = inputs["neighbourhood"]
        room_type = inputs["room_type"]
        accommodates = inputs["accommodates"]
        bedrooms = inputs["bedrooms"]

        neighbourhood = convert_nb(borough, neighbourhood)
        room_type = room_types[room_type]
        accommodates = int(accommodates)
        bedrooms = int(bedrooms)



        results = convert_out(borough, neighbourhood, accommodates, bedrooms, room_type)
        out = {"Inputs": inputs, "Results": results}
        return flask.jsonify(out)

if __name__ == "__main__":
    '''Connects to the server'''

    # HOST = '127.0.0.1'
    # PORT = '4000'
    # app.run(HOST, PORT)
    app.run(debug=True)
