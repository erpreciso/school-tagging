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
import sys
from time import localtime, strftime
from google.appengine.api import channel
from google.appengine.ext import ndb
from google.appengine.api import memcache

class Support():
	def get_from_username(self, username):
		data = memcache.get("%s:logged" % username)
		if data is not None:
			return data
		else:
			data = Logged.query(Logged.username == username).get()
			if not memcache.add("%s:logged" % username, data):
				MyLogs("Memcache set failed:", username, ":logged")
			return data
	
	def get_all_logged(self):
		"""return list of {role, username} of logged """
		data = memcache.get("all_logged")
		if data is not None:
			MyLogs("Return list of logged from memcache", data)
			return data
		else:
			all_logged = Logged.query().fetch()
			result = []
			for logged in all_logged:
				user = {
					"role": logged.role,
					"username": logged.username,
					}
				result.append(user)
			memcache.add("all_logged", result)
			MyLogs("Return list of logged from db", result)
			return result
	
	def get_all_registered(self):
		"""return list of {role, username, hashpassword} of registered"""
		data = memcache.get("all_registered")
		if data is not None:
			MyLogs("Return list of registered from memcache", data)
			return data
		else:
			all_registered = RegisteredUser.query().fetch()
			result = []
			for registered in all_registered:
				user = {
					"role": registered.role,
					"username": registered.username,
					"hashpassword": registered.hashpassword,
					}
				result.append(user)
			memcache.add("all_registered", result)
			MyLogs("Return list of registered from db", result)
			return result

	def user_in_database(self, cookie):
		if cookie:
			c = Cookie(cookie)
			c.extract_value()
			for user in Support().get_all_registered():
				MyLogs("Compare",user,"with",c.username,c.hashpassword)
				if c.username == user["username"] and \
					c.hashpassword == user["hashpassword"]:
					MyLogs("User in database, cookie verified")
					return True
		MyLogs("User not in database, cookie verified")
		return False
	
	def get_password_from_database(self, username):
		password = None
		for user in Support().get_all_registered():
			if user["username"] == username:
				password = user["hashpassword"]
		if password:
			MyLogs("Password retrieved for ", username)
			return password
		else:
			MyLogs("Password not existing for ", username)
			return password

	def remove_logged(self, username):
		entity = Support().get_from_username(username)
		MyLogs("To be removed:", entity)
		entity.key.delete()
		MyLogs("Removed from Logged ndb:", username)

	def create_a_channel(self, username):
		token = channel.create_channel(username)
		MyLogs("Channel created for ", username)
		return token

class Logged(ndb.Model):
	username = ndb.StringProperty()
	role = ndb.StringProperty()
	token = ndb.StringProperty()
	addtime = ndb.DateTimeProperty(auto_now_add=True)
	
	def add(self):
		all_logged = Support().get_all_logged()
		if self.username in [user["username"] for user in all_logged]:
			MyLogs("User already in Logged ndb:", self.username)
		else:
			self.put()
			memcache.delete("all_logged")
			memcache.delete("all_registered")
			MyLogs("User added to Logged ndb:", self.username)

class RegisteredUser(ndb.Model):
	username = ndb.StringProperty()
	role = ndb.StringProperty()
	hashpassword = ndb.StringProperty()
	
	def add(self):
		all_registered = Support().get_all_registered()
		if self.username in [user["username"] for user in all_registered]:
			MyLogs("User already in Registered ndb:", self.username)
		else:
			self.put()
			memcache.delete("all_registered")
			memcache.delete("all_logged")
			MyLogs("User added to Registered ndb:", self.username)
	
class Cookie():
	value = ""
	username = ""
	hashpassword = ""
	role = ""
	password = ""
	salt = ""

	def __init__(self, value=""):
		self.value = value
		if value:
			self.extract_value()

	def set_value(self, role, username, hashpassword):
		self.role = str(role)
		self.username = str(username)
		self.hashpassword = str(hashpassword)
	
	def stringify(self):
		self.value = "|".join([self.role, self.username, self.hashpassword])

	def send(self, http_self):
		self.stringify()
		http_self.response.set_cookie('schooltagging', self.value)
		MyLogs("Cookie sent", self.value)
			
	def extract_value(self):
		self.role = self.value.split("|")[0]
		self.username = self.value.split("|")[1]
		self.password = self.value.split("|")[2]
		self.salt = self.value.split("|")[3]
		self.hashpassword = self.password + "|" + self.salt
		#~ MyLogs("Info extracted from cookie")

class MyLogs():
	def __init__(self, *a):
		message = " ".join([str(chunk) for chunk in a])
		logging.info(str(message))
		
