# coding: utf-8
# [school-tagging] webapp

import lessonLogic as logic
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

def getExerciseList():
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
	loginStatus = ndb.StringProperty()
	connectionStatus = ndb.StringProperty()
	addtime = ndb.DateTimeProperty(auto_now_add=True)
	
	def safePut(self):
		memcache.add("%s:appuser" % self.username, self)
		return self.put()

class User():
	""" create a Login obj to manage all login stuffs """
	#~ username = ""
	#~ password = ""
	#~ verify_password = "foobar"
	#~ hashpassword = ""
	#~ salt = ""
	#~ role = ""
	#~ connection_status = ""
	#~ token = ""
	#~ login_status = ""
	RE_USERNAME = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
	RE_PASSWORD = r"^.{3,20}$"
	
	def __init__(self, username="", salt=""):
		self.salt = salt or self.make_salt()
		if username:
			self.username = username
			user = self.getAppUser()
			self.role = user.role
			self.connectionStatus = user.connectionStatus
	
	def setUsername(self, username):
		self.username = username
		return
	def setPassword(self, password):
		self.password = password
		self.hashpassword = ""
		return
	def setVerifyPassword(self, verify):
		self.verifyPassword = verify
		return
	def setRole(self, role):
		self.role = role
		return
		
	def make_salt(self):
		return ''.join(random.choice(string.letters) for x in xrange(5))
	
	def makeHashpassword(self):
		cript = self.username + self.password + self.salt
		encr_password = hashlib.sha256(cript).hexdigest()
		self.hashpassword = "%s|%s" % (encr_password, self.salt)

	def twoPasswordsMatch(self):
		""" return True if the two inserted psw match. """
		match = self.password == self.verifyPassword
		if match:
			return True
		else:
			MyLogs("The two passwords don't match")

	def passwordMatchesRE(self):
		""" return True if the psw matches the regular expression. """
		re_password = re.compile(self.RE_PASSWORD)
		if re_password.match(self.password):
			return True
		else:
			MyLogs("Password doesn't match the regex")
			return False
	
	def passwordIsValid(self):
		""" return True if the password matches the two rules above.
		also setup the hashpassword.
		
		"""
		result = self.passwordMatchesRE() and self.twoPasswordsMatch()
		if result:
			self.makeHashpassword()
			return True
		else:
			MyLogs("Password rejected. See log above")
			return False

	def usernameIsValid(self):
		""" return True if the inserted username matchs the re. """
		re_username = re.compile(self.RE_USERNAME)
		if re_username.match(self.username):
			return True
		else:
			MyLogs("Username rejected (it doesn't match the regex)")
			return False
	
	def getChannel(self):
		""" creates a channel and return the token. """
		if hasattr(self, "token") and self.token:
			return self.token
		else:
			token = channel.create_channel(self.username)
			if token:
				self.token = token
				return token
			else:
				MyLogs("Channel creation failure")
				return False

	def signup(self):
		""" signup the user.
		insert the user in the ndb with loginStatus "registered".
		return the ndb key
		
		"""
		appuser = AppUser(id=self.username)
		appuser.username = self.username
		appuser.role = self.role
		appuser.hashpassword = self.hashpassword
		appuser.loginStatus = "registered"
		key = appuser.safePut()
		
		return key

	def login(self):
		""" login the user.
		
		input=user ndb object
		change the user login_status from "registered" to "logged".
		change it in the db
		create the channel for the API
		return True if success
		
		"""
		if self.getChannel():
			self.connect()
			self.loginStatus = "logged"
			if self.updateAttr("loginStatus") and \
						self.updateAttr("token"):
				return True
		return False
	
	def logout(self):
		self.disconnect()
		self.loginStatus = "registered"
		if self.updateAttr("loginStatus"):
			return True
		else:
			return False

	def usernameAlreadyExisting(self):
		if self.getAppUser():
			return True
		else:
			return False

	def getAppUser(self):
		""" return the user object from memcache or from ndb.
		input=the user username.
		
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
		
	def updateAttr(self, attribute):
		appuser = self.getAppUser()
		if appuser:
			setattr(appuser, attribute, getattr(self, attribute))
			if appuser.safePut():
				return True
			else:
				MyLogs("updateAttr", attribute, ":safe put didn't work")
		else:
			MyLogs("updateAttr", attribute, ":error. user not retrieved")
		return False
	
	def connect(self):
		self.connection_status = "connected"
		self.updateAttr("connection_status")
		if self.role == "student":
			logic.connect_student(self.username)
		
	def disconnect(self):
		self.connectionStatus = "not connected"
		self.loginStatus = "registered"
		self.updateAttr("connectionStatus")
		self.updateAttr("loginStatus")
		if self.role == "student":
			logic.disconnect_student(self.username)

	def validUser(self):
		""" check if the user is entitled to login.
		input=username string and password not hashed
		return True if user is valid.
		
		"""
		user = self.getAppUser()
		if user:
			if self.hashpassword == "":
				self.salt = user.hashpassword.split("|")[1]
				self.makeHashpassword()
			if self.hashpassword == user.hashpassword:
				self.role = user.role
				self.token = user.token
				self.connectionStatus = user.connectionStatus
				return True
			else:
				MyLogs("Password incorrect for user", self.username)
		else:
			MyLogs("Username not in database")
			return False

class Cookie():

	def __init__(self, value=""):
		self.username = ""
		self.hashpassword = ""
		self.role = ""
		self.password = ""
		self.salt = ""
		self.value = value
		if value:
			self.extractValue()

	def setValue(self, role, username, hashpassword):
		self.role = str(role)
		self.username = str(username)
		self.hashpassword = str(hashpassword)
	
	def stringify(self):
		self.value = "|".join([self.role, self.username, self.hashpassword])

	def send(self, http_self):
		self.stringify()
		http_self.response.set_cookie('schooltagging-user', self.value)
			
	def extractValue(self):
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
	
	def getUserCookie(self):
		return self.request.cookies.get("schooltagging-user")
	
	def setLessonCookie(self, strLesson):
		self.response.set_cookie('schooltagging-lesson', strLesson)
	
	def getLessonCookie(self):
		return self.request.cookies.get("schooltagging-lesson")
		
	def validUser(self):
		""" check if the request is coming from a valid user.
		return the login object if valid, else False
		
		"""
		cookie = Cookie(self.getUserCookie())
		if cookie.value:
			user = User()
			user.username = cookie.username
			user.hashpassword = cookie.hashpassword
			if user.validUser():
				if user.login():
					return user
				else:
					MyLogs("valid_user:login failed. try again")
			else:
				MyLogs("valid_user:Invalid cookie")
		else:
			MyLogs("valid_user:cookie is not existing or has not value")
		return False
		
	def clearCookies(self):
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

class ConnectionHandler(MainHandler):
	def post(self, action):
		username = self.request.get('from')
		user = User(username=username)
		if action == "connected":
			user.connect()
		elif action == "disconnected":
			user.disconnect()

class LoginPageHandler(MainHandler):
	error = ""

	def enterLesson(self, user):
		if user.role == "teacher":
			#~ logic.add_teacher(login.username)
			self.redirect("/lesson/start_lesson")
		elif user.role == "student":
			#~ logic.add_student(login.username)
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
		self.clearCookies()
		if action == "up":
			self.signup()
		elif action == "in":
			self.login()
		
	def login(self):
		user = User()
		user.setUsername(self.request.get("username"))
		user.setPassword(self.request.get("password"))
		if user.usernameIsValid():
			#~ MyLogs("username is valid. move ahead")
			if user.validUser():
				#~ MyLogs("user in database and entitled to login. move")
				if user.login():
					#~ MyLogs("also login success!cookie now, and go")
					cookie = Cookie()
					cookie.setValue(
								user.role,
								user.username,
								user.hashpassword,
								)
					cookie.send(self)
					self.enterLesson(user)
					return
				else:
					self.error = "Login didn't work. Try again"
			else:
				self.error = "Invalid login"
		else:
			self.error = "Username not valid"
		self.write_check_page("login.html")

	def signup(self):
		user = User()
		user.setUsername(self.request.get("username"))
		user.setPassword(self.request.get("password"))
		user.setVerifyPassword(self.request.get("verify"))
		user.setRole(self.request.get("role"))
		if not user.usernameAlreadyExisting():
			MyLogs("username not yet existing. move ahead")
			if user.usernameIsValid():
				MyLogs("username is valid. move ahead")
				if user.passwordIsValid():
					MyLogs("password is valid. move ahead")
					if user.signup():
						MyLogs("signup succesful. move ahead")
						if user.login():
							MyLogs("also login success!cookie now, and go")
							cookie = Cookie()
							cookie.setValue(
										user.role,
										user.username,
										user.hashpassword,
										)
							cookie.send(self)
							self.enterLesson(user)
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
		cookie = Cookie(self.getUserCookie())
		if cookie.value:
			user = User()
			user.username = cookie.username
			user.hashpassword = cookie.hashpassword
			if user.validUser():
				user.logout()
				self.clearCookies()
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


class ExerciseHandler(MainHandler):
	def post(self, strExerciseType):
		user = self.validUser()
		if user:
			assert user.role == "student"
			objStudent = logic.get_student(user.username)
			objLesson = logic.get_lesson(self.getLessonCookie())
			strTeacher = objLesson.teacher
			strAnswer = self.request.get("answer")
			logic.add_answer(objStudent, objLesson, strExerciseType, strAnswer)
			message = {
					"type": "student_choice",
					"content": {
						"student": user.username,
						"answer": strAnswer,
						},
					}
			message = json.dumps(message)
			channel.send_message(strTeacher, message)
		else:
			self.redirect("/check/in")

class SessionHandler(MainHandler):
	def post(self, command):
		user = self.validUser()
		if user:
			if command == "exercise_request":
				type = self.request.get("type")
				id = self.request.get("id")
				exerciseList = getExerciseList()
				objLesson = logic.get_lesson(self.getLessonCookie())
				objExercise = [e for e in exerciseList if e["id"] == id][0]
				objType = [t for t in objExercise["goals"] if t["type"] == type][0]
				strIdSession = logic.add_session(objLesson, objExercise, objType)
				objSession = logic.get_session(strIdSession)
				self.send_exercise_to_classroom(
							objExercise,
							objSession.students,
							objType,
							)
	
	def send_exercise_to_classroom(self, exercise, students, type):
		message = {
			"type": "exercise",
			"message": {
				"exercise": exercise,
				"type": type,
				},
			}
		message = json.dumps(message)
		for student in students:
			channel.send_message(student, message)

class LessonHandler(MainHandler):

	def post(self, command):
		user = self.validUser()
		if user:
			if command == "start_lesson":
				assert user.role == "teacher"
				lesson_name = self.request.get("lesson")
				logic.add_lesson(user.username, lesson_name)
				self.set_lesson_cookie(lesson_name)
				return self.redirect("/lesson/start_session")
			elif command == "join_lesson":
				assert user.role == "student"
				teacher_name = self.request.get("teacher")
				lesson_name = logic.join_lesson(user.username, teacher_name)
				self.setLessonCookie(lesson_name)
				return self.redirect("/lesson/join_session")
		else:
			return self.redirect("/check/in")

	def get(self, command):
		user = self.validUser()
		if user:
			if command == "start_session":
				lessonName = self.getLessonCookie()
				exerciseList = getExerciseList()
				studentsList = logic.get_current_lesson_student_list(user.username)
				self.render_page("start_session.html",
							username = user.username,
							token = user.token,
							exercise_list = exerciseList,
							students_list = studentsList,
							)
				return
							
			elif command == "start_lesson":
				assert user.role == "teacher"
				self.render_page("start_lesson.html",
							username = user.username,
							token = user.token,
							)
				return
			elif command == "join_lesson":
				assert user.role == "student"
				currentTeachers = logic.get_teachers_list()
				self.render_page("join_lesson.html",
							username = user.username,
							token = user.token,
							current_teachers = currentTeachers,
							)
				return
			elif command == "join_session":
				assert user.role == "student"
				logic.connect_student(user.username)
				self.render_page("join_session.html",
							username = user.username,
							token = user.token,
							)
		else:
			self.redirect("/check/in")

class DataHandler(MainHandler):

	def get(self, command):
		user = self.validUser()
		if user:
			if command == "exercises_list":
				message = {
					"type": "exercises_list",
					"message": getExerciseList(),
					}
				message = json.dumps(message)
				channel.send_message(user.username, message)
		else:
			return self.redirect("/check/in")

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
			r'/exercise/<strExerciseType>',
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
	webapp2.Route(
			r'/data/<command>',
			handler=DataHandler,
			name="data"),
			])

