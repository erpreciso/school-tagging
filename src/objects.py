from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api import channel
# import logging
import json
import random
import re

class User(ndb.Model):
	username = ndb.StringProperty()
	status = ndb.StringProperty()
	currentLessonID = ndb.IntegerProperty()
	currentLessonName = ndb.StringProperty()
	lessons = ndb.IntegerProperty(repeated=True)
	token = ndb.StringProperty()
	currentSession = ndb.IntegerProperty()

	def connect(self):
		self.token = channel.create_channel(str(self.key.id()))
		self.status = "connected"
		self.save()
	
	def assignLesson(self, lessonID, lessonName):
		self.currentLessonID = lessonID
		self.currentLessonName = lessonName
		self.lessons.append(lessonID)
		self.save()

class Student(User):
	answers = ndb.PickleProperty()
# 		{sessionID1: answer, sessionID2: answer}
		
	def save(self):
		if self.currentLessonID == None:
			cl = "Empty"
		else:
			cl = self.currentLessonID
		self.put()
		memcache.set("Student:" + self.username + \
					"|CurrentLesson:" + str(cl), self)
		
	def joinLesson(self, lessonName):
		assert lessonName in getOpenLessonsNames()
		lesson = getLessonFromName(lessonName)
		lesson.addStudent(self)
		self.currentLessonID = lesson.key.id()
		self.currentLessonName = lessonName
		self.answers = []
		self.save()
		self.alertTeacherImArrived()
		return lesson.key.id()
	
	def exitLesson(self):
		lesson = getLesson(self.currentLessonID)
		lesson.removeStudent(self)
		self.currentLessonID = None
		self.currentLessonName = ""
# 		TODO: send message to student and redraw their dashboard
		self.save()
	
	def exitSession(self):
		if self.currentSession:
			session = getSession(self.currentSession)
			session.removeStudent(self)
			self.currentSession = None
			self.save()
	
	def alertTeacherImArrived(self):
		lesson = getLesson(self.currentLessonID)
		teacher = getTeacher(lesson.teacher)
		message = {
			"type": "student arrived",
			"message": {
				"studentName": self.username
				},
			}
		message = json.dumps(message)
		channel.send_message(teacher.token, message)
	
	def logout(self):
		self.alertTeacherImLogout()
		self.exitLesson()
		self.exitSession()
		self.token = ""
		self.status = ""
		self.save()
			
	def addAnswer(self, answer):
		self.answers.append({"session": self.currentSession, "answer": answer})
		self.save()
		
	def alertTeacherImLogout(self):
		# TODO merge all messages to alert teacher
		lesson = getLesson(self.currentLessonID)
		teacher = getTeacher(lesson.teacher)
		message = {
			"type": "student logout",
			"message": {
				"studentName": self.username
				},
			}
		message = json.dumps(message)
		channel.send_message(teacher.token, message)
	
class Teacher(User):
	password = ndb.StringProperty()
	def save(self):
		self.put()
		memcache.set("Teacher:" + self.username, self)
		
	def logout(self):
		self.currentLessonID = None
		self.currentLessonName = ""
		self.currentSession = None
		self.token = ""
		self.status = ""
		self.save()
		
def teacherUsernameExists(username):
	if getTeacher(username):
		return True
	else:
		return False

def getTeacher(username):
	teacher = memcache.get("Teacher:" + username)
	if not teacher:
		q = Teacher.query(Teacher.username == username)
		teacher = q.get()
		if teacher:
			memcache.set("Teacher:" + username, teacher)
	if teacher:
		return teacher
	else:
		return False

def getStudent(username, currentLessonID):
	student = memcache.get("Student:" + username + \
					"|CurrentLesson:" + str(currentLessonID))
	if not student:
		q = Student.query(Student.username == username,
							Student.currentLessonID == currentLessonID)
		student = q.get()
		if student:
			memcache.set("Student:" + username + \
					"|CurrentLesson:" + str(currentLessonID), student)
	if student:
		return student
	else:
		return False
		
def getFromID(sid):
	user = memcache.get("ID:" + sid)
	if not user:
		user = ndb.Key("Teacher", int(sid)).get() \
							or ndb.Key("Student", int(sid)).get()
		#~ user = ndb.get_by_id(int(id))
		if user:
			memcache.set("ID:" + str(sid), user)
	if user:
		return user
	else:
		return False
	
def studentAlreadyConnected(username):
	q = Student.query(Student.username == username,
						Student.currentLessonID != None)
	if q.get():
		return True
	else:
		return False
	
class Lesson(ndb.Model):
	lessonName = ndb.StringProperty()
	teacher = ndb.StringProperty()
	status = ndb.StringProperty()
	sessions = ndb.StringProperty(repeated=True)
	students = ndb.StringProperty(repeated=True)
	datetime = ndb.DateTimeProperty(auto_now_add=True)

	def end(self):
		teacher = getTeacher(self.teacher)
		for studentName in self.students:
			student = getStudent(studentName, self.key.id())
			student.exitLesson()
		teacher.currentLessonID = None
		teacher.currentLessonName = ""
		teacher.save()
		self.status = "closed"
		self.save()
		
	def save(self):
		self.put()
		memcache.set("Lesson:" + str(self.key.id()), self)
		return self.key.id()
	
	def addStudent(self, student):
		self.students.append(student.username)
		self.save()
	
	def removeStudent(self, student):
		if student.username in self.students:
			self.students.remove(student.username)
			self.save()
	
	def start(self, lessonName, teacher):
		self.lessonName = lessonName
		self.teacher = teacher.username
		self.status = "open"
		self.students = []
		self.sessions = []
		lessonID = self.save()
		teacher.assignLesson(lessonID, lessonName)

