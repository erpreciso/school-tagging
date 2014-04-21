# coding: utf-8
# [school-tagging] webapp

import school_tagging_core_process as st
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

def get_exercise_list():
	lst = memcache.get("exercise_list")
	if not lst:
		lst = json.loads(open("lists/exercises.json").read())
		memcache.set("exercise_list", lst)
	return lst
	
class AppUser(ndb.Model):
	username = ndb.StringProperty()
	role = ndb.StringProperty()
	token = ndb.StringProperty()
	hashpassword = ndb.StringProperty()
	login_status = ndb.StringProperty()
	connection_status = ndb.StringProperty()
	addtime = ndb.DateTimeProperty(auto_now_add=True)
	
	def safe_put(self):
		if not memcache.flush_all():
			MyLogs("safe_put:memcache error: not flushed")
		#~ else:
			#~ MyLogs("safe_put:memcache flushed")
		return self.put()

class Classroom():
	teacher = None
	students = []

	def send_connection(self, login, action):
		if action == "open":
			type = "connected_user"
		elif action == "close":
			type = "disconnected_user"
		message = {
			"type": type,
			"username": login.username,
			}
		message = json.dumps(message)
		if login.username != self.teacher.username:
			channel.send_message(self.teacher.username, message)
			
	def __init__(self):
		self.teacher = None
		self.students = []
		self.populate()

	def populate(self):
		allusersquery = memcache.get("allusersquery")
		if allusersquery is not None:
			q = allusersquery
		else:
			q = AppUser.query()
			memcache.add("allusersquery", q)
		if q:
			for user in q:
				if user.role == "teacher":
					self.teacher = user
				elif user.role == "student" and \
						user.login_status == "logged" and \
						user not in self.students:
							self.students.append(user)
			return True
		else:
			return False

	def logged_students(self):
		result = []
		for student in self.students:
			if student.login_status == "logged":
				result.append(student.username)
		return result

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
			self.role = user.role
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
		key = new_user.safe_put()
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
			if appuser.safe_put():
				return True
			else:
				MyLogs("update_attr", attribute, ":safe put didn't work")
		else:
			MyLogs("update_attr", attribute, ":error. user not retrieved")
		return False
	
	def connect(self):
		self.connection_status = "connected"
		self.update_attr("connection_status")
		classroom = Classroom()
		classroom.send_connection(self, "open")
		
	def disconnect(self):
		self.connection_status = "not connected"
		self.login_status = "registered"
		self.update_attr("connection_status")
		self.update_attr("login_status")
		#~ classroom = Classroom()
		#~ classroom.send_connection(self, "close")
		if self.role == "student":
			st.disconnect_student(self.username)

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
		else:
			MyLogs("Username not in database")
			return False

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
		http_self.response.set_cookie('schooltagging-user', self.value)
		#~ MyLogs("Cookie sent", self.value)
			
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
	
	def get_user_cookie(self):
		return self.request.cookies.get("schooltagging-user")
	
	def set_lesson_cookie(self, strLesson):
		self.response.set_cookie('schooltagging-lesson', strLesson)
	
	def get_lesson_cookie(self):
		return self.request.cookies.get("schooltagging-lesson")
		
	def valid_user(self):
		""" check if the request is coming from a valid user.
		return the login object if valid, else False
		
		"""
		cookie = Cookie(self.get_user_cookie())
		if cookie.value:
			login = Login()
			login.username = cookie.username
			login.hashpassword = cookie.hashpassword
			if login.valid_user():
				if login.login():
					return login
				else:
					MyLogs("valid_user:login failed. try again")
			else:
				MyLogs("valid_user:Invalid cookie")
		else:
			MyLogs("valid_user:cookie is not existing or has not value")
		return False
		
	def clear_cookie(self):
		""" clear my cookie if existing.
		input=server response
		return True if cookie existed and has been eliminated,
		return False if cookie wasn't existing
		
		"""
		self.response.delete_cookie('schooltagging-lesson', path = '/')
		cookie = Cookie(self.request.cookies.get("schooltagging-user"))
		if cookie.value:
			self.response.delete_cookie('schooltagging-user', path = '/')
			return True
		else:
			return False

