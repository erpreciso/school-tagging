# coding: utf-8
# [school-tagging] webapp

import os
import re
import random
import string
import hashlib
import logging
from google.appengine.ext import ndb
from google.appengine.api import memcache

class User():
	RE_USERNAME = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
	RE_PASSWORD = r"^.{3,20}$"
	
	def __init__(self):
		self.username = ""
		self.password = ""
		self.hashpassword = ""
		self.token = ""
		self.salt = ""
		
	def get(self):
		teacher = memcache.get("%s:teacher" % self.username)
		if teacher is None:
			q = Teacher.query(Teacher.username == self.username)
			if q.get():
				teacher = q.get()
				memcache.add("%s:teacher" % self.username, teacher)
			else:
				return "USERNAME NOT FOUND IN DB"
		if self.hashpassword == "":
			self.salt = teacher.hashpassword.split("|")[1]
			self.makeHashpassword()
		if self.hashpassword == teacher.hashpassword:
			self.token = teacher.token
			return "OK"
		else:
			return "PASSWORD DOESNT MATCH WITH DB"
			
	def save(self):
		if self.usernameNotYetExisting():
			if self.usernameIsValid():
				if self.passwordIsValid():
					self.putInDb()
					return "OK"
				else:
					return "PASSWORD NOT VALID"
			else:
				return "USERNAME NOT VALID"
		else:
			return "USERNAME ALREADY EXISTING"
		
		
	def putInDb(self):
		teacher = Teacher(id=self.username)
		teacher.username = self.username
		teacher.hashpassword = self.hashpassword
		teacher.token = self.token
		key = teacher.put()
		memcache.set("%s:teacher" % self.username, self)
		return key
	
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

		
	def makeSalt(self):
		return ''.join(random.choice(string.letters) for x in xrange(5))
	
	def makeHashpassword(self):
		if self.salt == "":
			self.salt = self.makeSalt()
		cript = self.username + self.password + self.salt
		encr_password = hashlib.sha256(cript).hexdigest()
		self.hashpassword = "%s|%s" % (encr_password, self.salt)

	def usernameNotYetExisting(self):
		if self.get() != "OK":
			return True
		else:
			return False
		
	def twoPasswordsMatch(self):
		""" return True if the two inserted psw match. """
		match = self.password == self.verifyPassword
		if match:
			return True
		else:
			logging.warning("The two passwords don't match")

	def passwordMatchesRE(self):
		""" return True if the psw matches the regular expression. """
		re_password = re.compile(self.RE_PASSWORD)
		if re_password.match(self.password):
			return True
		else:
			logging.warning("Password doesn't match the regex")
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
			logging.warning("Password rejected. See log above")
			return False

	def usernameIsValid(self):
		""" return True if the inserted username matchs the re. """
		re_username = re.compile(self.RE_USERNAME)
		if re_username.match(self.username):
			return True
		else:
			logging.warning("Username rejected (it doesn't match the regex)")
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
	
def nowtime():
	return strftime("%Y-%m-%d-%H:%M:%S", localtime())

class Person(ndb.Model):
	username = ndb.StringProperty()
	currentLesson = ndb.StringProperty()
	hashpassword = ndb.StringProperty()
	#~ connected = ndb.BooleanProperty()
	token = ndb.StringProperty()

class Teacher(Person):
	lessons = ndb.StringProperty(repeated=True)
	def safe_put(self):
		memcache.set("teacher:" + self.name, self)
		self.put()
		
class Student(Person):
	answers = ndb.PickleProperty()
	def safe_put(self):
		memcache.set("student:" + self.name, self)
		self.put()

class Lesson(ndb.Model):
	name = ndb.StringProperty()
	sessions = ndb.StringProperty(repeated=True)
	teacher = ndb.StringProperty()
	students = ndb.StringProperty(repeated=True)
	currentSession = ndb.StringProperty()
	
	def safe_put(self):
		memcache.set("lesson:" + self.name, self)
		self.put()

def addTeacher(strTeacher, strLesson):
	objTeacher = Teacher(id=strTeacher)
	objTeacher.name = strTeacher
	objTeacher.lessons = []
	objTeacher.currentLesson = strLesson
	objTeacher.safe_put()
	updateTeachersList("add", strTeacher)
	return objTeacher


def getTeachersList():
	lst = memcache.get("teachers_list")
	if not lst:
		lst = []
		q = Teacher.query()
		if q.get():
			lst = [t.name for t in q]
		memcache.add("teachers_list", lst)
	return lst
				
def updateTeachersList(command, strTeacher):
	lst = getTeachersList()
	if command == "add":
		lst.append(strTeacher)
	elif command == "remove":
		lst.remove(strTeacher)
	memcache.set("teachers_list", lst)
	return

