#Holds the backend code that will run the stock data, live tracking, 
#graphing plotting/tracking etc
from flask import Flask, request, jsonify 
from flask_cors import CORS
from datetime import datetime, timedelta
import yfinance as yStock
import pandas as pd

#This is to allow for the code to also run the front end section of it
app = Flask(__name__)
CORS(app)

#This will act as the temp memory that stores the users input data to track
userPortfolios = {}
userTransactions = []

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
        if stock_price == 0:
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

#This method is what connects that stock data to the app and will search based on
#what stock the user is specifically looking for to bring up the data related to the stock
@app.route('/api/stock/<ticker>', methods= ['GET'])
def display_stock_info(ticker):
    #It needs to call the stock info first and then check it through 
    #to see if the stock data can be retrieved
    try:
        stock_result = proper_stock_info(ticker.upper())
        #Check to make sure that the stock_result can actually exist before updating the JSON
        #to match that

        if stock_result is not None:
            #If its vaild data then we just return the stock 
            return jsonify(stock_result), 200
        
        else:
            response = {
            "symbol": 'active',
            "data": 'trackable',
            "ticker": ticker
            }
            return jsonify(response), 400
        
    except Exception as e:
     return jsonify({'error': str(e), 'ticker': ticker}), 500 #means the stock couldn't be located

