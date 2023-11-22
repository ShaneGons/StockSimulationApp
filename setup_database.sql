USE freedb_StockDB;

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

