from flask import Flask, render_template, session
from flask import request
import pymysql
app = Flask(__name__)



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
        cursor.execute("select * from users where email = %s and status = %", (email,))

        if cursor.rowcount == 1:
            # take me to a different route and create a session
            rows = cursor.fetchone()
            # get hashed password from db
            hashed_password = rows[1]
            # Provide the hashed password
            status = verify_password(hashed_password, password)
            if status ==True:
                return render_template('login.html', msg="Login Successful")
            else:
                return render_template('login.html', msg="Login Failed")

        else:
            return render_template('login.html', msg="The email does not exist")

    else:
        return render_template('login.html')




@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']

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
            cursor = conn.cursor()
            cursor.execute("insert into users(email,password) values (%s,%s)", (email, hash_password(password)))
            conn.commit()
            return render_template('signup.html', msg="Record Saved Succesfully")

    else:
        return render_template('signup.html')


if __name__ == '__main__':
    app.debug = True
    app.run()