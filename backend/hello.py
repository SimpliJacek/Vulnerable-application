import os
from flask import Flask, request, render_template
import mysql.connector
import sys
import sqlalchemy as db



class DBManager:
    def __init__(self, database='example', host="db", user="root", password_file=None):
        pf = open(password_file, 'r')
        pw = pf.read()
        self.connection = mysql.connector.connect(
            user=user,
            password=pw,
            host=host, # name of the mysql service as set in the docker compose file
            database=database,
            auth_plugin='mysql_native_password'
        )
        db_connection = db.create_engine('mysql+mysqlconnector://'+user+':'+pw+'@'+host+':3306/' + database, connect_args={'auth_plugin': 'mysql_native_password'})
        global c
        c = db_connection.connect()
        metadata_obj = db.MetaData()
        pf.close()
        self.cursor = self.connection.cursor()
        global passwd
        self.cursor.execute('DROP TABLE IF EXISTS users')
        passwd = db.Table('users', metadata_obj,                                    
            db.Column('id', db.Integer, primary_key=True),  
            db.Column('name', db.String(15)),                    
            db.Column('password', db.String(15))        
        )
        metadata_obj.create_all(db_connection)
        stmt = db.insert(passwd).values(id='1',name='admin',password='password')
        stmt.compile()
        c.execute(stmt)
        c.commit()

        
        
    
    def populate_db(self):
        self.cursor.execute('DROP TABLE IF EXISTS users')
        self.cursor.execute('CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), password VARCHAR(255))')
        self.cursor.execute('INSERT INTO users (id, name, password) VALUES (1, "admin", "p@ssw0rd");')
        self.cursor.execute('INSERT INTO users (id, name, password) VALUES (2, "gosia", "haslo");')
        self.connection.commit()


        
    def populate_blog(self):
        self.cursor.execute('DROP TABLE IF EXISTS blog')
        self.cursor.execute('CREATE TABLE blog (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255))')
        self.cursor.executemany('INSERT INTO blog (id, title) VALUES (%s, %s);', [(i, 'Blog post #%d'% i) for i in range (1,5)])
        self.connection.commit()
    
    
    def query_titles(self):
        self.cursor.execute('SELECT title FROM blog')
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec

    def check_login(self, login, psw):
        global c
        # query = "select name from users where (name='" + login + "' and password='" + psw + "');"     ### ' or 1=1)#
        # self.cursor.execute(query)
        # query = "select name from users where ( name = %s and password = %s );" # prepared Statement
        # self.cursor.execute(query, (login, psw))
        query = db.select(passwd).where((passwd.c.name == login) & (passwd.c.password == psw))
        return c.execute(query)
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec

    def delete_blog(self):
        self.cursor.execute('delete from blog where id != 1')

server = Flask(__name__)
conn = None
db_connection = None
metadata_obj = None
global c

@server.route('/login')
def my_form():
    return render_template('login2.html')

@server.route('/login', methods=['POST'])
def my_form_post():
    global conn
    if not conn:
        conn = DBManager(password_file='/run/secrets/db-password')
        # conn.populate_db()

    login = request.form['login']
    psw = request.form['password']
    result = conn.check_login(login,psw)
    print(result, file=sys.stdout)
    rezultat = result.first()
    if rezultat is not None:
        return "zalogowano jako " + str(rezultat[1])
    else:
        return "nie mozna zalogowac"


@server.route('/')
def listBlog():
    global conn
    if not conn:
        conn = DBManager(password_file='/run/secrets/db-password')
        conn.populate_blog()
    rec = conn.query_titles()

    response = '<p> BLOG <p> \n'
    for c in rec:
        response = response  + '<div>   Hello  ' + c + '</div>'
    return response


@server.route('/delete') #, methods=['POST'])
def delete():
    global conn
    if not conn:
        conn = DBManager(password_file='/run/secrets/db-password')
        conn.populate_blog()
    # csrfToken = request.form['CSRFToken']
    # if csrfToken == None or csrfToken != "dd1aaf26c557685cc37f93f53a2b6befb2c2e679f5ace6ec7a26d12086f358be":
    #     return "próba CSRF"
    conn.delete_blog()
    return ('',204)

@server.route('/normalna_strona_internetowa')
def kotki():
    return render_template('kotki.html')

@server.route('/naprawiona_strona_internetowa')
def kotki2():
    return render_template('kotki2.html')


if __name__ == '__main__':
    server.run()
