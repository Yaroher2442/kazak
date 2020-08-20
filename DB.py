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
    def find_user_by_id(self,u_id):
        try:
            conn=self.connect
            c = conn.cursor()
            res=c.execute("SELECT alevel,name,surname,lastname From users WHERE id=?",(u_id,))  
            results = c.fetchall()
            if results==[]:
                return False
            else:
                return list(results[0])
        except Error as e:
            print(e)

    def get_all_users(self):
        try:
            conn=self.connect
            c = conn.cursor()
            res=c.execute("SELECT id,name,surname,lastname,alevel,email From users")  
            results = c.fetchall()
            if results==[]:
                return False
            else:
                return list(list(i) for i in results)
        except Error as e:
            print(e)

    def get_urists(self):
        try:
            conn=self.connect
            c = conn.cursor()
            res=c.execute("SELECT name,surname,lastname From users WHERE alevel = 'Пользователь'")  
            results = c.fetchall()
            if results==[]:
                return False
            else:
                return list(list(i) for i in results)
        except Error as e:
            print(e)

    def insert_tables(self,table_name,data):
        try:
            conn=self.connect
            c = conn.cursor()
            if table_name == 'Affairs':
            	c.execute("INSERT INTO Affairs VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
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
                    l_list=[results.index(i)+1]+[i[0]]+list(i[2:7])+list(i[13:])+list(i[7:12])
                    l_list.pop(3)
                    dela_list.append(l_list)
                return dela_list
        except Error as e:
            print(e)

    def delite_data(self,table_name,t_id):
        try:
            conn=self.connect
            c = conn.cursor()
            res=c.execute("""DELETE FROM {} WHERE t_id = ?""".format(table_name),(t_id,)) 
            conn.commit()
            print('Success_dell')
            return 'Success'
        except Error as e:
            print(e)
    def change_invoice_status(self,t_id,status):
        try:
            conn=self.connect
            c = conn.cursor()
            res=c.execute("""UPDATE Affairs SET Invoice_status = ? WHERE t_id = ?""", (status,t_id,)) 
            conn.commit()
            print('Success_change_invoice_status')
            return 'Success_change_invoice_status'
        except Error as e:
            print(e)

def main():
    db=Database('123')
    db.create_connection()

    print(db.get_all_users())
    print(db.get_urists())
    # sql_file = open("shema.sql")
    # sql_as_string = sql_file.read()
    # db.create_connection().executescript(sql_as_string)

    # db.create_table(sql)
    # print(uuid.uuid4())

    # db.insert_tables('Affairs',
    # 	tuple([str(uuid.uuid4()),'user_id','Петров','Судебное дело'
    # 					,'Антимонопольное право','М.А. Девятирикова','Е.А. Норенко'
    # 					,'Соглашение.pdf','Счёт.pdf'
    # 					,'сайт','Подготовлен отзыв - 12.08.2020']))


    '''SELECT * FROM Affairs as a
		JOIN Litigation as l ON a.t_id = l.t_id'''

    # db.insert_tables('Litigation',
    # 	tuple(['15bf0436-a694-4b40-9fd5-8df911115786'
    # 		,'А40-23089/2020'
    # 		,'АСГМ'
    # 		,'Васичикин	'
    # 		]))
    # data=db.get_join_table('Litigation')
    # print(data[0])
    # print(db.find_user_by_id('4d4ce653-f2ff-489a-b7ba-143e2f36c3f9'))
    # print(data)

    # db.delite_data('Litigation','49428310-dd33-4dc9-81f5-ab7a54a83374')
    # db.change_invoice_status('50920196-4170-4ea9-b4e7-d2d3ba90ac0f','#008000')
    # print(db.get_join_table('Litigation'))
    # print(db.find_user('qwe'))
if __name__ == '__main__':
    main()

