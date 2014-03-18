# coding: utf-8
# [school-tagging] webapp

import webapp2
import jinja2
import os
import re
import random
import string
import hashlib

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

def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return "%s|%s" % (h,salt)

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
				self.response.headers.add_header('Set-Cookie',
								'schooltagging=%s|%s; Path=/' % (str(username),str(password)))
				self.redirect("/")
				


app = webapp2.WSGIApplication([
    ('/', HomePageHandler),
    ('/signup', SignupPageHandler),
	], debug=True)
