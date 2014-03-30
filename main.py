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
	
	def get_role_from_registered(self, username):
		role = None
		for user in Support().get_all_registered():
			if user["username"] == username:
				role = user["role"]
		if role:
			MyLogs("Role retrieved for ", username)
			return role
		else:
			MyLogs("Role not existing for ", username)
			return role
		
	def get_the_teacher(self):
		"""return the username of the teacher"""
		all_logged = Support().get_all_logged()
		result = None
		for logged in all_logged:
			if logged["role"] == "teacher":
				result = logged["username"]
		if result:
			MyLogs("Teacher is", result)
			return result
		else:
			MyLogs("No teacher found")
			return None
		
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
	
	def send_list_of_students(self, requester):
		lst = [user["username"] for user in Support().get_all_logged() \
						if user["role"] == "student"]
		
		message = {
			"type": "students list",
			"list": lst,
			}
		message = json.dumps(message)
		channel.send_message(requester, message)
		MyLogs("List sent to", requester)

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

class AppUser(ndb.Model):
	username = ndb.StringProperty()
	role = ndb.StringProperty()
	token = ndb.StringProperty()
	hashpassword = ndb.StringProperty()
	login_status = ndb.StringProperty()
	connection_status = ndb.StringProperty()
	addtime = ndb.DateTimeProperty(auto_now_add=True)

def get_all_logged():
	""" return list of logged [{all user info}] """
	pass

def get_user_info(username):
	""" return user info from logged list
	input=username string
	return {
				role,
				username,
				hashpassword,
				token,
				login_status,
				addtime,
			}
	
	"""
	pass

	
class Login():
	""" create a Login obj to manage all login stuffs """
	username = ""
	password = ""
	verify_password = "foobar"
	hashpassword = ""
	salt = ""
	role = ""
	connection_status = ""
	token = ""
	login_status = ""
	re_username = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
	re_password = r"^.{3,20}$"
	
	def __init__(self, username="", salt=""):
		self.salt = salt or self.make_salt()
		if username:
			self.username = username
			user = self.get_user()
			MyLogs(user)
			self.connection_status = user.connection_status
			
			
	def make_salt(self):
		return ''.join(random.choice(string.letters) for x in xrange(5))
	
	def make_hashpassword(self):
		cript = self.username + self.password + self.salt
		encr_password = hashlib.sha256(cript).hexdigest()
		self.hashpassword = "%s|%s" % (encr_password, self.salt)

	def two_passwords_match(self):
		""" return True if the two inserted psw match. """
		match = self.password == self.verify_password
		if match:
			return True
		else:
			MyLogs("The two passwords don't match")

	def password_matches_re(self):
		""" return True if the psw matches the regular expression. """
		re_password = re.compile(self.re_password)
		if re_password.match(self.password):
			return True
		else:
			MyLogs("Password doesn't match the regex")
			return False
	
	def password_is_valid(self):
		""" return True if the password matches the two rules above.
		also setup the hashpassword.
		
		"""
		result = self.password_matches_re() and self.two_passwords_match()
		if result:
			self.make_hashpassword()
			return True
		else:
			MyLogs("Password rejected. See log above")
			return False

	def username_is_valid(self):
		""" return True if the inserted username matchs the re. """
		re_username = re.compile(self.re_username)
		if re_username.match(self.username):
			return True
		else:
			MyLogs("Username rejected (it doesn't match the regex)")
			return False
	
	def build_channel(self):
		""" creates a channel and return the token. """
		token = channel.create_channel(self.username)
		if token:
			self.token = token
			return True
		else:
			MyLogs("Channel creation failure")
			return False

	def signup(self):
		""" signup the login.
		insert the user in the ndb with login_status "registered".
		return the ndb key
		
		"""
		new_user = AppUser()
		new_user.username = self.username
		new_user.role = self.role
		new_user.hashpassword = self.hashpassword
		new_user.login_status = "registered"
		key = new_user.put()
		memcache.add("%s:appuser" % self.username, new_user)
		return key

	def login(self):
		""" login the user.
		
		input=user ndb object
		change the user login_status from "registered" to "logged".
		change it in the db
		create the channel for the API
		return True if success
		
		"""
		if self.build_channel():
			self.login_status = "logged"
			if self.update_attr("login_status") and \
						self.update_attr("token"):
				return True
		return False
	
	def logout(self):
		self.disconnect()
		self.login_status = "registered"
		if self.update_attr("login_status"):
			return True
		else:
			return False

	def username_already_existing(self):
		if self.get_user():
			return True
		else:
			return False

	def get_user(self):
		""" return the user object from memcache or from ndb.
		input=the login username.
		
		"""
		user = memcache.get("%s:appuser" % self.username)
		if user is not None:
			return user
		else:
			q = AppUser.query(AppUser.username == self.username)
			if q.get():
				ndbuser = q.get()
				memcache.add("%s:appuser" % self.username, ndbuser)
				return ndbuser
			else:
				return None
		
	def update_attr(self, attribute):
		appuser = self.get_user()
		if appuser:
			setattr(appuser, attribute, getattr(self, attribute))
			if appuser.put() and \
					memcache.replace("%s:appuser" % self.username, appuser):
				return True
		MyLogs("attribute update", attribute,"not successful")
		return False
	
	def connect(self):
		self.connection_status = "connected"
		self.update_attr("connection_status")
		
	def disconnect(self):
		self.connection_status = "not connected"
		self.update_attr("connection_status")

	def valid_user(self):
		""" check if the user is entitled to login.
		input=username string and password not hashed
		return True if user is valid.
		
		"""
		user = self.get_user()
		if user:
			if self.hashpassword == "":
				self.salt = user.hashpassword.split("|")[1]
				self.make_hashpassword()
			if self.hashpassword == user.hashpassword:
				self.role = user.role
				self.token = user.token
				self.connection_status = user.connection_status
				return True
			else:
				MyLogs("Password incorrect for user", self.username)
				MyLogs("Correct one should be", user.hashpassword)
		else:
			MyLogs("Username not in database")
			return False


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
- don't send the exercise answer!
- logged datastore is not working (dups, memcache)
- recast exercises functions
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
		"id": 1,
		"sentence": "Of course, no man is entirely in his right mind at any time.",
		"to find": "verb",
		"answer": 4,
		},
	{
		"id": 2,
		"sentence": "Early to rise and early to bed makes a male healthy and wealthy and dead.",
		"to find": "article",
		"answer": 8,
		},
	{
		"id": 3,
		"sentence": "Expect nothing. Live frugally on surprise.",
		"to find": "adverb",
		"answer": 3,
		},
	{
		"id": 4,
		"sentence": "I'd rather be a lightning rod than a seismograph.",
		"to find": "pronom",
		"answer": 0,
		},
	{
		"id": 5,
		"sentence": "Children are all foreigners.",
		"to find": "subject",
		"answer": 0,
		},
	]

