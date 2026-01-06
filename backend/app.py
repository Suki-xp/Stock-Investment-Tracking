#Holds the backend code that will run the stock data, live tracking, 
#graphing plotting/tracking etc
from flask import Flask, request, jsonify 
from flask_cors import CORS
from datetime import datetime
import yfinance as ytrack
import pandas as pd

#This is to allow for the code to also run the front end section of it
app = Flask(__name__)
CORS(app)

#This will act as the temp memory that stores the users input data to track
userPortfolios = {}
userTranscations = []

#Need to verify that the health of the API is well
@app.route('/api/health', methods = ['GET'])
def health_check():
    try:
        response = {
            "status": "healthy",
            "service": "functional",
            "upTime": "GOOD"
        }
        return jsonify(response), 200
    except Exception as error:
        response = {
            "status": "Unhealthy",
            "service": "Non-functional",
            "upTime": "TERRIBLE",
            "error": error
        }
        return jsonify(response), 400

#This method is responsible for getting the stock information 
#via the yFinance and add to the sturcture array of the user
#With its goal being able to determine if its userful enough or not
@app.route('/api/stock/<ticker>', methods= ['GET'])
def proper_stock_info():

    #First thing we got to do now is creating the endpoint so we can get the stock data

if __name__ == "__main__":
    proper_stock_info()
    #app.run(host="0.0.0.0", port=5000, debug=True)