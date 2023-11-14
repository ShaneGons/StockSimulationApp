from string import printable
from flask import Flask, render_template, redirect, url_for, request, session
import re
import json
import time
from database import DatabaseConnection
from stock_api import buy_stock, sell_stock, get_current_quote, get_current_quote_2, which_stock_exchange
from stock_symbol import StockSearcher
import finnhub
import random
import mailtrap as mt
import base64
from pathlib import Path
import smtplib

app = Flask(__name__)
stock_searcher = StockSearcher()

app.secret_key = "BAD_SECRET_KEY"

# Home Page


@app.route('/')
def root():
    session['authenticationSuccessful'] = None
    return redirect(url_for('home'))


@app.route('/home/')
def home():
    session['authenticationSuccessful'] = None
    return render_template('home.html')


@app.route('/login/forgot-password/')
def forgot_password():
    return render_template('forgotpassword.html')

# @app.route('/login/forgot-password/authenticate/', methods=['POST'])
# def verify_otp():
#     if request.method == 'POST' and 'recoveryEmail' in request.form:
#         user_email = request.form['recoveryEmail']
#         #db = DatabaseConnection()
#         #user_portfolio = db.execute(f"SELECT * FROM Portfolios WHERE email = {user_email}")
#         if False:
#             print("Account doesn't exist")
#             return render_template('forgotpassword.html')
#         else:
#             otp = ""
#             for i in range(6):
#                 digit = random.randint(0,9)
#                 otp += str(digit)
            
#             msg = otp
#             send_email(user_email, msg)
#     return False


# Portfolio Overview


# @socketio.on("update_table")
@app.route('/update_table')
def update_table():
    db = DatabaseConnection()
    # getting data from database
    portfolioID = int(session["PortfolioID"])
    rows = db.execute(f"SELECT * FROM Stock_portfolio WHERE PortfolioID = {portfolioID};")
    # getting current price and updating p/l for each stock
    modified_rows = []
    for row in rows:
        stockName = row[0]
        row = list(row)

        try:
            current_quote = get_current_quote_2(stockName)
            
            price = float(current_quote["c"])

        except finnhub.FinnhubAPIException as e:
            if e.code == 429: # if we exceed 30 API Requests Per Minute
                # return "Error: Too many API Requests. Please wait a minute before buying or selling"
                price = row[4]

        # Handles Wrong Stockname Case
        if current_quote == {'c': 0, 'd': None, 'dp': None, 'h': 0, 'l': 0, 'o': 0, 'pc': 0, 't': 0}:
            return f"Error: {stockName} not found"
        
        row[4] = price
        pl = price*row[2] - row[3]*row[2]
        row[5] = pl
        modify_sql = f"""
            UPDATE Stock_portfolio 
            SET 
                current_price = {price},
                pl = {pl}
            WHERE
                StockName = '{stockName}';
            """
        db.execute(modify_sql)
        modified_row = {
            "stock_name": row[0],
            "quantity": row[2],
            "average_price": row[3],
            "current_price": row[4],
            "pl": row[5]
        }
        modified_rows.append(modified_row)

    return {"results": modified_rows}


# @socketio.on("search_for_stock")
# def handle_search_for_stock(data):
#     search_term = data["data"]
#     low, high = stock_searcher.search_by_name(search_term)
#     results = []
#     for i in range(low, high):
#         results.append([stock_searcher.sorted_name_list[0][i],
#                        stock_searcher.sorted_name_list[1][i]])
#     emit("search_stock_response", results)

@app.route('/stocksearch')
def stocksearch():
    search_term = request.args.get('search_term')
    low, high = stock_searcher.search_by_name(search_term)
    results = []
    for i in range(low, high):
        results.append([stock_searcher.sorted_name_list[0][i],
                       stock_searcher.sorted_name_list[1][i]])
        
    low, high = stock_searcher.search_by_symbol(search_term)
    for i in range(low, high):
        results.append([stock_searcher.sorted_symbol_list[0][i],
                       stock_searcher.sorted_symbol_list[1][i]])
    
    return {"results": results}

@app.route('/getcredit')
def getcredit():
    db = DatabaseConnection()
    portfolioID = int(session["PortfolioID"])
    virtual_money = db.execute(f"SELECT credit FROM Portfolios WHERE PortfolioID = {portfolioID};")
    db.close()
    return {"credit": virtual_money}