#Next we need to add a method that allows the users to create a portfoilio structure of all 
#stocks that they are currently tracking
@app.route('/api/portfolio/<portfolio_id>/transaction', methods=['POST'])
def adding_transactions(portfolio_id):
    try:
        #We got get the data from a JSON request first
        stock_data = request.json

        #Then we need to check to make sure that the 
        #json data of the stocks matches the parameters
        error_response = {
            "data": 'untrackable',
            "error": 'missing key stock information or error in stock formatting'
        }

        #All the different conditions to check
        if 'ticker' not in stock_data:
            return jsonify(error_response), 400
    
        if 'shares' not in stock_data:
            return jsonify(error_response), 400
    
        if 'purchase_date' not in stock_data:
            return jsonify(error_response), 400
    
        if 'purchase_price' not in stock_data:
            return jsonify(error_response), 400
    
        #Now that the boundaries are checked we need to vaildate the data types and values 
        shares = float(stock_data.get('shares'))
        if (shares <= 0):
            return jsonify({"Stock Shares need to be positive"}), 400
    
        prices = float(stock_data.get('purchase_price'))
        if (prices <= 0):
            return jsonify({"Stock Prices need to be positive"}), 400
        
        #Aftewards we can add to a transcation dictionary that will then be 
        #appended to the userTransactions list 
        total_transactions = {
            'portfolio_id': portfolio_id,
            'id': len(portfolio_id) + 1, 
            'ticker': stock_data.get('ticker').upper(), #Gets the stock information itself(name)
            'shares': shares, 
            'purchase_date': stock_data.get('purchase_date', "Unknown"),
            'purchase_price': prices, 
            'time_stamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }   
        #Then we append that data to the userTransactions list
        #and return the success
        userTransactions.append(total_transactions)
        return jsonify({"message": "Transactions have been updated"}), 201
    
    #Catching the two exceptions that could occur
    except ValueError as a:
         return jsonify({'Invaild data type due to error': str(a) }), 400
    
    except Exception as e:
        return jsonify({'Couldnt add to userTransactions due to error': str(e)}), 500

#This method gets the added transactions to return the filtered list of the data
@app.route('/api/portfolio/<portfolio_id>/transactions', methods=['GET'])
def getting_transactions(portfolio_id):

    #Need to filter the userTransactions data via its portfolio_id tags
    #we do this by using list comprehension
    try:
        portfolio_transactions = [transaction for transaction in userTransactions if transaction['portfolio_id'] == portfolio_id]
        #Then we can return the filitered list into a json format now 
        view_transactions = {
            "transactions": portfolio_transactions,
            "count": len(portfolio_transactions),
            "portfolio_id": portfolio_id
        }
        return jsonify(view_transactions), 200
    
    except Exception as noT:
        return jsonify({'Couldnt extract transaction information due to error': str(noT)}), 500

#Want to calculate the value of all the stocks in the portfolio value
#via all the transactions
def calculating_portfolio_value(total_transactions):
    #We need to first sort all the transactions via the ticker amount 
    #by sorting through the all the holdings within the transactions list

    total_holdings = {}
    for transaction in total_transactions:
        #Then we need to accumlate the same shares and costs respectively 
        #into each of the stocks
        named_stocks = transaction['ticker']

        if named_stocks not in total_holdings:
            total_holdings[named_stocks] = {'shares': 0, 'total_cost': 0}
            #Then we increment the proper amount tied to ticker name, calculate
            #the average cost of the share and total costs
        total_holdings[named_stocks]['shares'] += transaction['shares']
        total_holdings[named_stocks]['total_cost'] += transaction['shares'] * transaction['purchase_price']
    
    #Then once that is all accumlated we need to create a dictionary that can store all the metric data 
    #we do this by storing the position of the data itself
    position_data = []
    total_value = 0
    total_cost = 0

    #Fetching the current price of this ticker, and calculating the metrics for this position
    #that we can add to the list 
    for ticker, data in total_holdings.items():
        #Extracting the data 
        shares = data['shares']
        costs = data['total_cost']

        #Find the current price from earlier example format
        try:
            locate_stock = yStock.Ticker(ticker)
            locate_price = locate_stock.info.get('currentPrice') or locate_stock.info.get('regularMarketPrice', 0)

            if locate_price == 0:
                locate_price = 0
            
        except Exception as e:
            locate_price = 0
        
        #Now we got use the formuala to calculate the rest of the information
        if shares > 0:
            avg_cost = costs / shares
        else:
            avg_cost = 0

        current_value = shares * locate_price
        #Make sure we also find the absolute gain/loss of each of the stocks 

        gain_loss = current_value - costs
        if costs > 0:
            gain_loss_percent = (gain_loss / costs) * 100
        else:
            gain_loss_percent = 0

        #Now we can build a dictionary to store the positions which we 
        #can then loop through and check to see how much the stock weights
        #in its factor
        calculated_stock_positions = {
            'ticker': ticker, 
            'shares': shares,
            'avg_cost': avg_cost,
            'cost_amount': costs, 
            'current_price': locate_price, 
            'current_value': current_value, 
            'gain_loss': gain_loss, 
            'gain_loss_percent': gain_loss_percent,
            'weight': 0 #This is what we calculate to loop through
        }
        position_data.append(calculated_stock_positions)
        #Updates the storage amount and values of the data
        total_value += current_value
        total_cost += costs

    #Then we do the final loop through to check and add the proper weight value
    for position in position_data:
        if total_value > 0:
            position['weight'] = (position['current_value'] / total_value) * 100
        else:
            position['weight'] = 0
    
    #Update the portfilo metrics again
    total_returns = total_value - total_cost
    total_returns_percent = 0

    if total_cost > 0:
        total_returns_percent = (total_returns / total_cost) * 100
    else:
        total_returns_percent
    
    #Finally returning the full summary of it all
    return {
        'total_value': total_value,
        'total_cost': total_cost,
        'total_return': total_returns,
        'total_return_percent': total_returns_percent,
        'num_positions': len(position_data),
        'positions': position_data
    }

#Creating the function that get that calculation as a summary to display 
@app.route('/api/portfolio/<portfolio_id>/summary', methods=['GET'])
def get_portfolio_summary(portfolio_id):
    #First we want to filter the transactions based on the users portfolio id
    #same idea as before
    try:
        portfolio_calculations = [transaction for transaction in userTransactions if transaction['portfolio_id'] == portfolio_id]
        #Then check that any of them are empty
        if len(portfolio_calculations) == 0:
            return jsonify({'Result': "No summary created as data couldn't be located", }), 200
        
        summary = calculating_portfolio_value(portfolio_calculations)
        return jsonify(summary), 200
    
    #Catching the last place as always
    except Exception as noSummary:
        return jsonify({'Couldnt extract transaction information due to error': str(noSummary)}), 500

#Calculating the performance of the portfolio now, but for the daily measurements
#meaning that we need to deal with the real time data series of the stock data rather than all
#all the collective data
def calculating_real_time_portfolio_data(transactions_lists, start_date, end_date):
    
    #Set our data range and stock tickers
    data_range = pd.date_range(start=start_date, end=end_date, freq='D') #For daily occurance tracking
    stock_tickers = set([t['ticker'] for t in transactions_lists]) #Creates the unique range of symbols for the transactions

    #Once we have all that data we then need to fetch all the prices within the date range
    price_data = {}
    for ticker in stock_tickers:
        stocks = yStock.Ticker(ticker)
        stock_range = stocks.history(start=start_date, end=end_date)

        #One last check to make sure
        if not stock_range.empty:
            stock_range.index = stock_range.index.tz_localize(None)

        #Adding to the dictionary for the range
        price_data[ticker] = stock_range
    
    #Then for each date we got to calculate the value
    dates_list = []
    values_list = []

    #We do that through the filtering of the transactions up to the dates, etc
    for current_date in data_range: 

        transaction_range = [t for t in transactions_lists 
            if datetime.strptime(t['purchase_date'], '%Y-%m-%d') <= current_date
        ]

        #Once we have the proper range we can then sort by the ticker like in calculating 
        #portfolio method 
        daily_holdings = {}
        for holdings in transaction_range:
            tickers = holdings['ticker']

            if tickers not in daily_holdings:
                daily_holdings[tickers] = {'shares': 0, 'total_cost': 0}
            
            daily_holdings[tickers]['shares'] += holdings['shares']
            daily_holdings[tickers]['total_cost'] += holdings['shares'] * holdings['purchase_price']

        #Then we can calculate the total value of the stocks across that range
        total_value_of_stocks = 0
        for ticker, data in daily_holdings.items():
            #We do that by finding the date tied to it
            data_shares = data['shares']
            try:
                #Convert current_date to just the date part for lookup
                date_key = current_date.date()

                #Then we see if it falls within the range and formats the data contained
                #from the start to that end portion
                if date_key in price_data[ticker].index.date:

                    price = price_data[ticker].loc[current_date]['Close']
                    total_value_of_stocks += data_shares * price
                else:
                    available_dates = price_data[ticker].index[price_data[ticker].index <= current_date]

                    if len(available_dates) > 0:
                        last_date = available_dates[-1]
                        price = price_data[ticker].loc[last_date]['Close']
                        total_value_of_stocks += data_shares * price

            except Exception as e:
                pass #We just need to skip in this case

        #Then we store the data values to return
        dates_list.append(current_date.strftime('%Y-%m-%d'))
        values_list.append(total_value_of_stocks)

    return {
        'dates': dates_list,
        'values': values_list
    }

#The method to run the app for getting the date ranges
@app.route('/api/portfolio/<portfolio_id>/performance', methods=['GET'])
def getting_real_time_portfolio_data(portfolio_id):

    #Need to get the queries for the ranges(the start and end dates)
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    start_date = request.args.get('start_date', (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))

    try:
        date_range_portfolio = [transaction for transaction in userTransactions if transaction['portfolio_id'] == portfolio_id]
        #Then check that any of them are empty
        if len(date_range_portfolio) == 0:
            return jsonify({'Result': "No summary created as data couldn't be located", }), 200
        
        summary = calculating_real_time_portfolio_data(date_range_portfolio, start_date, end_date)
        return jsonify(summary), 200
    
    #Catching the last place as always
    except Exception as noSummary:
        return jsonify({'Couldnt extract transaction information due to error': str(noSummary)}), 500
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)