from flask import Flask, jsonify
from flask_cors import CORS
import json
import requests

app = Flask(__name__)
CORS(app)

"""
To use this, please run the flask application, everything will be printed in the terminal, however,
in order to get information on a specific stock you must do it through the url. I tried to do it by making
flask optional by separating the logic from flask and using sys.argv but it is too far from the goal 
of the project I thought it would be better to keep flask and the logic together.
"""


#default path
@app.route('/')
def portfolio_info():
    portfolio_path = 'C:\\Users\\ANTOI\\Programming_Projects\\Capstone_Projects\\Captstone_Project_0_backend\\portfoliotest.json'
    #open the file with the portfolio and write it into a variable
    with open(portfolio_path) as file:
        portfolio = json.load(file)
    #isolate all the symbols into a list
    symbols = []
    user = 'user1'
    for holding in portfolio[user]:
        symbols.append(holding)
    #print and return the symbols
    print(symbols)
    return jsonify(message="Hello, from Flask!")

#when symbol passed into URL, store that as a variable
@app.route('/stockinfo/<symbol>')
def stock_info(symbol):
    #get the info on that specific symbol from the API
    API_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=WMDORK6BEVBQ7K7S&outputsize=compact&datatype=json'
    response = requests.get(API_url)
    #if we successfully obtained the information, continue the code
    if response.status_code == 200:
        #store the APIs response into a variable
        stock_info = response.json()
        #make a sorted list of the 5 most recent dates
        time_series = stock_info['Time Series (Daily)']
        most_recent_dates = sorted(time_series.keys(), reverse=True)[0:5]
        #get the prices for the 5 most recent days
        stock_info_truncated = [{date: time_series[date]} for date in most_recent_dates]
        #print and return that data
        print(stock_info_truncated)
        return jsonify(stock_info_truncated)
    #if the API didnt return the info, inform the user of the error
    else:
        print('Alpha Vantage Error')
        return jsonify(error='Something went wrong with Alpha Vantage')


if __name__ == '__main__':
        app.run(debug=True, port=5000)

