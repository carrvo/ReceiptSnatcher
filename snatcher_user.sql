-- https://dev.mysql.com/doc/refman/8.4/en/grant.html
GRANT
-- https://dev.mysql.com/doc/refman/8.4/en/privileges-provided.html#priv_select
    -- SELECT,
-- https://dev.mysql.com/doc/refman/8.4/en/privileges-provided.html#priv_insert
    INSERT
    ON TABLE Financial.ReceiptSnatcher
    TO '{username}'@'localhost';

GRANT
    INSERT
    ON TABLE Financial.ReceiptSnatcher_ML
    TO '{username}'@'localhost';

