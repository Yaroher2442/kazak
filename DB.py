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

    def insert_tables(self,table_name,data):
        try:
            conn=self.connect
            c = conn.cursor()
            if table_name == 'Affairs':
            	c.execute("INSERT INTO Affairs VALUES (?,?,?,?,?,?,?,?,?,?,?)"
                    ,data)
            if table_name == 'Bankruptcy':
            	c.execute("INSERT INTO Bankruptcy VALUES (?,?,?)"
                    ,data)
            if table_name == 'Enforcement_proceedings':
            	c.execute("INSERT INTO Enforcement_proceedings VALUES (?,?,?,?,?)"
                    ,data)
            if table_name == 'Litigation':
            	c.execute("INSERT INTO Litigation VALUES (?,?,?,?)"
                    ,data)
            if table_name == 'Non_judicial':
            	c.execute("INSERT INTO Non_judicial VALUES (?,?,?)"
                    ,data)
            if table_name == 'Pre_trial_settlement':
            	c.execute("INSERT INTO Pre_trial_settlement VALUES (?,?,?)"
                    ,data)
            if table_name == 'Сourts':
            	c.execute("INSERT INTO Сourts VALUES (?,?,?,?,?,?,?,?,?)"
                    ,data)
            print('insert_tables_OK')
            conn.commit()
        except Error as e:
            print(e)

    def get_join_table(self,join_table):
        try:
            conn=self.connect
            c = conn.cursor()
            res=c.execute("SELECT * FROM Affairs as a JOIN {} as l ON a.t_id = l.t_id".format(join_table))  
            results = c.fetchall()
            if results==[]:
                return False
            else:
                dela_list=[]
                for i in results:
                    dela_list.append(list(i[2:7])+list(i[12:])+list(i[7:11]))
                return dela_list
        except Error as e:
            print(e)


def main():
    db=Database('123')
    db.create_connection()

    # sql_file = open("shema.sql")
    # sql_as_string = sql_file.read()
    # db.create_connection().executescript(sql_as_string)

    # db.create_table(sql)
    # print(uuid.uuid4())

    db.insert_tables('Affairs',
    	tuple([str(uuid.uuid4()),'user_id','Петров','Судебное дело'
    					,'Антимонопольное право','М.А. Девятирикова','Е.А. Норенко'
    					,'Соглашение.pdf','Счёт.pdf'
    					,'сайт','Подготовлен отзыв - 12.08.2020']))


    '''SELECT * FROM Affairs as a
		JOIN Litigation as l ON a.t_id = l.t_id'''

    # db.insert_tables('Litigation',
    # 	tuple(['15bf0436-a694-4b40-9fd5-8df911115786'
    # 		,'А40-23089/2020'
    # 		,'АСГМ'
    # 		,'Васичикин	'
    # 		]))
    data=db.get_join_table('Litigation')
    print(data)
    # print(data)
    
    # print(db.find_user('qwe'))
if __name__ == '__main__':
    main()

