
from flask import Flask, render_template, url_for, request, redirect, flash, Response, make_response, jsonify
import db
import json
import logging
import flask_login
import re
from bson.objectid import ObjectId
from datetime import datetime
import humanize

"""
CONFIGS
===================================
"""
app = Flask('app')
app.secret_key = 'some secret password :p' # will be put in OS environment
# Mutes console output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

"""
CLEARING CACHE
===================================
Don't delete any of this lol
"""
@app.after_request
def add_header(r):
	r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	r.headers["Pragma"] = "no-cache"
	r.headers["Expires"] = "0"
	r.headers['Cache-Control'] = 'public, max-age=0'
	return r

"""
LOGIN
===============================================
Just several notes:
`flask_login.login_user(User())` to log in a user
`flask_login.current_user.id` to get the current user's name
"""
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
class User(flask_login.UserMixin):
	pass
@login_manager.user_loader
def user_loader(username):
	u = db.get_user_by("name", username)
	if not u: return
	user = User()
	user.id = u["name"]
	return user
@login_manager.request_loader
def request_loader(request):
	if request.form:
		username = request.form["username"]
		if not db.verify_user(username, request.form["password"]):
			# Authenticated failed
			return
		u = db.get_user_by("name", username)
		user = User()
		user.id = u["name"]
		return user
# Handle unauthorized access redirects to login page
@login_manager.unauthorized_handler
def unauthorized_handler():
	# Unauthorized people will be redirected to the main page
	return redirect(url_for('index'))

"""
ROUTES
==============================
Create new pages/links here!
"""
@app.template_filter('get_thread')
def get_thread(tid):
    return db.threads.find_one({"_id": ObjectId(tid)})
@app.template_filter('humantime')
def humantime(time):
    return humanize.naturaltime(time - datetime.now())

@app.route('/', methods=["POST", "GET"])
def index():
	if request.form:
		# If inputPassword2 field is not empty, this is a registration.
		name = request.form["username"]
		pwrd = request.form["password"]
		# Registration
		if request.form["password2"]:
			# Check for illegal characters in the name
			for x in name:
				if not re.match(r'[A-Za-z0-9_]+$', name):
					flash("Your name has an illegal character! Only letters, numbers, and underscores are allowed.")
					return render_template('index.html', page_name="index", current_user=False)
			if (pwrd != request.form["password2"]):
				flash("Passwords do not match!")
				return render_template('index.html', page_name="index", current_user=False)
			if (len(pwrd) < 6):
				flash("Password must be at least 6 characters.")
				return render_template('index.html', page_name="index", current_user=False)
			if db.get_user_by("username", name):
				flash("User '{}' already exists!".format(name))
				return render_template('index.html', page_name="index", current_user=False)
			else:
				print("New user {} registered!".format(name))
				db.create_user(name, pwrd)
				flash("User created!")
				return render_template('index.html', page_name="index", newuser=True, current_user=False)
		# Validated user
		elif db.verify_user(name, pwrd):
			print(name, "has been verified!")
			user = User()
			user.id = name
			flask_login.login_user(user)
			return redirect("/")
		else:
			flash("Incorrect credentials!")
			return render_template('index.html', page_name="index", current_user=False)
	else:
		current_user = flask_login.current_user
		# Structure of threads
		thread = db.get_comments()
		# If the user isn't logged in the id isn't defined
		try: current_user.id
		except: current_user = None
		return render_template('index.html', page_name="index", current_user=current_user, main_thread=thread)

@app.route('/comment', methods=["POST"])
def comment():
	current_user = flask_login.current_user
	comment = request.form['comment']
	thread_id = request.form["id"]
	color = request.form["color"]
	db.create_comment(thread_id, {"author": current_user.id, "content": comment, "color": color})
	
	thread = db.get_comments()
	return render_template('index.html', page_name="index", current_user=current_user, main_thread=thread)

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect('/')

"""
RUN APP
===================================
Note: might need to change host and set
debug to false once deployed.
"""

if __name__ == "__main__":
    app.run(port=8000)