TODO = """
- create teacher dashboard
-- list of students logged
-- activity for each student
--- exercise delivered
--- response
- remove teacher/student drop down in the login page
- implement memcache also for messages
- when a channel is closed, remove the user from the LOGGED list.
- algorithm to send messages to be revisited to avoid dups.
- add all possible url to the handler (regular expressions?)
- allow only a teacher per session
- verify all channels are up by sending a pin sometime, 
		to remove from logged not responding ones
- when a channel is closed, remove the user from the LOGGED list.
- algorithm to send messages to be revisited to avoid dups.
- datastore writes too slow: to enhance memcache interface.

"""

EXERCISES_POOL = [
	{
		"sentence": "Of course, no man is entirely in his right mind at any time.",
		"to find": "article",
		},
	{
		"sentence": "Early to rise and early to bed makes a male healthy and wealthy and dead.",
		"to find": "pronom",
		},
	{
		"sentence": "Expect nothing. Live frugally on surprise.",
		"to find": "pronom",
		},
	{
		"sentence": "I'd rather be a lightning rod than a seismograph.",
		"to find": "pronom",
		},
	{
		"sentence": "Children are all foreigners.",
		"to find": "pronom",
		},
	]

MESSAGES = []

def pick_an_exercise():
	exercise = EXERCISES_POOL[1]
	return {
		"sentence": exercise["sentence"],
		"to find": exercise["to find"],
		"words": exercise["sentence"].split(" "),
		}

def get_all_exercises():
	return [{
		"sentence": exercise["sentence"],
		"to find": exercise["to find"],
		"words": exercise["sentence"].split(" "),
		} for exercise in EXERCISES_POOL]

def store_message(*a):
	message = {
		"username": a[0],
		"timestamp": a[1],
		"message": a[2],
		"type": "msg",
		}
	global MESSAGES
	MESSAGES.append(message)
	MyLogs("Message added to db --> ", message)
	return message

def select_template(role):
	assert role in ["student", "teacher"]
	if role == "student":
		return "student.html"
	elif role == "teacher":
		return "teacher.html"
				
def get_all_messages():
	return [message for message in MESSAGES]

def clear_messages():
	global MESSAGES
	MESSAGES = []
	MyLogs("Messages list cleared")

def broadcast_clear_messages():
	for user in Support().get_all_logged():
		message = {
					"type": "clear message history",
					}
		message = json.dumps(message)
		channel.send_message(user["username"], message)
	MyLogs("Clear messages list broadcasted")

def broadcast_message(message, sender):
	timestamp = strftime("%a, %d %b %H:%M:%S",localtime())
	message = store_message(sender, timestamp, message)
	for user in Support().get_all_logged():
		send_message_to_user(user["username"], message)
	MyLogs("Message broadcasted")

def send_message_to_user(username, message):
	message = json.dumps(message)
	channel.send_message(username, message)
	MyLogs("Message", message, "delivered to", username)

def broadcast_exercise_to_students(exercise):
	for user in Support().get_all_logged():
		send_exercise(user["username"], exercise)
	MyLogs("Exercise broadcasted")

def send_exercise(username, exercise):
	message = {
		"type": "exercise",
		"message": exercise,
		}
	message = json.dumps(message)
	channel.send_message(username, message)
	MyLogs("Exercise delivered to ", username)
	
def send_exercises_list(username):
	exercises = get_all_exercises()
	message = {
		"type": "exercises list",
		"message": exercises,
		}
	message = json.dumps(message)
	channel.send_message(username, message)
	MyLogs("Exercises list delivered to ", username)

def broadcast_user_connection_info(target_user, status):
	for user in Support().get_all_logged():
		if user["username"] != target_user:
			send_message_of_user_connection_info(
					target_user,
					status,
					user["role"],
					user["username"],
					)
	MyLogs("All messages of new connection sent")

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
	MyLogs("Message that the user is ", status, " delivered to ", recipient)

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
	
	def get_my_cookie(self):
		return self.request.cookies.get("schooltagging")
	
	def clear_my_cookie(self):
		cookie = Cookie(self.request.cookies.get("schooltagging"))
		if cookie.value:
			self.response.delete_cookie('schooltagging', path = '/')
			MyLogs("Cookie deleted")
		else:
			MyLogs("Cookie not existing")
		
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
		self.clear_my_cookie()
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
			all_registered = Support().get_all_registered()
			if username in [user["username"] for user in all_registered]:
				username_error = "That user already exists"
				self.write_signup(username,
						username_error,
						password_missing_error_sw,
						password_match_error_sw,
						)
			else:
				MyLogs("No errors, user allowed to be registered")
				role = self.request.get("role")
				hashpassword = make_pw_hash(username, password)
				new_user = RegisteredUser(
					username = username,
					hashpassword = hashpassword,
					role = role,
					)
				new_user.add()
				token = Support().create_a_channel(username)
				new_logged = Logged(
								username = username,
								role = role,
								token = token
								)
				new_logged.add()
				cookie = Cookie()
				cookie.set_value(role, username, hashpassword)
				cookie.send(self)
				self.redirect("/welcome")
				
