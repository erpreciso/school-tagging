# coding: utf-8
# [school-tagging] webapp

import webapp2
import jinja2
import os
import re
import random
import string
import hashlib
import logging
import json
from time import localtime, strftime
from google.appengine.api import channel
from google.appengine.api import users


TODO = """
when a channel is closed, remove the user from the LOGGED list.
algorithm to send messages to be revisited to avoid dups.

"""

MYLOGS = True

EXERCISES_POOL = [
	{
		"sentence": "The cat is on the table",
		"to find": "article",
		},
	{
		"sentence": "The dog is the best",
		"to find": "pronom",
		},
	]

MESSAGES = []

LOGGED = []

USERS = [
	{
		'username': u'tizio',
		'role': u'student',
		'hashpassword': 'b43eb7400b6faf49c758b0838c974a1efef2c58d4d1468ff2a5dbe306e826501|yfcBy',
	},
	{
		'username': u'caio',
		'role': u'student',
		'hashpassword': 'e1d382f8d7d6ea53f3c0ca42c50f82d9ea2be6d4afd11675858789570a0226b0|zLGNf',
	},
	{
		'username': u'sempronio',
		'role': u'teacher',
		'hashpassword': '42b13e20a38202b273fdb6ea29e240710acca6c7f7a627276cbc9253fefc3941|LxXVd',
	},
	]

def pick_an_exercise():
	exercise = EXERCISES_POOL[1]
	return {
		"sentence": exercise["sentence"],
		"to find": exercise["to find"],
		"words": exercise["sentence"].split(" "),
		}

def store_message(*a):
	message = {
		"username": a[0],
		"timestamp": a[1],
		"message": a[2],
		"type": "msg",
		}
	global MESSAGES
	MESSAGES.append(message)
	if MYLOGS:
		logging.info(str("Message added to db --> " + str(message)))
	return message

def select_template(role):
	assert role in ["student", "teacher"]
	if role == "student":
		return "student.html"
	elif role == "teacher":
		return "teacher.html"
				
def get_all_messages():
	return [message for message in MESSAGES]

def remove_from_LOGGED(username):
	global LOGGED
	for user in LOGGED:
		if user["username"] == username:
			LOGGED.remove(user)
			if MYLOGS:
				logging.info(str("Removed " + username + " from LOGGED"))

def add_user_to_LOGGED(role, username, token):
	if (role, username) not in get_all_LOGGED_users():
		global LOGGED
		user = {
				"username": username,
				"role": role,
				"token": token,
				}
		LOGGED.append(user)
		if MYLOGS:
			logging.info(str("User added to LOGGED list --> " + str(user)))
			logging.info(str("Count of logged users --> " + str(len(LOGGED))))
	else:
		if MYLOGS:
			logging.info("User already in LOGGED list")

def get_all_LOGGED_users():
	"""return tuple (role, username) """
	return [(user["role"], user["username"]) for user in LOGGED]

def user_in_LOGGED(username, role):
	return (role, username) in get_all_LOGGED_users()

def get_all_usernames_in_USERS():
	return [user["username"] for user in USERS]

def get_token_from_LOGGED(username):
	for user in LOGGED:
		if user["username"] == username:
			return user["token"]

def get_password_from_database(username):
	password = None
	for user in USERS:
		if user["username"] == username:
			password = user["hashpassword"]
	if password:
		if MYLOGS:
			logging.info(str("Password retrieved for " + username))
		return password
	else:
		if MYLOGS:
			logging.info(str("Password not existing for " + username))
		return password
	
def add_user_to_database(role, username, password):
	global USERS
	user = {
			"username": username,
			"hashpassword": password,
			"role": role,
			}
	USERS.append(user)
	if MYLOGS:
		logging.info(str("User added to db --> " + str(user)))
		logging.info(str("Count of registered users --> " + str(len(USERS))))

def user_info_from_cookie(cookie):
	assert cookie.count("|") == 3
	info = {
		"role": cookie.split("|")[0],
		"username": cookie.split("|")[1],
		"hashpassword": cookie.split("|")[2],
		"salt": cookie.split("|")[3],
		}
	if MYLOGS:
		logging.info(str("Extracted info from cookie --> " + str(info)))
	return info
	
