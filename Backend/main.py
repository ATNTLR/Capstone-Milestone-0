from flask import Flask, jsonify, redirect, url_for, request
from flask_cors import CORS
import json
import requests
import oracledb
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Identity, create_engine, select, join, inspect, text
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import relationship, backref, sessionmaker, declarative_base
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
CORS(app)

un = 'ADMIN'
pw = 'Mycapstonedatabase1'
dsn = '(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=gd299c42c87507e_capstoneantoine_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'
hostname, service_name = ["adb.eu-madrid-1.oraclecloud.com", "gd299c42c87507e_capstoneantoine_high.adb.oraclecloud.com"]
port = 1521

"""
# Standalone connection
engine = create_engine(
    f'oracle+oracledb://{un}:{pw}@',
    thick_mode=None,
    connect_args={
        "host": hostname,
        "port": port,
        "service_name": service_name
    }
)
"""


pool = oracledb.create_pool(user=un, password=pw,
                            dsn=dsn)



engine = create_engine("oracle+oracledb://", creator=pool.acquire, poolclass=NullPool, echo=True)

# The base class which our objects will be defined on.
Base = declarative_base()

class USERS(Base):
    __tablename__ = 'USERS'
    USERID = Column(Integer, Identity(start=1), primary_key=True)
    USERNAME = Column(String(255))
    PASSWORD = Column(String(255))

class USER_STOCKS(Base):
    __tablename__ = 'USER_STOCKS'
    USERID = Column(Integer, ForeignKey('USERS.USERID'), primary_key=True)
    STOCKSYMBOL = Column(String(255), primary_key=True)
    QUANTITY = Column(Integer)

Base.metadata.create_all(engine)

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

@app.route('/modify_portfolio/<userID>', methods=['POST'])
def modify_portfolio(userID):
    data = request.json
    add_or_remove = data.get('operation')
    symbol = data.get('symbol')
    quantity = data.get('quantity', 0)
    portfolio = user_database()[userID]

    if add_or_remove == 'add':
        if symbol in portfolio:
            portfolio[symbol] += quantity
        else:
            portfolio[symbol] = quantity
    elif add_or_remove == 'remove':
        if symbol in portfolio and portfolio[symbol] >= quantity:
            portfolio[symbol] -= quantity
            if portfolio[symbol] == 0:
                del portfolio[symbol]
        else:
            return jsonify(error='Not enough quantity to remove or symbol does not exist'), 400

    # Assuming you have a function to save the updated portfolio back to the database
    save_user_portfolio(userID, portfolio)
    return jsonify(success=True, portfolio=portfolio)


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