def getOpenLessonsID():
	q = Lesson.query(Lesson.status == "open")
	if q.count(limit=None) > 0:
		lessons = q.fetch(limit=None)
		return [lesson.key.id() for lesson in lessons]
	else:
		return []

def getOpenLessonsNames():
	q = Lesson.query(Lesson.status == "open")
	if q.count(limit=None) > 0:
		lessons = q.fetch(limit=None)
		return [lesson.lessonName for lesson in lessons]
	else:
		return []
	
def getLesson(lessonID):
	lesson = memcache.get("Lesson:" + str(lessonID))
	if not lesson:
		lesson = ndb.Key("Lesson", lessonID).get()
		if lesson:
			memcache.set("Lesson:" + str(lessonID), lesson)
	if lesson:
		return lesson
	else:
		return False
	
def getLessonFromName(lessonName):
	q = Lesson.query(Lesson.lessonName == lessonName)
	teacher = q.get()
	if teacher:
		return teacher
	else:
		return False

def getSession(sessionID):
	session = memcache.get("Session:" + str(sessionID))
	if not session:
		session = ndb.Key("Session", sessionID).get()
		if session:
			memcache.set("Session:" + str(sessionID), session)
	if session:
		return session
	else:
		return False
	
def getSentence():
	pool = open("sentence-pool.txt").readlines()
	i = int(random.random() * len(pool))
	return pool[i]
	
def clean():
	ndb.delete_multi(Lesson.query().fetch(keys_only=True))
	ndb.delete_multi(Session.query().fetch(keys_only=True))
	ndb.delete_multi(Student.query().fetch(keys_only=True))
	ndb.delete_multi(Teacher.query().fetch(keys_only=True))
	memcache.flush_all()


class Session(ndb.Model):
	teacher = ndb.StringProperty()
	lesson = ndb.IntegerProperty()
	students = ndb.StringProperty(repeated=True)
	datetime = ndb.DateTimeProperty(auto_now_add=True)
	exerciseText = ndb.StringProperty()
# 		sentence to be analized from the student
	target = ndb.IntegerProperty()
# 		index of the word that the student should recognize
	answersProposed = ndb.StringProperty(repeated=True)
# 		options available for the student
	exerciseWords = ndb.StringProperty(repeated=True)
# 		list of the words componing the exercise
	validatedAnswer = ndb.IntegerProperty()
# 		index of the teacher's validated answer in the answersProposed list
	studentAnswers = ndb.PickleProperty()
# 	 	{student1: answer1, student2: answer2}
	answersStudents = ndb.PickleProperty()
# 		{answer1:[student1, student2], answer2:[], answer3:[student3]}
	
	def addStudentAnswer(self, studentName, answer):
		self.studentAnswers[studentName] = answer
		if answer in self.answersStudents.keys():
			self.answersStudents[answer].append(studentName)
		else:
			self.answersStudents[answer] = [studentName]
		self.save()
		
	def save(self):
		self.put()
		memcache.set("Session:" + str(self.key.id()), self)
		return self.key.id()
		
	def sendStatusToTeacher(self):
		teacher = getTeacher(self.teacher)
		status = {
			"type": "sessionStatus",
			"message": {
				"possibleAnswers": self.answersStudents,
				"totalAnswers": {
					"answered": self.studentAnswers.keys(),
					"missing": [s for s in self.students \
									if s not in self.studentAnswers.keys()]
					}
				},
			}
		channel.send_message(teacher.token, json.dumps(status))
	
	def removeStudent(self, student):
		self.students.remove(student.username)
		self.save()
	
	def start(self, lessonID):
		self.lessonID = lessonID
		lesson = getLesson(lessonID)
		self.teacher = lesson.teacher
		self.students = lesson.students
		self.exerciseText = getSentence()
		self.exerciseWords = re.split(' ', self.exerciseText)
		self.answersProposed = ["Noun", "Adj", "Verb"]
		self.studentAnswers = {}
		self.answersStudents = {}
		self.target = int(random.random() * len(self.exerciseWords))
		sid = self.save()
		teacher = getTeacher(self.teacher)
		teacher.currentSession = self.key.id()
		teacher.save()
		message = {
			"type": "session",
			"message": {
				"id": sid,
				"wordsList": self.exerciseWords,
				"answersProposed": self.answersProposed,
				"target": self.target
				},
			}
		message = json.dumps(message)
		channel.send_message(teacher.token, message)
		for studentName in self.students:
			student = getStudent(studentName, self.lessonID)
			student.currentSession = sid
			student.save()
			channel.send_message(student.token, message)
		self.sendStatusToTeacher()
