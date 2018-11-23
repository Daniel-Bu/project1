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
            g.user = current_user.id
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
    message = "Welcome back! " + current_user.name
    if request.method == 'GET':
        query = '''
        select tmp.jid as id, tmp.name as name, tmp.type as type,
               tmp.sal_from as sfrom, tmp.sal_to as sto, 
               tmp.sal_freq as sfreq, tmp.posting_time as ptime
        from (vacancy v natural join job j) as tmp, application ap
        where ap.uemail = \'''' + session["user_id"] + '\' and ap.jid = tmp.jid and ap.vtype = tmp.type'
        cursor = g.conn.execute(text(query))
        data = cursor.fetchall()
        return render_template("user_home_page.html", message = message, data = data)
    return render_template("user_home_page.html", message = message)


# @Search vacancy with keyword
@app.route("/search", methods=["GET", "POST"])
@login_required
def search_vacancy():
    if request.method == 'POST':
        key = str(request.form['keyword']).strip()
        if not key:
            return render_template("search.html")
        attr = request.form.get('attr')
        ptf = str(request.form['pt_from']).strip()  # posting time from
        ptt = str(request.form['pt_to']).strip()  # posting time from
        order = request.form.get('order')
        order_attr = request.form.get('order_attr')
        limit = str(request.form['limit']).strip()
        query = '''
        select j.jid as id, j.name as name, v.type as type,
               v.sal_from as sfrom, v.sal_to as sto, 
               v.sal_freq as sfreq ,v.posting_time as ptime
        from vacancy as v inner join job as j on v.jid = j.jid
        '''
        if ptf and ptt:
            query += 'where v.posting_time>=\'' + ptf + '\' and v.posting_time<=\'' + ptt + '\' and '
        elif ptf and not ptt:
            query += 'where v.posting_time>=\'' + ptf + '\' and '
        elif not ptf and ptt:
            query += 'where v.posting_time<=\'' + ptt + '\' and '
        else:
            query += 'where '
        
        if attr == 'name':
            query += 'lower(j.name) like lower(\'%' + key + '%\') '    # use lower() to ignore case 
        elif attr == 'salary':
            query += 'v.sal_from <= ' + key + ' and v.sal_to >=' + key + ' '
        elif attr == 'skill':
            query += 'j.pre_skl like \'%' + key + '%\' or j.job_des like \'%''' + key + '%\' '
        
        if order_attr == 'pt':
            query += 'order by v.posting_time ' + order
        elif order_attr == 'id':
            query += 'order by j.jid ' + order
        elif order_attr == 'name':
            query += 'order by j.name ' + order
        elif order_attr == 'lows':
            query += 'order by v.sal_from ' + order
        elif order_attr == 'highs':
            query += 'order by v.sal_to ' + order
        
        if limit and limit != 'all':
            query += ' limit ' + limit
        cursor = g.conn.execute(text(query))  # !Very important here, must convert type text()
        job = []
        for row in cursor:
            job.append(row)
        data = job
        return render_template("search.html", data=data, keyword = key)
    return render_template("search.html")

# detailed info of a vacancy
@app.route("/detailed_info", methods=["GET", "POST"])
@login_required
def detailed_info():
    if request.method == 'POST':
        jid = request.form.get('jid')
        vtype = request.form.get('vtype')
        query = '''
        select *
        from vacancy v natural join job j
        where j.jid=''' + jid + ' and v.type=\'' + vtype +'\''
        cursor = g.conn.execute(text(query))
        data = cursor.fetchall()
        col_names = ['JID', 'Type', '# Positions', 'Salary from', 'Salary to', 'Salary Frequency', 'Post Until', 'Posting Time', 'Updated Time', 'Unit', 'Agency', 'Level', 'Job Name', 'Preferred Skills', 'Job Description', 'Location', 'Hour/Shift', 'Title code', 'Civil Service TiTle']  # column header
        return render_template("detailed_info.html", zippedlist = zip(col_names, data[0]), jid = jid, vtype = vtype) # zip to help us iterate two lists parallelly
    return render_template("detailed_info.html")

# apply for the vacancy
@app.route("/apply", methods=["GET", "POST"])
@login_required
def apply():
    if request.method == 'POST':
        jid = request.form.get('jid')
        vtype = request.form.get('vtype')
        query = '''
        insert into Application
        values (\'''' + session["user_id"] + '\', ' + jid + ', \'' + vtype + '\')'  # Zihan: I tried to use current_user.id here and it returned nothing. So I use session["user_id"] instead.
        g.conn.execute(text(query))
        return render_template("apply.html", jid = jid, vtype = vtype)
    return render_template("apply.html")

# cancel application for the vacancy
@app.route("/canel_apply", methods=["GET", "POST"])
@login_required
def cancel_apply():
    if request.method == 'POST':
        jid = request.form.get('jid')
        vtype = request.form.get('vtype')
        query = '''
        delete from Application
        where uemail=\'''' + session["user_id"] + '\' and jid=' + jid + ' and vtype=\'' + vtype + '\'' 
        g.conn.execute(text(query))
        return render_template("cancel_apply.html", jid = jid, vtype = vtype)
    return render_template("cancel_apply.html")

# some statistic info

# insert job (TBD)

# delete job (TBD)

# update job (TBD)

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