def user_in_database(cookie):
	if cookie:
		info = user_info_from_cookie(cookie)
		cookie_username = info["username"]
		cookie_saltpassword = "%s|%s" % (info["hashpassword"], info["salt"])
		for user in USERS:
			if cookie_username == user["username"] and \
				cookie_saltpassword == user['hashpassword']:
				if MYLOGS:
					logging.info("User in database, cookie verified")
				return True
	if MYLOGS:
		logging.info("User not in database, cookie verified")
	return False

def set_my_cookie(self, role, username, password):
	cookie = "|".join([str(role),str(username),str(password)])
	self.response.headers.add_header('Set-Cookie', 'schooltagging=' + cookie)
	if MYLOGS:
		logging.info(str("Setup Cookie --> " + cookie))

def clear_my_cookie(self):
	cookie = self.request.cookies.get("schooltagging")
	if cookie:
		self.response.delete_cookie('schooltagging', path = '/')
		if MYLOGS:
			logging.info(str("Cookie deleted"))
	else:
		if MYLOGS:
			logging.info(str("Cookie not existing"))

def create_a_channel(username):
	token = channel.create_channel(username)
	if MYLOGS:
		logging.info(str("Channel created for " + username))
	return token

def broadcast_message(message, sender):
	timestamp = strftime("%a, %d %b %H:%M:%S",localtime())
	message = store_message(sender, timestamp, message)
	for (role, user) in get_all_LOGGED_users():
		send_message_to_user(user, message)

	if MYLOGS:
		logging.info("Message broadcasted")

def send_message_to_user(username, message):
	message = json.dumps(message)
	channel.send_message(username, message)
	if MYLOGS:
		logging.info("Message delivered")

def send_exercise(username):
	exercise = pick_an_exercise()
	message = {
		"type": "exercise",
		"message": exercise,
		}
	message = json.dumps(message)
	channel.send_message(username, message)
	if MYLOGS:
		logging.info(str("Exercise delivered to " + username))
	
def broadcast_user_connection_info(target_user, status):
	for (role, username) in get_all_LOGGED_users():
		if username != target_user:
			send_message_of_user_connection_info(target_user, status, role, username)
	if MYLOGS:
		logging.info("All messages of new connection sent")

def send_message_of_user_connection_info(target_user, status, role, recipient):
	if status == "open":
		type = "connected user"
	elif status == "close":
		type = "disconnected user"
	message = {
		"type": type,
		"username": target_user,
		"role": role,
		}
	message = json.dumps(message)
	channel.send_message(recipient, message)
	if MYLOGS:
		logging.info("Message that the user is " + status + " delivered to " + str(recipient))

def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return "%s|%s" % (h,salt)

def valid_pw(name, pw, h, salt):
	return h == make_pw_hash(name, pw, salt)

class MainHandler(webapp2.RequestHandler):
	template_dir = os.path.join(os.path.dirname(__file__), 'pages')
	jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
		autoescape = True)
	def writeout(self, *a, **kw):
		self.response.out.write(*a, **kw)
	
	def readout(self,param):
		return self.request.get(param)
		
	def render_str(self, template, **params):
		return self.jinja_env.get_template(template).render(params)
		
	def render_page(self, template, **kw):
		self.writeout(self.render_str(template, **kw))

class SignupPageHandler(MainHandler):
	def write_signup(self,
				username="",
				username_error="",
				password_missing_error_sw=False,
				password_match_error_sw=False,
				):
		if password_missing_error_sw:
			password_missing_error="That wasn't a valid password."
		else:
			password_missing_error=""
		if password_match_error_sw:
			password_match_error="Your passwords didn't match."
		else:
			password_match_error=""
		self.render_page("signup.html",username = username,
						username_error = username_error,
						password_missing_error = password_missing_error,
						password_match_error = password_match_error,
						)

	def get(self):
		clear_my_cookie(self)
		self.write_signup()

	def post(self):
		username=self.request.get("username")
		password=self.request.get("password")
		verify_password=self.request.get("verify")
		username_error_sw = False
		username_error=""
		password_missing_error_sw = False
		password_match_error_sw = False
		username_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
		if username == "" or username_re.match(username) == None:
			username_error = "That's not a valid username."
			username_error_sw = True
		if password == "":
			password_missing_error_sw = True
		password_re = re.compile(r"^.{3,20}$")
		if password_re.match(password) == None:
			password_missing_error_sw = True
		if password != verify_password:
			password_match_error_sw = True
		if password_match_error_sw or username_error_sw or password_missing_error_sw:
			self.write_signup(username,
						username_error,
						password_missing_error_sw,
						password_match_error_sw,
						)
		else:
			if username in get_all_usernames_in_USERS():
				username_error = "That user already exists"
				self.write_signup(username,
						username_error,
						password_missing_error_sw,
						password_match_error_sw,
						)
			else:
				if MYLOGS:
					logging.info("No errors, user allowed to be registered")
				role = self.request.get("role")
				password = make_pw_hash(username, password)
				add_user_to_database(role, username, password)
				add_user_to_LOGGED(role, username, "")
				set_my_cookie(self, role, username, password)
				self.redirect("/welcome")
				