@app.route('/portfolio/')
def portfoliooverview():
    session['authenticationSuccessful'] = None
    try:
        if session['loggedin']:
            pass
    except:
        session['loggedin'] = False
        session['UserID'] = 0
        session['username'] = ""
        session['email'] = ""
        session['PortfolioID'] = 0
    if session['loggedin'] == False:
        return redirect(url_for('login'))
    else:
        db = DatabaseConnection()
        portfolioID = int(session["PortfolioID"])
        rows = db.execute(f"SELECT * FROM Stock_portfolio WHERE PortfolioID = {portfolioID};")
        stocks = []
        symbols = []
        for row in rows:
            stockName = row[0]
            stock_exchange = which_stock_exchange(stockName)
            stocks.append([stockName, stock_exchange + ":" + stockName])
            symbols.append([stockName, stockName+"|"+"1D"])
        virtual_money = db.execute(f"SELECT credit FROM Portfolios WHERE PortfolioID = {portfolioID};")
        virtual_money = list(virtual_money)
        virtual_money = re.sub('\D', '', str(virtual_money[0]))
        virtual_money = "$"+ virtual_money
        print(symbols)
        return render_template('portfoliooverview.html', stocks = stocks, symbols = symbols, virtual_money = virtual_money)

@app.route('/stockInfo/', methods=['GET'])
def stockInfo():
    stock_name = request.args.get("stockName")
    stock_exchange = which_stock_exchange(stock_name)
    return render_template('stockInfo.html', stock_name = stock_name, stock_exchange = stock_exchange)


@app.route('/leaderboard/')
def leaderboard():
    session['authenticationSuccessful'] = None
    users = []
    db = DatabaseConnection()
    players = []
    list_of_players = db.execute(f"SELECT UserID, username FROM Users;")
    for i, player in enumerate(list_of_players):

        try:
            portfolio = db.execute(f"SELECT PortfolioID FROM Portfolios WHERE UserID = '{player[0]}';")
            list_of_shares = db.execute(f"SELECT StockName, amount FROM Stock_portfolio WHERE PortfolioID = '{portfolio[0][0]}';")
        except:
            print("No portfolio found for: "+player[1])

        players.append([player[1]])

        for j, share in enumerate(list_of_shares):
            players[i].append([share[0]])
            players[i][j+1].append(share[1])
    for person in players:
        score = 0
        for stock in person[1:]:
            current_quote = get_current_quote(stock[0])
            # Handles Wrong Stockname Case
            if current_quote == {'c': 0, 'd': None, 'dp': None, 'h': 0, 'l': 0, 'o': 0, 'pc': 0, 't': 0}:
                print("Error: "+stock[0]+" not found")
                price = 0.0
            else: 
                price = float(current_quote["c"])
            score += price*stock[1]
        userID = db.execute(f"SELECT UserID from Users WHERE username = '{person[0]}';")
        credits = db.execute(f"SELECT credit FROM Portfolios WHERE UserID = '{userID[0][0]}';")
        score += credits[0][0]
        user = [person[0],'$'+str(score)]
        users.append(user)
    users = bubbleSort(users)
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return render_template('leaderboard.html', users=users, current_time=current_time)

# Buying and Selling

@app.route('/to-buy')
def buy_stock_route():
    stockName = request.args.get('stockName')
    portfolioID = session["PortfolioID"]
    amount = float(request.args.get('amount'))

    r = buy_stock(stockName, portfolioID, amount)
    return {"message": r}


@app.route('/to-sell')
def sell_stock_route():
    stockName = request.args.get('stockName')
    portfolioID = session["PortfolioID"]
    amount = float(request.args.get('amount'))

    r = sell_stock(stockName, portfolioID, amount)
    return {"message": r}

# Login and Registration


@app.route('/login/')
def login():
    try:
        session['authenticationSuccessful']
    except NameError:
        session['authenticationSuccessful'] = None
    return render_template('login.html')


@app.route('/login/authenticate/', methods=['POST'])
def authenticate():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'loginUsername' in request.form and 'loginPassword' in request.form:
        # Create variables for easy access
        username = request.form['loginUsername']
        password = request.form['loginPassword']
        # Check if account exists using MySQL
        db = DatabaseConnection()
        # Fetch one record and return result
        account = db.execute(
            f"SELECT * FROM Users WHERE username = '{username}' AND password = '{password}'")
        # If account exists in accounts table in our database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['UserID'] = account[0][0]
            session['username'] = account[0][1]
            session['email'] = account[0][2]
            # Get user portfolio and save ID to session
            user_portfolio = db.execute(f"SELECT * FROM Portfolios WHERE UserID = {account[0][0]}")
            if user_portfolio == ():
                userID = account[0][0]
                db.execute(f"INSERT INTO Portfolios(UserID, credit) VALUES ('{str(userID)}', '{100000}');")

            user_portfolio = db.execute(f"SELECT * FROM Portfolios WHERE UserID = {account[0][0]}")   
            session["PortfolioID"] = user_portfolio[0][1]

            session['authenticationSuccessful'] = True
            # Redirect to home page
            return redirect('/home')
        else:
            # Account doesnt exist or username/password incorrect
            message = 'The password or username is invalid!'
        # Show the login form with message (if any)
        db.close()
    session['authenticationSuccessful'] = False
    return redirect(url_for('login'))


