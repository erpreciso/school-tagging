# coding: utf-8
# [school-tagging] webapp

import webapp2
import jinja2
import os
import re
from google.appengine.ext import ndb

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

class People(ndb.Model):
	username = ndb.StringProperty()
	password = ndb.StringProperty()
	email = ndb.TextProperty()
	created =  ndb.DateTimeProperty(auto_now_add = True)

def user_key(ukey = 'default'):
	return ndb.Key.from_path("People", ukey)

class SignupPageHandler(MainHandler):
	def write_signup(self,
				username="",
				email="",
				username_error="",
				password_missing_error_sw=False,
				password_match_error_sw=False,
				mail_error_sw=False,
				):
		if password_missing_error_sw:
			password_missing_error="That wasn't a valid password."
		else:
			password_missing_error=""
		if password_match_error_sw:
			password_match_error="Your passwords didn't match."
		else:
			password_match_error=""
		if mail_error_sw:
			mail_error="That's not a valid email."
		else:
			mail_error=""
		tutt = People.query().order(People.created)
		self.render_page("signup.html",username = username,
												email = email,
												username_error = username_error,
												password_missing_error = password_missing_error,
												password_match_error = password_match_error,
												mail_error = mail_error,
												tutt = tutt)

	def get(self):
		self.write_signup()

	def post(self):
		username=self.request.get("username")
		password=self.request.get("password")
		verify_password=self.request.get("verify")
		email=self.request.get("email")
		
		#verifica presenza username
		username_error_sw = False
		username_error=""
		if username == "":
			username_error = "That's not a valid username."
			username_error_sw = True
		#verifica correttezza username
		username_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
		if username_re.match(username) == None:
			username_error_sw = True
		#verifica presenza password
		password_missing_error_sw = False
		if password == "":
			password_missing_error_sw = True
		#verifica correttezza password
		password_re = re.compile(r"^.{3,20}$")
		if password_re.match(password) == None:
			password_missing_error_sw = True
		#verifica consistenza password
		password_match_error_sw = False
		if password != verify_password:
			password_match_error_sw = True
		#verifica correttezza email
		mail_error_sw = False
		if email != "":
			mail_re=re.compile(r"^[\S]+@[\S]+\.[\S]+$")
			if mail_re.match(email) == None:
				mail_error_sw = True
		if password_match_error_sw or username_error_sw or password_missing_error_sw or mail_error_sw == True:
			self.write_signup(username,
						email,
						username_error,
						password_missing_error_sw,
						password_match_error_sw,
						mail_error_sw,
						)
		else:
			#~ ck = ndb.GqlQuery("SELECT * FROM People WHERE username = :1",username)
			ck = People.query(People.username == username)
			if not ck.get():
				u = People(parent = user_key())
				u.username = username
				u.password = make_pw_hash(username, password)
				if email != "":
					u.email = email
				k = u.put()
				self.response.headers.add_header('Set-Cookie',
								'schooltagging=%s|%s; Path=/' % (str(k.id()),u.password))
				self.redirect("/")
			else:
				username_error = "That user already exists"
				self.write_signup(username,
						email,
						username_error,
						password_missing_error_sw,
						password_match_error_sw,
						mail_error_sw,
						)


app = webapp2.WSGIApplication([
    ('/', HomePageHandler),
    ('/signup', SignupPageHandler),
	], debug=True)
