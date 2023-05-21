import os
from flask import Flask, request, render_template
import mysql.connector
import sys

class DBManager:
    def __init__(self, database='example', host="db", user="root", password_file=None):
        pf = open(password_file, 'r')
        self.connection = mysql.connector.connect(
            user=user, 
            password=pf.read(),
            host=host, # name of the mysql service as set in the docker compose file
            database=database,
            auth_plugin='mysql_native_password'
        )
        pf.close()
        self.cursor = self.connection.cursor()
    
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
        # query = "select name from users where (name='" + login + "' and password='" + psw + "');"     ### ' or 1=1)#
        # self.cursor.execute(query)
        query = "select name from users where ( name = %s and password = %s );" # prepared Statement
        self.cursor.execute(query, (login, psw))
        rec = []
        for c in self.cursor:
            rec.append(c[0])
        return rec

    def delete_blog(self):
        self.cursor.execute('delete from blog where id != 1')

server = Flask(__name__)
conn = None

@server.route('/login')
def my_form():
    return render_template('login2.html')

@server.route('/login', methods=['POST'])
def my_form_post():
    global conn
    if not conn:
        conn = DBManager(password_file='/run/secrets/db-password')
        conn.populate_db()

    login = request.form['login']
    psw = request.form['password']
    result = conn.check_login(login,psw)
    print(result, file=sys.stdout)
    if len(result) > 0:
        return "zalogowano jako " + str(result[0])
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
