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
            self.db = MySQLdb.Connect(host="sql8.freesqldatabase.com", user="sql8637257", password="1NWfhSLf2g")

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
        cursor.execute("USE sql8637257;", vars)
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
    db.setup_database() # This line of code runs setup_database.sql
    # add_user_sql = """
    # INSERT INTO Users (username, email, password)
    # VALUES ('abhinav03', 'abhinav.akkena@student.manchester.ac.uk', 'mineman125');
    # """
    # db.execute(add_user_sql)
    # response = db.execute("SELECT UserID FROM Users WHERE username = 'abhinav03';")
    # userID = response[0][0]
    # add_profile_sql = f"""
    # INSERT INTO Portfolios (UserID, credit)
    # VALUES ({userID}, 100000);
    # """
    # db.execute(add_profile_sql)
    print(db.execute("SELECT * FROM Portfolios"))