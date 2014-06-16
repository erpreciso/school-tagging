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
	#~ loginStatus = ndb.StringProperty()

class User():
	RE_USERNAME = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
	RE_PASSWORD = r"^.{3,20}$"
	
	def __init__(self):
		#~ self.salt = self.makeSalt()
		self.username = ""
		self.password = ""
		self.hashpassword = ""
		self.role = ""
		self.token = ""
		self.salt = ""
		#~ self.loginStatus = ""
	
	#~ def __init__(self, salt=""):
		#~ self.salt = salt or self.makeSalt()
		#~ if username:
			#~ self.username = username
			#~ user = self.getAppUser()
			#~ if user:
				#~ self.role = user.role
				#~ self.loginStatus = user.loginStatus
				#~ self.token = user.token
			#~ else:
				#~ MyLogs("User constructor didn't work")
	def save(self):
		appuser = AppUser(id=self.username)
		appuser.username = self.username
		appuser.role = self.role
		appuser.hashpassword = self.hashpassword
		appuser.token = self.token
		#~ appuser.loginStatus = self.loginStatus
		key = appuser.put()
		memcache.set("%s:appuser" % self.username, self)
		return key
		
	def get(self):
		"""overwrite self with appuser from ndb. return true if OK"""
		appuser = memcache.get("%s:appuser" % self.username)
		if appuser is None:
			q = AppUser.query(AppUser.username == self.username)
			if q.get():
				appuser = q.get()
				memcache.add("%s:appuser" % self.username, appuser)
			else:
				MyLogs("User.get: Username not found in ndb")
				return None
		if self.hashpassword == "":
			self.salt = appuser.hashpassword.split("|")[1]
			self.makeHashpassword()
		if self.hashpassword == appuser.hashpassword:
			self.role = appuser.role
			self.token = appuser.token
			return True
		else:
			MyLogs("User.get: password in db doesn't match")
			return False
	
	def setUsername(self, username):
		self.username = username
		return
	
	def setPassword(self, password):
		self.password = password
		return
		
	def setHashpassword(self, hashpassword):
		self.hashpassword = hashpassword
		return
	
	def setVerifyPassword(self, verify):
		self.verifyPassword = verify
		return
	
	def setRole(self, role):
		self.role = role
		return
		
	def makeSalt(self):
		return ''.join(random.choice(string.letters) for x in xrange(5))
	
	def makeHashpassword(self):
		if self.salt == "":
			self.salt = self.makeSalt()
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
	
	def setChannel(self):
		if self.token == "":
			token = channel.create_channel(self.username)
			if token:
				self.token = token
				self.save()
			else:
				MyLogs("Channel creation failure")
				return False
		return True

	#~ def addAppUser(self):
		#~ self.loginStatus = "registered"
		#~ appuser = AppUser(id=self.username)
		#~ appuser.username = self.username
		#~ appuser.role = self.role
		#~ appuser.hashpassword = self.hashpassword
		#~ appuser.loginStatus = self.loginStatus
		#~ key = appuser.safePut()
		#~ return key

	def logout(self):
		self.token = ""
		#~ self.loginStatus = "registered"
		if self.role == "student":
			logic.disconnect_student(self.username)
		else:
			logic.disconnectTeacher(self.username)
		self.save()
		#~ if self.updateAttr("loginStatus") and self.updateAttr("token"):
			#~ return True
		#~ else:
			#~ return False

	def usernameNotYetExisting(self):
		if self.get() == None:
			return True
		else:
			return False

	
		
	#~ def updateAttr(self, attribute):
		#~ appuser = self.getAppUser()
		#~ if appuser:
			#~ setattr(appuser, attribute, getattr(self, attribute))
			#~ if appuser.safePut():
				#~ return True
			#~ else:
				#~ MyLogs("updateAttr", attribute, ":safe put didn't work")
		#~ else:
			#~ MyLogs("updateAttr", attribute, ":error. user not retrieved")
		#~ return False
	
	#~ def validUser(self):
		""" check if the user is entitled to login.
		input=username string and password not hashed
		return True if user is valid.
		
		"""
		#~ user = self.getAppUser()
		#~ if user:
			#~ if self.hashpassword == "":
				#~ self.salt = user.hashpassword.split("|")[1]
				#~ self.makeHashpassword()
			#~ if self.hashpassword == user.hashpassword:
				#~ self.role = user.role
				#~ self.token = user.token
				#~ self.loginStatus = "logged"
				#~ self.updateAttr("loginStatus")
				#~ return True
			#~ else:
				#~ MyLogs("Password incorrect for user", self.username)
		#~ else:
			#~ MyLogs("Username not in database")
			#~ return False

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
		
	def validUserFromCookie(self):
		""" check if the request is coming from a valid user.
		return the user object if valid, else False
		
		"""
		cookie = Cookie(self.getUserCookie())
		if cookie.value:
			user = User()
			user.setUsername(cookie.username)
			user.setHashpassword(cookie.hashpassword)
			if user.get():
				return user
			else:
				MyLogs("MainHandler:Invalid cookie")
		else:
			MyLogs("MainHandler:cookie is not existing or has not value")
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
		user = logic.getStudent(username)
		if action == "disconnected" and user:
			logic.disconnect_student(username)

