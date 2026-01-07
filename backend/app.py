#Holds the backend code that will run the stock data, live tracking, 
#graphing plotting/tracking etc
from flask import Flask, request, jsonify 
from flask_cors import CORS
from datetime import datetime
import yfinance as yStock
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
def proper_stock_info(ticker):
    #Working with the try and except format to retrieve the data
    #this makes it that onces the user visits the /api/stock/"" that 
    #will try and retrieve that stock info
    
    try:
        find_stock = yStock.Ticker(ticker)
        stock_info = find_stock.info #Grabs relavent info about the stock

        #Need to check that the stock isnt empty and has a current price ready
        stock_price = stock_info.get('currentPrice') or stock_info.get('regularMarketPrice', 0)
        if stock_price is 0:
            return None
        
        #Make sure stock is relevant enough to find all the info on
        if (len(stock_info) > 5):
            #Then add it to the dictionary which gets the tags to it
            stock_data = {
                'symbol': stock_info.get('symbol', ticker.upper()),
                'longName': stock_info.get('longName', 'unknown'),
                'currentPrice': stock_price,
                'marketCap': stock_info.get('marketCap', 0),
                'sector': stock_info.get('sector', 'Unknown'), 
                'industry': stock_info.get('industry', 'Unknown'),
                'currency': stock_info.get('currency', 'USD')
            }
            return stock_data
    except Exception as e:
        return {'error': str(e), 'ticker': ticker} #means the stock couldn't be located

if __name__ == "__main__":
    proper_stock_info()
    #app.run(host="0.0.0.0", port=5000, debug=True)