#Flask,scikit-learn,pandas,pickle-mixin
from flask import Flask,render_template,request
import pandas as pd
import numpy as np
import pickle
import json
 
app=Flask(__name__,static_url_path='/static')
data=pd.read_csv('Cleaned_data.csv')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    locations =sorted(data['location'].unique())
    
    return render_template('index.html',locations=locations)

__locations = None
__data_columns = None
with open("columns.json") as f:
        __data_columns = json.loads(f.read())["data_columns"]
        __locations = __data_columns[3:]
model = pickle.load(open("bangalore_home_prices_model.pickle","rb"))


def get_estimated_price(input_json):
    try:
        loc_index = __data_columns.index(input_json['location'].lower())
        print(loc_index)
    except:
        loc_index = -1
    if(loc_index==0 or loc_index==1 or loc_index==2):
        loc_index=8
    x = np.zeros(244)
    x[0] = input_json['sqft']
    x[1] = input_json['bath']
    x[2] = input_json['bhk']
    if loc_index >= 0:
        x[loc_index] = 1
    result = round(model.predict([x])[0],2)
    print(loc_index)
    if(x[0]<600):
        if(x[0]>=50 and x[0]<=140):
            result=14
        elif(x[0]>140 and x[0]<=300):
            result=25
        elif(x[0]>300 and x[0]<=500):
            result=29.8
        else:
            result=32
    if(x[0]==0 or x[2]==0):
        result=0
    elif(result<=0):
        result=0
    return result

def get_location_names():
    return __locations

def load_saved_artifacts():
    print("Loading the saved artifacts...start !")
    global __data_columns
    global __locations
    global model


    

@app.route('/predict',methods=['POST'])
def predict():
    if request.method == 'POST':
        input_json = {
            "location": request.form['location'],
            "sqft": request.form['total_sqft'],
            "bhk": request.form['bhk'],
            "bath": request.form['bath']
        }
        result = get_estimated_price(input_json)
        print(result)
        if result==0:
            result="you cannot predict with given values"
            return render_template('predict.html',result=result)
        elif result > 100:
            result = round(result/100, 2)
            result = str(result) + ' Crore'
        else:
            result = str(result) + ' Lakhs'
        return render_template('predict.html',result=result)

if __name__ == "__main__":
    app.run(debug=True,port=4042)