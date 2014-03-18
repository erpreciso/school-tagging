# coding: utf-8
# [school-tagging] webapp

import webapp2
import jinja2
import os
import re
import random
import string
import hashlib

USER_CACHE = {}

#~ temp cookie rrr|7a6990be279be51803e015ffcb32ed3523205a73bfee13e7c45ed14c31b242a0|aqRpS
USERS = {
	"teachers": [
		{
			"id": "teacher 1",
			"username": "t",
			"password": "t",
			},
		],
	"students": [
		{
			"id": "student 1",
			"username": "s",
			"password": "s",
		},
		{
			"id": "student 2",
			"username": "s2",
			"password": "s2",
		},
	],
}

def all_usernames():
	a = [x["username"] for x in USERS["teachers"]]
	b = [x["username"] for x in USERS["students"]]
	return a + b

def add_user(role, username, password, id="default"):
	a = {
				"id": id,
				"username": username,
				"password": password,
			}
	USERS[role].append(a)

def get_user_password(role, username):
	for k in USERS[role]:
		if k["username"] == username:
			return k["password"]
	return False
		
def set_my_cookie(username, password):
	cookie = 'schooltagging=' + str(username)
	cookie = cookie + '|' + str(password)
	return cookie

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
				add_user(role, username, password)
				self.response.headers.add_header(
						'Set-Cookie',
						set_my_cookie(username, password),
						)
				global USER_CACHE
				USER_CACHE['user'] = username
				USER_CACHE['hashpassword'] = password
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
					self.response.headers.add_header(
							'Set-Cookie',
							set_my_cookie(username, login_password),
							)
					global USER_CACHE
					USER_CACHE['user'] = username
					USER_CACHE['hashpassword'] = login_password
					self.redirect("/welcome")
			self.write_login(login_error = "Invalid login")

class LogoutPageHandler(MainHandler):
	
	def get(self):
		clear_my_cookie(self)
		USER_CACHE.clear()
		self.redirect("/login")

class WelcomePageHandler(MainHandler):
	def get(self):
		cookie = self.request.cookies.get("schooltagging")
		if check_cookie(cookie):
			self.render_page(
					"welcome.html",
					username=USER_CACHE["user"],
					)
		else:
			self.redirect("/login")

def check_cookie(c):
	if 'user' in USER_CACHE.keys():
		if c and '|' in c:
			if '|' in c[c.find('|') + 1:]:
				username = c.split('|')[0]
				user_pswsalt = '%s|%s' % (c.split('|')[1], c.split('|')[2])
				if username == USER_CACHE['user'] and user_pswsalt == USER_CACHE['hashpassword']:
					return True
	global USER_CACHE
	USER_CACHE.clear()
	return False

app = webapp2.WSGIApplication([
    ('/', HomePageHandler),
    ('/signup', SignupPageHandler),
    ('/login', LoginPageHandler),
    ('/welcome', WelcomePageHandler),
    ('/logout', LogoutPageHandler),
	], debug=True)