MESSAGES = []

def pick_an_exercise():
	exercise = EXERCISES_POOL[1]
	return {
		"sentence": exercise["sentence"],
		"to find": exercise["to find"],
		"answer": exercise["answer"],
		"id": exercise["id"],
		"words": exercise["sentence"].split(" "),
		}

def get_all_exercises():
	return [{
		"sentence": exercise["sentence"],
		"to find": exercise["to find"],
		"answer": exercise["answer"],
		"id": exercise["id"],
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

def send_message_to_teacher(message):
	teacher = Support().get_the_teacher()
	assert teacher
	send_message_to_user(teacher, message)
	MyLogs("Message", message, "delivered to the teacher")

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
	
	def valid_cookie(self):
		""" get cookie info from the server response.
		input=server response
		return obj containing user info, or False
		
		"""
		pass
		
	def clear_cookie(self):
		""" clear my cookie if existing.
		input=server response
		return True if cookie existed and has been eliminated,
		return False if cookie wasn't existing
		
		"""
		cookie = Cookie(self.request.cookies.get("schooltagging"))
		if cookie.value:
			self.response.delete_cookie('schooltagging', path = '/')
			return True
		else:
			return False

class WelcomePageHandler(MainHandler):
	
	def write_welcome(self, cookie, token):
		self.render_page(
					"welcome.html",
					username = cookie.username,
					role = cookie.role,
					token = token,
					#~ logged = Support().get_all_logged(),
					#~ messages = get_all_messages(),
					#~ exercise = pick_an_exercise(),
					)

	def get(self):
		cookie = Cookie(self.get_my_cookie())
		if cookie.value:
			MyLogs("habeamus cookie. move ahead")
			login = Login()
			login.username = cookie.username
			login.hashpassword = cookie.hashpassword
			if login.valid_user():
				MyLogs("cookie verified. move")
				if login.login():
					MyLogs("login successful. go")
					self.write_welcome(cookie, login.token)
					return
				else:
					MyLogs("login failed. try again")
			else:
				MyLogs("Invalid cookie")
		else:
			MyLogs("cookie is not existing or has not value")
		self.redirect("/check/in")
		
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
			message = {
				"type": "student choice",
				"content": {
					"student": cookie.username,
					"choice": word_number,
					},
				}
			send_message_to_teacher(message)
		else:
			self.redirect("/login")
	
class ClearMessagesHandler(MainHandler):
	def get(self):
		clear_messages()
		broadcast_clear_messages()
		
class ConnectionHandler(MainHandler):
	def post(self, action):
		username = self.request.get('from')
		login = Login(username=username)
		if action == "connected":
			login.connect()
		elif action == "disconnected":
			login.disconnect()

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

class GetLoggedListHandler(MainHandler):
	def get(self):
		cookie = Cookie(self.get_my_cookie())
		if Support().user_in_database(cookie.value):
			MyLogs("Students List request from ", cookie.username)
			Support().send_list_of_students(cookie.username)
		else:
			self.redirect("/login")

class LoginPageHandler(MainHandler):
	
	error = ""
	
	def write_check_page(self, template):
		self.render_page(template, error=self.error)

	def get(self, action):
		if action == "up":
			template = "signup.html"
		elif action == "in":
			template = "login.html"
		elif action == "out":
			self.logout()
			template = "login.html"
		self.write_check_page(template)
		
	def post(self, action):
		self.clear_cookie()
		if action == "up":
			self.signup()
		elif action == "in":
			self.login()
		
	def login(self):
		login = Login()
		login.username = self.request.get("username")
		login.password = self.request.get("password")
		if login.username_is_valid():
			MyLogs("username is valid. move ahead")
			if login.valid_user():
				MyLogs("user in database and entitled to login. move")
				if login.login():
					MyLogs("also login success!cookie now, and go")
					cookie = Cookie()
					cookie.set_value(
								login.role,
								login.username,
								login.hashpassword,
								)
					cookie.send(self)
					self.redirect("/welcome")
					return
				else:
					self.error = "Login didn't work. Try again"
			else:
				self.error = "Invalid login"
		else:
			self.error = "Username not valid"
		self.write_check_page("in")

	def signup(self):
		login = Login()
		login.username = self.request.get("username")
		login.password = self.request.get("password")
		login.verify_password = self.request.get("verify")
		login.role = self.request.get("role")
		if not login.username_already_existing():
			MyLogs("username not yet existing. move ahead")
			if login.username_is_valid():
				MyLogs("username is valid. move ahead")
				if login.password_is_valid():
					MyLogs("password is valid. move ahead")
					if login.signup():
						MyLogs("signup succesful. move ahead")
						if login.login():
							MyLogs("also login success!cookie now, and go")
							cookie = Cookie()
							cookie.set_value(
										login.role,
										login.username,
										login.hashpassword,
										)
							cookie.send(self)
							self.redirect("/welcome")
							return
						else:
							self.error = "Login didn't work. Try again"
					else:
						self.error = "Signup didn't work. Try again"
				else:
					self.error = "Password not valid"
			else:
				self.error = "Username not valid"
		else:
			self.error = "Username already existing"
		self.write_check_page("up")

	def logout(self):
		cookie = Cookie(self.get_my_cookie())
		if cookie.value:
			MyLogs("habeamus cookie. move ahead")
			login = Login()
			login.username = cookie.username
			login.hashpassword = cookie.hashpassword
			if login.valid_user():
				MyLogs("cookie verified. move")
				#~ broadcast_user_connection_info(cookie.username, "close")
				login.logout()
				self.clear_cookie()
			else:
				MyLogs("Invalid cookie")
		else:
			MyLogs("cookie is not existing or has not value")
		self.redirect("/check/in")
		

app = webapp2.WSGIApplication([
    ('/', LoginPageHandler),
    ('/check/(in|out|up)', LoginPageHandler),
    ('/welcome', WelcomePageHandler),
    ('/message', MessageHandler),
    ('/_ah/channel/(connected|disconnected)/', ConnectionHandler),
    ('/exercise_list_request', ExerciseListRequestHandler),
    ('/exercise_request', ExerciseRequestHandler),
    ('/clear_messages', ClearMessagesHandler),
    ("/word_clicked", WordChosenHandler),
    ("/get_logged", GetLoggedListHandler),
	], debug=True)
