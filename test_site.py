import flask

app = flask.Flask(__name__, static_folder='static', template_folder='templates')

test_var = 'T'
def test_before_all():
	global test_var
	test_var += 'a'

def test_before_req():
	global test_var
	test_var += 'b'

def test_after_req(response):
	global test_var
	test_var += 'c'
	return response

@app.route('/')
def default():
	print(flask.request.__dict__)
	print(dir(flask.request))
	return test_var

app.before_first_request(test_before_all)
app.before_request(test_before_req)
app.after_request(test_after_req)

if __name__ == '__main__':
	app.run(host='localhost', port=1203, debug=False, threaded=True)
	
