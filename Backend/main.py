from flask import Flask, jsonify, redirect, url_for
from flask_cors import CORS
import json
import requests

app = Flask(__name__)
CORS(app)

portfolio_dict = {"total_value": 0, "symbols":{}}


#load the users portfolio
def user_database():
    return {
  "user1": {
    "AAPL": 10,
    "GOOGL": 5,
    "AMZN": 3
  }
}

#temporary redirect to user1 page for added convenience
@app.route('/')
def home():
    return redirect(url_for('portfolio_info', userID='user1'))


@app.route('/<userID>')
def portfolio_info(userID):
    portfolio = user_database()
    new_symbols = {}
    for holding in portfolio[userID]:
        API_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={holding}&apikey=WMDORK6BEVBQ7K7S&outputsize=compact&datatype=json'
        response = requests.get(API_url)
        #if we successfully obtained the information, continue the code
        if response.status_code == 200:
            value = response.json()['Global Quote']['05. price']
            new_symbols[holding] = {'quantity': portfolio[userID][holding], 'value': round(float(value), 2)}
        else:
            return jsonify(error='Something went wrong with Alpha Vantage')
    portfolio_dict['symbols'].update(new_symbols)
    total = 0
    for symbol in portfolio_dict['symbols']:
        total += portfolio_dict['symbols'][symbol]['quantity'] * portfolio_dict['symbols'][symbol]['value']
    portfolio_dict['total_value'] = round(total, 2)
    return jsonify(portfolio_dict)

@app.route('/stockinfo/<symbol>')
def stock_info(symbol):
    API_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=WMDORK6BEVBQ7K7S&outputsize=compact&datatype=json'
    response = requests.get(API_url)
    if response.status_code == 200:
        stock_info = response.json()
        #sort the 5 most recent dates
        time_series = stock_info['Time Series (Daily)']
        most_recent_dates = sorted(time_series.keys(), reverse=True)[0:5]
        stock_info_truncated = [[date, time_series[date]] for date in most_recent_dates]
        #round all the values (1 in chatgpt readme)
        for item in stock_info_truncated:
            for key, value in item[1].items():
                if key == '5. volume':
                    item[1][key] = int(value)
                else:
                    item[1][key] = round(float(value), 2)
        return jsonify(stock_info_truncated)
    else:
        return jsonify(error='Something went wrong with Alpha Vantage')


if __name__ == '__main__':
        app.run(debug=True, port=5000)

