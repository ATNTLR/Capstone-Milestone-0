from flask import Flask, jsonify
from flask_cors import CORS
import json
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def portfolio_info():
    portfolio_path = 'portfoliotest.json'
    with open(portfolio_path) as file:
        portfolio = json.load(file)
    symbols = []
    user = 'user1'
    for holding in portfolio[user]:
        symbols.append(holding)
    print(symbols)
    return jsonify(message=symbols)

@app.route('/stockinfo/<symbol>')
def stock_info(symbol):
    API_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=WMDORK6BEVBQ7K7S&outputsize=compact&datatype=json'
    response = requests.get(API_url)
    #if we successfully obtained the information, continue the code
    if response.status_code == 200:
        stock_info = response.json()
        #sort the 5 most recent dates
        time_series = stock_info['Time Series (Daily)']
        most_recent_dates = sorted(time_series.keys(), reverse=True)[0:5]
        stock_info_truncated = [{date: time_series[date]} for date in most_recent_dates]
        print(stock_info_truncated)
        return jsonify(stock_info_truncated)
    else:
        print('Alpha Vantage Error')
        return jsonify(error='Something went wrong with Alpha Vantage')


if __name__ == '__main__':
        app.run(debug=True, port=5000)

