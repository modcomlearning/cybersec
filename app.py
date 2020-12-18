from datetime import timedelta
from urllib import response

from flask import Flask, render_template, session
from flask import request
import pymysql

# importing module
import logging

# Create and configure logger
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

#response.headers['X-Frame-Options'] = 'DENY'

app = Flask(__name__)
app.secret_key = "#$$sol15indra^nsPP@Rrrshshsh$$%%%%^^^^"

app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(seconds=10000)


# # Implement csrf token
# from flask_wtf.csrf import  CSRFProtect
# csrf = CSRFProtect(app)
# above code will generate a random token for each visitor

import hashlib, binascii, os
# This function receives a password as a parameter
# its hashes and salts using sha512 encoding
def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


# this function checks if hashed password is the same as
# provided password
def verify_password(hashed_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = hashed_password[:64]
    hashed_password = hashed_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == hashed_password



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        # # hash the password/ strength
        # # we first connect to localhost and soko_db
        conn = pymysql.connect("localhost", "root", "", "cs_db")

        # insert the records into the users tables
        cursor = conn.cursor()
        cursor.execute("select * from users where email = %s", (email))

        if cursor.rowcount == 1:

            # take me to a different route and create a session
            rows = cursor.fetchone()
            # get hashed password from db
            hashed_password = rows[1]

            # Provide the hashed password
            status = verify_password(hashed_password, password)
            if status ==True:
                # do session here

                session['key']  = email
                logger.info("Logged in ", email)
                # here we get the role of logged in user
                role = rows[3]
                # we store the role in a session
                session['role'] = role
                session.permanent = True
                # session.modified = True
                from flask import redirect
                return redirect('/home')
            else:
                # program a code to check record failures
                logger.info("Login failed")
                return render_template('login.html', msg="Login Failed")

        else:
            logger.info("The email does not exist")
            return render_template('login.html', msg="The email does not exist")

    else:
        return render_template('login.html')


# python, pycharm, XAMPP
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']
        # assuming there were more here like phone, credit card,

        import re
        # define a function to check password strength
        if (len(password) < 8):
            return render_template('signup.html', msg1="Must be eight characters")

        elif not re.search("[a-z]", password):
            return render_template('signup.html', msg1="Must have at least one small letters")

        elif not re.search("[A-Z]", password):
            return render_template('signup.html', msg1="Must have at least one capital letters")

        elif not re.search("[0-9]", password):
            return render_template('signup.html', msg1="Must have at least one number")

        elif not re.search("[_@#$]", password):
            return render_template('signup.html', msg1="Must have at least one symbol")
        else:
            # at this point, password is valid, we save to users table
            # we connect to database
            conn = pymysql.connect("localhost", "root", "", "cs_db")

            # insert email, password records into the users tables
            try:
                cursor = conn.cursor()
                cursor.execute("insert into users(email,password) values (%s,%s)", (email, hash_password(password)))
                logger.info("Saved successful")
                conn.commit()
                return render_template('signup.html', msg="Record Saved Succesfully")
            except:
                logger.critical("Failed to save")
                conn.rollback()
                return render_template('signup.html', msg="Record not Saved Succesfully")


    else:
        return render_template('signup.html')


# Restrict parts that should need user to login
from flask import redirect
@app.route('/home')
def home():
    if 'key' in session:
        # proceed with login here
        role = session['role']
        # if role != 'admin' :
        #     return redirect('/login')
        if role =='admin' or role =='user':
            return render_template('home.html')
        # Roles
        else:
            return redirect('/login')

    else:
        # Dont proceed
        return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('key',None)
    session.pop('role', None)
    return redirect('/login')



if __name__ == '__main__':
    app.debug = True
    app.run()