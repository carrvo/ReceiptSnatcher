CREATE DATABASE IF NOT EXISTS Financial;
USE Financial;
CREATE TABLE IF NOT EXISTS ReceiptSnatcher(
    transaction_date DATE NOT NULL,
    item VARCHAR(32) NOT NULL,
    -- price = +/-0000.00
    price DECIMAL(4,2) NOT NULL
    -- CONSTRAINT ReceiptSnatcher_unique UNIQUE(transaction_date, item, price)
    CONSTRAINT ReceiptSnatcher_pk PRIMARY KEY(transaction_date, item, price)
);