class LoginPageHandler(MainHandler):
	def write_login(self, username = "", login_error = ""):
		self.render_page(
				"login.html",
				username = username,
				login_error = login_error,
				)

	def get(self):
		self.write_login()
	
	def post(self):
		self.clear_my_cookie()
		username = self.request.get("username")
		userpassword = self.request.get("password")
		role = self.request.get("role")
		if username == "" or userpassword == "":
			self.write_login(login_error = "Invalid login")
		else:
			db_password = Support().get_password_from_database(username)
			if db_password:
				salt = db_password.split('|')[1]
				login_password = make_pw_hash(username, userpassword, salt)
				if login_password == db_password:
					
					cookie = Cookie()
					cookie.set_value(role, username, login_password)
					cookie.send(self)

					self.redirect("/welcome")
			self.write_login(login_error = "Invalid login")

class LogoutPageHandler(MainHandler):
	def get(self):
		cookie = Cookie(self.get_my_cookie())
		if cookie.value:
			broadcast_user_connection_info(cookie.username, "close")
			self.clear_my_cookie()
			Support().remove_logged(cookie.username)
		self.redirect("/login")

class WelcomePageHandler(MainHandler):
	def write_welcome(self, template, username, role, token):
		self.render_page(
					template,
					username = username,
					role = role,
					token = token,
					logged = Support().get_all_logged(),
					messages = get_all_messages(),
					exercise = pick_an_exercise(),
					)

	def get(self):
		cookie = Cookie(self.get_my_cookie())
		if cookie.value:
			if Support().user_in_database(cookie.value):
				all_logged = Support().get_all_logged()
				if not cookie.username in [user["username"] for user in all_logged]:
					token = Support().create_a_channel(cookie.username)
					new_logged = Logged(
									username = cookie.username,
									role = cookie.role,
									token = token
									)
					new_logged.add()
				else:
					logged = Support().get_from_username(cookie.username)
					token = logged.token
				template = "welcome.html"
				self.write_welcome(
									template,
									cookie.username,
									cookie.role,
									token,
									)
			else:
				self.redirect("/login")
		else:
			self.redirect("/login")
		
class MessageHandler(MainHandler):
	def post(self):
		cookie = Cookie(self.get_my_cookie())
		message = self.request.get("message")
		if Support().user_in_database(cookie.value):
			if message:
				broadcast_message(message, cookie.username)
			#~ self.redirect("/welcome")
		else:
			self.redirect("/login")

class ExerciseListRequestHandler(MainHandler):
	def get(self):
		cookie = Cookie(self.get_my_cookie())
		if Support().user_in_database(cookie.value):
			MyLogs("Exercise List request from ", cookie.username)
			send_exercises_list(cookie.username)
		else:
			self.redirect("/login")

class ExerciseRequestHandler(MainHandler):
	def post(self):
		cookie = Cookie(self.get_my_cookie())
		if Support().user_in_database(cookie.value):
			MyLogs("Exercise request from ", cookie.username)
			exercise_number = int(self.request.get("exercise_number"))
			exercise = get_all_exercises()[exercise_number]
			broadcast_exercise_to_students(exercise)
		else:
			self.redirect("/login")

class WordChosenHandler(MainHandler):
	def post(self):
		cookie = Cookie(self.get_my_cookie())
		if Support().user_in_database(cookie.value):
			word_number = int(self.request.get("word_number"))
			MyLogs("word", word_number, "chosen from ", cookie.username)
		else:
			self.redirect("/login")
	
	
class ClearMessagesHandler(MainHandler):
	def get(self):
		clear_messages()
		broadcast_clear_messages()
		
class ConnectedHandler(MainHandler):
	def post(self):
		client_id = self.request.get('from')
		MyLogs("connected ID --> ", client_id)
		broadcast_user_connection_info(client_id, "open")

class DisconnectedHandler(MainHandler):
	def post(self):
		client_id = self.request.get('from')
		MyLogs("Disconnected ID --> ", client_id)
		broadcast_user_connection_info(client_id, "close")
		Support().remove_logged(client_id)

app = webapp2.WSGIApplication([
    ('/', LoginPageHandler),
    ('/signup', SignupPageHandler),
    ('/login', LoginPageHandler),
    ('/welcome', WelcomePageHandler),
    ('/logout', LogoutPageHandler),
    ('/message', MessageHandler),
    ('/_ah/channel/connected/', ConnectedHandler),
    ('/_ah/channel/disconnected/', DisconnectedHandler),
    ('/exercise_list_request', ExerciseListRequestHandler),
    ('/exercise_request', ExerciseRequestHandler),
    ('/clear_messages', ClearMessagesHandler),
    ("/word_clicked", WordChosenHandler),
	], debug=True)
