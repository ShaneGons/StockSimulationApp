import MySQLdb
import os

USE_LOCAL_DATABASE = False
DB_LOGIN_FILE = "dblogin.txt"

class DatabaseConnection:
    def __init__(self):
        if USE_LOCAL_DATABASE:
            login = self.get_db_login_for_local()
            self.db = MySQLdb.Connect(host="dbhost.cs.man.ac.uk", user=login[0], password=login[1])
        else:
            self.db = MySQLdb.Connect(host="sql.freedb.tech", user="freedb_ShaneGons", password="gkK!dGb&6qv9&8!")

    def get_db_login_for_local(self):
        if not os.path.exists(DB_LOGIN_FILE):
            raise Exception("""You must create a file: dblogin.txt, and put in your login details for the uni database.
            The format should be as follows: the username should be on the first line and the password should be on the second.
            To create a database account, follow the instructions here: https://wiki.cs.manchester.ac.uk/index.php/Web_Dashboard/Database
            """)

        with open(DB_LOGIN_FILE) as file:
            user = file.readline().rstrip("\n")
            pwd = file.readline().rstrip("\n")
        
        return user, pwd

    def execute(self, sql, vars=()):
        cursor = self.db.cursor()
        cursor.execute("USE freedb_StockDB;", vars)
        # print("Executing: " + sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        # print("Result: " + str(result))
        # print("-"*50)
        cursor.close()
        self.db.commit()
        return result

    def setup_database(self):
        with open("setup_database.sql") as file:
            sql_code = file.read()

        cursor = self.db.cursor()
        # cursor.execute("USE xpstock;")
        cursor.execute(sql_code)
        result = cursor.fetchall()
        cursor.close()

    def close(self):
        self.db.close()
if __name__ == "__main__":
    db = DatabaseConnection()
    db.setup_database()
    print(db.execute("SELECT * FROM Portfolios"))