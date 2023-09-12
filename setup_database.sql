USE sql8637257;

DROP TABLE IF EXISTS Stock_portfolio;
DROP TABLE IF EXISTS Portfolios;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Stocks;

CREATE TABLE Users (
    UserID INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(45) NOT NULL,
    email VARCHAR(45) NOT NULL,
    password VARCHAR(128) NOT NULL);

CREATE TABLE Portfolios (
    PortfolioID INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    UserID INT(6) UNSIGNED,
    credit INT(12) ,
    public BOOLEAN,
    FOREIGN KEY (UserID) REFERENCES Users(UserID));

CREATE TABLE Stocks (
    StockName VARCHAR(30) NOT NULL PRIMARY KEY);

CREATE TABLE Stock_portfolio (
    StockName VARCHAR(30),
    PortfolioID INT(6) UNSIGNED,
    amount FLOAT(12) UNSIGNED,
    -- Added for Table of Portfolio
    average_price FLOAT(12),
    current_price FLOAT(12),
    pl FLOAT(12),
    -- End of Addition
    FOREIGN KEY (StockName) REFERENCES Stocks(StockName),
    FOREIGN KEY (PortfolioID) REFERENCES Portfolios(PortfolioID),
    PRIMARY KEY (StockName, PortfolioID));

INSERT INTO Stocks (StockName)
    VALUES ('AAPL');

INSERT INTO Users (username, email, password)
    VALUES ('abhinav03', 'abhinav.akkena@student.manchester.ac.uk', 'mineman125'),
     ('jay1', 'jay.hebblethwaite@student.manchester.ac.uk', 'pa55w0rd'),
     ('matthew12', 'matthew.richards-4@student.manchester.ac.uk', 'manguscarson');

INSERT INTO Portfolios (UserID, credit)
    VALUES (1, 100000),
     (2, 100000),
     (3, 100000);

INSERT INTO Stock_portfolio (StockName, PortfolioID, amount, average_price, current_price, pl)
    VALUES ('AAPL', 1, 9, 150.47, 150.47, 0),
     ('AAPL', 2, 6, 150.47, 150.47, 0),
     ('AAPL', 3, 18, 150.47, 150.47, 0);
