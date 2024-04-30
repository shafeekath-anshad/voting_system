from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from sqlalchemy import delete, update

app = Flask(__name__)

app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shafeekkath'
app.config['MYSQL_DB'] = 'voting_system'

mysql = MySQL(app)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_register WHERE username = % s AND password = % s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('user_page.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'mobile' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        mobile = request.form['mobile']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_register WHERE username = % s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not re.match(r'[A-Za-z0-9]+', mobile):
            msg = 're enter mobile number !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user_register VALUES (NULL, % s, % s,% s,% s)',
                           (username, password, email, mobile,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/add_candidates', methods=['GET', 'POST'])
def add_candidates():
    msg = ''
    if request.method == 'POST' and 'candidate' in request.form and 'address' in request.form and 'mobile' in request.form and 'email' in request.form:
        candidate = request.form['candidate']
        address = request.form['address']
        email = request.form['email']
        mobile = request.form['mobile']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM candidate WHERE candidate = % s', (candidate,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', candidate):
            msg = 'Username must contain only characters and numbers !'
        elif not re.match(r'[A-Za-z0-9]+', mobile):
            msg = 're enter mobile number !'
        elif not candidate or not mobile or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO candidate VALUES (NULL, % s, % s,% s,% s)',
                           (candidate, address, email, mobile,))
            mysql.connection.commit()
            msg = 'candidates are added !'
    elif request.method == 'POST':
        msg = 'Please add the candidates for election!'
    return render_template('add_candidates.html', msg=msg)


@app.route('/view_candidates')
def view_candidates():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM candidate")
    data = cursor.fetchall()

    return render_template('view_candidates.html',value=data)


@app.route('/update')
def update():
    return render_template('update.html')


@app.route('/delete')
def delete():
    return render_template('delete.html')


@app.route('/vote')
def vote():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM candidate")
    data = cursor.fetchall()
    return render_template('vote.html', value=data)


if __name__ == '__main__':
    app.run(debug=True)
