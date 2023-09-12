import requests
from database import DatabaseConnection
import finnhub

## Finnhub Quote Endpoint
# Limit of 30 API Calls per minute per API Key 
# Best Free Option Available

finnhub_client_1 = finnhub.Client(api_key="cgdr3n1r01qpf4i2a2fgcgdr3n1r01qpf4i2a2g0")
finnhub_client_2 = finnhub.Client(api_key="cgdr75pr01qpf4i2a7bgcgdr75pr01qpf4i2a7c0")

## Polygon Ticker Endpoind
# Unlimited API Calls
# Used to know if stock is in NYSE or NASDAQ

TICKER_URL = "https://api.polygon.io/v3/reference/tickers?ticker={stockTicker}&market=stocks&active=true&apiKey=inmqGwW8in5GRX7psn9DiA4IPKMRUrFs"


def get_current_quote(stockName):
    """
    Makes API Call to Finnhub : Quote Endpoint to get most recent price.
    (Least Delay in Free APIs and Biggest Limit)
    """
    return(finnhub_client_1.quote(stockName))

def get_current_quote_2(stockName):
    """
    Makes API Call to Finnhub: Quote Endpoint to get most recent price.
    (Least Delay in Free APIs and Biggest Limit)
    """
    return(finnhub_client_2.quote(stockName))

def which_stock_exchange(stockName):
    stockName.upper()
    r = requests.get(TICKER_URL.format(stockTicker=stockName))
    r = r.json()
    try:
        mic_code = r["results"][0]["primary_exchange"]
    except:
        mic_code = None
    
    if mic_code == "XNAS":
        stock_exchange = "NASDAQ"
    elif mic_code == "XNYS":
        stock_exchange = "NYSE"
    elif mic_code == "XASE":
        stock_exchange = "AMEX"
    else:
        return f"Error: {stockName} is not in NASDAQ, NYSE, or AMEX. CSVs had wrong data"
    
    return stock_exchange

def get_portfolio(portfolioID):
    db = DatabaseConnection()
    response = db.execute(f"SELECT * FROM Portfolios WHERE PortfolioID = {portfolioID}")
    db.close()
    if len(response) == 0:
        return None
    else:
        return response[0]
    
def add_stock(stockName):
    db = DatabaseConnection()
    response = db.execute(f"SELECT * FROM Stocks WHERE StockName = '{stockName}';")
    if len(response) == 0:
        # need to add stock and its stock exchange
        add_stock_sql = f"""
        INSERT INTO Stocks (StockName)
        VALUES ('{stockName}');
        """
        db.execute(add_stock_sql)
    
    db.close()

def modify_portfolio(portfolioID, new_credit):
    db = DatabaseConnection()
    modify_sql = f"""
    UPDATE Portfolios 
    SET 
        credit = {new_credit}
    WHERE
        PortfolioID = {portfolioID};
    """
    db.execute(modify_sql)
    db.close()

def update_stock_portfolio_buy(portfolioID, stockName, amount, price):
    db = DatabaseConnection()
    response = db.execute(f"""SELECT * FROM Stock_portfolio 
                            WHERE StockName = '{stockName}' 
                            AND PortfolioID = {portfolioID};""")
    if len(response) == 0:
        # need to add stock portfolio entry
        add_stock_sql = f"""
        INSERT INTO Stock_portfolio (StockName, PortfolioID, amount, current_price, average_price, pl)
        VALUES ('{stockName}', '{portfolioID}', {amount}, {price}, {price}, {0});
        """
        db.execute(add_stock_sql)
    else:
        # Calculate New Average Price
        total_amount = response[0][2]
        total_price = response[0][3] * total_amount
        new_total_amount = total_amount + amount
        new_total_price = total_price + (amount * price)
        new_average_price = new_total_price / new_total_amount
        new_pl = (new_total_amount*price) - (new_total_amount*new_average_price)
        
        modify_sql = f"""
            UPDATE Stock_portfolio 
            SET 
                amount = {new_total_amount},
                current_price = {price},
                average_price = {new_average_price},
                pl = {new_pl}
            WHERE
                PortfolioID = {portfolioID}
            AND
                StockName = '{stockName}';
            """
        db.execute(modify_sql)

