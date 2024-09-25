CREATE DATABASE IF NOT EXISTS Financial;
USE Financial;
CREATE TABLE IF NOT EXISTS ReceiptSnatcher(
    item VARCHAR(32) NOT NULL,
    -- price = +/-0000.00
    price DECIMAL(4,2) NOT NULL
);

