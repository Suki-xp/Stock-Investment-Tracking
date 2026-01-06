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
def proper_stock_info():

    #Playing around with some commands 

    #stock = ytrack.Ticker("AAPL")
    #info = stock.info
    #Sees what type of stock it is
    #print(type(info))
    #What inside the stock specifically
    #print(type(info.keys()))

    #Accessing the fields of the yFinance for more information on the stock
    #month_data = stock.history(period="1y") #Sorts the stock by relevance performance of the past month
    #print(stock.dividends)
    #Format to view in the terminal

    #Can also do multiple stocks at the same time
    #multiStocks = ytrack.download(["GOOG", "MSFT", "TSLA"], interval="1d")
    #print(multiStocks)

if __name__ == "__main__":
    proper_stock_info()
    #app.run(host="0.0.0.0", port=5000, debug=True)