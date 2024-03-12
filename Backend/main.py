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
port = 1521

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
user_stocks = {
    "AAPL": 10,
    "GOOGL": 5,
    "AMZN": 3
}

Session = sessionmaker(bind=engine)

#create our default test user if it does not exist
def create_user_if_not_exists(username, user_stocks):
    session = Session()
    #check if the user already exists
    user = session.query(USERS).filter_by(USERNAME=username).first()
    
    if user is None:
        #user doesn't exist so create it
        new_user = USERS(USERNAME=username, PASSWORD='defaultpassword')
        session.add(new_user)
        session.flush()  # This will assign an ID to new_user without committing the transaction
        
        #add the user's stocks
        for symbol, quantity in user_stocks.items():
            new_stock = USER_STOCKS(USERID=new_user.USERID, STOCKSYMBOL=symbol, QUANTITY=quantity)
            session.add(new_stock)
        
        session.commit() 
        print(f"User {username} created with stocks.")
    else:
        print(f"User {username} already exists.")
    
    session.close()


create_user_if_not_exists('user1', user_stocks)

#temporary redirect to user1 page for added convenience
@app.route('/')
def home():
    return redirect(url_for('portfolio_info', userID='user1'))

#reusable way to check if a symbol exists
def symbol_exists(symbol):
    API_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=WMDORK6BEVBQ7K7S&outputsize=compact&datatype=json'
    response = requests.get(API_url)
    data = response.json()
    
    #check for the expected response 
    if "Time Series (Daily)" in data:
        return True
    else:
        return False

@app.route('/modify_portfolio/<userID>', methods=['POST'])
def modify_portfolio(userID):
    session = Session()
    data = request.json
    add_or_remove = data.get('operation')
    symbol = data.get('symbol')
    quantity = data.get('quantity', 0)
    
    if symbol_exists(symbol) == False:
        return jsonify(error='Symbol does not exist')

    user = session.query(USERS).filter_by(USERNAME=userID).first()

    #fetch or create stock holding for user
    user_stock = session.query(USER_STOCKS).filter_by(USERID=user.USERID, STOCKSYMBOL=symbol).first()

    if add_or_remove == 'add':
        if user_stock:
            user_stock.QUANTITY += quantity
        else:
            #create a new stock holding for the user
            new_stock = USER_STOCKS(USERID=user.USERID, STOCKSYMBOL=symbol, QUANTITY=quantity)
            session.add(new_stock)
    elif add_or_remove == 'remove':
        if user_stock and user_stock.QUANTITY >= quantity:
            user_stock.QUANTITY -= quantity
            if user_stock.QUANTITY == 0:
                session.delete(user_stock)
        else:
            session.close()
            return jsonify(error='Not enough quantity to remove')

    session.commit()
    session.close()

    return jsonify(success=True, message="Portfolio updated successfully.")


@app.route('/<userID>')
def portfolio_info(userID):
    session = Session()
    portfolio_dict = {"total_value": 0, "symbols": {}}

    user = session.query(USERS).filter_by(USERNAME=userID).first()
    if not user:
        return jsonify(error="User not found"), 404

    #fetch the stocks owned by user
    user_stocks = session.query(USER_STOCKS).filter_by(USERID=user.USERID).all()

    new_symbols = {}
    for user_stock in user_stocks:
        symbol = user_stock.STOCKSYMBOL
        quantity = user_stock.QUANTITY
        API_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=WMDORK6BEVBQ7K7S&outputsize=compact&datatype=json'
        response = requests.get(API_url)
        
        if response.status_code == 200:
            value = response.json()['Global Quote']['05. price']
            new_symbols[symbol] = {'quantity': quantity, 'value': round(float(value), 2)}
        else:
            return jsonify(error='Something went wrong with Alpha Vantage')
    
    portfolio_dict['symbols'].update(new_symbols)
    total = 0
    for symbol in portfolio_dict['symbols']:
        total += portfolio_dict['symbols'][symbol]['quantity'] * portfolio_dict['symbols'][symbol]['value']
    portfolio_dict['total_value'] = round(total, 2)

    session.close() 
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

