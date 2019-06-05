import flask
import random
import sys,os
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
sys.path.insert(1, os.path.join(sys.path[0], '..'))

app = flask.Flask(__name__)
app.config.from_object('testsite_config')

test_var = 'T'
def test_before_all():
	global test_var
	test_var += 'a'

def test_before_req():
	# print(flask.request.headers)
	# print(flask.request.args)
	# print(flask.request.authorization)
	# print(flask.request.form)
	# print(flask.request.method)
	# print(flask.request.mimetype)
	
	global test_var
	test_var += 'b'

def test_after_req(response):
	global test_var
	test_var += 'c'
	# return flask.make_response('hu') #Turns the response into 'hu'!
	return response

@app.route('/')
def view_default():
	out_text = flask.session.get('cur_user', '') + ' : ' + test_var
	out_text += '<br><a href="'+flask.url_for('login')+'"> Log in! </a>'
	out_text += '<br><a href="'+flask.url_for('logout')+'"> Log out! </a>'
	return out_text

@app.route('/mynum')
def rand_session_num():
	'''
		Gives each session a single random number.
	'''
	current_num = flask.session.get('rand_user_num', None)
	if current_num is None:
		current_num = random.randrange(0,50)
		flask.session['rand_user_num'] = str(current_num)
	out_text = 'Your number is: '+flask.session['rand_user_num']
	out_text += '<br><a href="'+flask.url_for('logout')+'"> Log out! </a>'
	return out_text
	
@app.route('/name/<name>')
def view_name(name):
	return name+': '+test_var
	
#db.execute("CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL);")
def get_db():
	if 'db' not in flask.g:
		flask.g.db = sqlite3.connect('test_db')
		flask.g.db.row_factory = sqlite3.Row
	return flask.g.db
	
def close_db(e = None):
	db = flask.g.pop('db', None)
	
	if db is not None:
		db.close
	
@app.route('/register', methods=('GET', 'POST'))
def register():
	if flask.request.method == 'POST':
		new_username = flask.request.form.get('username', None)
		new_password = flask.request.form.get('password', None)
		new_password_confirm = flask.request.form.get('password_confirm', None)
		
		db = get_db()
		
		error = None
		if (new_username is None):
			error = 'You must include a username!'
		elif (new_password is None or len(new_password) < 6):
			error = 'Your password must be at least 6 characters!'
		elif (new_password != new_password_confirm):
			error = 'Your password and confirmation must match!'
		elif (db.execute(
			'SELECT id FROM user WHERE username = ?', (new_username,)
		).fetchone() is not None):
			error = 'That username already exists!'
		
		if error is None:
			db.execute(
				'INSERT INTO user (username, password) VALUES (?, ?)',
				(new_username, generate_password_hash(new_password))
			)
			db.commit()
			return flask.redirect(flask.url_for('login'))
			
		flask.flash(error)
		
	return flask.render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
	if flask.request.method == 'POST':
		username = flask.request.form['username']
		password = flask.request.form['password']
		
		db = get_db()
		user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
		
		error = None
		if user is None:
			error = 'User not found.'
		elif not check_password_hash(user['password'], password):
			print(user['password'])
			print(password)
			print(generate_password_hash(password))
			error = 'Incorrect password.'
		
		if error is None:
			flask.session.clear()
			flask.session['cur_user'] = flask.request.form['username']
			return flask.redirect(flask.url_for('view_default'))
		
		flask.flash(error)
		
	return flask.render_template('login.html')
	
@app.route('/logout')
def logout():
	flask.session.clear()
	return flask.redirect(flask.url_for('view_default'))
	
@app.errorhandler(404)
def page_not_found(error):
	return 'Page not found, sorry!', 404 #Not sure what returning the 404 does here

app.before_first_request(test_before_all) #happens before first request
app.before_request(test_before_req) #happens before each request
app.after_request(test_after_req) #happens after each request, must return the response
app.teardown_appcontext(close_db)

if __name__ == '__main__':
	app.run(host='localhost', port=1203, threaded=True)
	
