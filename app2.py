import os
from os.path import join, dirname, realpath

from flask import Flask, render_template, request, redirect, session

# we create a flask application parsing its name
app2 = Flask(__name__)

# We now want to create a session to identify each user
# We first generate a secret key used for encrypting the session. You can also import random  and use x= random.randit(0,5)
app2.secret_key = "sssss34567890hgffghjk(*&^%$#@#$%^&"

# we want to now upload Images and files
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/')  # create path where the image file will be saved
# specify allowed extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# configure upload folder in the app
app2.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app2.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024


# this function is used to check if the allowed image extensions has been met

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# we import pymysql
import pymysql


# make route aware of methods to be received
@app2.route('/addSheets', methods=['POST', 'GET'])
def addsheet():
    # We first have to check the methods sent either POST or Get so that we can extract the data sent. We do this by importing a module called request

    if request.method == 'POST':
        file = request.files['file']  # receive file
        title = request.form['title']
        sheet_number = request.form['sheetNumber']
        desc = request.form['description']
        tag = request.form['tag']

        # check if file is present and allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # save the file with its filename
            file.save(os.path.join(app2.config['UPLOAD_FOLDER'], filename))

        # once the file is saved, save the link to the db
        # now we want to save this data in the database hence we have to import pymysql as the connector to the sql -top
        connection = pymysql.connect("localhost", "root", "", "datasuit_db")

        # connection has true or false connection
        # create a cursor and use it to execute SQL --- Cursor helps to execute sql

        cursor = connection.cursor()

        sql = """INSERT INTO tbl_sheets(file,title,sheet_number,sheet_desc,tag) VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (filename, title, sheet_number, desc, tag))

        # commit/rollback -if the connection crashes before it commits, it should render back
        try:
            connection.commit()
            return redirect('/sheetsDashboard')
        except:
            connection.commit()
            return render_template('SheetsDashboard.html', msg="Error Occurred during transmission")

    else:
        return render_template('SheetsDashboard.html', msg2="Sorry, connection failed. Try again!")


@app2.route('/sheetsDashboard')
def sheets_dashboard():
    # first connect to the database using pymysql
    connection = pymysql.connect("localhost", "root", "", "datasuit_db")

    # we now use the cursor function to execute on the database
    cursor = connection.cursor()

    sql = """SELECT * FROM tbl_sheets ORDER BY edited_when DESC """  # shows records in descending order or use ASC

    cursor.execute(sql)

    rows = cursor.fetchall()  # rows can contain 0,1 or more rows

    # perform a row count
    if cursor.rowcount == 0:
        return render_template('SheetsDashboard.html', msg='No records')
    else:
        return render_template('SheetsDashboard.html', data=rows)


# make our routes return
@app2.route('/')
def main():
    return render_template('main_testing_components.html')


@app2.route('/register', methods=['POST', 'GET'])
def register():
    # We first have to check the methods sent either POST or Get so that we can extract the data sent. We do this by importing a module called request
    if request.method == 'POST':
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        email_add = request.form['email_add']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if password1 == "":
            return render_template('Registration_template.html', msg1="Empty password")
        elif password1 != password2:
            return render_template('Registration_template.html', msg2="!Passwords do not match")
        elif email_add == "":
            return render_template('Registration_template.html', msg3="Please enter a Valid email address")
        else:
            connection = pymysql.connect("localhost", "root", "", "datasuit_db")

            cursor = connection.cursor()

            sql = """INSERT INTO tbl_register(f_name, l_name, email_add, password) VALUES(%s, %s, %s, %s)"""

            # cursor() method is used to execute on sql
            # commit/rollback -if the connection crashes before it commits, it should render back

            # lets try and catch errors during commit and execution
            try:
                cursor.execute(sql, (f_name, l_name, email_add, password1))
                connection.commit()
                return redirect('/login')
            except:
                connection.commit()
                return render_template('Registration_template.html', msg5="Error Occurred during transmission")

    else:
        return render_template('Registration_template.html')


@app2.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email_add = request.form['email_add']
        password = request.form['password']

        connection = pymysql.connect("localhost", "root", "", "datasuit_db")

        cursor = connection.cursor()

        sql = """SELECT * FROM tbl_register WHERE email_add=%s AND password=%s """
        cursor.execute(sql, (email_add, password))

        if cursor.rowcount == 0:
            return render_template('login_template.html', msg6="unsuccessful Login. Check if you are registered")
        elif cursor.rowcount == 1:
            # session['key'] = email_add
            # rows = cursor.fetchall()
            # session['key1'] = rows[0]
            # session['key2'] = rows[3]
            # print(rows[3])
            return redirect('/projects')

        else:
            return render_template('login_template.html', msg6="Something went Wrong. sorry for the Inconvinience "
                                                               "with the system! We are trying to resolve the Issue. "
                                                               "Contact support at +254716681166 and "
                                                               " we will resolve the issue as soon as possible")
    else:
        return render_template('login_template.html')


@app2.route('/Dashboard')
def dashboard():
    return render_template('Dashboard.html')


@app2.route('/add_projects', methods=['POST', 'GET'])
def add_projects():
    # we want to protect the Projects templates with a session
    if 'key' in session:
        # pull out the key and get back your email and store that email in a variable called email
        # This helps you track who was in session when a certain activity was executed
        # you can render this email to the database to monitor various aspects
        # We use the email from the session to track what a specific user does.
        # i.e we can track individual products or projects and use that to make specific user profiles
        # also don't forget to add a column to cater for the email session in the database.
        email = session['key']

        if request.method == 'POST':
            project_name = request.form['project_name']
            project_code = request.form['project_code']
            project_status = request.form['project_status']
            project_location = request.form['project_location']

            connection = pymysql.connect("localhost", "root", "", "datasuit_db")

            cursor = connection.cursor()
            sql = """INSERT INTO tbl_projects (project_name, project_code, project_status, project_location, email_add) VALUES (%s, %s, %s, %s, %s)"""

            try:
                cursor.execute(sql, (project_name, project_code, project_status, project_location, email))
                connection.commit()
                return redirect("/Dashboard")
            except:
                connection.commit()
                return render_template('Projects.html', msg="Error during transimmission")

        else:
            return render_template('Projects.html', msg10=email)


    elif 'key' not in session:
        return redirect('/login')
    else:
        return redirect('/login')


@app2.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':

        project_name = request.form['search']
        project_code = request.form['search']


        # Validate your passwords
        # if project_name=="":

        connection = pymysql.connect("localhost", "root", "", "datasuit_db")

        cursor = connection.cursor()

        sql = """SELECT * FROM tbl_projects WHERE project_name=%s or project_code=%s"""

        # sql="""SELECT * FROM employees WHERE f_name=%s AND l_name=%s"""
        #  you can also use OR , LIKE to help in querying    --- Research further on this

        cursor.execute(sql, (project_name, project_code))

        # fetch rows
        rows = cursor.fetchall()  # rows can contain 0,1 or more rows

        # perform a row count
        if cursor.rowcount == 0:
            return render_template('search_results.html', msg='No records')
        else:
            return render_template('search_results.html', data=rows)

    else:  # shows the user the form for the first time --- for the first time it skips the POST and shows the user the template for the first time
        return render_template('Projects.html')


@app2.route('/products')
def products():
    connection = pymysql.connect("localhost", "root", "", "datasuit_db")

    cursor = connection.cursor()

    sql = """SELECT * FROM tbl_products """

    cursor.execute(sql)

    # fetch rows
    rows = cursor.fetchall()  # rows can contain 0,1 or more rows

    # perform a row count
    if cursor.rowcount == 0:
        return render_template('Products.html', msg='No records')
    else:
        return render_template('Products.html', data=rows)


@app2.route('/projects')
def projects():
    if 'key' in session:

        # you can check the session roles here
        # if not
        # check algorithms to encrypt passwords Bcrypt

        connection = pymysql.connect("localhost", "root", "", "datasuit_db")

        cursor = connection.cursor()

        sql = """SELECT * FROM tbl_projects WHERE email_add = %s  ORDER BY time_created DESC """  # shows records in descending order / ASC
        email = session['key']
        cursor.execute(sql, (email))

        # fetch rows
        rows = cursor.fetchall()  # rows can contain 0,1 or more rows

        # perform a row count
        if cursor.rowcount == 0:
            return render_template('Projects.html', msg='No update in Projects')
        else:
            return render_template('Projects.html', data=rows)

    elif 'key' not in session:
        return redirect('/login')
    else:
        return redirect('/login')

# make sure to add a logout link to the website to clear sessions
@app2.route('/logout')
def logout():
    # remove the key from the session
    session.pop('key', None)
    return redirect('/login')


if __name__ == '__main__':
    app2.run()

'''

to store data in the database you have to run the xampp server

to run xampp server in linux we run the following command in linux

sudo /opt/lampp/lampp start

then go to http://localhost/dashboard/phpmyadmin  to access the database

to host your application, host it in Heruku or python anywhere

'''