class WelcomePageHandler(MainHandler):
	def write_welcome(self, login):
		classroom = Classroom()
		if login.role == "teacher":
			#~ exercise = Exercise()
			MyLogs("hit")
			self.render_page(
						"teacher.html",
						username = login.username,
						token = login.token,
						#~ logged = classroom.logged_students(),
						#~ exercises_types = exercise.types()
						)
		elif login.role == "student":
			self.render_page(
						"student.html",
						username = login.username,
						token = login.token,
						)

	def get(self):
		login = self.valid_user()
		if login:
			self.write_welcome(login)
		else:
			self.redirect("/check/in")		

class ConnectionHandler(MainHandler):
	def post(self, action):
		username = self.request.get('from')
		login = Login(username=username)
		if action == "connected":
			login.connect()
		elif action == "disconnected":
			login.disconnect()

class LoginPageHandler(MainHandler):
	error = ""

	def enter_lesson(self, login):
		if login.role == "teacher":
			#~ st.add_teacher(login.username)
			self.redirect("/lesson/start_lesson")
		elif login.role == "student":
			#~ st.add_student(login.username)
			self.redirect("/lesson/join_lesson")
		else:
			raise Exception("Login role not valid")
	
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
					self.enter_lesson(login)
					return
				else:
					self.error = "Login didn't work. Try again"
			else:
				self.error = "Invalid login"
		else:
			self.error = "Username not valid"
		self.write_check_page("login.html")

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
							self.enter_lesson(login)
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
		self.write_check_page("signup.html")

	def logout(self):
		cookie = Cookie(self.get_user_cookie())
		if cookie.value:
			login = Login()
			login.username = cookie.username
			login.hashpassword = cookie.hashpassword
			if login.valid_user():
				login.logout()
				self.clear_cookie()
			else:
				MyLogs("Invalid cookie")
		else:
			MyLogs("cookie is not existing or has not value")
		self.redirect("/check/in")
		
class DashboardHandler(MainHandler):
	def post(self, action):
		login = self.valid_user()
		if login:
			if action == "exercise_request":
				exercise_id = self.request.get("id")
				exercise_type = self.request.get("type")
				exercise = Exercise()
				exercise.select(exercise_id, exercise_type)
				exercise.send_to_classroom()
				exercise.send_to_teacher()
		else:
			MyLogs("user seems not valid")
			self.redirect("/check/in")

	def get(self, action):
		login = self.valid_user()
		if login:
			if action == "get_exercises_list":
				exercise = Exercise()
				exercise.send_list(login)
			elif action == "get_logged_students":
				classroom = Classroom()
				
		else:
			MyLogs("user seems not valid")
			self.redirect("/check/in")

class Exercise():
	selected = None
	list = None
	exercise_type = None
	
	def __init__(self):
		self.list = json.loads(open("lists/exercises.json").read())

	def send_list(self, login):
		message = {
					"type": "exercises_list",
					"message": self.list,
					}
		message = json.dumps(message)
		channel.send_message(login.username, message)

	def types(self):
		return [
			{"id": "type_1", "name": "find the element"},
			{"id": "type_2", "name": "recognize the word"},
			]

	def select(self, exercise_id, exercise_type):
		self.selected = self.list[exercise_id]
		self.exercise_type = exercise_type
	
	def send_to_classroom(self):
		classroom = Classroom()
		message = {
			"type": "exercise",
			"message": {
				"exercise": self.selected,
				"exercise_type": self.exercise_type,
				},
			}
		message = json.dumps(message)
		for student in classroom.logged_students():
			channel.send_message(student, message)

	def send_to_teacher(self):
		classroom = Classroom()
		message = {
			"type": "exercise",
			"message": {
				"exercise": self.selected,
				"exercise_type": self.exercise_type,
				},
			}
		message = json.dumps(message)
		channel.send_message(classroom.teacher.username, message)

