import sqlite3
import os

class DB(object):
    DB_FILE_NAME = 'url.db'
    def __init__(self , *args , **kwargs):
        super(DB, self).__init__(*args, **kwargs)
        self.conn = sqlite3.connect('url.db')
        print('db created')

    def create_db(self , name , statement):
        try:
            self.cursor.execute('create table ' + name + ' ' + statement)
        except sqlite3.OperationalError:
            print('the table exists')
    def insert(self , name , keys , values):
        self.cursor.execute('insert into ' + name + ' ' + keys + ' values ' + values)

    def query(self , statement):
        self.cursor.execute(statement)

    def query_count(self , name):
        self.cursor.execute('select count(*) from ' + name)
        values = self.cursor.fetchall()
        return values[0][0]

    def commit(self):
        self.cursor.close()
        self.conn.commit()
    
    def start(self):
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()
        
def test():
    db = DB()
    db.start()
    db.create_db( 'url' ,'(id varchar(20) primary key , md5 varchar(32)  unique ,name varchar(50) , url varchar(500))') 
    db.insert('url' , '(md5 ,name , url)' , '(\'8a0sdf8a0s\' , \' 1.jpg\' , \'http:baidu.com.jpg\')')
    print(db.query_count('url'))
    db.commit()
    #db.start()
    #db.query('select * from url where name = \'1.jpg\'')
    #db.commit()

if __name__ == '__main__':
    test()