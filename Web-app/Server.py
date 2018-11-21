import os
from sqlalchemy import *
from flask import Flask, request, render_template, g, redirect, Response, flash, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from Database import engine
from User import User

# set app and login system
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.secret_key = 'I love database'


# Get current user's information
@login_manager.user_loader
def load_user(s_id):
    email = str(s_id)
    query = '''select * from usr where email like\'''' + email + '\''
    cursor = g.conn.execute(query)
    user = User()
    for row in cursor:
        user.name = str(row.name)
        user.email = str(row.email)
        break
    return user


# Prepare the page
@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None


@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception:
    pass


# @The function for user login
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    page = 'login'
    if request.method == 'POST':

        # Obtain input value and pass to User object
        email = str(request.form['email']).strip()
        password = str(request.form['password']).strip()
        user = User(email, password)
        user.user_verify()

        if not user.valid:
            error = 'Invalid login information'
        else:
            session['logged_in'] = True
            login_user(user)
            print current_user.id
            flash('You were logged in')
            return redirect(url_for('user_home_page'))

    return render_template('login.html', error=error, page=page)


# @This function is for user sign-up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    page = 'signup'
    if request.method == 'POST':
        name = str(request.form['username']).strip()
        password = str(request.form['password']).strip()
        email = str(request.form['email']).strip()
        print name, password, email
        newuser = User(email, password, name)
        newuser.insert_new_user()
        if not newuser.valid:
            error = 'Invalid user information, please choose another one'
        else:
            session['logged_in'] = True
            login_user(newuser)
            flash('Thanks for signing up, you are now logged in')
            return redirect(url_for('user_home_page'))
    return render_template('signup.html', error=error, page=page)


@app.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    logout_user()
    return redirect(url_for('login'))


'''
This part is the User Homepage, add app functions here
Modify user_home_page.html as well
'''


@app.route("/", methods=["GET", "POST"])
@login_required
def user_home_page():
    message1 = "Welcome back!"
    message2 = "Current User: "+ current_user.name
    message3 = "Here is your home page"
    return render_template("user_home_page.html", message1=message1, message2=message2, message3=message3)


# @Search job with keyword
@app.route("/search", methods=["GET", "POST"])
@login_required
def search_vacancy():
    if request.method == 'POST':
        key = str(request.form['keyword']).strip()
        print key
        query = '''
        select j.name as name, v.aname as agency,
                v.uname as unit, v.sal_from as sfrom, 
                v.sal_to as sto, v.sal_freq as sfreq
        from vacancy as v inner join job as j on v.jid = j.jid
        where j.name like \'%''' + key + '%\' or j.pre_skl like \'%''' + key + '%\''
        cursor = g.conn.execute(text(query))  # !Very important here, must convert type text()
        job = []
        for row in cursor:
            job.append(row)
        data = job
        return render_template("search.html", data=data, keyword = key)
    return render_template("search.html")





if __name__ == '__main__':
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using

            python server.py

        Show the help text using

            python server.py --help

        """
        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()