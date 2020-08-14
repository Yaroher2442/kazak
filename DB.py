import sqlite3
from sqlite3 import Error
import os,uuid
 
class Database(object):
    """docstring for Database"""
    def __init__(self,connection):
        super(Database, self).__init__()
        self.connect=connection
        self.db_direction=os.path.join(os.getcwd(),'db','data_file.db')
    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_direction)
            self.connect=conn
            return conn
        except Error as e:
            print(e)     
        return conn      
    def create_table(self,create_table_sql):
        try:
            conn=self.connect
            c = conn.cursor()
            c.execute(create_table_sql)
            return c
        except Error as e:
            print(e)
    def insert_User(self,data):
        try:
            conn=self.connect
            c = conn.cursor()
            c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)"
                    ,data)
            print('insert_User_OK')
            conn.commit()
            # (u_id,email,password,name,surname)
        except Error as e:
            print(e)
    def find_user(self,email):
        try:
            conn=self.connect
            c = conn.cursor()
            res=c.execute("SELECT * From users WHERE email=?",(email,))  
            results = c.fetchall()
            if results==[]:
                return False
            else:
                return results
        except Error as e:
            print(e)

def main():
    db=Database('123')
    db.create_connection()

    sql="""CREATE TABLE `Сourts` (
    `c_id` TEXT NULL  DEFAULT NULL,
    `u_id` TEXT NULL DEFAULT NULL,
    ` initials` TEXT NULL DEFAULT NULL,
    `date` TEXT NULL DEFAULT NULL,
    `time` TEXT NULL DEFAULT NULL,
    `judge` TEXT NULL DEFAULT NULL,
    `tribunal` TEXT NULL DEFAULT NULL,
    `Instance` TEXT NULL DEFAULT NULL,
    `comment` TEXT NULL DEFAULT NULL,
    PRIMARY KEY (`c_id`)
    );"""

    # sql_file = open("shema.sql")
    # sql_as_string = sql_file.read()
    # db.create_connection().executescript(sql_as_string)
    db.create_table(sql)
    # print(uuid.uuid4())
    # db.insert_User(tuple([str(uuid.uuid4()),1,1,1]))
    print(db.find_user('qwe'))
if __name__ == '__main__':
    main()