class ExerciseHandler(MainHandler):
	def post(self, action):
		login = self.valid_user()
		if login:
			classroom = Classroom()
			if action == "word_clicked":
				word_number = int(self.request.get("word_number"))
				message = {
					"type": "student_choice",
					"content": {
						"student": login.username,
						"choice": word_number,
						"etype": "type_1",
						},
					}
			elif action == "type_answer":
				answer = self.request.get("answer")
				message = {
					"type": "student_choice",
					"content": {
						"student": login.username,
						"choice": answer,
						"etype": "type_2",
						},
					}
			message = json.dumps(message)
			channel.send_message(classroom.teacher.username, message)
		else:
			self.redirect("/check/in")

class SessionHandler(MainHandler):
	def post(self, command):
		login = self.valid_user()
		if login:
			if command == "exercise_request":
				type = self.request.get("type")
				id = self.request.get("id")
				exerciseList = get_exercise_list()
				objLesson = st.get_lesson(self.get_lesson_cookie())
				objExercise = [e for e in exerciseList if e["id"] == id][0]
				strIdSession = st.add_session(objLesson, objExercise)
				objSession = st.get_session(strIdSession)
				self.send_exercise_to_classroom(objExercise, objSession.students)
	
	def send_exercise_to_classroom(self, exercise, students):
		message = {
			"type": "exercise",
			"message": {
				"exercise": exercise,
				},
			}
		message = json.dumps(message)
		for student in students:
			channel.send_message(student, message)

class LessonHandler(MainHandler):

	def post(self, command):
		login = self.valid_user()
		if login:
			if command == "start_lesson":
				assert login.role == "teacher"
				lesson_name = self.request.get("lesson")
				st.add_lesson(login.username, lesson_name)
				self.set_lesson_cookie(lesson_name)
				return self.redirect("/lesson/start_session")
			elif command == "join_lesson":
				assert login.role == "student"
				teacher_name = self.request.get("teacher")
				lesson_name = st.join_lesson(login.username, teacher_name)
				self.set_lesson_cookie(lesson_name)
				return self.redirect("/lesson/join_session")
		else:
			return self.redirect("/check/in")

	def get(self, command):
		login = self.valid_user()
		if login:
			if command == "start_session":
				lesson_name = self.get_lesson_cookie()
				exercise_list = get_exercise_list()
				students_list = st.get_current_lesson_student_list(login.username)
				self.render_page("start_session.html",
							username = login.username,
							token = login.token,
							exercise_list = exercise_list,
							students_list = students_list,
							)
				return
							
			elif command == "start_lesson":
				assert login.role == "teacher"
				self.render_page("start_lesson.html",
							username = login.username,
							token = login.token,
							)
				return
			elif command == "join_lesson":
				assert login.role == "student"
				current_teachers = st.get_teachers_list()
				self.render_page("join_lesson.html",
							username = login.username,
							token = login.token,
							current_teachers = current_teachers,
							)
				return
			elif command == "join_session":
				assert login.role == "student"
				self.render_page("join_session.html",
							username = login.username,
							token = login.token,
							)
		else:
			self.redirect("/check/in")
	
app = webapp2.WSGIApplication([
	webapp2.Route(
			r'/dashboard/<action>',
			handler=DashboardHandler,
			name="dashboard"),
	webapp2.Route(
			r'/check/<action>',
			handler=LoginPageHandler,
			name="login"),
	webapp2.Route(
			r'/welcome',
			handler=WelcomePageHandler,
			name="welcome"),
	webapp2.Route(
			r'/exercise/<action>',
			handler=ExerciseHandler,
			name="exercise"),
	webapp2.Route(
			r'/_ah/channel/<action>/',
			handler=ConnectionHandler,
			name="connection"),
	webapp2.Route(
			r'/lesson/<command>',
			handler=LessonHandler,
			name="lesson"),
	webapp2.Route(
			r'/session/<command>',
			handler=SessionHandler,
			name="session"),
			])

