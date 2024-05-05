from flask import Flask, render_template, request, redirect, url_for, session

import MySQLdb.cursors
import mysql.connector
from flask_mysqldb import MySQL
import re
from flask import abort
import logging
from sqlalchemy import update, delete

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shafeekkath'
app.config['MYSQL_DB'] = 'voting_system'

mysql = MySQL(app)

app.secret_key = 'your_secret_key'





@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_register WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        mobile = request.form['mobile']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO user_register(username, password,email,mobile) VALUES (%s, %s,%s,%s)', (username, password,email,mobile))

        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/add_candidates', methods=['GET', 'POST'])
def add_candidates():
    msg = ''
    if request.method == 'POST':
        candidate = request.form['candidate']
        address = request.form['address']
        email = request.form['email']
        mobile = request.form['mobile']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO candidate(candidate, address,email,mobile) VALUES (%s, %s,%s,%s)',
                       (candidate, address, email, mobile))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('view_candidates'))

    return render_template('add_candidates.html', msg=msg)


@app.route('/view_candidates')
def view_candidates():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM candidate")
    candidates = cursor.fetchall()
    cursor.close()

    return render_template('view_candidates.html', candidates=candidates)


@app.route('/view_candidates/update_candidate/<int:id>', methods=['GET', 'POST'])
def update_candidate(id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        candidate = request.form['candidate']
        address = request.form['address']
        email = request.form['email']
        mobile = request.form['mobile']
        cursor.execute("UPDATE candidate SET candidate = %s, address = %s, email = %s, mobile = %s WHERE id = %s", (candidate, address,email,mobile, id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('view_candidates'))
    else:
        cursor.execute("SELECT id, candidate, address, email, mobile FROM candidate WHERE id = %s", (id,))
        candidate = cursor.fetchone()
        cursor.close()
        return render_template('update_candidate.html', candidate=candidate)


@app.route('/view_candidates/delete/<int:id>', methods=['POST'])
def delete_candidate(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM candidate WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('view_candidates'))


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        try:
            candidate_id = int(request.form['candidate'])  # Ensure candidate_id is an integer
        except ValueError:
            abort(400, "Invalid candidate ID")
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE candidate SET votes = votes + 1 WHERE id = %s", (candidate_id,))
            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            logging.error(f"Failed to update vote count: {str(e)}")
            abort(500, "Internal Server Error")
        return redirect(url_for('results'))  # Redirect to an existing route
    else:
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT id, candidate FROM candidate")
            candidates = cursor.fetchall()
        except Exception as e:
            logging.error(f"Failed to fetch candidates: {str(e)}")
            abort(500, "Internal Server Error")
        return render_template('vote.html', candidates=candidates)

@app.route('/results')
def results():
    # Fetch candidates and their votes from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT candidate, votes FROM candidate ORDER BY votes DESC")
    results = cursor.fetchall()
    return render_template('results.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
