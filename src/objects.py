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
		message = {"type": "lessonTerminated"}
		message = json.dumps(message)
		channel.send_message(self.token, message)
		self.currentLessonID = None
		self.currentLessonName = ""
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
			"type": "studentArrived",
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
		session = getSession(self.currentSession)
		if session.open:
			self.answers.append({"session": self.currentSession, "answer": answer})
			self.save()
		
	def alertTeacherImLogout(self):
		# TODO: merge all messages to alert teacher
		lesson = getLesson(self.currentLessonID)
		teacher = getTeacher(lesson.teacher)
		message = {
			"type": "studentLogout",
			"message": {
				"studentName": self.username
				},
			}
		message = json.dumps(message)
		channel.send_message(teacher.token, message)
	
	def alertTeacherImAlive(self):
		# TODO: merge all messages to alert teacher
		lesson = getLesson(self.currentLessonID)
		teacher = getTeacher(lesson.teacher)
		message = {
			"type": "studentAlive",
			"message": {
				"studentName": self.username
				},
			}
		message = json.dumps(message)
		channel.send_message(teacher.token, message)
	
	def warnTeacherImOffline(self):
		# TODO: merge all messages to alert teacher
		lesson = getLesson(self.currentLessonID)
		teacher = getTeacher(lesson.teacher)
		message = {
			"type": "studentDisconnected",
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
		
	def sendPingToStudent(self, studentName):
		lesson = getLesson(self.currentLessonID)
		student = getStudent(studentName, self.currentLessonID)
		message = {"type": "pingFromTeacher"}
		message = json.dumps(message)
		channel.send_message(student.token, message)
	
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
	
def studentAlreadyConnected(username, lessonName):
	q = Student.query(Student.username == username,
						Student.currentLessonName == lessonName)
	if q.get():
		return True
	else:
		return False
	
class Lesson(ndb.Model):
	lessonName = ndb.StringProperty()
	teacher = ndb.StringProperty()
	status = ndb.StringProperty()
	sessions = ndb.IntegerProperty(repeated=True)
	students = ndb.StringProperty(repeated=True)
	datetime = ndb.DateTimeProperty(auto_now_add=True)

	def start(self, lessonName, teacher):
		self.lessonName = lessonName
		self.teacher = teacher.username
		self.status = "open"
		self.students = []
		self.sessions = []
		lessonID = self.save()
		teacher.assignLesson(lessonID, lessonName)

	def save(self):
		self.put()
		memcache.set("Lesson:" + str(self.key.id()), self)
		return self.key.id()

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
		
	def addStudent(self, student):
		self.students.append(student.username)
		self.save()
	
	def addSession(self, sessionID):
		self.sessions.append(sessionID)
		self.save()
	
	def removeStudent(self, student):
		if student.username in self.students:
			self.students.remove(student.username)
			self.save()
	
	def produceAndSendStats(self):
		teacher = getTeacher(self.teacher)
		stats = None
		if self.sessions:
			stats = []
			for sessionID in self.sessions:
				ses = getSession(sessionID)
				if ses:
					students = ses.studentAnswers.keys()
					if students:
						corrects = [st for st in students \
							if ses.studentAnswers[st] == ses.validatedAnswer]
						stats += corrects
# 		TODO: include names even if they're 0
		statsDict = {}
		for name in stats:
			if name in statsDict.keys():
				statsDict[name] += 1
			else:
				statsDict[name] = 1 
		message = {
			"type": "lessonStats",
			"message": {
				"stats": statsDict
				},
			}
		message = json.dumps(message)
		channel.send_message(teacher.token, message)
	
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
	lesson = q.get()
	if lesson:
		return lesson
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
	open = ndb.BooleanProperty()
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
	validatedAnswer = ndb.StringProperty()
# 		index of the teacher's validated answer in the answersProposed list
	studentAnswers = ndb.PickleProperty()
# 	 	{student1: answer1, student2: answer2}
	answersStudents = ndb.PickleProperty()
# 		{answer1:[student1, student2], answer2:[], answer3:[student3]}
	
	def addStudentAnswer(self, studentName, answer):
		if self.open:
			self.studentAnswers[studentName] = answer
			if answer in self.answersStudents.keys():
				self.answersStudents[answer].append(studentName)
			else:
				self.answersStudents[answer] = [studentName]
			self.save()
		
	def addValidAnswer(self, validAnswer):
		self.validatedAnswer = validAnswer
		self.save()
		
	def sendFeedbackToStudents(self):
		for studentName in self.students:
			student = getStudent(studentName, self.lesson)
			myanswer = [a["answer"] for a in student.answers \
					if a["session"] == self.key.id()]
			if myanswer:
				myanswer = myanswer[0]
				message = {
					"type": "validAnswer",
					"message": {
						"validAnswer": self.validatedAnswer,
						"myAnswer": myanswer
						}
					}
			else:
				message = {
						"type": "sessionExpired",
						"message": {"validAnswer": self.validatedAnswer}
						}
			message = json.dumps(message)
			channel.send_message(student.token, message)
		
	def save(self):
		self.put()
		memcache.set("Session:" + str(self.key.id()), self)
		return self.key.id()
		
	def sendStatusToTeacher(self):
		if self.open:
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
	
	def end(self):
		self.open = False
		self.save()
		
	def start(self, lessonID):
		self.lesson = lessonID
		lesson = getLesson(lessonID)
		self.teacher = lesson.teacher
		self.students = lesson.students
		self.exerciseText = getSentence()
		self.exerciseWords = re.split(' ', self.exerciseText)
		self.answersProposed = ["Noun", "Adj", "Verb"]
		self.studentAnswers = {}
		self.answersStudents = {}
		self.open = True
		self.target = int(random.random() * len(self.exerciseWords))
		sid = self.save()
		lesson.addSession(sid)
		teacher = getTeacher(self.teacher)
		teacher.currentSession = self.key.id()
		teacher.save()
		message = {
			"type": "sessionExercise",
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
			student = getStudent(studentName, self.lesson)
			student.currentSession = sid
			student.save()
			channel.send_message(student.token, message)
		self.sendStatusToTeacher()
		
		def pushResultsToTeacher(self):
			pass