@app.route('/register/')
def register():
    return render_template('register.html')


@app.route('/register/authenticate/', methods=['POST'])
def registerLogic():
    if request.method == 'POST' and 'loginEmail' in request.form and 'loginPassword' in request.form:
        # Variables for Easy access
        email = request.form['loginEmail']
        username = request.form['loginUsername']
        password = request.form['loginPassword']
        # Check if Account already Exists
        db = DatabaseConnection()
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # cursor object, Dictionary
        # cursor.execute('SELECT * FROM Users WHERE email = %s AND username = %s AND password = %s ', (email, username, password))
        # Fetch User
        # account  = cursor.fetchone()
        account = db.execute(
            f"SELECT * FROM Users WHERE email = '{email}' AND username = '{username}' AND password = '{password}';")
        # If account exits in Users table
        usernameCheck = db.execute(
            f"SELECT * FROM Users WHERE email = '{email}' OR username = '{username}';")
        if account:
            message = 'Account already Exists! Please login'
            session['registrationSuccessful'] = "A"
            db.close()
            return redirect(url_for('register'))
        # Catching Invalid Entry
        elif usernameCheck:
            session['registrationSuccessful'] = "E"
            db.close()
            return redirect(url_for('register'))
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
            session['registrationSuccessful'] = "B"
            db.close()
            return redirect(url_for('register'))
        elif not re.match(r'[A-Za-z0-9]+', username):
            message = 'Username must contain only characters and numbers!'
            session['registrationSuccessful'] = "C"
            db.close()
            return redirect(url_for('register'))
        elif not username or not password or not email:
            message = 'Please fill out the form!'
            session['registrationSuccessful'] = "D"
            db.close()
            return redirect(url_for('register'))
        # Account doesn't exist and form data is valid. Inserting new account data into Users Table
        else:
            db.execute(
                f"INSERT INTO Users(username, email, password) VALUES ('{username}', '{email}', '{password}');")
            userID = db.execute(f"SELECT UserID FROM Users WHERE email = '{email}' AND username = '{username}' AND password = '{password}';")
            db.execute(f"INSERT INTO Portfolios(UserID, credit) VALUES ('{userID[0][0]}', '{10000}');")
            message = 'You have successfully registered!'
            session['registrationSuccessful'] = True
            db.close()
            return redirect(url_for('portfolio'))
        # Show registration form with message (if any)




@app.route('/account/')
def account():
    return render_template('account.html')

@app.route('/logout')
def logout():
    session['loggedin'] = False
    session['UserID'] = None
    session['username'] = None
    session['email'] = None
    session['PortfolioID'] = None
    print("Logged out")
    return redirect(url_for('home'))

# Currently Irrelevant
# Left if needed during Redesign

@app.route('/main/')
def main():
    return render_template('main.html')



@app.route('/following/')
def following():
    return render_template('sidebar/following.html')


@app.route('/analysis/')
def analysis():
    return render_template('sidebar/analysis.html')


@app.route('/trends/')
def trends():
    return render_template('sidebar/trends.html')


@app.route('/portfolio/')
def portfolio():
    return render_template('sidebar/portfolio.html')


@app.route('/chatroom/')
def chatroom():
    return render_template('sidebar/chatroom.html')

@app.route('/trade/')
def trade():
    return render_template('sidebar/trade.html')


@app.route('/main/tabs/')
def tabs():
    return render_template('main/tabs.html')


@app.route('/main/graph/')
def graph():
    return render_template('main/graph.html')


@app.route('/main/news/')
def news():
    return render_template('main/news.html')

def bubbleSort(users):
    for i in range(len(users)):
        for j in range(len(users)-1):
            if float((users[j][1])[1:]) < float((users[j+1][1])[1:]):
                temp = users[j]
                users[j] = users[j+1]
                users[j+1] = temp
    return users

# def send_email(user_email, msg):
#     send_email = "xpstockofficial@gmail.com"
#     send_pass = "vxepilhkczftmwbw"

#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.starttls()
#     server.login(send_email, send_pass)
#     server.sendmail(send_email,user_email,msg)
#     print("Email Sent")