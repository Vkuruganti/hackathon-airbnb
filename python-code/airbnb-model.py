
# coding: utf-8

# # Set up notebook

# In[250]:

import numpy as np
import pandas as pd
from collections import Counter
import flask
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing, decomposition, pipeline
from sklearn import metrics, model_selection, linear_model
import xgboost
import pickle
import json


# In[2]:

plt.style.use("fivethirtyeight")


# In[3]:

plt.rcParams["figure.figsize"]=[5.0, 3.0]


# In[4]:

pd.set_option("max_colwidth",0)


# # Load data

# In[5]:

df = pd.read_csv("../data/nyc/listings.csv.gz", low_memory=False)


# In[6]:

df.columns


# In[29]:

features = ["id", "neighbourhood_group_cleansed", "neighbourhood_cleansed", "accommodates", "bedrooms", "room_type", "price"]


# In[30]:

df2 = df.copy()[features]


# In[31]:

df2.head()


# In[32]:

df2["price"] = df2["price"].map(lambda x: float(x.strip("$").replace(",","")))


# In[33]:

df2.head()


# In[35]:

df2[df2["neighbourhood_cleansed"] == "Hell's Kitchen"]["bedrooms"].value_counts()


# In[41]:

n = df2.groupby("neighbourhood_cleansed")[["price"]].median().reset_index()
n.head()


# In[46]:

plt.subplots(figsize=(16,32));
sns.barplot(y="neighbourhood_cleansed", x="price", orient="h", data=n);
plt.show();


# In[109]:

df2.head()


# # Data wrangling

# In[115]:

df3 = df2.copy()


# ## room_type

# In[113]:

types_of_rooms = df2["room_type"].unique()
types_of_rooms


# In[232]:

room_types = {"Shared room": 0, "Private room": 1, "Entire home/apt": 2}


# In[233]:

df3["room_type"] = df3["room_type"].map(room_types)


# ## Split boroughs

# In[117]:

boroughs = df3["neighbourhood_group_cleansed"].unique()
boroughs


# In[119]:

manhattan = df3[df3["neighbourhood_group_cleansed"] == boroughs[0]].copy()


# In[120]:

brooklyn = df3[df3["neighbourhood_group_cleansed"] == boroughs[1]].copy()


# In[121]:

queens = df3[df3["neighbourhood_group_cleansed"] == boroughs[2]].copy()


# In[122]:

staten = df3[df3["neighbourhood_group_cleansed"] == boroughs[3]].copy()


# In[123]:

bronx = df3[df3["neighbourhood_group_cleansed"] == boroughs[4]].copy()


# In[156]:

b_list = [manhattan, brooklyn, queens, staten, bronx]


# ## Rank neighborhoods

# In[162]:

def rank_neighborhood(data):
    price = data.groupby("neighbourhood_cleansed")[["price"]].median().reset_index()
    price.sort_values(by="price", ascending=True, inplace=True)
    price = {j: i for i,j in enumerate(list(price["neighbourhood_cleansed"]))}
    data["neighbourhood"] = data["neighbourhood_cleansed"].map(price)
    return data, price


# In[163]:

bn_list = [rank_neighborhood(i)[0] for i in b_list]
n_ranks = {boroughs[i]: rank_neighborhood(b_list[i])[1] for i, _ in enumerate(b_list)}


# In[165]:

bn_list[0].head()


# # Modeling

# # Predicting

# ## Convert input

# In[184]:

def convert_nb(borough, nb):
    ref = n_ranks[borough]
    return ref[nb]


# In[187]:

def convert_sample_input(sample):
    features = ["borough", "neighbourhood", "accommodates", "bedrooms", "room_type"]
    orig = [sample[i] for i in features]
    con = [convert_nb(orig[i-1], orig[i]) if i==1 else encode_room(j) if i==4 else j for i,j in enumerate(orig)]
    return con


# In[194]:

sample_input = {"borough": "Manhattan", 
                "neighbourhood": "Upper East Side", 
                "accommodates": 5, 
                "bedrooms": 2, 
                "room_type": "Private room"}


# In[195]:

convert_sample_input(sample_input)


# ## Changing inputs

# In[220]:

def gen_output(sample_input):
    X = convert_sample_input(sample_input)
#     model = model_list[X[0]]
    
    old_input = X[1:]
#     original = model.predict(old_input)
    
    change_list = ["neighbourhood", "accommodates", "bedrooms", "room_type"]
    out = {}
#     out["original"] = original
    for i,a in enumerate(change_list):
        if a != "accommodates":
            new_input = [k if i!=j else k-1 if k-1>= 0 else k for j,k in enumerate(old_input)]
        else:
            new_input = [k if i!=j else k-1 if k-1 > 0 else k for j,k in enumerate(old_input)]
        print new_input
#         out[a] = [new_input[i], model.predict(new_input)]
#     return out
#     return new_input


# In[235]:

sample_input


# In[ ]:




# In[ ]:




# ## Converting outputs

# In[231]:

sample_out = {"original": 200.0, 
              "neighbourhood": [11, 180.5], 
              "accommodates": [4, 186.0], 
              "bedrooms": [1, 150.0], 
              "room_type": [0, 147.5]}


# In[234]:

sample_out_list = [i for i in sample_out.keys()]


# In[241]:

def unconvert_nb(borough, num):
    ref = n_ranks[borough]
    ref = {ref[k]:k for k in ref}
    return ref[num]


# In[248]:

def convert_out(sample_input, sample_out):
    final_out = {}
    features = ["borough", "neighbourhood", "accommodates", "bedrooms", "room_type"]
    for i in sample_out_list:
        if i == "original":
            final_out["original"] = sample_out[i]
        elif i == "neighbourhood":
            n_name = unconvert_nb(sample_input["borough"], sample_out[i][0])
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


# In[249]:

convert_out(sample_input, sample_out)


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:



