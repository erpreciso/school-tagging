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

DEBUG = True
#~ Debug settings
#~ --------------
#~ in check_cookie: returns True even if there are no cookie
#~ USER_CACHE global variable always contains a student login
#~ in Logout class: doesn't clear the cache
#~ -----------------------------------------------------------

USER_CACHE = {
	'hashpassword': '7d69e7ad3f56a8cfa6b35450ac1903b64557c1d9223393e6b863c9cc86bd26db|Okzmj',
	'username': u'rrr',
	'role': u'students',
	}

USERS = {
	"teachers": [
		{
		'hashpassword': 'cbf37cbdaa4b4bf387264b1b980f0b8e0345aeeb47bb56678477bd70ad71ee47|BOZCt',
		'role': u'teachers',
		'username': u'ttt'
		}
	],
	"students": [
		{
		'hashpassword': '7d69e7ad3f56a8cfa6b35450ac1903b64557c1d9223393e6b863c9cc86bd26db|Okzmj',
		'username': u'rrr',
		'role': u'students',
		}
	]
	}

def get_user_role():
	if USER_CACHE["role"] == "students":
		return "student"
	elif USER_CACHE["role"] == "teachers":
		return "teacher"
	else:
		raise Exception("No known role")

def get_user_name():
	return USER_CACHE["username"]

def add_user_to_cache(role, username, password):
	global USER_CACHE
	USER_CACHE["role"] = role
	USER_CACHE["username"] = username
	USER_CACHE["hashpassword"] = password
	
def all_usernames():
	a = [x["username"] for x in USERS["teachers"]]
	b = [x["username"] for x in USERS["students"]]
	return a + b

def add_user_to_database(role, username, password, id="default"):
	user = {
			"id": id,
			"username": username,
			"hashpassword": password,
			}
	USERS[role].append(user)

def get_user_password(role, username):
	logging.info(role)
	for user in USERS[role]:
		if user["username"] == username:
			return user["hashpassword"]
	return False

def check_cookie(c):
	if DEBUG:
		return True
	if 'username' in USER_CACHE.keys():
		if c and '|' in c:
			if '|' in c[c.find('|') + 1:]:
				username = c.split('|')[0]
				user_pswsalt = '%s|%s' % (c.split('|')[1], c.split('|')[2])
				if username == USER_CACHE['username'] and user_pswsalt == USER_CACHE['hashpassword']:
					return True
	global USER_CACHE
	USER_CACHE.clear()
	return False

def set_my_cookie(self, username, password):
	cookie = 'schooltagging=' + str(username)
	cookie = cookie + '|' + str(password)
	self.response.headers.add_header('Set-Cookie', cookie)

def clear_my_cookie(self):
	self.response.delete_cookie('schooltagging', path = '/')

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

class HomePageHandler(MainHandler):
	def get(self):
		self.render_page("content.html")

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
			if username in all_usernames():
				username_error = "That user already exists"
				self.write_signup(username,
						username_error,
						password_missing_error_sw,
						password_match_error_sw,
						mail_error_sw,
						)
			else:
				role = self.request.get("role")
				password = make_pw_hash(username, password)
				add_user_to_database(role, username, password)
				add_user_to_cache(role, username, password)
				set_my_cookie(self, username, password)
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
		user_password = self.request.get("password")
		role = self.request.get("role")
		if username == "" or user_password == "":
			self.write_login(login_error = "Invalid login")
		else:
			db_password = get_user_password(role, username)
			if db_password:
				salt = db_password.split('|')[1]
				login_password = make_pw_hash(username, user_password, salt)
				if login_password == db_password:
					set_my_cookie(self, username, login_password)
					add_user_to_cache(role, username, login_password)
					self.redirect("/welcome")
			self.write_login(login_error = "Invalid login")

class LogoutPageHandler(MainHandler):
	
	def get(self):
		clear_my_cookie(self)
		if not DEBUG:
			USER_CACHE.clear()
		self.redirect("/login")

class WelcomePageHandler(MainHandler):
	def get(self):
		cookie = self.request.cookies.get("schooltagging")
		if check_cookie(cookie):
			if get_user_role() == "student":
				self.render_page(
						"student.html",
						username=get_user_name(),
						)
			elif get_user_role() == "teacher":
				self.render_page(
						"teacher.html",
						username=get_user_name(),
						cache=USER_CACHE,
						)
		else:
			self.redirect("/login")


app = webapp2.WSGIApplication([
    ('/', HomePageHandler),
    ('/signup', SignupPageHandler),
    ('/login', LoginPageHandler),
    ('/welcome', WelcomePageHandler),
    ('/logout', LogoutPageHandler),
	], debug=True)
