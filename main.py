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
from google.appengine.api import channel
from google.appengine.api import users

DEBUG = False
MYLOGS = True

TODO = """
when a channel is closed, remove the user from the LOGGED list.

"""

CHANNELS = {}

LOGGED = []

USERS = [
	{
		'hashpassword': 'cbf37cbdaa4b4bf387264b1b980f0b8e0345aeeb47bb56678477bd70ad71ee47|BOZCt',
		'role': u'teacher',
		'username': u'ttt'
	},
	{
		'hashpassword': '7d69e7ad3f56a8cfa6b35450ac1903b64557c1d9223393e6b863c9cc86bd26db|Okzmj',
		'username': u'rrr',
		'role': u'student',
	},
	]


def remove_from_LOGGED(username):
	global LOGGED
	for user in LOGGED:
		if user["username"] == username:
			LOGGED.remove(user)
			if MYLOGS:
				logging.info(str("Removed " + username + " from LOGGED"))

def add_user_to_LOGGED(role, username, password):
	global LOGGED
	user = {
			"username": username,
			"hashpassword": password,
			"role": role,
			}
	LOGGED.append(user)
	if MYLOGS:
		logging.info(str("User added to LOGGED list --> " + str(user)))
		logging.info(str("Count of logged users --> " + str(len(LOGGED))))

def get_all_LOGGED_users():
	return [(user["role"], user["username"]) for user in LOGGED]
	
def get_all_usernames_in_USERS():
	return [user["username"] for user in USERS]

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
	global CHANNELS
	CHANNELS["username"] = token
	if MYLOGS:
		logging.info(str("Channel created for " + username))
	return token

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
						mail_error_sw,
						)
			else:
				if MYLOGS:
					logging.info("No errors, user allowed to be registered")
				role = self.request.get("role")
				password = make_pw_hash(username, password)
				add_user_to_database(role, username, password)
				add_user_to_LOGGED(role, username, password)
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
					add_user_to_LOGGED(role, username, login_password)
					self.redirect("/welcome")
			self.write_login(login_error = "Invalid login")

class LogoutPageHandler(MainHandler):
	
	def get(self):
		cookie = self.request.cookies.get("schooltagging")
		if cookie:
			username = user_info_from_cookie(cookie)["username"]
			clear_my_cookie(self)
			remove_from_LOGGED(username)
		self.redirect("/login")

class WelcomePageHandler(MainHandler):
	def get(self):
		cookie = self.request.cookies.get("schooltagging")
		if user_in_database(cookie):
			user_info = user_info_from_cookie(cookie)
			username = user_info["username"]
			role = user_info["role"]
			token = create_a_channel(username)
			if role == "student":
				templ = "student.html"
			elif role == "teacher":
				templ = "teacher.html"
			self.render_page(
					templ,
					username=username,
					token=token,
					logged=get_all_LOGGED_users(),
					)
		else:
			self.redirect("/login")
	
	def post(self):
		cookie = self.request.cookies.get("schooltagging")
		message = self.request.get("message")
		if check_cookie(cookie):
			role = get_user_role(get_user_from_cookie(cookie))
			username = get_user_from_cookie(cookie)
			if role == "student":
				role = "teacher"
			else:
				role = "student"
			channel.send_message(CHANNEL[role], message)
			self.redirect("/welcome")
			

class DevPageHandler(MainHandler):
	def get(self):
		cookie = self.request.cookies.get("schooltagging")
		user = get_user_from_cookie(cookie)
		token = channel.create_channel(user)
		self.render_page("dev.html", token=token, user=user)
		
app = webapp2.WSGIApplication([
    ('/', LoginPageHandler),
    ('/signup', SignupPageHandler),
    ('/login', LoginPageHandler),
    ('/welcome', WelcomePageHandler),
    ('/logout', LogoutPageHandler),
    ('/dev', DevPageHandler),
	], debug=True)
