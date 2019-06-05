import flask
import random
import sys,os
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
	return test_var

@app.route('/mynum')
def rand_session_num():
	'''
		Gives each session a single random number.
	'''
	current_num = flask.session.get('rand_user_num', None)
	if current_num is None:
		current_num = random.randrange(0,50)
		flask.session['rand_user_num'] = str(current_num)
	return 'Your number is: '+flask.session['rand_user_num']
	
@app.route('/name/<name>')
def view_name(name):
	return name+': '+test_var
	
def get_db():
	if 'db' not in g:
		g.db = sqlite3.connect(test_db)
	return g.db
	
def close_db():
	db = flask.g.pop('db', None)
	if db is not None:
		db.close()
	
@app.route('/main', methods=('GET', 'POST'))
def main_page():
	test_var_user = 'Nobody'
	if flask.request.method == 'POST':
		test_var_user = flask.request.form['username']
	return flask.render_template('main.html', user = test_var_user)
	
@app.errorhandler(404)
def page_not_found(error):
	return 'Page not found, sorry!', 404 #Not sure what returning the 404 does here

app.before_first_request(test_before_all) #happens before first request
app.before_request(test_before_req) #happens before each request
app.after_request(test_after_req) #happens after each request, must return the response

if __name__ == '__main__':
	app.run(host='localhost', port=1203, threaded=True)
	
