#Holds the backend code that will run the stock data, live tracking, 
#graphing plotting/tracking etc
from flask import Flask, requst, jsonify 
from flask_cors import CORS
from dateTime import datetime
import yfinance as ytrack
import pandas as pd

#This is to allow for the code to also run the front end section of it
app = Flask(__name___)
CORS(app)

#This will act as the temp memory that stores the users input data to track