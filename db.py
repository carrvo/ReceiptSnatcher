"""
https://dev.mysql.com/doc/connector-python/en/connector-python-examples.html
"""

from mysql import connector as mysql

class DB:
    MySQLUrl = 'my.sql.local'
    SnatcherDB = 'Financial'

    SnatcherTable = 'ReceiptSnatcher'
    
    def __init__(self):

        '''
        if (!isset($_SERVER['PHP_AUTH_USER'])) {
	        header('WWW-Authenticate: Basic realm="$ServerReportedDomain"');
	        header('HTTP/1.0 401 Unauthorized');
	        echo '401 Unauthorized';
	        exit;
        }
        '''

        ### TODO: replace
        self.auth_user = ''
        self.auth_pass = ''
        '''
        $_SESSION["conn"] = new mysqli($MySQLUrl, $_SERVER['PHP_AUTH_USER'], $_SERVER['PHP_AUTH_PW'], $dbname);
        '''

    def __enter__(self):
        self.connection = mysql.connect(host=DB.MySQLUrl,
                                        user=self.auth_user,
                                        password=self.auth_pass,
                                        database=DB.SnatcherDB,
                                        use_pure=True)
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.connection.close()

    def insert(self, rows):
        with self.connection.cursor() as cursor:
            row_ids = []
            for row in rows:
                cursor.execute('INSERT INTO ReceiptSnatcher(item, price) VALUES(%(correctedItem)s, %(correctedPrice)s)', row)
                row_ids.append(cursor.lastrowid)
            self.connection.commit()
            return row_ids

    def select(self):
        with self.connection.cursor() as cursor:
            cursor.execute('select * from receiptsnatcher')
            for row in cursor:
                yield row