def check_stock_portfolio(portfolioID, stockName):
    db = DatabaseConnection()
    response = db.execute(f"""SELECT * FROM Stock_portfolio 
                            WHERE StockName = '{stockName}' 
                            AND PortfolioID = {portfolioID}
                            AND amount > 0;""")
    if len(response) == 0:
        return 0
    else:
        return int(response[0][2])

def update_stock_portfolio_sell(portfolioID, stockName, amount, price):
    db = DatabaseConnection()
    response = db.execute(f"""SELECT * FROM Stock_portfolio 
                            WHERE StockName = '{stockName}' 
                            AND PortfolioID = {portfolioID};""")
    print("remaining stock:",response[0][2]-amount)
    if len(response) == 0:
        return "Error: Stock doesn't exist"
    
    elif (response[0][2]-amount) <= 0:

        # Delete the stock from the porfolio if its amount reaches 0
        # Next check if the stock is not in any other portfolio
        # If the stock is not in any other portfolio, delete it from the Stocks table

        sql1 = f"""
        DELETE FROM Stock_portfolio 
        WHERE StockName = '{stockName}';
        """
        sql2 = f"""
            SELECT *
            FROM Stock_portfolio
            WHERE StockName = '{stockName}';
        """
        sql3 = f"""
            DELETE FROM Stocks
            WHERE StockName = '{stockName}';
        """
        db.execute(sql1)
        response = db.execute(sql2)
        if len(response) == 0:
            response = db.execute(sql3)
        db.close()

    else:
        # Calculate New Average Price
        total_amount = response[0][2]
        total_price = response[0][3] * total_amount
        new_total_amount = total_amount - amount   
        new_total_price = total_price - (amount * price)
        new_average_price = new_total_price / new_total_amount
        new_pl = (new_total_amount*price) - (new_total_amount*new_average_price)
        modify_sql = f"""
            UPDATE Stock_portfolio 
            SET 
                amount = {new_total_amount},
                current_price = {price},
                average_price = {new_average_price},
                pl = {new_pl}

            WHERE
                PortfolioID = {portfolioID}
            AND
                StockName = '{stockName}';
            """
        db.execute(modify_sql)
        db.close()


def buy_stock(stockName, portfolioID, amount):
    """
    - Takes stock name, portfolio id, amount of stock. (Done)
    - Gets Portfolio if it exists else error message. (Open)
        - Is the Error Message Necessary? Isn't a portfolio generated for all users?
        - If it is, is the User notified of the Error Message? How is it handled?
    - Checks if Quote exists and gets current price if exists. (Open)
        - Error Message needs to be incorporated in Front-End somehow
    - Checks if portfoli credit > (amount*stockname price) (Open)
        - Error Message needs to be incorporated in Front-End somehow
    write stockname to database Done
    write to database: portfoli credit - (amount*stockname current price) Done
    check Stock_portfolio to see if user already owns stock and is buying more, if so modifiy existing entry
    else create new entry in stock portfolio
    """

    # Get portfolio
    portfolio = get_portfolio(portfolioID)
    if portfolio is None:
        return "Error: Portfolio doesn't Exist"
    
    # Gets Quote through API Call
    try:
        current_quote = get_current_quote(stockName)
    except finnhub.FinnhubAPIException as e:
        if e.code == 429: # if we exceed 30 API Requests Per Minute
            return "Error: Too many API Requests. Please wait a minute before buying or selling"

    # Handles Wrong Stockname Case
    if current_quote == {'c': 0, 'd': None, 'dp': None, 'h': 0, 'l': 0, 'o': 0, 'pc': 0, 't': 0}:
        return f"Error: {stockName} not found"
    
    # Gets Price from Quote    
    price = float(current_quote["c"])

    # Checks if User has enough Credit
    porfolio_credit = portfolio[2]
    total_cost = amount * price
    if total_cost >  porfolio_credit:
        return "Error: Insuffient Credit"
    
    # Add stock to database if it doesn't already exist
    add_stock(stockName)

    # Update Portfolio Credit
    new_credit = porfolio_credit - total_cost
    modify_portfolio(portfolioID, new_credit)

    # Buy stock
    update_stock_portfolio_buy(portfolioID, stockName, amount, price)
    return "Successfully purchased Stock!"

