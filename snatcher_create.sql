CREATE DATABASE IF NOT EXISTS Financial;
USE Financial;
CREATE TABLE IF NOT EXISTS ReceiptSnatcher(
    business_name VARCHAR(32) NOT NULL,
    transaction_date DATE NOT NULL,
    item VARCHAR(32) NOT NULL,
    -- price = +/-0000.00
    price DECIMAL(4,2) NOT NULL,
    quantity TINYINT UNSIGNED NOT NULL,
    -- CONSTRAINT ReceiptSnatcher_unique UNIQUE(business_name, transaction_date, item, price)
    CONSTRAINT ReceiptSnatcher_pk PRIMARY KEY(business_name, transaction_date, item, price)
);
CREATE TABLE IF NOT EXISTS ReceiptSnatcher_ML(
    business_name VARCHAR(32) NOT NULL,
    parsedItem VARCHAR(32) NOT NULL,
    correctedItem VARCHAR(32) NOT NULL,
    parsedPrice DECIMAL(4,2) NOT NULL,
    correctedPrice DECIMAL(4,2) NOT NULL
);

