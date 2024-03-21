from flask import Flask, jsonify, redirect, url_for, request, make_response
from flask_cors import CORS
from flask import session as flask_session
import requests
import oracledb
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Identity, create_engine, select, join, inspect, text
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import relationship, backref, sessionmaker, declarative_base

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

app.config.update(
    SECRET_KEY='unsecure_key',
    SESSION_COOKIE_SECURE=True,  # Ensure cookies are only sent over HTTPS
    SESSION_COOKIE_SAMESITE='None',  # Allow cookies to be sent with cross-site requests
)
app.secret_key = 'unsecure_key'


un = 'ADMIN'
pw = 'Mycapstonedatabase1'
dsn = '(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.eu-madrid-1.oraclecloud.com))(connect_data=(service_name=gd299c42c87507e_capstoneantoine_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'
port = 1521

pool = oracledb.create_pool(user=un, password=pw,
                            dsn=dsn)



engine = create_engine("oracle+oracledb://", creator=pool.acquire, poolclass=NullPool, echo=True)

#the base class which our objects will be defined on.
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


Session = sessionmaker(bind=engine)

def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return add_cors_headers(make_response())
    session = Session()
    username = request.json.get('username')
    password = request.json.get('password')
    
    user = session.query(USERS).filter_by(USERNAME=username).first()
    if user and user.PASSWORD == password:
        flask_session['user_id'] = user.USERID  # Simple session management
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/logout', methods=['GET'])
def logout():
    flask_session.pop('user_id', None)  # Logout by removing user from session
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        
        session = Session()
        # Check if username already exists
        existing_user = session.query(USERS).filter_by(USERNAME=username).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 409

        # Create new user without adding predefined stocks
        new_user = USERS(USERNAME=username, PASSWORD=password)
        session.add(new_user)
        session.commit()
        
        return jsonify({'message': 'Registration successful'}), 201
    except Exception as e:
        return jsonify({'error': 'An internal error occurred'}), 500
    finally:
        session.close()


#temporary redirect to user1 page for added convenience
@app.route('/')
def home():
    return redirect(url_for('portfolio_info'))

#reusable way to check if a symbol exists
def symbol_exists(symbol):
    API_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=WMDORK6BEVBQ7K7S&outputsize=compact&datatype=json'
    response = requests.get(API_url)
    data = response.json()
    
    #check for the expected response 
    if "Time Series (Daily)" in data:
        return True
    else:
        return False


@app.route('/modifyPortfolio', methods=['POST'])
def modify_portfolio():
    #check for user session
    if 'user_id' not in flask_session:
        return jsonify({'error': 'User not logged in modify'})

    user_id = flask_session['user_id']
    session = Session()
    data = request.json
    operation = data.get('operation').upper()
    symbol = data.get('stock_symbol').upper()
    quantity = int(data.get('quantity', 0))  

    #check if the symbol exists
    if not symbol_exists(symbol):
        return jsonify({'error': 'Invalid stock symbol'}), 400

    #fetch or create stock holding for the user
    user_stock = session.query(USER_STOCKS).filter_by(USERID=user_id, STOCKSYMBOL=symbol).first()

    if operation == 'ADD':
        if user_stock:
            user_stock.QUANTITY += quantity
        else:
            #create new stock holding for the user
            new_stock = USER_STOCKS(USERID=user_id, STOCKSYMBOL=symbol, QUANTITY=quantity)
            session.add(new_stock)
    elif operation == 'REMOVE':
        if user_stock and user_stock.QUANTITY >= quantity:
            user_stock.QUANTITY -= quantity
            if user_stock.QUANTITY == 0:
                session.delete(user_stock)
        else:
            #stock not found or quantity exceeds what we have
            if not user_stock:
                errorMsg = 'Stock not found in portfolio'
            else:
                errorMsg = 'Requested quantity exceeds stocks in portfolio'
            session.close()
            return jsonify(error=errorMsg), 400

    session.commit()
    session.close()
    #redirect to overview to render updated portfolio
    return redirect(url_for('portfolio_info'))

@app.route('/overview')
def portfolio_info():
    #check if a user is logged in
    if 'user_id' not in flask_session:
        return jsonify({'error': 'User not logged in overview'}), 401

    user_id = flask_session['user_id']
    session = Session()
    
    #initialize the structure for portfolio response
    portfolio_dict = {"total_value": 0, "symbols": {}}

    try:
        #fetch the stocks owned by logged-in user
        user_stocks = session.query(USER_STOCKS).filter_by(USERID=user_id).all()

        if not user_stocks:
            # If the user has no stocks, return an empty portfolio structure
            return jsonify(portfolio_dict), 200

        #if user has stocks, fetch their current values and calculate total portfolio value
        for user_stock in user_stocks:
            symbol = user_stock.STOCKSYMBOL
            quantity = user_stock.QUANTITY
            API_url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=WMDORK6BEVBQ7K7S&outputsize=compact&datatype=json'
            response = requests.get(API_url)
            
            if response.status_code == 200:
                data = response.json()
                price = float(data['Global Quote']['05. price'])
                total_value = price * quantity
                portfolio_dict['symbols'][symbol] = {'quantity': quantity, 'value': round(price, 2)}
                portfolio_dict['total_value'] += total_value
            else:
                app.logger.error(f'Failed to fetch stock data for {symbol}')
                continue  #skip this stock and continue with others

        portfolio_dict['total_value'] = round(portfolio_dict['total_value'], 2)

    except Exception as e:
        app.logger.error(f'An error occurred while fetching the portfolio: {e}')
        return jsonify({'error': 'Failed to fetch portfolio information'}), 500
    
    finally:
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