def sell_stock(stockName, portfolioID, amount):
    """
    - Takes stock name, portfolio id, amount of stock. (Done)
    - Check portfolio exist and get if exists else error message. (Open)
        - Link Error to Frontend somehow
    - Check if a specific stock exists in portfolio and how much. (Open)
        - Link Error to Frontend somehow
    - Store current price if exists and give error others. (Open)
        - Link Error to Frontend somehow
    - Write to database: portfolio credit + (amount*stockname current price) (Done)
    - Modify existing entry by amount sold (Done)
    """
    # Get portfolio
    portfolio = get_portfolio(portfolioID)
    if portfolio is None:
        return "Error: Portfolio doesn't Exist"
    
    db = DatabaseConnection()
    response = db.execute(f"""SELECT * FROM Stock_portfolio 
                            WHERE StockName = '{stockName}' 
                            AND PortfolioID = {portfolioID};""")
    print("db response:", response)
    if len(response) == 0:
        return "Stock doesn't exist"
    amount_owned = response[0][2] 
    db.close()

    if (amount_owned - amount) < 0:
        return "Error: Shorts are not Allowed"
    
    # Gets Quote through API Call
    try:
        current_quote = get_current_quote(stockName)
    except finnhub.FinnhubAPIException as e:
        if e.code == 429: # if we exceed 30 API Requests Per Minute
            return "Error: Too many API Requests. Please wait a minute before buying or selling"

    # Handles Wrong Stockname Case
    if current_quote == {'c': 0, 'd': None, 'dp': None, 'h': 0, 'l': 0, 'o': 0, 'pc': 0, 't': 0}:
        return f"Error: {stockName} not found"
    
    # Gets Price from Quote    
    price = float(current_quote["c"])

    # Update Portfolio Credit
    porfolio_credit = portfolio[2]
    new_credit =  porfolio_credit + (amount*price)
    modify_portfolio(portfolioID, new_credit)

    # Sell Stock
    update_stock_portfolio_sell(portfolioID, stockName, amount, price)
    return "Successfully sold Stock!"

if __name__ == "__main__":
    """
    Will only run if file is run directly.
    Meant for testing

    Tests buying and selling functionality
    """
    db = DatabaseConnection()

    # Testing New API

    # current_quote = get_current_quote("AAPL")
    # print(current_quote)
    # price = float(current_quote["c"])
    # print(price)
    # current_quote = get_current_quote("Whatever")
    # print(current_quote)
    # if current_quote == {'c': 0, 'd': None, 'dp': None, 'h': 0, 'l': 0, 'o': 0, 'pc': 0, 't': 0}:
    #     print("0")

    # Check DB
    print(db.execute(f"SELECT * FROM Portfolios WHERE PortfolioID = 1"))

    print("buying:  ")
    # Actual Buying

    for x in range(35):
        buy_stock("GOOGL", 1, 5)
    buy_stock("AAPL", 1, 7)


    # Check New Credit
    print(db.execute("SELECT * FROM Portfolios WHERE PortfolioID = 1"))
    # Check New Stock Amount
    print(db.execute("SELECT * FROM Stock_portfolio WHERE PortfolioID = 1"))

    print("selling:  ")
    # Actual Selling
    sell_stock("GOOGL", 1, 3)
    sell_stock("AAPL", 1, 2)
      
    # Check New Credit
    print(db.execute("SELECT * FROM Portfolios WHERE PortfolioID = 1"))
    # Check New Stock Amount
    print(db.execute("SELECT * FROM Stock_portfolio WHERE PortfolioID = 1"))
    
    db.close()