class LoginPageHandler(MainHandler):
	error = ""

	def enterLesson(self, user):
		if user.role == "teacher":
			self.redirect("/lesson/start_lesson")
		elif user.role == "student":
			#~ logic.connect_student(user.username)
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
			if user.get():
				user.setChannel()
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
		if user.usernameNotYetExisting():
			if user.usernameIsValid():
				if user.passwordIsValid():
					user.save()
					user.setChannel()
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
			if user.get():
				user.logout()
				self.clearCookies()
			else:
				MyLogs("Invalid cookie")
		else:
			MyLogs("cookie is not existing or has not value")
		self.redirect("/check/in")


class ExerciseHandler(MainHandler):
	def post(self, strExerciseType):
		user = self.validUserFromCookie()
		if user:
			assert user.role == "student"
			objStudent = logic.getStudent(user.username)
			objLesson = logic.get_lesson(self.getLessonCookie())
			strTeacher = objLesson.teacher
			objTeacher = logic.getTeacher(strTeacher)
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
			channel.send_message(objTeacher.token, message)
		else:
			self.redirect("/check/in")

class SessionHandler(MainHandler):
	def post(self, command):
		user = self.validUserFromCookie()
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
				self.sendExerciseToStudents(
							objExercise,
							objSession.students,
							objType,
							)
	
	def sendExerciseToStudents(self, exercise, students, type):
		message = {
			"type": "exercise",
			"message": {
				"exercise": exercise,
				"type": type,
				},
			}
		message = json.dumps(message)
		for student in students:
			
			user = logic.getStudent(student)
			channel.send_message(user.token, message)

class LessonHandler(MainHandler):

	def post(self, command):
		user = self.validUserFromCookie()
		if user:
			
			if command == "start_lesson":
				assert user.role == "teacher"
				strLessonName = self.request.get("lesson")
				logic.addLesson(user.username, user.token, strLessonName)
				self.setLessonCookie(strLessonName)
				return self.redirect("/lesson/dashboard")
			elif command == "join_lesson":
				assert user.role == "student"
				strTeacherName = self.request.get("teacher")
				strLessonName = logic.joinLesson(user.username, user.token, strTeacherName)
				self.setLessonCookie(strLessonName)
				return self.redirect("/lesson/join_session")
		else:
			return self.redirect("/check/in")

	def get(self, command):
		
		user = self.validUserFromCookie()
		#~ raise Exception
		if user:
			if command == "dashboard":
				exerciseList = getExerciseList()
				studentsList = logic.getCurrentLessonStudentList(user.username) or []
				self.render_page("dashboard.html",
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
				currentTeachers = logic.getTeachersList()
				self.render_page("join_lesson.html",
							username = user.username,
							token = user.token,
							current_teachers = currentTeachers,
							)
				return
			elif command == "join_session":
				assert user.role == "student"
				strLessonName = self.getLessonCookie()
				if not logic.checkInLesson(user.username, strLessonName):
					self.response.delete_cookie('schooltagging-lesson', path = '/')
				#~ logic.connect_student(user.username)
				self.render_page("join_session.html",
							username = user.username,
							token = user.token,
							)
		else:
			self.redirect("/check/in")

class DataHandler(MainHandler):

	def get(self, command):
		user = self.validUserFromCookie()
		if user:
			if command == "exercises_list":
				message = {
					"type": "exercises_list",
					"message": getExerciseList(),
					}
				message = json.dumps(message)
				channel.send_message(user.token, message)
		else:
			return self.redirect("/check/in")

class JollyHandler(MainHandler):
	def get(self, *a):
		return self.redirect("/check/in")
			
app = webapp2.WSGIApplication([
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
	webapp2.Route(
			r'/<:[a-zA-Z0-9]*>',
			handler=JollyHandler,
			name="jolly"),
			])

dictLabelBook = {
	"TeacherLogin": {
		"username": {
			"EN": "Username",
			"IT": "Nome utente",
			},
		"password": {
			"EN": "Password",
			"IT": "Password",
			},
		"or_signup": {
			"EN": "or Signup",
			"IT": "oppure registrati",
			},
		"login": {
			"EN": "Login",
			"IT": "Entra",
			},
		},
	"TeacherSignup": {
		"username": {
			"EN": "Username",
			"IT": "Nome utente",
			},
		"password": {
			"EN": "Password",
			"IT": "Password",
			},
		"verify": {
			"EN": "Verify password",
			"IT": "Ripeti la password",
			},
		"register": {
			"EN": "Register my data",
			"IT": "Registrami",
			},
		},
	"TeacherLessonStart": {
		"lesson_name": {
			"EN": "Lesson name",
			"IT": "Nome per la lezione",
			},
		"": {
			"EN": "",
			"IT": "",
			},
		"welcome": {
			"EN": "Welcome",
			"IT": "Benvenuto",
			},
		"start": {
			"EN": "Start the lesson",
			"IT": "Inizia la lezione",
			},
		},
	}