def addStudent(strStudent, strToken, strLesson):
	objStudent = Student(id=strStudent)
	objStudent.name = strStudent
	objStudent.token = strToken
	objStudent.currentLesson = strLesson
	objStudent.answers = {}
	#~ objStudent.connected = True
	objStudent.safe_put()
	return objStudent

def disconnect_student(strStudent):
	student = getStudent(strStudent)
	if student:
		#~ student.connected = False
		student.token = ""
		student.safe_put()

def disconnectTeacher(strTeacher):
	teacher = getTeacher(strTeacher)
	if teacher:
		teacher.token = ""
		
#~ def connect_student(strStudent):
	#~ student = getStudent(strStudent)
	#~ if student and not student.connected:
		#~ student.connected = True
		#~ student.safe_put()
	
def getCurrentLessonStudentList(strTeacher):
	"""return list of string students for the current lesson of the teacher."""
	objTeacher = getTeacher(strTeacher)
	if objTeacher:
		strCurrentLesson = objTeacher.currentLesson
		objCurrentLesson = get_lesson(strCurrentLesson)
		students = [s for s in objCurrentLesson.students \
							if getStudent(s).token != ""]
		return students
	else:
		return False
	
def getTeacher(strTeacher):
	t = memcache.get("teacher:" + strTeacher)
	if not t:
		k = ndb.Key("Teacher", strTeacher)
		t = k.get()
		memcache.add("teacher:" + strTeacher, t)
	return t

def getStudent(strStudent):
	t = memcache.get("student:" + strStudent)
	if not t:
		k = ndb.Key("Student", strStudent)
		if k.get():
			t = k.get()
			memcache.add("student:" + strStudent, t)
	return t

def addLesson(strTeacher, strLesson):
	objTeacher = addTeacher(strTeacher, strLesson)
	objLesson = Lesson(id=strLesson)
	objLesson.name = strLesson
	objLesson.teacher = strTeacher
	objLesson.safe_put()
	return objLesson

def get_lesson(strLesson):
	t = memcache.get("lesson:" + strLesson)
	if not t:
		k = ndb.Key("Lesson", strLesson)
		t = k.get()
		memcache.add("lesson:" + strLesson, t)
	return t

def joinLesson(strStudent, strToken, strTeacher):
	objTeacher = getTeacher(strTeacher)
	strLesson = objTeacher.currentLesson
	objStudent = addStudent(strStudent, strToken, strLesson)
	objLesson = get_lesson(strLesson)
	if strStudent not in objLesson.students:
		objLesson.students.append(strStudent)
	objLesson.safe_put()
	return strLesson

def checkInLesson(strStudent, strLesson):
	objStudent = getStudent(strStudent)
	if objStudent and objStudent.currentLesson == strLesson:
		objLesson = get_lesson(strLesson)
		if strStudent not in objLesson.students:
			objLesson.students.append(strStudent)
			objLesson.safe_put()
		return True
	else:
		return False
	
	
class Session(ndb.Model):
	start = ndb.StringProperty()
	exercise = ndb.PickleProperty()
	exerciseType = ndb.PickleProperty()
	lesson = ndb.StringProperty()
	students = ndb.StringProperty(repeated=True)
	
	def safe_put(self):
		memcache.set("session:" + self.start, self)
		self.put()
	def is_correct(self, answer):
		if self.exerciseType["type"] == "find_element":
			answer = int(answer)
			answers = self.exerciseType["answers"]
		elif self.exerciseType["type"] == "which_type":
			answers = [self.exerciseType["options"][a] for a in self.exerciseType["answers"]]
		return answer in answers

def add_session(objLesson, objExercise, objExerciseType):
	strSession = nowtime()
	objSession = Session(id=strSession)
	objSession.start = strSession
	objSession.lesson = objLesson.name
	objSession.exercise = objExercise
	objSession.exerciseType = objExerciseType
	objSession.students = objLesson.students
	objSession.safe_put()
	objLesson.currentSession = strSession
	if strSession not in objLesson.sessions:
		objLesson.sessions.append(strSession)
	objLesson.safe_put()
	return strSession

def get_session(strSession):
	t = memcache.get("session:" + strSession)
	if not t:
		k = ndb.Key("Session", strSession)
		t = k.get()
		memcache.add("session:" + strSession, t)
	return t

def add_answer(objStudent, objLesson, strExerciseType, strAnswer):
	strSession = objLesson.currentSession
	objSession = get_session(strSession)
	if strSession in objStudent.answers.keys():
		objStudent.answers[strSession].append(strAnswer)
	else:
		objStudent.answers[strSession] = [strAnswer]
	booCorrect = objSession.is_correct(strAnswer)
