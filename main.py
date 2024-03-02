from flask import Flask, jsonify
from flask_cors import CORS
import json
import requests

app = Flask(__name__)
CORS(app)

portfolio_dict = {}

def data_formatter(portfolio_dict):
    total = 0
    for stock, info in portfolio_dict.items():
        #if total key exists skip it
        if stock == 'total':
            continue
        #our variable is nested deep in the data structure so we retrieve it this way
        most_recent_stock_data = list(info['values'][0].values())[0]
        most_recent_close_price = most_recent_stock_data['4. close']
        total += float(info['quantity']) * float(most_recent_close_price)
    portfolio_dict['total'] = total
    return portfolio_dict

@app.route('/')
def portfolio_info():
    portfolio_path = 'portfoliotest.json'
    with open(portfolio_path) as file:
        portfolio = json.load(file)
    user = 'user1'
    for holding in portfolio[user]:
        API_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={holding}&apikey=WMDORK6BEVBQ7K7S&outputsize=compact&datatype=json'
        response = requests.get(API_url)
        #if we successfully obtained the information, continue the code
        if response.status_code == 200:
            stock_info = response.json()
            #sort the 5 most recent dates
            time_series = stock_info['Time Series (Daily)']
            most_recent_dates = sorted(time_series.keys(), reverse=True)[0:5]
            stock_info_truncated = [{date: time_series[date]} for date in most_recent_dates]
            portfolio_dict[holding] = {'quantity':portfolio[user][holding], 'values':stock_info_truncated}
        else:
            print('Alpha Vantage Error')
            return jsonify(error='Something went wrong with Alpha Vantage')
    data_formatter(portfolio_dict)
    return jsonify(user=portfolio_dict)

@app.route('/stockinfo/<symbol>')
def stock_info(symbol):
    # Create a dictionary with a dynamic key using dictionary unpacking
    #1 in chatgpt readme
    response_data = {symbol: portfolio_dict[symbol]['values']}
    return jsonify(response_data)

if __name__ == '__main__':
        app.run(debug=True, port=5000)