class LoginPageHandler(MainHandler):

	def write_login(self, username = "", login_error = ""):
		self.render_page(
				"login.html",
				username = username,
				login_error = login_error,
				)

	def get(self):
		clear_my_cookie(self)
		self.write_login()
	
	def post(self):
		username = self.request.get("username")
		userpassword = self.request.get("password")
		role = self.request.get("role")
		if username == "" or userpassword == "":
			self.write_login(login_error = "Invalid login")
		else:
			db_password = get_password_from_database(username)
			if db_password:
				salt = db_password.split('|')[1]
				login_password = make_pw_hash(username, userpassword, salt)
				if login_password == db_password:
					set_my_cookie(self, role, username, login_password)
					#~ add_user_to_LOGGED(role, username)
					self.redirect("/welcome")
			self.write_login(login_error = "Invalid login")

class LogoutPageHandler(MainHandler):
	
	def get(self):
		cookie = self.request.cookies.get("schooltagging")
		if cookie:
			username = user_info_from_cookie(cookie)["username"]
			broadcast_user_connection_info(username, "close")
			clear_my_cookie(self)
			remove_from_LOGGED(username)
		self.redirect("/login")

class WelcomePageHandler(MainHandler):
	def write_welcome(self, template, username, role, token):
		self.render_page(
					template,
					username = username,
					role = role,
					token = token,
					logged = get_all_LOGGED_users(),
					messages = get_all_messages(),
					exercise = pick_an_exercise(),
					)

	def get(self):
		cookie = self.request.cookies.get("schooltagging")
		if user_in_database(cookie):
			user_info = user_info_from_cookie(cookie)
			username = user_info["username"]
			role = user_info["role"]
			if not user_in_LOGGED(username, role) or get_token_from_LOGGED == "":
				token = create_a_channel(username)
				add_user_to_LOGGED(role, username, token)
			else:
				token = get_token_from_LOGGED(username)
			#~ template = select_template(role)
			template = "welcome.html"
			self.write_welcome(template, username, role, token)
		else:
			self.redirect("/login")

class MessageHandler(MainHandler):
	def post(self):
		cookie = self.request.cookies.get("schooltagging")
		message = self.request.get("message")
		if user_in_database(cookie):
			if message:
				user_info = user_info_from_cookie(cookie)
				sender = user_info["username"]
				broadcast_message(message, sender)
			#~ self.redirect("/welcome")
		else:
			self.redirect("/login")

class ExerciseRequestHandler(MainHandler):
	def get(self):
		cookie = self.request.cookies.get("schooltagging")
		if user_in_database(cookie):
			user_info = user_info_from_cookie(cookie)
			username = user_info["username"]
			if MYLOGS:
				logging.info(str("Exercise request from " + username))
			send_exercise(username)

class ConnectedHandler(MainHandler):
	def post(self):
		client_id = self.request.get('from')
		logging.info(str("connected ID --> " + str(client_id)))
		broadcast_user_connection_info(client_id, "open")

class DisconnectedHandler(MainHandler):
	def post(self):
		client_id = self.request.get('from')
		logging.info(str("Disconnected ID --> " + str(client_id)))
		broadcast_user_connection_info(client_id, "close")
		remove_from_LOGGED(client_id)

app = webapp2.WSGIApplication([
    ('/', LoginPageHandler),
    ('/signup', SignupPageHandler),
    ('/login', LoginPageHandler),
    ('/welcome', WelcomePageHandler),
    ('/logout', LogoutPageHandler),
    ('/message', MessageHandler),
    ('/_ah/channel/connected/', ConnectedHandler),
    ('/_ah/channel/disconnected/', DisconnectedHandler),
    ('/exercise_request', ExerciseRequestHandler),
	], debug=True)
