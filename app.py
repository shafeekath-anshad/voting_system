from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import mysql.connector
import re
from flask import abort
import logging
from sqlalchemy import update, delete

app = Flask(__name__)

app.secret_key = 'your_secret_key'

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="shafeekkath",
    database="voting_system"
)
cursor = conn.cursor()



@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor.execute('SELECT username, password FROM user_register')
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True

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

        cursor.execute("SELECT * FROM user_register")
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
            conn.commit()
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
            conn.commit()
            msg = 'candidates are added !'
    elif request.method == 'POST':
        msg = 'Please add the candidates for election!'
    return render_template('add_candidates.html', msg=msg)


@app.route('/view_candidates')
def view_candidates():
    cursor.execute("SELECT * FROM candidate")
    data = cursor.fetchall()

    return render_template('view_candidates.html', data=data)


@app.route('/update')
def update():
    return render_template('update.html')


@app.route('/delete')
def delete():
    return render_template('delete.html')


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        try:
            candidate_id = request.form['candidate']
        except ValueError:
            abort(400, "Invalid candidate ID")
        try:
            cursor.execute("UPDATE candidate SET votes = votes + 1 WHERE id = %s", (candidate_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            abort(500, f"Failed to update vote count: {str(e)}")
        return redirect(url_for('results'))
    else:
        try:
            cursor.execute("SELECT id, candidate FROM candidate")
            candidates = cursor.fetchall()
        except Exception as e:
            logging.error(f"Failed to fetch candidates: {str(e)}")
            abort(500, "Internal Server Error")
        return render_template('vote.html', candidates=candidates)

@app.route('/results')
def results():
    # Fetch candidates and their votes from the database
    cursor.execute("SELECT candidate, votes FROM candidate ORDER BY votes DESC")
    results = cursor.fetchall()
    return render_template('results.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
